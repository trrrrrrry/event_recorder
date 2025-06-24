# config.py

# ------- 视频格式校验 -------
# 支持的分辨率列表（宽，高）
ACCEPTED_RESOLUTIONS = [
    (1920, 1080),
    (1920, 1200),
    (2560, 1440),
    (2560, 1600),
    (3200, 1800),
    (3200, 2000),
    (3840, 2400),
]

# 支持的帧率（FPS）
ACCEPTED_FRAMERATES = [24, 30, 60]

# 支持的视频文件后缀
ACCEPTED_FORMATS = ['.mp4', '.mov', '.avi']

# ------- 默认路径与语言等 -------
# 默认事件保存目录（文件夹）
DEFAULT_SAVE_DIR = r"D:\reaudition_2509\event_recorder\saved"

# 默认语言选项
DEFAULT_LANGUAGE = 'en_US'

# 默认事件持续时长（帧）
DEFAULT_DURATION_FRAMES = 0
