import os
import tkinter as tk
from tkinter import ttk, filedialog
from event_recorder.config import DEFAULT_SAVE_DIR

class EventDialog(tk.Toplevel):
    def __init__(self, parent, game_types, event_types, event_texts, on_save, prefill=None):
        super().__init__(parent)
        self.title("添加/编辑事件")
        self.on_save = on_save
        self.prefill = prefill or {}
        self.event_texts = event_texts

        frm = ttk.Frame(self, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        # 1. 游戏类型
        ttk.Label(frm, text="游戏类型：").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.cb_game = ttk.Combobox(frm, values=game_types, state="readonly")
        self.cb_game.grid(row=0, column=1, sticky=tk.EW, pady=2)
        self.cb_game.set(self.prefill.get("game_type", game_types[0] if game_types else ""))

        # 2. 事件类型 + Others
        ttk.Label(frm, text="事件类型：").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.cb_event = ttk.Combobox(frm, values=event_types + ["Others"], state="readonly")
        self.cb_event.grid(row=1, column=1, sticky=tk.EW, pady=2)
        self.cb_event.set(self.prefill.get("event_type", event_types[0] if event_types else ""))
        self.entry_other = ttk.Entry(frm)
        self.entry_other.grid(row=1, column=2, sticky=tk.EW, pady=2)
        self.entry_other.insert(0, self.prefill.get("event_text", ""))
        def on_event_change(e=None):
            if self.cb_event.get() == "Others":
                self.entry_other.config(state="normal")
            else:
                self.entry_other.delete(0, tk.END)
                self.entry_other.config(state="disabled")
        self.cb_event.bind("<<ComboboxSelected>>", on_event_change)
        on_event_change()

        # 3. 高光帧数
        ttk.Label(frm, text="高光帧数：").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.entry_frame = ttk.Entry(frm)
        self.entry_frame.grid(row=2, column=1, sticky=tk.EW, pady=2)
        self.entry_frame.insert(0, str(self.prefill.get("highlight_frame", 0)))

        # 4. 持续帧数
        ttk.Label(frm, text="持续帧数：").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.entry_dframe = ttk.Entry(frm)
        self.entry_dframe.grid(row=3, column=1, sticky=tk.EW, pady=2)
        self.entry_dframe.insert(0, str(self.prefill.get("duration_frames", 0)))

        # 5. 显示内容（可选配置 or 手动输入）
        ttk.Label(frm, text="显示内容：").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.text_var = tk.StringVar(value=self.prefill.get("event_text", ""))
        if self.event_texts:
            self.cb_text = ttk.Combobox(frm, textvariable=self.text_var, values=self.event_texts)
            self.cb_text.grid(row=4, column=1, columnspan=2, sticky=tk.EW, pady=2)
            # 默认允许手动输入
        else:
            self.entry_text = ttk.Entry(frm, textvariable=self.text_var)
            self.entry_text.grid(row=4, column=1, columnspan=2, sticky=tk.EW, pady=2)

        # 6. 保存路径
        ttk.Label(frm, text="保存路径：").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.entry_path = ttk.Entry(frm)
        self.entry_path.grid(row=5, column=1, sticky=tk.EW, pady=2)
        default = self.prefill.get("save_path", DEFAULT_SAVE_DIR)
        self.entry_path.insert(0, default)
        btn_browse = ttk.Button(frm, text="选择…", command=self._browse)
        btn_browse.grid(row=5, column=2, sticky=tk.E, pady=2)

        # 7. 语言
        ttk.Label(frm, text="语言：").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.cb_lang = ttk.Combobox(frm, values=["zh_CN", "en_US", "all"], state="readonly")
        self.cb_lang.grid(row=6, column=1, sticky=tk.EW, pady=2)
        self.cb_lang.set(self.prefill.get("language", "zh_CN"))

        # 8. 备注
        ttk.Label(frm, text="备注：").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.entry_comment = ttk.Entry(frm)
        self.entry_comment.grid(row=7, column=1, columnspan=2, sticky=tk.EW, pady=2)
        self.entry_comment.insert(0, str(self.prefill.get("comment", "0")))

        # 保存 / 取消
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=8, column=0, columnspan=3, pady=(10,0))
        ttk.Button(btn_frame, text="取消", command=self.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="保存", command=self._save).pack(side=tk.RIGHT)

        frm.columnconfigure(1, weight=1)
        frm.columnconfigure(2, weight=1)

    def _browse(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON 文件", "*.json")],
            initialdir=os.path.dirname(self.entry_path.get()) or DEFAULT_SAVE_DIR
        )
        if path:
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, path)

    def _save(self):
        evt = {
            "game_type":       self.cb_game.get(),
            "event_type":      self.cb_event.get() if self.cb_event.get()!="Others" else self.entry_other.get(),
            "highlight_frame": int(self.entry_frame.get()),
            "duration_frames": int(self.entry_dframe.get()),
            "event_text":      self.text_var.get(),
            "save_path":       self.entry_path.get(),
            "language":        self.cb_lang.get(),
            "comment":         self.entry_comment.get(),
            "highlight_time":   None,
            "duration_seconds": None,
        }
        self.on_save(evt)
        self.destroy()
