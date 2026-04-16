import os
from PIL import Image

def batch_resize_images(target_width, target_height, input_folder='.', output_folder='resized_targets'):
    # 1. 创建输出文件夹
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"📁 已创建文件夹: {output_folder}")

    # 2. 遍历当前目录下的所有文件
    count = 0
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            img_path = os.path.join(input_folder, filename)
            
            with Image.open(img_path) as img:
                # 使用高质量滤镜进行缩放 (LANCZOS)
                # 如果你想保持比例不拉伸，可以使用 img.thumbnail((target_width, target_height))
                resized_img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # 保存到新文件夹
                save_path = os.path.join(output_folder, filename)
                resized_img.save(save_path, quality=95) # 保持高画质
                
                print(f"✅ 已处理: {filename} -> {target_width}x{target_height}")
                count += 1

    print(f"\n🎉 处理完成！共缩放 {count} 张图片，保存在: {output_folder}")

# --- 设置区域 ---
# 在这里输入你想要的尺寸（比如 800, 800）
MY_WIDTH = 800
MY_HEIGHT = 800

batch_resize_images(MY_WIDTH, MY_HEIGHT)