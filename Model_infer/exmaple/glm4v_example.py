"""
This script creates a CLI demo with transformers backend for the glm-4v-9b model,
allowing users to interact with the model through a command-line interface.

Usage:
- Run the script to start the CLI demo.
- Interact with the model by typing questions and receiving responses.

Note: The script includes a modification to handle markdown to plain text conversion,
ensuring that the CLI interface displays formatted text correctly.
"""
import json
import pandas as pd
import torch
from threading import Thread
from transformers import (
    AutoTokenizer,
    StoppingCriteria,
    StoppingCriteriaList,
    TextIteratorStreamer,
    AutoModel,
    BitsAndBytesConfig
)
import time
from PIL import Image
import copy
import os
import argparse
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


 
def init(MODEL_PATH):
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_PATH,
        trust_remote_code=True,
        encode_special_tokens=True
    )

    model = AutoModel.from_pretrained(
        MODEL_PATH,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        device_map="cuda:0",
    ).eval()
    return model,tokenizer


def gen_messages_list(jsonl_path):
    messages_list = []

    with open(jsonl_path, 'r', encoding='utf-8') as infile:
        for line in infile:
            if not line.strip():
                continue
            data = json.loads(line.strip())
            messages_list.append(data)
    return messages_list

def infer(messages,model,tokenizer):
        
    inputs = tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, tokenize=True, return_tensors="pt",return_dict=True
    )

    inputs = inputs.to(model.device)

    gen_kwargs = {"max_length": 2500, "do_sample": True, "top_k": 1}
    
    with torch.no_grad():
        outputs = model.generate(**inputs, **gen_kwargs)
        outputs = outputs[:, inputs['input_ids'].shape[1]:]
        output_text = tokenizer.decode(outputs[0])
        
    return str(output_text)


def main(test_jsonl_path, output_jsonl_path,base_path,model,tokenizer):
    if test_jsonl_path is None:
        return []
    messages_list = gen_messages_list(test_jsonl_path)
    data = []
    start_time = time.time()
    for messages in messages_list:
        output_messages = copy.deepcopy(messages)
        image_path = os.path.join(base_path,messages['img_path'])
        question = messages['question']
        try:
            image = Image.open(image_path).convert("RGB")
        except:
            print("Invalid image path. Continuing with text conversation.")
        message = [{"role": "user", "image": image, "content": question, "image_path": image_path}] 
        res = infer(message,model=model,tokenizer=tokenizer)
        print(res)
        output_messages['model_id'] = 'GLM-4'
        question_id = output_messages['question_id']
        output_messages['answer_id'] = f'{question_id}_GLM-4'
        output_messages['answer'] = res
        data.append(output_messages)    
    end_time = time.time()  
    elapsed_time = end_time - start_time  
    logging.info(f'Processing {test_jsonl_path} took {elapsed_time:.5f} seconds')
    with open(output_jsonl_path, 'w+',encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def run(args):
    model,tokenizer=init(args.model_path)
    english_test_jsonl=args.english_test_jsonl
    chinese_test_jsonl =args.chinese_test_jsonl
    base=args.output_folder
    test_jsonl_list= [english_test_jsonl, chinese_test_jsonl]
    for test_jsonl_path in  test_jsonl_list:
        output_jsonl_path = os.path.join(base, os.path.basename(test_jsonl_path).replace('.jsonl', '_GLM-4.jsonl'))
        main(test_jsonl_path, output_jsonl_path,args.image,model,tokenizer)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='path to image_base')
    parser.add_argument('-i', '--image', type=str, help='image_base',default='./images')
    parser.add_argument('-e', '--english_test_jsonl', type=str, help='path to english_test_jsonl')
    parser.add_argument('-c', '--chinese_test_jsonl', type=str, help='path to chinese_test_jsonl')
    parser.add_argument('-o', '--output_folder', type=str, help='path to output_folder')
    parser.add_argument('-m', '--model_path', type=str, required=True, help='Path to the pre-trained GLM model')
    args = parser.parse_args()
    run(args)