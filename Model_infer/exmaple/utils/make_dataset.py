import pandas as pd
import os
import prompt as cprompt
import random
import gpt4
import re
import requests
import json
from json import JSONDecodeError


def sample_group(group):
    min_value=1
    max_value=8
    value = random.randint(min_value, max_value)
    if len(group) >= value:
        return group.sample(value)
    else:
        return group
    
def make_question_dataset(path:str,df):
    if not os.path.exists(path):
        print(path,"is not exits.")
        return []
    sampled_groups = df.groupby('label2').apply(sample_group).reset_index(drop=True)
    prompt=cprompt.create_english_question_prompt(sampled_groups)
    js=gpt4.start_image({'text':prompt,'image':path})
    print(js)
    if not js:
        return []
    try:
        pattern = r'\[[^\]]*\]'
        matche = re.findall(pattern, js)[0]
        data=json.loads(matche)
    except JSONDecodeError as e:
        print(e)
        return []
    return data


def make_label_dataset(path:str):
    if not os.path.exists(path):
        print(path,"is not exits.")
        return []
    prompt=cprompt.get_image_english_label_promptv2()
    js=gpt4.start_image({'text':prompt,'image':path})
    print(js)
    if not js:
        return []
    try:
        pattern = r'\[[^\[\]]*\]'
        matche = re.findall(pattern, js)
        if len(matche) > 0:
            data=json.loads(matche[0])
        else :
            data=json.loads(js)
        return data[0]
    except JSONDecodeError as e:
        print(e)
        return []