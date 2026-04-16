import os
import subprocess
import re

def get_silence_sections(filename):
    """ 使用 FFmpeg 探测静音处，作为断句的参考点 """
    print("🔍 正在分析语音停顿点...")
    command = [
        'ffmpeg', '-i', filename,
        '-af', 'silencedetect=n=-30dB:d=0.5',
        '-f', 'null', '-'
    ]
    output = subprocess.run(command, stderr=subprocess.PIPE, text=True).stderr
    # 提取静音结束的时间点
    silence_ends = re.findall(r'silence_end: (\d+\.\d+)', output)
    return [float(x) for x in silence_ends]

def split_video_smartly(input_file, segment_length=20):
    """ 
    智能裁剪：每3分钟左右寻找最近的静音点进行切割 
    """
    silences = get_silence_sections(input_file)
    current_pos = 0
    page_num = 0
    
    # 获取视频总时长
    duration_cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_file]
    total_duration = float(subprocess.check_output(duration_cmd))

    while current_pos < total_duration:
        # 目标切割点是当前位置 + 20秒
        target_cut = current_pos + segment_length
        
        # 在目标点前后10秒内找一个静音点
        best_cut = target_cut
        for s in silences:
            if target_cut - 10 < s < target_cut + 15:
                best_cut = s
                break
        
        if best_cut > total_duration:
            best_cut = total_duration

        output_video = f"page_{page_num}.mp4"
        output_frame = f"target_{page_num}.jpg"

        print(f"📦 正在生成第 {page_num} 页：从 {current_pos}s 到 {best_cut}s")

        # 1. 裁剪视频段
        subprocess.run([
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-ss', str(current_pos), '-to', str(best_cut),
            '-i', input_file, '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', output_video
        ], check=True)

        # 设定你要求的尺寸 (宽度:高度)
        # 建议尺寸控制在 800-1000 左右，太大会增加编译时间且不提升识别率
        target_size = "800:800" 

        # 2. 提取该段的首帧作为识别图，并缩放
        subprocess.run([
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-i', output_video, 
            '-vf', f'scale={target_size}', # 【核心修改】调用 scale 滤镜
            '-frames:v', '1', output_frame
        ], check=True)

        current_pos = best_cut
        page_num += 1
    
    print(f"🎉 处理完成！共生成 {page_num} 个故事章节。")

# 使用示例
split_video_smartly("story3.mp4")