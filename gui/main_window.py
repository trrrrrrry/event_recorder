import math
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import json
import os

from skimage.color.rgb_colors import cyan

from event_recorder.core.video_core import VideoCore
from event_recorder.core.event_logic import EventManager
from event_recorder.config import DEFAULT_SAVE_DIR
from event_recorder.gui.event_dialog import EventDialog

# 主题色
DARK_BG       = "#2e2e2e"
DARK_FG       = "#ffffff"
VIDEO_BG      = "#a6acb2"  # 视频区背景
BTN_NORMAL_BG = "#485d70"  # 其他按钮
BTN_HIGHLIGHT_BG = "#b0beca"  # 添加/开始/结束按钮
BTN_FG        = "#b6cadc"

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("视频事件标注器")
        self.configure(bg=DARK_BG)
        self.state('zoomed')

        # 绑定左右箭头逐帧
        self.bind('<Left>',  lambda e: self.step_frame(-1))
        self.bind('<Right>', lambda e: self.step_frame(1))
        self.bind('<Up>', lambda e: self.toggle_play())

        # 核心状态
        self.video_core = VideoCore()  # VideoCore 实例，负责视频的加载、读取和基本操作
        self.event_manager = EventManager()  # EventManager 实例，负责事件的管理、添加、删除、保存等逻辑
        self.current_frame_idx = 0  # 当前展示的帧索引（整数，从 0 开始）
        self.playing = False  # 播放状态标志，True 表示正在播放，False 表示已暂停
        self.after_id = None  # tkinter after 调度返回的 ID，用于取消定时任务
        self.playback_speed = 1  # 播放倍速，1x/2x/4x/8x
        self.event_texts = []
        self.total_frames = 0  # 视频的总帧数，在加载视频后由 VideoCore 赋值
        self.start_frame = 0  # 记录事件的起始帧
        self.frame_rate = 1  # 视频的帧率（FPS），在加载视频后由 VideoCore 赋值
        self.updating_scale = False  # 进度条更新标志，True 时跳过 seek 回调，避免递归调用
        self.game_types = []  # 从配置文件加载的游戏类型列表
        self.event_types = []  # 从配置文件加载的事件类型列表

        # 主布局
        main_frame = tk.Frame(self, bg=DARK_BG)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧按钮栏
        left_bar = tk.Frame(main_frame, bg=DARK_BG)
        left_bar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=10)

        normal_btn_opts = dict(
            bg=BTN_NORMAL_BG, fg=BTN_FG,
            activebackground=BTN_NORMAL_BG, activeforeground=BTN_FG,
            width=12, height=1
        )
        highlight_btn_opts = dict(
            bg=BTN_HIGHLIGHT_BG, fg="#4f5a64",
            activebackground=BTN_HIGHLIGHT_BG, activeforeground=BTN_FG,
            width=12, height=5
        )

        tk.Button(left_bar, text="加载视频",   command=self.load_video,  **normal_btn_opts).pack(pady=5)
        tk.Button(left_bar, text="加载事件",   command=self.load_events, **normal_btn_opts).pack(pady=5)
        tk.Button(left_bar, text="加载配置",   command=self.load_config, **normal_btn_opts).pack(pady=5)
        tk.Button(left_bar, text="保存事件",   command=self.save_events, **normal_btn_opts).pack(pady=5)
        tk.Frame(left_bar, bg=DARK_BG, height=20).pack()

        tk.Button(left_bar, text="+ 添加事件", command=self.add_event,   **highlight_btn_opts).pack(pady=5)
        tk.Button(left_bar, text="开始标记",   command=self.mark_start, **highlight_btn_opts).pack(pady=5)
        self.btn_mark_end = tk.Button(left_bar, text="结束标记", command=self.mark_end, **highlight_btn_opts)
        self.btn_mark_end.pack(pady=5)
        self.btn_mark_end.config(state=tk.DISABLED)

        # 右侧内容区
        right_frame = tk.Frame(main_frame, bg=DARK_BG)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 视频显示区
        video_container = tk.Frame(right_frame, bg=VIDEO_BG)
        video_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        video_container.pack_propagate(False)
        self.video_panel = tk.Label(video_container, bg=VIDEO_BG)
        self.video_panel.pack(fill=tk.BOTH, expand=True)

        # 播放控制 + 进度
        ctrl = tk.Frame(right_frame, bg=DARK_BG)
        ctrl.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(0,5))

        self.btn_play = tk.Button(
            ctrl,
            text="播放(↑)",
            command=self.toggle_play,
            **normal_btn_opts
        )
        self.btn_play.pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(ctrl, text="<<",   command=lambda: self.step_frame(-1), **normal_btn_opts).pack(side=tk.LEFT)
        tk.Button(ctrl, text=">>",   command=lambda: self.step_frame(1), **normal_btn_opts).pack(side=tk.LEFT)

        speed_var = tk.StringVar(value="1x")
        om = tk.OptionMenu(ctrl, speed_var, "1x", "2x", "4x", "8x", command=self.change_speed)
        om.config(bg=BTN_NORMAL_BG, fg=BTN_FG, width=4)
        om["menu"].config(bg=BTN_NORMAL_BG, fg=BTN_FG)
        om.pack(side=tk.LEFT, padx=5)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TScale", background=DARK_BG)
        self.scale = ttk.Scale(ctrl, from_=0, to=1, orient=tk.HORIZONTAL, command=self.seek)
        self.scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        # 跳转帧 / 秒
        tk.Label(ctrl, text="帧跳转:", bg=DARK_BG, fg=DARK_FG).pack(side=tk.LEFT, padx=5)
        self.entry_jump_frame = tk.Entry(ctrl, width=6, bg="#ffffff", fg=BTN_FG, insertbackground=BTN_FG)
        self.entry_jump_frame.pack(side=tk.LEFT)
        self.entry_jump_frame.bind("<Return>", lambda e: self.jump_to_frame())
        tk.Button(ctrl, text="跳转", command=self.jump_to_frame, **normal_btn_opts).pack(side=tk.LEFT, padx=5)

        tk.Label(ctrl, text="秒跳转:", bg=DARK_BG, fg=DARK_FG).pack(side=tk.LEFT, padx=5)
        self.entry_jump_second = tk.Entry(ctrl, width=6, bg="#ffffff", fg=BTN_FG, insertbackground=BTN_FG)
        self.entry_jump_second.pack(side=tk.LEFT)
        self.entry_jump_second.bind("<Return>", lambda e: self.jump_to_second())
        tk.Button(ctrl, text="跳转", command=self.jump_to_second, **normal_btn_opts).pack(side=tk.LEFT, padx=5)

        # 状态显示：视频名、分辨率、帧、时间
        status = tk.Frame(right_frame, bg=DARK_BG)
        status.pack(side=tk.TOP, fill=tk.X, padx=5, pady=(0,5))
        self.lbl_video_name  = tk.Label(status, text="名称: N/A", bg=DARK_BG, fg=DARK_FG)
        self.lbl_video_name.pack(side=tk.LEFT, padx=10)
        self.lbl_resolution  = tk.Label(status, text="分辨率: N/A", bg=DARK_BG, fg=DARK_FG)
        self.lbl_resolution.pack(side=tk.LEFT, padx=10)
        self.lbl_frame_info  = tk.Label(status, text="帧: 0/0", bg=DARK_BG, fg=DARK_FG)
        self.lbl_frame_info.pack(side=tk.LEFT, padx=10)
        self.lbl_time_info   = tk.Label(status, text="时间: 0.00/0.00", bg=DARK_BG, fg=DARK_FG)
        self.lbl_time_info.pack(side=tk.LEFT, padx=10)

        # 事件列表（表头 + 内容）
        cols = [
            "game_type", "event_type", "highlight_frame", "highlight_time",
            "duration_frames", "duration_seconds", "event_text",
            "save_path", "language", "comment"
        ]
        self.tree = ttk.Treeview(right_frame, columns=cols, show='headings', height=8)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, anchor=tk.CENTER, width=100)
        self.tree.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        self.tree.bind('<Button-3>', self.show_event_menu)

        self._refresh_event_list()

    def change_speed(self, val):
        try:
            self.playback_speed = int(val.rstrip('x'))
        except:
            self.playback_speed = 1

    def load_video(self):
        path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.mov *.avi")])
        if not path:
            return
        info = self.video_core.open(path)
        # 记录无扩展名的视频名，作为 save_path 子文件夹
        self.current_video_name = os.path.splitext(os.path.basename(path))[0]
        self.lbl_video_name.config(text=f"名称: {self.current_video_name}")

        w, h = info['width'], info['height']
        self.lbl_resolution.config(text=f"分辨率: {w}x{h}")

        self.total_frames      = info['total_frames']
        self.frame_rate        = info['fps']
        self.scale.config(to=self.total_frames - 1)
        self.current_frame_idx = 0
        self.show_frame(0)

    def show_frame(self, idx):
        """
        每次渲染一帧时：
         1. 从 VideoCore 取出 frame
         2. 在 frame 上画所有 self.overlays 定义的框 & 文本
         3. 转成 PhotoImage 显示
        """
        ret, frame = self.video_core.get_frame(idx)
        if not ret:
            return

        # 在 frame 上绘制所有 overlay
        if hasattr(self, 'overlays'):
            for o in self.overlays:
                x1, y1 = int(o['x1']), int(o['y1'])
                x2, y2 = int(o['x2']), int(o['y2'])
                # 画矩形框
                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    color=(0, 255, 224),
                    thickness=2
                )
                # 在框顶部绘制文字
                cv2.putText(
                    frame,
                    o['text'],
                    (x1, max( y1-10, 0)),             # 文字位置：框左上角上方 10 像素
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.8,
                    color=(0, 255, 224),
                    thickness=2,
                    lineType=cv2.LINE_AA
                )

        # 转为 RGB + PIL Image，再等比缩放 & 居中
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        pw, ph = self.video_panel.winfo_width(), self.video_panel.winfo_height()
        img.thumbnail((pw, ph), Image.LANCZOS)
        bg = Image.new("RGB", (pw, ph), VIDEO_BG)
        bg.paste(img, ((pw - img.width)//2, (ph - img.height)//2))

        # 更新显示
        self.photo = ImageTk.PhotoImage(bg)
        self.video_panel.config(image=self.photo)

        # —— 后续进度条 & 状态更新保持不变 ——
        self.current_frame_idx = idx
        self.updating_scale    = True
        self.scale.set(idx)
        self.updating_scale    = False

        cur_s = self.video_core.frame_to_time(idx)
        tot_s = self.video_core.frame_to_time(self.total_frames - 1)
        self.lbl_frame_info.config(text=f"帧: {idx}/{self.total_frames - 1}")
        self.lbl_time_info .config(text=f"时间: {cur_s:.2f}/{tot_s:.2f}")

    def toggle_play(self):
        if self.playing:
            self.playing = False
            self.btn_play.config(text="播放(↑)")
            if self.after_id:
                self.after_cancel(self.after_id)
        else:
            self.playing = True
            self.btn_play.config(text="暂停(↑)")
            self.play_loop()

    def play_loop(self):
        if not self.playing:
            return
        next_idx = self.current_frame_idx + 1
        if next_idx >= self.total_frames:
            self.playing = False
            self.btn_play.config(text="播放")
            return
        self.show_frame(next_idx)
        delay = int(480 / self.frame_rate / self.playback_speed)
        self.after_id = self.after(delay, self.play_loop)

    def step_frame(self, step):
        idx = max(0, min(self.total_frames - 1, self.current_frame_idx + step))
        self.show_frame(idx)

    def seek(self, value):
        if self.updating_scale:
            return
        idx = int(float(value))
        self.show_frame(idx)

    def jump_to_frame(self):
        try:
            idx = int(self.entry_jump_frame.get())
        except ValueError:
            messagebox.showerror("错误", "帧数无效")
            return
        self.show_frame(max(0, min(self.total_frames - 1, idx)))

    def jump_to_second(self):
        try:
            sec = float(self.entry_jump_second.get())
        except ValueError:
            messagebox.showerror("错误", "秒数无效")
            return
        idx = int(self.video_core.time_to_frame(sec))
        self.show_frame(max(0, min(self.total_frames - 1, idx)))

    def load_events(self):
        path = filedialog.askopenfilename(
            title="选择事件文件",
            initialdir=DEFAULT_SAVE_DIR,
            filetypes=[("JSON 文件", "*.json")]
        )
        if not path:
            return
        try:
            self.event_manager.load_events(path)
            self._refresh_event_list()
            messagebox.showinfo("提示", f"已加载事件：{path}")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def load_config(self):
        path = filedialog.askopenfilename(
            title="选择配置文件",
            initialdir=r"D:\reaudition_2509\event_recorder",
            filetypes=[("JSON 文件", "*.json")]
        )
        if not path:
            return
        cfg = json.load(open(path, 'r', encoding='utf-8'))
        self.game_types  = [cfg.get('game_type')]
        self.event_types = cfg.get('event_types', [])
        self.event_texts = cfg.get('event_texts', [])
        self.overlays    = cfg.get('overlays', [])
        messagebox.showinfo("提示", f"已加载配置：{path}")

    def add_event(self):
        if not self.game_types or not self.event_types: return messagebox.showwarning("善意的警告", "别急啊 加载配置了吗")
        pre = {"save_path": os.path.join(DEFAULT_SAVE_DIR, self.current_video_name),
               "highlight_frame": self.current_frame_idx}
        dlg = EventDialog(self, self.game_types, self.event_types,
    self.event_texts, on_save=self._on_event_saved, prefill=pre)
        self.wait_window(dlg)

    def mark_start(self):
        self.start_frame = self.current_frame_idx;
        self.btn_mark_end.config(state=tk.NORMAL)

    def mark_end(self):

        if self.start_frame is None: return messagebox.showwarning("警告", "别急啊 先点击开始标记按钮！")
        if not self.game_types or not self.event_types: return messagebox.showwarning("善意的警告", "别急啊 加载配置了吗")
        duration = self.current_frame_idx - self.start_frame
        pre = {"game_type": self.game_types[0] if self.game_types else "", "highlight_frame": self.start_frame,
               "duration_frames": duration, "save_path": os.path.join(DEFAULT_SAVE_DIR, self.current_video_name)}
        dlg = EventDialog(self, self.game_types, self.event_types
                             , self.event_texts, on_save=self._on_event_saved, prefill=pre);
        self.wait_window(dlg)
        self.start_frame = None;
        self.btn_mark_end.config(state=tk.DISABLED)


    def _on_event_saved(self, evt):
        hf, df = evt["highlight_frame"], evt["duration_frames"]
        evt["highlight_time"]   = math.ceil(self.video_core.frame_to_time(hf))
        evt["duration_seconds"] = df / self.frame_rate
        os.makedirs(os.path.dirname(evt["save_path"]) or evt["save_path"], exist_ok=True)
        self.event_manager.add_event(evt)
        self._refresh_event_list()

    def _refresh_event_list(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for idx, e in enumerate(self.event_manager.events):
            values = (
                e.get("game_type",""),
                e.get("event_type",""),
                e.get("highlight_frame",""),
                f"{e.get('highlight_time',0):.2f}",
                e.get("duration_frames",""),
                f"{e.get('duration_seconds',0):.2f}",
                e.get("event_text",""),
                e.get("save_path",""),
                e.get("language",""),
                e.get("comment","")
            )
            self.tree.insert('', 'end', iid=str(idx), values=values)

    def show_event_menu(self, event):
        row = self.tree.identify_row(event.y)
        if not row:
            return
        idx = int(row)
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="修改事件", command=lambda: self._edit_event(idx))
        menu.add_command(label="删除事件", command=lambda: self._delete_event(idx))
        menu.post(event.x_root, event.y_root)

    def _delete_event(self, idx):
        self.event_manager.delete_event(idx)
        self._refresh_event_list()

    def _edit_event(self, idx):
        old = self.event_manager.events[idx]
        dlg = EventDialog(
            self, self.game_types, self.event_types,
            on_save=lambda ne: self._on_event_updated(idx, ne),
            prefill=old
        )
        self.wait_window(dlg)

    def _on_event_updated(self, idx, ne):
        hf, df = ne["highlight_frame"], ne["duration_frames"]
        ne["highlight_time"]   = self.video_core.frame_to_time(hf)
        ne["duration_seconds"] = math.ceil(df / self.frame_rate)
        self.event_manager.update_event(idx, ne)
        self._refresh_event_list()

    def save_events(self):
        try:
            self.event_manager.save_events()
            messagebox.showinfo("提示", "事件已保存！")
        except Exception as e:
            messagebox.showerror("错误", str(e))


if __name__ == '__main__':
    app = MainWindow()
    app.mainloop()
