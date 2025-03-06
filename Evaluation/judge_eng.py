# -*- coding: utf-8 -*-
import base64
from functools import partial
import openai
import json
import os
import re
import argparse
import requests
import dataclasses
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from tenacity import retry, wait_random_exponential, stop_after_attempt
import time
from collections import OrderedDict
import pandas as pd


@dataclasses.dataclass
class Sample:
    question: str
    reference: str
    answer: str
    category: str
    subcategory: str

    def __init__(self, question, reference, answer, category, subcategory):
        self.question = question
        self.answer = answer
        self.category = category
        self.subcategory = subcategory

        self.reference = reference


@dataclasses.dataclass
class Judge:
    dimensions: list
    prompt: str
    judgment: str
    rating: str
    score: str


class Config:
    def __init__(self, config_file_path) -> None:
        with open(config_file_path, 'r') as config_file:
            self.config = json.load(config_file, object_pairs_hook=OrderedDict)

        self.openai_api_key = self.config['OpenAI']['api_key']
        self.openai_api_url = self.config['OpenAI']['api_url']
        self.dimension_set_filepath = self.config['Paths']['dimension_set_filepath']
        self.dimension_def_filepath = self.config['Paths']['dimension_def_filepath']
        self.model_answer_dir = self.config['Paths']['model_answer_dir']
        self.model_judgment_dir = self.config['Paths']['model_judgement_dir']
        self.excel_dir = self.config['Paths']['excel_dir']
        self.subcategory_mapping = self.config['Paths']['subcategory_mapping']
        self.openai_api_model_name = self.config['OpenAI']['model_name']
        self.img_root_dir = self.config['Paths']['img_root_dir']

        if not os.path.exists(self.model_judgment_dir):
            os.makedirs(self.model_judgment_dir, exist_ok=True)

        with open(self.dimension_set_filepath, 'r') as f:
            self.category_dimension_map = json.load(f, object_pairs_hook=OrderedDict)
        with open(self.dimension_def_filepath, 'r') as f:
            self.dimension_def_map = json.load(f, object_pairs_hook=OrderedDict)
        with open(self.subcategory_mapping, 'r') as f:
            self.subcategory_type_map = json.load(f, object_pairs_hook=OrderedDict)

    def category2dimensions(self, category):
        ques_type = self.subcategory_type_map.get(category, None)
        return self.category_dimension_map.get(ques_type, None)

    def dimension2def(self, dimension):
        return self.dimension_def_map.get(dimension, None)

    def category2type(self, category):
        return self.subcategory_type_map.get(category, None)


def prompt_construct(sample: Sample, config: Config):
    dimensions = config.category2dimensions(sample.subcategory)
    dim_description = ""
    if dimensions is None:
        # Handle the case where dimensions is None
        print('***** dimensions is none *****', sample.subcategory, dimensions)

        dimensions = []
    for index, dim in enumerate(dimensions):
        dim_description += f"{index + 1}. {dim[0]}: {config.dimension2def(dim[0])}Importance: {dim[1]}Score\n"

    base_prompt = '''You are an assistant skilled at evaluating text quality. \nPlease act as an impartial judge and assess the quality of an AI assistant's response to a user's query. Since the primary category of the responses you are evaluating is {category} and the secondary category is {sub_category}, you need to evaluate the responses from the following dimensions: \n{dimensions}
We will provide you with the user's uploaded image, the user's question based on the image, a high-quality reference answer, and the AI assistant's answer that you need to evaluate. When performing your evaluation, you must reference the input image, not just the reference answer, and you need to compare the image with the reference answer and the AI assistant's answer to determine which one is more reasonable. When you begin your evaluation, you need to follow these steps:
1. Determine if the AI assistant's answer is safe and harmless, meaning that the response should not incite dangerous or harmful behavior, nor should it disseminate harmful information. If the AI assistant's answer does not meet the safety and harmlessness criteria, each dimension's score must be 0.
2. If the question specifies a particular location, then you need to check the corresponding location's object in the image to confirm whether the AI assistant’s response aligns with the object at the specified location in the image. The reference answer certainly describes the object at the corresponding location. If the AI assistant's answer correctly describes the content in the image but the described location doesn't match the specified location in the question, then the scores for all evaluation dimensions should be lowered.
3. Compare the AI assistant's answer with the reference answer and, in conjunction with the input image, point out the deficiencies in the AI assistant's answer, providing further explanations.
4. Evaluate the AI assistant's answer from different dimensions, giving a score between 1 and 10 for each dimension after evaluation. You must score all given dimensions.
5. Finally, provide an overall score between 1 and 10 for the AI assistant's answer, based on the evaluations of each dimension. Each evaluation dimension has an importance score ranging from 1 to 3, with higher scores indicating greater importance. When calculating the overall score, please weight each dimension's scores according to their importance scores.
6. Your scoring needs to be as strict as possible. After scoring each dimension and calculating the total score, you need to adjust the scores for each dimension and the total score based on the following rules: Accuracy, User Needs Fulfillment, and Visual Positioning Ability are the most important dimensions. If any of these dimensions perform poorly, the scores for other dimensions should be lowered accordingly. If the response contains irrelevant issues or has significant factual errors or generates harmful content, the total score must be 1 to 2. If the response has no major errors and is generally harmless but of low quality and fails to meet user needs, the total score is 3 to 4. If the response generally meets user requirements but performs poorly in some dimensions, indicating moderate quality, the total score can be 5 to 6. If the response quality is close to the reference answer and performs well in all dimensions, the total score is 7 to 8. Only when the response quality significantly exceeds the reference answer, fully resolving the user's issues and needs and performing near-perfectly in all dimensions can it score 9 to 10. As an example, the reference answer can be scored 8.
Remember, you must conduct evaluation and explanation before scoring. After explaining each dimension, you need to add the score for that dimension. At the end of your response, return all your scores in the following dictionary format (including brackets), ensuring your scores are whole numbers:
{{"Dimension One": [Score, Importance Score], "Dimension Two": [Score, Importance Score], ..., "Overall Score": Score}}.

User's Question: {question}
[Reference Answer Start]\n{reference}\n[Reference Answer End]\n
[Assistant's Answer Start]\n{answer}\n[Assistant's Answer End]\n
        '''

    prompt = base_prompt.format(category=sample.category, dimensions=dim_description, question=sample.question,
                                reference=sample.reference, answer=sample.answer, sub_category=sample.subcategory)

    return dimensions, prompt


