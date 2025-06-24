import math
import os
import cv2
from event_recorder.config import ACCEPTED_RESOLUTIONS, ACCEPTED_FRAMERATES, ACCEPTED_FORMATS

class VideoCore:
    """
    视频加载与校验核心类

    提供：
    - 打开视频并校验格式、分辨率、帧率
    - 读取当前帧、跳转至指定帧/时间
    - 帧数与时间互转
    """
    def __init__(self):
        self.cap = None
        self.frame_rate = 0
        self.total_frames = 0
        self.width = 0
        self.height = 0

    def open(self, filepath: str):
        """
        打开并校验视频文件
        :param filepath: 视频文件路径
        :raises ValueError: 格式、分辨率或帧率不支持
        :raises IOError: 无法打开文件
        """
        ext = os.path.splitext(filepath)[1].lower()
        if ext not in ACCEPTED_FORMATS:
            raise ValueError(f"不支持的格式：{ext}")

        cap = cv2.VideoCapture(filepath)
        if not cap.isOpened():
            raise IOError(f"无法打开视频：{filepath}")

        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if (width, height) not in ACCEPTED_RESOLUTIONS:
            cap.release()
            raise ValueError(f"不支持的分辨率：{width}x{height}")
        if int(round(fps)) not in ACCEPTED_FRAMERATES:
            cap.release()
            raise ValueError(f"不支持的帧率：{fps}")

        # 校验通过，保存属性
        self.cap = cap
        self.frame_rate = fps
        self.total_frames = total
        self.width = width
        self.height = height
        return {
            'width': width,
            'height': height,
            'fps': fps,
            'total_frames': total
        }

    def read_frame(self):
        """读取当前帧"""
        if not self.cap:
            return False, None
        ret, frame = self.cap.read()
        return ret, frame

    def get_frame(self, frame_idx: int):
        """跳转并读取指定帧"""
        if not self.cap:
            return False, None
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        return self.read_frame()

    def next_frame(self):
        """读取下一帧"""
        return self.read_frame()

    def seek_frame(self, frame_idx: int):
        """跳转至指定帧，不读取"""
        if not self.cap:
            return
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)

    def frame_to_time(self, frame_idx: int) -> float:
        """将帧数转换为秒"""
        if self.frame_rate <= 0:
            return 0.0
        return frame_idx / self.frame_rate

    def time_to_frame(self, seconds: float) -> int:
        """将时间（秒）转换为最接近的帧数"""
        if self.frame_rate <= 0:
            return 0
        return int(round(seconds * self.frame_rate))

    def release(self):
        """释放视频资源"""
        if self.cap:
            self.cap.release()
            self.cap = None
