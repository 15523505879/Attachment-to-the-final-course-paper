import os
import cv2

video_path = '幻海映月.mp4'  # 视频路径
output_folder = '视频截取'

# 创建输出文件夹
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 打开视频文件
vid_cap = cv2.VideoCapture(video_path)
if not vid_cap.isOpened():
    print("无法打开视频文件")
    exit()

# 获取帧速率
frame_rate = vid_cap.get(cv2.CAP_PROP_FPS)
print(f"视频帧速率: {frame_rate} FPS")

# 设置时间间隔为0.5秒
time_interval = 0.5  # 秒
frame_interval = int(frame_rate * time_interval)  # 每0.5秒提取一帧
if frame_interval == 0:
    frame_interval = 1  # 防止除以零的情况

frame_count = 0
extracted_frame_number = 0

while True:
    rval, frame = vid_cap.read()
    if not rval:
        break
    if frame_count % frame_interval == 0:
        extracted_frame_number += frame_rate*0.5
        # 生成文件名
        output_path = os.path.join(output_folder, f'{extracted_frame_number}帧.jpg')
        # 保存帧
        cv2.imwrite(output_path, frame)
        # 输出提示信息
        print(f'截取视频第: {extracted_frame_number}帧')
    frame_count += 1

# 释放资源
vid_cap.release()
print("视频处理完成")