import os
import re
import subprocess
from pathlib import Path

class VideoPreprocessor:
    def __init__(self, input_dir, output_dir, target_fps=30, target_res="1280x720"):
        """
        初始化视频预处理器
        :param input_dir: 原始视频存放目录
        :param output_dir: 处理后视频存放目录
        :param target_fps: 目标帧率 (默认 30)
        :param target_res: 目标分辨率 (默认 720p，格式 "宽x高")
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.target_fps = target_fps
        self.target_res = target_res
        
        # 确保输出目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_files_with_robust_matching(self, pattern_str):
        """
        针对命名不一致的数据集，使用正则进行柔性字符串匹配
        :param pattern_str: 正则表达式字符串 (例如: r'.*(scene|shot)_?\d+.*')
        :return: 匹配到的文件路径列表
        """
        matched_files = []
        # 忽略大小写的正则编译
        regex = re.compile(pattern_str, re.IGNORECASE)
        
        # 支持常见视频格式
        valid_extensions = {'.mp4', '.avi', '.mov', '.webm', '.mkv'}
        
        print(f"🔍 正在扫描目录，匹配规则: {pattern_str}")
        for file_path in self.input_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in valid_extensions:
                # 针对文件名进行特定字符串特征提取
                if regex.search(file_path.name):
                    matched_files.append(file_path)
                    
        print(f"✅ 共找到 {len(matched_files)} 个符合条件的文件。")
        return matched_files

    def process_video(self, input_path):
        """
        调用 FFmpeg 执行核心预处理：转码、重采样、尺寸统一
        """
        # 统一输出格式为 .mp4
        output_path = self.output_dir / f"{input_path.stem}_processed.mp4"
        
        # FFmpeg 核心参数构建
        # 1. 缩放并自动补黑边填充 (保持原始宽高比)
        # 2. H.264 编码，CRF 23 (平衡画质与体积)
        # 3. 音频 AAC 编码 (确保视听协同数据的音频轨道完整)
        vf_filter = f"scale={self.target_res}:force_original_aspect_ratio=decrease,pad={self.target_res}:(ow-iw)/2:(oh-ih)/2"
        
        cmd = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-i', str(input_path),
            '-vf', vf_filter,
            '-r', str(self.target_fps),
            '-c:v', 'libx264', 
            '-crf', '23', 
            '-preset', 'fast',
            '-c:a', 'aac', 
            '-b:a', '128k',
            '-ar', '44100', # 统一音频采样率
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"  ➜ 成功: {output_path.name}")
        except subprocess.CalledProcessError as e:
            print(f"  ❌ 失败: {input_path.name} | 错误码: {e.returncode}")

    def run_pipeline(self, match_pattern=r'.*'):
        files = self.get_files_with_robust_matching(match_pattern)
        if not files:
            return
            
        print("-" * 40)
        print("🚀 开始批量预处理...")
        for idx, file in enumerate(files, 1):
            print(f"[{idx}/{len(files)}] 处理中: {file.name}")
            self.process_video(file)
        print("🎉 所有视频处理完毕！")

if __name__ == "__main__":
    # --- 配置区域 ---
    INPUT_FOLDER = "."
    OUTPUT_FOLDER = "./processed_videos"
    
    # 初始化处理器，设定标准为 30fps, 720p
    processor = VideoPreprocessor(INPUT_FOLDER, OUTPUT_FOLDER, target_fps=30, target_res="1280x720")
    
    # 设定正则匹配规则 (例如提取所有包含特定前缀或关键字的文件，应对不规则命名)
    # 匹配示例: 提取文件名中带有 'story', 'anim' 或者 'scene_01' 的文件
    regex_pattern = r'.*(story|anim|scene[_-]?01).*' 
    
    processor.run_pipeline(match_pattern=regex_pattern)