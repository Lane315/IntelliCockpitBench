import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from tqdm import tqdm
import datetime

try:
    from .utils.gpt4 import getGTP4oResult
    from .utils.utils import write_to_excel_with_image
    from .prompt import answer_prompt as cprompt
    from .utils.gpt4 import start 
    from .utils.exclude import EXCLUDE_FILE_PATH
    from .utils.labels import question_label, road_labels
except ImportError:
    from utils.gpt4 import getGTP4oResult
    from utils.utils import write_to_excel_with_image
    import prompt.answer_prompt as cprompt
    from utils.gpt4 import start
    from utils.exclude import EXCLUDE_FILE_PATH
    from utils.labels import question_label, road_labels

def make_answer(path: str, question: str):
    if not os.path.exists(path):
        print(path, "is not exits.")
        return []
    prompt = cprompt.create_english_answer_prompt(question)
    js = start({'text': prompt, 'image': path})
    if not js:
        return []
    try:
        start_idx = js.index('[')
        end_idx = js.rindex(']') + 1
        json_str = js[start_idx:end_idx]
        data = json.loads(json_str)
        return data[0]
    except (ValueError, json.JSONDecodeError, IndexError) as e:
        print(f"Error encountered: {e}")
        return []

def translate_question_answer(question, answer):
    message = [{"role": "user", "content": cprompt.get_translate_question_answer_prompt(question, answer)}]
    response = getGTP4oResult(message)
    if response:
        try:
            start_idx = response.index('[')
            end_idx = response.rindex(']') + 1
            json_str = response[start_idx:end_idx]
            data = json.loads(json_str)
            return data[0]
        except (ValueError, json.JSONDecodeError, IndexError) as e:
            print(f"Error encountered: {e}")
            return []
    else:
        print("Failed to get response")
        return None

def get_chinese_label(df):
    road_english2chinese = {value: key for key, value in road_labels.items()}
    question_english2chinese = {value: key for key, value in question_label.items()}
    df['chinese_category'] = df['category'].map(question_english2chinese)
    df['chinese_sub_category'] = df['sub_category'].map(question_english2chinese)
    df['chinese_roadway'] = df['roadway'].map(road_english2chinese)
    df['chinese_sub_roadway'] = df['sub_roadway'].map(road_english2chinese)
    return df

def load_excluded_paths(exclude_file):
    if os.path.exists(exclude_file):
        with open(exclude_file, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def append_to_exclude_file(exclude_file, paths):
    if os.path.exists(exclude_file):
        with open(exclude_file, "a") as f:
            for path in paths:
                f.write(path + "\n")

def process_row(idx,row):
    js = make_answer(row['path'], row['question'])
    return idx, js

def translate_row(idx,row):
    res = translate_question_answer(row['question'], row['answer'])
    return idx, res

def main(file_path=None, output_folder="./image_answer", max_workers=10):
    if file_path is None or not os.path.exists(file_path):
        raise FileNotFoundError(f"The specified file path does not exist: {file_path}")
    
    df = pd.read_excel(file_path)
    current_time = datetime.datetime.now()
    time_str = current_time.strftime("%Y%m%d_%H%M%S")
    file_name = f"response_{time_str}.xlsx"
    outputfile = os.path.join(output_folder, file_name)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_row = {executor.submit(process_row, idx,row): row for idx, row in df.iterrows()}
        for future in tqdm(as_completed(future_to_row), total=len(future_to_row), desc="get image answer"):
            row = future_to_row[future]
            try:
                idx, js = future.result()
                if not js:
                    print("error with file")
                else:
                    df.at[idx, 'category'] = js.get("Primary Tag", "")
                    df.at[idx, 'sub_category'] = js.get("Secondary Tag", "")
                    df.at[idx, 'answer'] = js.get("Answer", "")
            except Exception as e:
                print(f"Error processing row {e}")

    df.to_excel(outputfile, index=False)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_row = {executor.submit(translate_row, idx,row): row for idx, row in df.iterrows()}
        for future in tqdm(as_completed(future_to_row), total=len(future_to_row), desc="translate question"):
            row = future_to_row[future]
            try:
                idx, res = future.result()
                if not res:
                    print("error with file")
                else:
                    df.at[idx, 'chinese_question'] = res.get('question', "")
                    df.at[idx, 'chinese_answer'] = res.get('answer', "")
            except Exception as e:
                print(f"Error processing row {row}: {e}")

    df = get_chinese_label(df)
    df.to_excel(outputfile, index=False)
    write_to_excel_with_image(outputfile)
    reses = df['path'].to_list()
    append_to_exclude_file(EXCLUDE_FILE_PATH, reses)
    return outputfile

if __name__ =='__main__':
    inputfile=""
    outputfile=main(file_path=inputfile,output_folder="../image_answer")
    print("get image answer file save to:",outputfile)