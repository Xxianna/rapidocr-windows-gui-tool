## V0.2 使用新版RapidOCR的torch cuda推理，能够推理server模型，大大提高速度

from pathlib import Path
import os

# 确保已经安装了RapidOCR相应的依赖
from rapidocr import RapidOCR
# from rapidocr_onnxruntime import RapidOCR
from tkinter import Tk, Label, Text, Scrollbar, Frame, Button, filedialog, END, Canvas
from PIL import Image, ImageTk, ImageDraw
import math

# pyinstaller -D -w main.py -i"C:\PRJ\docansys\output.ico" -n myocr --noupx
####################给pyinstaller看的依赖#####################
import torch
########################################################

def scale_image(img, max_width, max_height):
    """根据最大宽度和高度等比例缩放图片"""
    original_width, original_height = img.size
    
    # 计算缩放比例
    width_ratio = max_width / original_width
    height_ratio = max_height / original_height
    scaling_factor = min(width_ratio, height_ratio)
    
    new_width = int(original_width * scaling_factor)
    new_height = int(original_height * scaling_factor)
    
    # 缩放图片
    scaled_img = img.resize((new_width, new_height))
    return ImageTk.PhotoImage(scaled_img)

def load_image():
    """打开文件对话框以选择图片，并在窗口中显示"""
    img_path = filedialog.askopenfilename(title="选择一张图片",
                                          filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
    if not img_path:
        return  # 如果用户取消选择，则返回
    
    draw_ocr_result(img_path)

def draw_ocr_result(img_path):
    """加载图片并根据OCR结果在其上绘制矩形"""
    img = Image.open(img_path)
    img_draw = img.copy()  # 创建副本用于绘制
    draw = ImageDraw.Draw(img_draw)

    #清空文本框
    text_box.config(state='normal')  # 先启用文本框以修改内容
    text_box.delete('1.0', END)  # 清空文本框内容
    text_box.config(state='disabled')  # 设置回不可编辑状态
    
    # 这里假设 engine 函数已经定义，并且它接受图片路径作为参数，
    # 返回识别的结果 result 和耗时 elapse。
    result = engine(str(img_path))  # 需要替换engine为你实际使用的函数
    #清理cuda缓存
    torch.cuda.empty_cache()
    squares = result.boxes
    txts = result.txts
    for i in range(len(squares)):
        vertices = squares[i]
        text = txts[i]

        # 计算四边中最短的一边的长度
        distances = [math.dist(vertices[i], vertices[(i + 1) % len(vertices)]) for i in range(len(vertices))]
        min_distance = min(distances)
        k = 0.1  # 设置k值，可以根据需要调整
        width = int(min_distance * k)

        # 绘制四条线段形成矩形
        for i in range(4):
            next_i = (i + 1) % 4
            draw.line([tuple(vertices[i]), tuple(vertices[next_i])], fill="red", width=width)

        update_text_box(text)  # 假设你有一个更新文本框的方法

    global img_tk
    img_dd = scale_image(img_draw, pic_max_width, pic_max_height)  # 注意这里是对img_draw调用scale_image
    image_label.config(image=img_dd)  # 直接配置img_dd到image_label
    image_label.image = img_dd  # 保持对PhotoImage对象的引用，防止被垃圾回收

def update_text_box(text):
    """更新文本框内容"""
    text_box.config(state='normal')  # 先启用文本框以修改内容
    text_box.insert(END, f"{text}\n")
    text_box.config(state='disabled')  # 设置回不可编辑状态

engine = RapidOCR(config_path="config.yaml")

# 创建主窗口
root = Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
max_width = screen_width // 3
max_height = screen_height * 2 // 3
pic_max_width = screen_width // 3
pic_max_height = screen_height // 3
root.maxsize(max_width, max_height)
root.title("OCR Viewer")

# 添加一个按钮用于加载图片
btn = Button(root, text="加载图片", command=load_image)
btn.pack()

# 打开并显示图片（初始为空）
img_tk = None
image_label = Label(root)
image_label.pack()

# 显示OCR结果的框架和组件
frame = Frame(root)
frame.pack(fill='both', expand=True)

text_box = Text(frame, height=10, wrap='none')
scroll = Scrollbar(frame, orient='vertical', command=text_box.yview)
text_box['yscrollcommand'] = scroll.set

text_box.pack(side='left', fill='both', expand=True)
scroll.pack(side='right', fill='y')

root.mainloop()