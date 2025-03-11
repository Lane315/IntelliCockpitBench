import pandas as pd
import requests
import os
from tqdm import tqdm
import re
import base64
from tenacity import retry, stop_after_attempt, wait_fixed
from openai import OpenAI
try:
    from api_key import API_KEY
    import utils
except:
    from .api_key import API_KEY
    from . import utils
#client = OpenAI(api_key=API_KEY)
client = OpenAI(api_key="", base_url="")
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def getGTP4oResult(message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-2024-11-20",
            messages=message,
            max_tokens=1000,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    
def start(ques):
    message=[
        {
        "role": "user",
        "content": [
            {"type": "text", "text": ques['text']},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{utils.encode_image(ques['image'])}",
                },
            },
        ],
        }
    ]
    response = getGTP4oResult(message)
    if response:
        return response
    else:
        logging.error(f"{ques['image']} fail to get response")
        return None