def post_process(ques_id, judgment: str):
    def extract_rating(text):
        pattern = r'{(.*?)}(?![^{]*{)'  # match last brackets
        match = re.search(pattern, text)

        if match:
            dictionary_str = match.group(1)
            print(f'\n***** question_id: {ques_id} *****\n matched: {dictionary_str}')
            kv_pattern = r'"(.*?)": (\[.*?\]|\d+)'

            matches = re.findall(kv_pattern, dictionary_str)

            result_dict = {}
            for key, value in matches:
                if value.startswith('['):
                    result_dict[key] = [int(x) for x in re.findall(r'\d+', value)]
                else:
                    result_dict[key] = int(value)

            return result_dict
        else:
            print("No matching dictionary found")
            return {}

    def extract_score(text):
        pattern = r'\'Overall Score\': (\d+(\.\d{1,2})?)'
        match = re.search(pattern, text)
        if match:
            return float(match.group(1))
        return -1

    rating = extract_rating(judgment)

    score = rating.get("Overall Score", -1)
    if score == -1:
        score = extract_score(judgment)

    return rating, score


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
def get_GPT_4_judgment(config, prompt, image_path):
    def single_turn_wrapper(text, image_path):
        return [{
            "role": "user",
            "content": [
                {"type": "text", "text": text},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{encode_image(image_path=image_path)}",
                    },
                },
            ],
        }]

    url = config.openai_api_url
    key = config.openai_api_key
    name = config.openai_api_model_name

    messages = single_turn_wrapper(prompt, image_path)
    client = openai.OpenAI(
        api_key=key,
        base_url=url
    )
    try:
        response = client.chat.completions.create(
            model=name,
            messages=messages,
            temperature=0.1,
            top_p=0.1)
        ans = response.choices[0].message.content
    except Exception as e:
        print(e)
        ans = "Model Call Failure"
        print(ans)
    return ans


def run_sample(doc: OrderedDict, config: Config) -> Judge:
    start_time = time.time()
    ques_id = doc['question_id']

    ques = doc['question']
    ref = doc['reference']
    ans = doc['answer']

    # second category for mapping
    cat = doc['category']
    subcat = doc['subcategory']
    if cat == 'Description': subcat = 'Description'
    image_path = os.path.join(config.img_root_dir, doc['img_path'])
    sample = Sample(ques, ref, ans, cat, subcat)

    dimensions, prompt = prompt_construct(sample, config)

    judgment = get_GPT_4_judgment(config, prompt, image_path)

    rating, score = post_process(ques_id, judgment)

    end_time = time.time()
    judge_time = end_time - start_time

    print(f"Sample processing time: {judge_time:.2f} seconds")

    return Judge(dimensions, prompt, judgment, rating, score), judge_time


def main(args, config: Config):
    answer_file = os.path.join(config.model_answer_dir, args.model_name + '.jsonl')
    save_file = os.path.join(config.model_judgment_dir, args.model_name + '.jsonl')
    excel_file_path = os.path.join(config.excel_dir, args.model_name + '.xlsx')

    docs = []
    with open(answer_file, "r") as f:
        for line in f.readlines():
            docs.append(json.loads(line, object_pairs_hook=OrderedDict))
    print(f">>> loaded {len(docs)} docs from {answer_file}")

    def run_sample_and_save(doc: OrderedDict, save_file: str):
        judge, judge_time = run_sample(doc, config)

        doc["dimensions"] = judge.dimensions
        # doc["judge_prompt"] = judge.prompt
        doc["judgment"] = judge.judgment
        doc["rating"] = judge.rating
        doc["score"] = judge.score
        doc["judge_time"] = judge_time

        with open(save_file, "a") as f:
            f.write(json.dumps(doc, ensure_ascii=False, sort_keys=False))
            f.write('\n')

    if args.parallel == 1:
        for idx, doc in enumerate(tqdm(docs)):
            run_sample_and_save(doc, save_file)
    else:
        run_sample_and_save_wrapper = partial(run_sample_and_save, save_file=save_file)
        with ThreadPoolExecutor(args.parallel) as executor:
            for _ in tqdm(
                    executor.map(run_sample_and_save_wrapper, docs), total=len(docs)
            ):
                pass

    data = []

    with open(save_file, 'r', encoding='utf-8') as file:
        for line in file:
            data.append(json.loads(line.strip()))

    df = pd.DataFrame(data)

    df.to_excel(excel_file_path, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a test with a specified model.')
    parser.add_argument('--config-path', type=str, help='path to the config file',
                        default='config/multi-dimension.json')
    parser.add_argument('--model-name', type=str, help='Name of the file to test, name of jsonl file',
                        default='')
    parser.add_argument('--parallel', type=int, help='Number of parallel evaluations', default=16)
    args = parser.parse_args()
    print(args)

    config = Config(args.config_path)
    start_time = time.time()
    main(args, config)
    print(f"overall: {(time.time() - start_time):.2f} seconds")
