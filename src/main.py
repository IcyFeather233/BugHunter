from BCEmbedding.tools.langchain import BCERerank
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain.retrievers import ContextualCompressionRetriever
from langchain.schema import Document
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents.map_reduce import MapReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.reduce import ReduceDocumentsChain
import random
import configparser
import os
import json
import time

from utils import *
from actions import *
from logger import Log
from record import Record


config = configparser.ConfigParser()

config.read('config.ini')

readme_path = config.get('Paths', 'readme_path')
selected_app_path = config.get('Paths', 'selected_app_path')

# init embedding model and reranker model
embedding_model_name = config.get('Paths', 'embedding_model_name')
reranker_model_name = config.get('Paths', 'reranker_model_name')
embedding_model_kwargs = {'device': 'cuda'}
embedding_encode_kwargs = {'batch_size': 32, 'normalize_embeddings': True, 'show_progress_bar': False}

embed_model = HuggingFaceEmbeddings(
  model_name=embedding_model_name,
  model_kwargs=embedding_model_kwargs,
  encode_kwargs=embedding_encode_kwargs
)

reranker_args = {'model': reranker_model_name, 'top_n': 10, 'device': 'cuda'}
reranker = BCERerank(**reranker_args)

# init documents
documents = []

readme_path = config.get('Paths', 'readme_path')
selected_app_path = config.get('Paths', 'selected_app_path')

for file_name in os.listdir(readme_path):
    if file_name.endswith('.txt'):
        file_path = os.path.join(readme_path, file_name)
        loader = TextLoader(file_path, encoding='utf-8')
        documents.extend(loader.load())

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

# Check if FAISS index exists, if not, create it
faiss_index_path = './readme_cache'
if os.path.exists(faiss_index_path):
    # Load the existing FAISS index
    vectorstore = FAISS.load_local(faiss_index_path, embed_model)
else:
    # Create a new FAISS index and save it
    vectorstore = FAISS.from_documents(texts, embed_model, distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT)
    vectorstore.save_local(faiss_index_path)

# retrieval with embedding and reranker
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})

compression_retriever = ContextualCompressionRetriever(
    base_compressor=reranker, base_retriever=retriever
)


# init Android logger and recorder
log = Log()
logger = log.logger

android_device = config.get('uiautomator2', 'android_device')
record = Record(android_device)
logger.info("Record initialized, uiautomator2 initialized.")

logger.debug(f"Current Page Info: {record.get_running_info()}")


record.record()

cur_step = record.current_steps
logger.info(f"Now is the {cur_step}-th step")


file_path = f'screenshots/{cur_step}.jpg'

prompt = f"The app name is {record.get_running_info()['app']}, and current activity is {record.get_running_info()['activity']}."
prompt += "Please generate a very short README(less than 200 tokens) of this APP based on the screenshot information of the interface."

logger.info("generate README prompt:")
logger.info(prompt)
app_desc = get_response_from_lm([file_path], prompt)
logger.info("generated README:")
logger.info(app_desc)

logger.info("app description:")
logger.info(app_desc)

response = compression_retriever.get_relevant_documents(app_desc)

logger.info("retrieval app-level relevant documents:")
logger.info(response)

relevance_score_list = []
available_issues_list = []
available_issue_number_list = []
app_name_list = []
github_link_list = []

for each_response in response:
    logger.info(each_response.metadata['source'])
    logger.info("relevance_score: %s", each_response.metadata['relevance_score'])
    relevance_score_list.append(each_response.metadata['relevance_score'])
    each_source_hash = each_response.metadata['source'].split('\\')[-1].split('.')[0]
    each_repo_issues = find_matching_github_links(each_source_hash)
    logger.info("app_name: %s", each_repo_issues[0]['app_name'])
    logger.info("github link: %s", each_repo_issues[0]['github_link'])
    app_name_list.append(each_repo_issues[0]['app_name'])
    github_link_list.append(each_repo_issues[0]['github_link'])
    logger.info("len(each_repo_issues): %d", len(each_repo_issues))
    available_issues = [each for each in each_repo_issues if each['level'] <= 1]
    available_issues_list.append(available_issues)
    logger.info("len(available_issues): %d", len(available_issues))
    available_issue_number_list.append(len(available_issues))


prompt = """
## Role
You are an Android app tester.

## Task
You will be provided with the similarity of the app's README and the number of quality issues on the app's Github that can be referred to.
And you should choose one app from the following data for reference.
You should choose the app with a higher number of available issues, as long as the relevance score is acceptable.
This way, you can have more data to refer to.
You can only choose one app. 
If there is a reference app with the same name or package name as this app, it is necessary to skip this app and proceed to the second most suitable option.

## Similar Apps Information
"""

for i in range(len(available_issue_number_list)):
    prompt += f"id: {i}, relevance score: {relevance_score_list[i]}, available issues: {available_issue_number_list[i]}"

prompt += """
## Expected Output
Please give your answer in JSON format and provide reasons.

```json
{
  "selected_app": "id(just a number, like: 1, 2, ..)",
  "reason": "your reason"
}
```
"""

