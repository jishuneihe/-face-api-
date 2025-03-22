import tkinter as tk
from tkinter import filedialog, Scrollbar, messagebox
from PIL import Image, ImageTk
import urllib.request
import urllib.error
import time
import json

# 创建主窗口
root = tk.Tk()
# 减小窗口宽度
root.title("基于深度学习的性别年龄检测器")
root.geometry("1000x900")
root.configure(bg="#FFFFCC")  # 设置整体背景颜色为淡黄色

# 创建标题标签
title_label = tk.Label(root, text="基于深度学习的性别年龄检测器", font=("宋体", 20), bg="#FFFFCC")
title_label.pack(pady=20)

# API Key 和 Secret 输入框
api_key_label = tk.Label(root, text="请输入 API Key:", bg="#FFFFCC")
api_key_label.pack(pady=5)
api_key_entry = tk.Entry(root, width=50)
api_key_entry.pack(pady=5)

api_secret_label = tk.Label(root, text="请输入 API Secret:", bg="#FFFFCC")
api_secret_label.pack(pady=5)
api_secret_entry = tk.Entry(root, width=50)
api_secret_entry.pack(pady=5)

# 创建横线
line = tk.Frame(root, width=960, height=1, bg="#B1B1B1")
line.pack()

# 创建一个主框架用于布局中间内容
middle_frame = tk.Frame(root, bg="#FFFFCC")
middle_frame.pack(pady=20, padx=20, anchor='w')  # 靠左边放置，设置垂直和水平间距

# 创建中间偏左的画布，适当放大
canvas = tk.Canvas(middle_frame, width=500, height=580, bg="white")
canvas.pack(side=tk.LEFT)

# 创建右边的框架用于放置两个矩形区域
right_frame = tk.Frame(middle_frame, bg="#FFFFCC")
right_frame.pack(side=tk.LEFT, padx=20)

# 检测结果区域，适当放大
result_label = tk.Label(right_frame, text="检测结果", font=("宋体", 16), bg="#FFFFCC")
result_label.pack()

result_rect = tk.Canvas(right_frame, width=300, height=250, bg="white", bd=1, relief=tk.SOLID)
result_rect.pack(pady=5)

# 操作行为区域，适当放大
action_label = tk.Label(right_frame, text="操作行为", font=("宋体", 16), bg="#FFFFCC")
action_label.pack(pady=20)

action_rect = tk.Canvas(right_frame, width=300, height=250, bg="white", bd=1, relief=tk.SOLID)
action_rect.pack()

# 当前选择的图片路径
current_image_path = None

# 绘制检测结果的标签
result_rect.create_text(20, 20, anchor=tk.W, text="检测时间: ")
result_rect.create_text(20, 80, anchor=tk.W, text="年龄: ")
result_rect.create_text(150, 20, anchor=tk.W, text="人脸数: ")
result_rect.create_text(150, 80, anchor=tk.W, text="性别: ")

# 存储结果文本的 ID，方便后续更新
time_used_text_id = result_rect.create_text(90, 20, anchor=tk.W, text="")
age_text_id = result_rect.create_text(60, 80, anchor=tk.W, text="")
face_num_text_id = result_rect.create_text(200, 20, anchor=tk.W, text="")
gender_text_id = result_rect.create_text(200, 80, anchor=tk.W, text="")

# 记录调用 API 的次数
api_call_count = 0
api_call_count_label = tk.Label(right_frame, text=f"API 调用次数: {api_call_count}", bg="#FFFFCC")
api_call_count_label.pack(pady=5)


# 上传图片的函数
def upload_image():
    global current_image_path
    file_path = filedialog.askopenfilename()
    if file_path:
        try:
            # 打开图片文件
            img = Image.open(file_path)
            # 调整图片大小以完全契合画布
            img = img.resize((500, 580), Image.LANCZOS)
            # 将图片转换为 Tkinter 可用的格式
            photo = ImageTk.PhotoImage(img)
            # 清空画布上原有的内容
            canvas.delete("all")
            # 在画布上显示图片
            canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            # 保存图片引用，防止被垃圾回收
            canvas.image = photo
            current_image_path = file_path
        except Exception as e:
            print(f"图片处理出错: {e}")


