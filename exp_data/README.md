# Experiment Data

## Overview

The dataset for this study consists of 71 applications with a total of 121 crash bugs. The applications are sourced from two main datasets: 20 applications with 34 bugs from the Themis benchmark, and an additional 51 applications with 87 bugs collected from F-Droid.

You can download the additional added dataset in [google drive](https://drive.google.com/drive/folders/1vjCY1Tr6Tp_QctP_KpbeCb7-erTJn_-N?usp=sharing).

## Data Details

### `Bugtobetest`

It includes the APK installation package of the tested app, as well as the corresponding information related to the Bug.

### `readme`

The README file of all apps. The filename is the hashed github link.

### `selected_data`

All of the issues, including the following info:

`app_name,category,github_link,issue_title,issue_description,issue_link,level,comments,bug_steps`

### `app_activities.csv`

The file contains the following app-level information.:

`app_name,github_link,github_xml_link,activities,ATG`

### `app2package.csv`

Recorded the start activities for launching various apps.

### `manual_bugs.csv`

Bug-related information used as test data.


## Hash Calculation

To prevent naming conflicts for software with the same name but different categories, we use the hash value of the GitHub link as the file name for app-level information. For example, the readme file is named using the hash method. The algorithm is as follows:

```python
import hashlib

def hash_github_link(github_link: str):
    """
    github_link example: https://github.com/izivkov/CasioGShockPhoneSync
    """
    repo_name = github_link.split('github.com/')[-1].rstrip('/')
    hash_name = hashlib.md5(repo_name.encode()).hexdigest()[:32]
    return hash_name
```