logger.info("selected app prompt:")
logger.info(prompt)

chosen_reference_app = get_response_from_lm([], prompt)

logger.info("chosen reference app:")
logger.info(chosen_reference_app)

chosen_app_id = int(extract_json_from_str(chosen_reference_app)['selected_app'])

logger.info("chosen app name:")
logger.info(app_name_list[chosen_app_id])
logger.info("chosen github link:", github_link_list[chosen_app_id])


relevant_documents = available_issues_list[int(chosen_app_id)]


documents = []

for item in relevant_documents:
    if item['issue_description'] and item['issue_description'] != 'nan':
        documents.append(Document(page_content=item['issue_description']))

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
texts = text_splitter.split_documents(documents)

# sample 20 for accelerate
if len(texts) > 20:
    random_20_texts = random.sample(texts, 20)
else:
    random_20_texts = texts


llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)


map_template = """The following is a set of issue descriptions taken from an app, 
they are delimited by ``` . 

Based on these descriptions please create a comprehensive list of functionalities 
where bug defects are found. 

If similar categories are encountered, try to consolidate them into a larger category.

If a description does not relate to any specific functionality, 
please do not include them in the list of generated functionalities.
```
{issues}
```
"""


map_prompt = PromptTemplate.from_template(map_template)
map_chain = LLMChain(llm=llm, prompt=map_prompt)


reduce_template = """The following is a set of functionalities where bug defects are found, 
which are delimited by ``` .

Take these and organize these into a final, consolidated list of unique functionalities. 

You should combine functionalities into one that are similar but use different variations of 
the same words. If similar categories are encountered, try to consolidate them into a larger category.

Also, you should combine functionalities that use an acronym versus the full spelling. 

For example, 'Login Issues' and 'Sign-in Problems' should be a single functionality called 
'Login/Sign-in Issues'.

{format_instructions}

```
{functionalities}
```
"""

output_parser = CommaSeparatedListOutputParser()
format_instructions = output_parser.get_format_instructions()

reduce_prompt = PromptTemplate(template=reduce_template,
                               input_variables=["functionalities"],
                               partial_variables={"format_instructions": format_instructions})
reduce_chain = LLMChain(llm=llm, prompt=reduce_prompt)


combine_documents_chain = StuffDocumentsChain(
    llm_chain=reduce_chain, document_variable_name="functionalities"
)


reduce_documents_chain = ReduceDocumentsChain(
    combine_documents_chain=combine_documents_chain,
    collapse_documents_chain=combine_documents_chain,
    token_max=4000
)

map_reduce_chain = MapReduceDocumentsChain(
    llm_chain=map_chain,
    reduce_documents_chain=reduce_documents_chain,
    document_variable_name="issues",
    return_intermediate_steps=False
)

summary_of_random_20 = map_reduce_chain.run(random_20_texts)

logger.info("summary of random 20:")
logger.info(summary_of_random_20)


file_path = f'screenshots/{cur_step}.jpg'

prompt = f"""You are an Android APP tester. 
Below is a README description of the APP under test and a screenshot of the APP's main interface,
as well as a list of functional categories.
This list is summarized from the issues of an APP similar to the one being tested (summarizing where bugs are distributed in functionalities).
You need to combine these two to analyze which of these functionalities might also appear in the APP under test,
and sort these functionalities, with those more likely to have issues tested ranked at the front.

### README of the APP under test

{app_desc}

### Functional Categories
{summary_of_random_20}
"""

prompt += """
### Expected Output Format
(Do not comment in json)
```json
{
    "ranked_functionalities": ["xxx", "xxx", ...]
}
```
"""
logger.info("ask for rank functionalities")
logger.info(prompt)
cold_start_analysis = get_response_from_lm([file_path], prompt)
logger.info("cold start analysis")
logger.info(cold_start_analysis)


ranked_functionalities = extract_json_from_str(cold_start_analysis)["ranked_functionalities"]
logger.info("ranked functionalities")
logger.info(ranked_functionalities)


# Check if FAISS index exists, if not, create it
faiss_index_path = './issues_cache'

# Create a new FAISS index and save it
vectorstore = FAISS.from_documents(texts, embed_model, distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT)
vectorstore.save_local(faiss_index_path)

# example 1. retrieval with embedding and reranker
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})

compression_retriever = ContextualCompressionRetriever(
    base_compressor=reranker, base_retriever=retriever
)

MAX_STEPS = 50

ranked_func_id = 0

change_document = True

page_ui_desc = ""
relevant_issue_description = ""