# 检测图片的函数
def detect_image():
    global current_image_path, record_count, api_call_count
    if not current_image_path:
        messagebox.showwarning("警告", "请先上传图片！")
        return
    api_key = api_key_entry.get()
    api_secret = api_secret_entry.get()
    if not api_key or not api_secret:
        messagebox.showwarning("警告", "请输入 API Key 和 Secret！")
        return
    http_url = 'https://api-cn.faceplusplus.com/facepp/v3/detect'
    filepath = current_image_path

    boundary = '----------%s' % hex(int(time.time() * 1000))
    data = []
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_key')
    data.append(api_key)
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_secret')
    data.append(api_secret)
    data.append('--%s' % boundary)
    try:
        fr = open(filepath, 'rb')
        data.append('Content-Disposition: form-data; name="%s"; filename=" "' % 'image_file')
        data.append('Content-Type: %s\r\n' % 'application/octet-stream')
        data.append(fr.read())
        fr.close()
    except Exception as e:
        messagebox.showerror("错误", f"文件读取错误: {e}")
        return
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_landmark')
    data.append('1')
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_attributes')
    data.append(
        "gender,age,smiling,headpose,facequality,blur,eyestatus,emotion,ethnicity,beauty,mouthstatus,eyegaze,skinstatus")
    data.append('--%s--\r\n' % boundary)

    for i, d in enumerate(data):
        if isinstance(d, str):
            data[i] = d.encode('utf-8')

    http_body = b'\r\n'.join(data)

    # build http request
    req = urllib.request.Request(url=http_url, data=http_body)

    # header
    req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)

    try:
        # post data to server
        resp = urllib.request.urlopen(req, timeout=5)
        # get response
        qrcont = resp.read()

        result = json.loads(qrcont.decode('utf-8'))
        time_used = result.get('time_used')
        face_num = result.get("face_num")
        if face_num > 0:
            gender_en = result["faces"][0]["attributes"]["gender"]["value"]
            # 性别英文到中文的映射
            gender_mapping = {
                "Male": "男",
                "Female": "女"
            }
            gender = gender_mapping.get(gender_en, "未知")
            age = result["faces"][0]["attributes"]["age"]["value"]
        else:
            gender = "未检测到人脸"
            age = "未检测到人脸"

        # 更新结果文本
        result_rect.itemconfig(time_used_text_id, text=f"{time_used} 毫秒")
        result_rect.itemconfig(age_text_id, text=str(age))
        result_rect.itemconfig(face_num_text_id, text=str(face_num))
        result_rect.itemconfig(gender_text_id, text=gender)

        # 更新识别结果信息
        record_count += 1
        result_text = f"{gender} {age}"
        y_position = 50 + (record_count - 1) * 25  # 调整行间距

        # 调整各列起始 x 坐标
        bottom_rect.create_text(20, y_position, anchor=tk.W, text=str(record_count))
        bottom_rect.create_text(100, y_position, anchor=tk.W, text=filepath)
        bottom_rect.create_text(500, y_position, anchor=tk.W, text=result_text)
        # 减小检测时间列的 x 坐标
        bottom_rect.create_text(700, y_position, anchor=tk.W, text=f"{time_used} 毫秒")

        # 更新画布滚动区域
        bottom_rect.config(scrollregion=bottom_rect.bbox("all"))

        # 更新 API 调用次数
        api_call_count += 1
        api_call_count_label.config(text=f"API 调用次数: {api_call_count}")

    except urllib.error.HTTPError as e:
        messagebox.showerror("错误", e.read().decode('utf-8'))
    except Exception as e:
        messagebox.showerror("错误", f"发生未知错误: {e}")


# 创建上传图片按钮，并将其放置在操作行为画布内部
upload_button = tk.Button(action_rect, text="上传图片", command=upload_image)
# 为按钮设置合适的布局，使用 place 方法可以精确控制位置，避免改变画布大小
upload_button.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

# 创建检测图片按钮，并将其放置在操作行为画布内部
detect_button = tk.Button(action_rect, text="检测图片", command=detect_image)
detect_button.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

# 在画布和操作行为的检测边框下添加一个矩形边框
bottom_frame = tk.Frame(root, bg="#FFFFCC")
bottom_frame.pack(pady=20, padx=20)

# 减小底部矩形框宽度
bottom_rect = tk.Canvas(bottom_frame, width=960, height=200, bg="white", bd=1, relief=tk.SOLID)
bottom_rect.pack(side=tk.LEFT)

# 添加滚动条
scrollbar = Scrollbar(bottom_frame, command=bottom_rect.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
bottom_rect.config(yscrollcommand=scrollbar.set)

# 绘制标题和子标题
bottom_rect.create_text(20, 10, anchor=tk.W, text="识别结果信息", font=("宋体", 12, "bold"))
bottom_rect.create_text(20, 30, anchor=tk.W, text="序号", font=("宋体", 10, "bold"))
bottom_rect.create_text(100, 30, anchor=tk.W, text="文件路径", font=("宋体", 10, "bold"))
bottom_rect.create_text(500, 30, anchor=tk.W, text="结果", font=("宋体", 10, "bold"))
# 减小检测时间列的 x 坐标
bottom_rect.create_text(700, 30, anchor=tk.W, text="检测时间", font=("宋体", 10, "bold"))

# 记录检测次数
record_count = 0

# 进入主循环
root.mainloop()
