import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import dataset.get_image_label as get_image_label
import dataset.get_image_question as get_image_question
import dataset.get_image_answer as get_image_answer
import pandas as pd
import yaml

def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

def makedataset(image_list,sample_number):
        outputfile=get_image_label.main(output_folder='./image_label',image_list=image_list,sample=sample_number)
        print("get image label file save to:",outputfile)
        outputfile=get_image_question.main(file_path=outputfile,output_folder="./image_question")
        print("get image question file save to:",outputfile)
        outputfile=get_image_answer.main(file_path=outputfile,output_folder="./image_answer")
        print("get image answer file save to:",outputfile)


def main():
    config=load_config("./config/run.yaml")
    image_list=config['image_path']
    sample_number=config['sample_number']
    epoch=config['epoch']
    for _ in range(epoch):
        makedataset(image_list,sample_number)

if __name__ =='__main__':
        main()