while True:
    if record.current_steps == MAX_STEPS:
        logger.info("Reached MAX_STEPS, exit.")
        break

    logger.debug(f"Current Page Info: {record.get_running_info()}")

    record.record()

    cur_step = record.current_steps
    logger.info(f"Now is the {cur_step}-th step")

    if change_document:
        logger.info("need to change relevant document")
        change_document = False
        file_path = f'screenshots/{cur_step}.jpg'
        prompt = f"The app name is {record.get_running_info()['app']}, and current activity is {record.get_running_info()['activity']}."
        prompt += "Please generate a short description(less than 200 tokens) of the current page of this APP based on the screenshot information of the interface."
        prompt += f"Please describe the functionalities of this APP from the perspective of {ranked_functionalities[ranked_func_id]}."
        logger.info("ask for readme prompt:")
        logger.info(prompt)
        page_ui_desc = get_response_from_lm([file_path], prompt)
        logger.info(f"page ui description:")
        logger.info(page_ui_desc)
        response = compression_retriever.get_relevant_documents(page_ui_desc)
        relevant_issue_description = response[0].page_content
        logger.info(f"relevant issue description:")
        logger.info(relevant_issue_description)

    component_file = f"components/{cur_step}.json"

    retrieve_list = []
    with open(component_file, 'r', encoding='utf-8') as f:
        component_data = json.load(f)

    prompt = f"""
## Role
You are an Android app tester.

## App Information
The app name is {record.get_running_info()['app']}, and the current activity is {record.get_running_info()['activity']}.

## GUI Information
You will be provided with a screenshot of the current page, an issue description similar to the current app, and information about all the components on the current interface.
Here are the components:
{component_data}

## Similar Issue Description
{relevant_issue_description}

## Task
Reproduce the issue through a similar path based on the provided similar issue description.
Your previous operation history is: {record.action_history}.
You can choose to "click" or "long press" on a component, or perform the actions of "swiping left", "swiping right", "going back", or "change_orientation"
The operation type is one of ["click", "long_press", "swiping_left", "swiping_right", "going_back"].
And if you choose click or long_press, you should also give the component id you want to operate on.
Please output the next operation in JSON format."""

    prompt += """
## Expected Output
```json
{
    "operationType": one of ["click", "long_press", "swiping_left", "swiping_right", "going_back", "change_orientation"],
    "component_id": "index id of the component to be clicked/long_pressed(just a number), if you choose the other operations, just leave this None",
    "action_description": "brief description of this action"
}
```
"""
    logger.info("ask each step click what prompt:")
    logger.info(prompt)

    action_res = get_response_from_lm([file_path], prompt)
    logger.info("action res:")
    logger.info(action_res)

    target_json = extract_json_from_str(action_res)

    operation_type = target_json["operationType"]
    component_id = target_json["component_id"]
    action_description = target_json["action_description"]

    if operation_type == "click" or operation_type == "long_press":
        click_item = {}
        with open(component_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for each in data:
                if each['id'] == component_id:
                    click_item = each

        bound = click_item['bound']
        draw_bounds(record.current_steps, bound)
        if operation_type == "click":
            click_node(bound, record.device_name)
        else:
            long_press_node(bound, record.device_name)
    else:
        if operation_type == "swiping_left":
            swipe_left(record.device_name)
        elif operation_type == "swiping_right":
            swipe_right(record.device_name)
        elif operation_type == "going_back":
            go_back(record.device_name)
        elif operation_type == "change_orientation":
            change_orientation(record.device_name)
        else:
            raise ValueError(f"operation type {operation_type} not supported")

    logger.info(f"current step action: {action_description}")
    record.action_history.append(action_description)

    # wait for the page to change
    time.sleep(3)

    prompt = f"""
## Role
You are an Android app tester.

## App Information
The app name is {record.get_running_info()['app']}, and the current activity is {record.get_running_info()['activity']}.

## GUI Information
You will be provided with a screenshot of the current page, an issue description similar to the current app, and information about all the components on the current interface.
Here are the components:
{component_data}

## Similar Issue Description
{relevant_issue_description}

## Task
You need to replicate similar test operation paths in this app based on similar Issues from similar apps.
The operations you have performed so far are: {record.action_history}.
Please determine whether you have currently replicated the complete similar test operation path,
or whether the test operation path in the issue is judged to be unable to be replicated in this app."""

    prompt += """
## Expected Output
(no comments in json)
```json
{
    "can_be_replicated": "1" or "0"(1 means able to be replicated, 0 means not),
    "is_complete": "1" or "0"(whether the current action history has replicated the complete test operation path),
    "reason" "reason for can/cannot be replicated, and reason for completed/not completed"
}
```"""
    logger.info("each step judgement prompt:")
    logger.info(prompt)

    judgement = get_response_from_lm([file_path], prompt)

    logger.info("judgement:")
    logger.info(judgement)

    judgement_json = extract_json_from_str(judgement)

    if judgement_json['can_be_replicated'] == "0":
        change_document = True
        ranked_func_id += 1
        logger.info("cannot be replicated, change a reference")
        continue
    else:
        logger.info("can be replicated, continue")

    if judgement_json['is_complete'] == "1":
        change_document = True
        ranked_func_id += 1
        record.action_history.clear()
        logger.info('completed')
        logger.info(judgement_json['reason'])
        logger.info("relevant doc:")
        logger.info(relevant_issue_description)
    else:
        logger.info('not completed')