import os
import fitz  # PyMuPDF

def convert_pdfs_to_png(input_folder, output_folder, dpi=150):
    """
    将一个文件夹内所有 PDF 文件中的每一页转换为 PNG 并保存。

    :param input_folder: 包含 PDF 文件的输入文件夹路径
    :param output_folder: PNG 图片保存的目标文件夹路径
    :param dpi: 图片分辨率，默认 150
    """
    # 确保输出目录存在
    os.makedirs(output_folder, exist_ok=True)

    # 遍历文件夹内的所有文件
    for file_name in os.listdir(input_folder):
        # 检查文件后缀是否是 PDF（忽略大小写）
        if file_name.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_folder, file_name)
            try:
                # 打开 PDF 文件
                doc = fitz.open(pdf_path)
                print(f"正在处理 PDF: {file_name}, 总页数: {len(doc)}")

                # 遍历 PDF 的每一页
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)  # 加载页面
                    # 设置图片分辨率（通过缩放控制 DPI）
                    mat = fitz.Matrix(dpi / 72, dpi / 72)  # DPI = 原始分辨率 x 缩放系数
                    pix = page.get_pixmap(matrix=mat)  # 渲染为像素对象

                    # 生成图片文件的输出路径
                    output_file_name = f"{os.path.splitext(file_name)[0]}_page_{page_num + 1}.png"
                    output_file_path = os.path.join(output_folder, output_file_name)

                    # 保存图片
                    pix.save(output_file_path)
                    print(f"已保存: {output_file_path}")

                # 关闭当前 PDF
                doc.close()
            except Exception as e:
                print(f"处理 PDF 文件时出错: {file_name}, 错误: {e}")

    print("所有 PDF 文件已处理完成！")
# ========== 配置输入和输出路径 ==========
input_folder = "1/"  # 替换为PDF文件夹路径
output_folder = "1/"  # 输出文件夹

# 调用转换函数
convert_pdfs_to_png(input_folder, output_folder, dpi=150)