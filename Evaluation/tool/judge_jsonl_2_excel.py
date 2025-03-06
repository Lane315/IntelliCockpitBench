import json
import pandas as pd

# Define the path of the JSONL file and the output Excel file path
jsonl_file_path = '../data/jsonl/english_test.jsonl'
excel_file_path = '../data/excel/english_qwen2vl_0212.xlsx'

data = []

# Read the JSONL file line by line
with open(jsonl_file_path, 'r', encoding='utf-8') as file:
    for line in file:
        data.append(json.loads(line.strip()))

# Convert the data into a DataFrame
df = pd.DataFrame(data)

# Write the DataFrame to an Excel file
df.to_excel(excel_file_path, index=False)
