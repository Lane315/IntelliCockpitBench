import pandas as pd
import json
import os
from tqdm import tqdm
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import datetime

try:
    from .utils.gpt4 import getGTP4oResult
    from .utils.utils import write_to_excel_with_image
    from .utils.utils import get_image_list
    from .utils.utils import encode_image
    from .prompt import question_prompt as cprompt
    from .utils.gpt4 import start
except:
    from utils.gpt4 import getGTP4oResult
    from utils.utils import write_to_excel_with_image
    from utils.utils import get_image_list
    from utils.utils import encode_image
    from prompt import question_prompt as cprompt
    from utils.gpt4 import start


def sample_group(group):
    min_value = 1
    max_value = 8
    value = random.randint(min_value, max_value)
    if len(group) >= value:
        return group.sample(value)
    else:
        return group


def make_question(path: str, df: pd.DataFrame):
    if not os.path.exists(path):
        print(path, "is not exits.")
        return []
    sampled_groups = df.groupby('label2').apply(sample_group).reset_index(drop=True)
    prompt = cprompt.create_english_question_prompt(sampled_groups)
    js = start({'text': prompt, 'image': path})
    if not js:
        return []
    try:
        pattern = r'\[[^\]]*\]'
        match = re.findall(pattern, js)[0]
        data = json.loads(match)
    except (ValueError, json.JSONDecodeError, IndexError) as e:
        print(e)
        return []
    return data


def process_row(row, sample_df):
    js = make_question(row['path'], sample_df)
    result = []
    if not js:
        print("Error with file", row['path'])
    else:
        for question in js:
            result.append(row.tolist() + [question.get('Question', ""), question.get('Perspective', "")])
    return result


def main(file_path=None, output_folder="./image_question", sample_file=None, max_workers=10):
    '''
    sample_file is None
    Due to privacy considerations, we cannot provide sample results of the actual questions.
    '''
    if file_path is None or not os.path.exists(file_path):
        raise FileNotFoundError(f"The specified file path does not exist: {file_path}")

    df = pd.read_excel(file_path)
    current_time = datetime.datetime.now()
    time_str = current_time.strftime("%Y%m%d_%H%M%S")
    file_name = f"response_{time_str}.xlsx"
    output_file = os.path.join(output_folder, file_name)
    image_json_list = []
    col = list(df.columns)
    col.append('question')
    col.append('q_type')
    try:
        sample_df = pd.read_excel(sample_file)
    except:
        sample_df=pd.DataFrame(columns=['label2','english'])
    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for idx, row in tqdm(df.iterrows(), total=df.shape[0], desc="Submitting tasks:"):
            futures.append(executor.submit(process_row, row, sample_df))

        for future in tqdm(as_completed(futures), total=len(futures), desc="get image question:"):
            result = future.result()
            if result:
                image_json_list.extend(result)

    df_result = pd.DataFrame(columns=col, data=image_json_list)
    df_result.to_excel(output_file, index=False)
    write_to_excel_with_image(output_file)
    return output_file


if __name__ =='__main__':
    inputfile="path/to/your/input/file"
    outputfile=main(file_path=inputfile,output_folder="../image_question")
    print("get image question file save to:",outputfile)
    