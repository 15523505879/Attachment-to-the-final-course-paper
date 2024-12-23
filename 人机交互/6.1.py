import os
import time
import cv2
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Alignment

# Step1: 打印提示信息
print("开始创建文件夹并准备调用摄像头...")

# Step2: 创建homework6文件夹，设置捕捉区域等信息
folder_name = 'homework6'
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Step3: 创建Excel表用于存储照片的信息
wb = Workbook()
ws = wb.active
ws.title = "PhotoInfo"
alignment_center = Alignment(horizontal="center", vertical="center")
for col in ws.columns:
    for cell in col:
        cell.alignment = alignment_center
ws.append(["序号", "照片名称", "时刻"])

# Step4: 拍摄操作
cap = cv2.VideoCapture(0)  # 调用默认摄像头
count = 0
for i in range(1, 21):  # 尝试拍摄20张照片
    ret, frame = cap.read()
    if not ret:
        print("未能捕获图像")
        break
    flipped_frame = cv2.flip(frame, 1)  # 水平翻转
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"image_{i}.jpg"
    filepath = os.path.join(folder_name, filename)
    cv2.imwrite(filepath, flipped_frame)

    # 记录拍照时间和文件名到Excel中
    ws.append([i, filename, timestamp])

    count += 1
    print(f"已拍摄 {count} 张照片")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    time.sleep(1)

# Step5: 保存工作表，关闭所有窗口
wb.save(os.path.join(folder_name, "photos_info.xlsx"))
cap.release()
cv2.destroyAllWindows()