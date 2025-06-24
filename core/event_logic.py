# event_recorder/core/event_logic.py

import json
import os
from event_recorder.config import DEFAULT_SAVE_DIR

class EventManager:
    """
    事件管理器：维护内存中的事件列表，支持加载、保存、增删改。
    """

    def __init__(self, save_dir: str = None):
        # 事件默认存放目录
        self.save_dir = save_dir or DEFAULT_SAVE_DIR
        self.events = []
        # 尝试初始化载入已有事件
        try:
            self.load_events()
        except Exception:
            self.events = []

    def load_events(self, path: str = None):
        """
        加载事件列表。
        - 如果 path 为空：从 save_dir/events.json 加载
        - 如果 path 是相对名：在 save_dir 下拼接加载
        - 如果 path 是绝对路径：直接加载
        """
        # 确定实际文件路径
        if path is None:
            file_path = os.path.join(self.save_dir, "events.json")
        elif os.path.isabs(path):
            file_path = path
        else:
            file_path = os.path.join(self.save_dir, path)

        if not os.path.exists(file_path):
            # 文件不存在，不报错，只清空列表
            self.events = []
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError(f"事件文件格式错误：根节点应为列表，实际得到 {type(data)}")
        self.events = data

    def save_events(self, file_name: str = "events.json"):
        """
        将当前事件列表写入 save_dir/file_name。
        """
        os.makedirs(self.save_dir, exist_ok=True)
        file_path = file_name if os.path.isabs(file_name) else os.path.join(self.save_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.events, f, ensure_ascii=False, indent=4)

    def add_event(self, evt: dict):
        self.events.append(evt)

    def delete_event(self, idx: int):
        if 0 <= idx < len(self.events):
            self.events.pop(idx)
        else:
            raise IndexError(f"删除事件失败：索引 {idx} 越界")

    def update_event(self, idx: int, evt: dict):
        if 0 <= idx < len(self.events):
            self.events[idx] = evt
        else:
            raise IndexError(f"更新事件失败：索引 {idx} 越界")


if __name__ == "__main__":
    # 简单测试
    mgr = EventManager()
    print("初始：", mgr.events)
    mgr.load_events()  # 默认
    mgr.load_events(r"D:\reaudition_2509\event_recorder\saved\events.json")  # 绝对
    mgr.load_events("events.json")  # 相对
    mgr.add_event({"game_type":"T","event_type":"e","highlight_frame":1,"duration_frames":1,
                   "highlight_time":0.0,"duration_seconds":0.0,
                   "event_text":"","save_path":DEFAULT_SAVE_DIR,"language":"zh_CN","comment":""})
    mgr.save_events()
    print("完成")
