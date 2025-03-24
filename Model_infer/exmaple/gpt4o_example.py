import os
from tqdm import tqdm
import time
import copy
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import argparse
import logging
try:
    from .utils.gpt4 import start
except:
    from utils.gpt4 import start


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_question(messages, base_path):
    image_path = messages['img_path']
    question = messages['question']
    image_path = os.path.join(base_path, os.path.basename(image_path))
    res = start({'text': question, 'image': image_path})

    output_messages = copy.deepcopy(messages)
    output_messages['model_id'] = 'GPT-4o'
    question_id = output_messages['question_id']
    output_messages['answer_id'] = f'{question_id}_GPT-4o'
    output_messages['answer'] = res
    return output_messages


def gen_messages_list(jsonl_path):
    messages_list = []
    with open(jsonl_path, 'r', encoding='utf-8') as infile:
        for line in infile:
            if not line.strip():
                continue
            data = json.loads(line.strip())  
            messages_list.append(data)
    return messages_list


def main(test_jsonl_path, output_jsonl_path,base_path):
    if test_jsonl_path is None:
        return []
    messages_list = gen_messages_list(test_jsonl_path)
    
    data = []
    start_time = time.time()

    with ThreadPoolExecutor() as executor:
        future_to_message = {executor.submit(process_question, messages, base_path): messages for messages in messages_list}
        for future in tqdm(as_completed(future_to_message), total=len(messages_list), desc="Processing messages"):
            try:
                output_message = future.result()
                data.append(output_message)
            except Exception as e:
                print(f"Error processing message {future_to_message[future]}: {e}")

    end_time = time.time() 
    elapsed_time = end_time - start_time
    logging.info(f'Processing {test_jsonl_path} took {elapsed_time:.5f} seconds')

    with open(output_jsonl_path, 'w+', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')


def run(args):
    english_test_jsonl=args.english_test_jsonl
    chinese_test_jsonl =args.chinese_test_jsonl
    base=args.output_folder
    test_jsonl_list= [english_test_jsonl, chinese_test_jsonl]
    for test_jsonl_path in  test_jsonl_list:
        output_jsonl_path = os.path.join(base, os.path.basename(test_jsonl_path).replace('.jsonl', '_GPT4o.jsonl'))
        main(test_jsonl_path, output_jsonl_path,args.image)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='path to image_base')
    parser.add_argument('-i', '--image', type=str, help='image_base',default='./images')
    parser.add_argument('-e', '--english_test_jsonl', type=str, help='path to english_test_jsonl')
    parser.add_argument('-c', '--chinese_test_jsonl', type=str, help='path to chinese_test_jsonl')
    parser.add_argument('-o', '--output_folder', type=str, help='path to output_folder')
    args = parser.parse_args()
    run(args)
