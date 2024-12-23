import cv2
import os


def resize_image(image, scale_factor=0.4):
    """Resize the image to a specified scale factor."""
    width = int(image.shape[1] * scale_factor)
    height = int(image.shape[0] * scale_factor)
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)


def show_images_from_folder(folder_path):
    images = [img for img in os.listdir(folder_path) if img.endswith('.jpg') or img.endswith('.jpeg')]
    for image in images:
        img_path = os.path.join(folder_path, image)
        img = cv2.imread(img_path)
        if img is None:
            print(f"无法读取图片: {img_path}")
            continue

        resized_img = resize_image(img, scale_factor=0.5)
        print(f'显示图片：{image}')
        cv2.imshow('image', resized_img)
        cv2.waitKey(1000)  # 显示1秒

        cv2.destroyAllWindows()


# 使用函数并指定文件夹路径
show_images_from_folder('视频截取')
