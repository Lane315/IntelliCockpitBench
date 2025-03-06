import os
import json
import pandas as pd
import random
import datetime
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

try:
    from .utils.utils import get_image_list
    from .prompt import label_prompt as cprompt
    from .utils.gpt4 import start
    from .utils.exclude import EXCLUDE_FILE_PATH
except:
    from utils.utils import get_image_list
    from prompt import label_prompt as cprompt
    from utils.gpt4 import start
    from utils.exclude import EXCLUDE_FILE_PATH



def make_label(path: str):
    if not os.path.exists(path):
        print(path, "is not exits.")
        return None, None
    prompt = cprompt.get_image_english_label_prompt()
    js = start({'text': prompt, 'image': path})
    if not js:
        return path, None
    try:
        pattern = r'\[[^\[\]]*\]'
        match = re.findall(pattern, js)
        if len(match) > 0:
            data = json.loads(match[0])
        else:
            data = json.loads(js)
        return path, data[0]
    except (ValueError, json.JSONDecodeError, IndexError) as e:
        print(e)
        return path, None


def load_excluded_paths(exclude_file):
    if os.path.exists(exclude_file):
        with open(exclude_file, "r") as f:
            return set(line.strip() for line in f if line.strip())
    else:
        raise 'file not exists'
    return set()


def process_image_list(image_list,excluded_paths):
    image_json_list = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_image = {executor.submit(make_label, img): img for img in image_list}
        
        for future in tqdm(as_completed(future_to_image), total=len(future_to_image), desc="generate image label"):
            img = future_to_image[future]
            try:
                path, js = future.result()
                if path and js:
                    image_json_list.append((
                        "",
                        path,
                        js.get("Road Condition Primary Label", ""),
                        js.get("Road Condition Secondary Label", ""),
                        js.get("Driving Status", ""),
                        js.get("Shooting Angle", ""),
                        js.get("Weather Condition", "")
                    ))
            except Exception as exc:
                print(f"Error with file {img}: {exc}")

    return image_json_list


def main(output_folder='./image_label', image_list=['.images'], sample=-1):
    current_time = datetime.datetime.now()
    time_str = current_time.strftime("%Y%m%d_%H%M%S")
    file_name = f"response_{time_str}.xlsx"
    outputfile = os.path.join(output_folder, file_name)
    
    excluded_paths = load_excluded_paths(EXCLUDE_FILE_PATH)
    print("finish image:", len(excluded_paths))
    
    reses = []
    for img in image_list:
        reses += get_image_list(img)
        
    print("total image num:", len(reses))
    reses = [res for res in reses if res not in excluded_paths]
    if sample != -1:
        reses = random.sample(reses, sample)

    image_json_list = process_image_list(reses, excluded_paths)
    
    df = pd.DataFrame(columns=['image', 'path', 'roadway', 'sub_roadway', 'driving_status', 'shooting_angle', 'weather_conditions'], data=image_json_list)
    df.to_excel(outputfile, index=False)
    return outputfile

if __name__ == "__main__":
    image_list=['path/to/image_folder1','path/to/image_folder2']
    sample_number=500
    outputfile=main(output_folder='../image_label',image_list=image_list,sample=sample_number)
    print("get image label file save to:",outputfile)