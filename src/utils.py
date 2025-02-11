import base64
import re
import os
import pandas as pd
import hashlib
import cv2
import requests
import json
import base64
import requests
import configparser

def get_response_from_lm(images, prompt):
    # Function to encode an image to base64
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    # Initialize the message list with the prompt
    msg = [{
        "type": "text",
        "text": prompt
    }]

    api_key = os.environ('OPENAI_API_KEY')

    # Encode each image and append it to the message list
    for image in images:
        base64_image = encode_image(image)
        msg.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        })

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # Payload for the API request
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": msg
            }
        ],
        "max_tokens": 3000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    # Retry logic in case of failure
    retry = True
    outputs = "empty"
    while retry:
        try:
            outputs = response.json()['choices'][0]['message']['content'].strip()
            retry = False
        except KeyError:
            retry = True

    return outputs


config = configparser.ConfigParser()

config.read('config.ini')
selected_data_path = config.get('Paths', 'selected_data_path')

def hash_github_link(github_link):
    repo_name = github_link.split('github.com/')[-1].rstrip('/')
    hash_name = hashlib.md5(repo_name.encode()).hexdigest()[:32]
    return hash_name

def find_matching_github_links(hash_string):
    return_data_list = []

    for filename in os.listdir(selected_data_path):
        if filename.endswith('_issue.csv'):
            file_path = os.path.join(selected_data_path, filename)

            df = pd.read_csv(file_path)

            for index, row in df[df['github_link'].notna()].iterrows():
                github_link = row['github_link']

                hash_name = hash_github_link(github_link)

                if hash_name == hash_string:
                    return_data_list.append(row.to_dict())

    return return_data_list


def extract_json_from_str(json_str):
    json_pattern = r'```json\s*([\s\S]*?)\s*```'

    matches = re.findall(json_pattern, json_str)

    target_json = json.loads(matches[0])

    return target_json


def draw_bounds(i, bounds):
    image_path = os.path.join("screenshots", f"{i}.jpg")
    image = cv2.imread(image_path)
    x1, y1, x2, y2 = bounds
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)  # Blue colorunds1
    output_path = os.path.join("actions", f"{i}.jpg")
    cv2.imwrite(output_path, image)