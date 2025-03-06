import pandas as pd
import os
import base64

def write_to_excel_with_image(excel_file):
    df=pd.read_excel(excel_file)
    writer = pd.ExcelWriter(excel_file, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', index=False)

    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    worksheet.set_column('A:A', 100)  
    worksheet.set_column('B:B', 20)  

    print(df.columns)
    for idx, image_path in enumerate(df['path']):
        row_height=250
        worksheet.set_row(idx+1,row_height)
        worksheet.insert_image(idx + 1, 0, image_path, {'x_scale': 0.2, 'y_scale': 0.2})

    writer.close()


def get_image_list(folder):
    res=[]
    for file in os.listdir(folder):
        file_path=os.path.join(folder,file)
        if os.path.isdir(file_path):
            res+=get_image_list(file_path)
        elif file.endswith(".jpg"):
            res.append(file_path)
    return res

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
