# Video Event Marker

项目概述
Event Recorder 是一个基于 Python 和 Tkinter 的视频事件标注工具，主要功能：

- `加载视频`：支持常见视频格式（`MP4`/`MOV`/`AVI`）。

- `加载/保存事件`：以 `JSON` 格式读写事件记录。

- `加载配置`：从 `config.json` 中读取游戏类型、事件类型和可选文本。

- `添加事件`：提供 `“添加事件”`、`“开始标记”`、`“结束标记”` 三步，记录事件起止帧并填写元数据；`“结束标记”` 按钮仅在点击 `“开始标记”` 后可用。

- `可选文本`：在对话框中，用户可从预置 `event_texts` 列表中选择，也可手动输入自定义文本。

- `导出格式`：标注完成后生成结构化的 `JSON` 文件，便于后续分析或训练模型。

---

项目结构

```bash
event_recorder/
├── core/
│   ├── video_core.py       # 视频加载与帧读取核心
│   └── event_logic.py      # 事件列表管理：增删改查、保存
├── gui/
│   ├── main_window.py      # 主界面：Tkinter 窗口、按钮、画面渲染、进度条
│   └── event_dialog.py     # 事件对话框：填写/选择事件信息
├── saved/
│   ├── config.json         # 示例配置文件（见下文）
│   └── events.json         # 标注完成后导出的事件记录
├── config.py               # 默认保存路径等全局配置
└── README.md               # 本文件
```
---
配置文件示例 (config.json)
放在 event_recorder/saved/config.json，用于填充下拉项：
```json
{
  "game_types": [
    "Apex Legends",
    "CS2",
    "League of Legends"
  ],
  "event_types": [
    "Kill",
    "Assist",
    "Death",
    "ObjectiveCaptured",
    "Revive"
  ],
  "event_texts": [
    "Headshot",
    "Triple Kill",
    "Final Blow",
    "Team Wipe",
    "Clutch Play"
  ],
  "overlays": [
    {
      "text": "kill",
      "x1": 689.0,
      "y1": 686.2,
      "x2": 1256.42,
      "y2": 880.14
    },
    {
      "text": "revive",
      "x1": 100,
      "y1": 50,
      "x2": 400,
      "y2": 300
    },
    {
      "text": "hi",
      "x1": 0,
      "y1": 0,
      "x2": 1000,
      "y2": 50
    }

}
```
- game_types：游戏种类，下拉选择固定值。

- event_types：事件类型，下拉选择，包含 “Others” 以手动输入。

- event_texts：可选显示文本，下拉/手输两用。

- overlays: 要全程显示的标注框及文本

---
## 导出文件格式与示例 (events.json)
```json
[
  {
    "game_type": "Apex Legends",
    "event_type": "Kill",
    "highlight_frame": 154,
    "highlight_time": 5.12,
    "duration_frames": 38,
    "duration_seconds": 1.27,
    "event_text": "Headshot",
    "save_path": "/path/to/save/Apex_2025-06-30.json",
    "language": "en_US",
    "comment": "0"
  },
  {
    "game_type": "CS2",
    "event_type": "Others",
    "highlight_frame": 212,
    "highlight_time": 7.04,
    "duration_frames": 54,
    "duration_seconds": 1.80,
    "event_text": "My Custom Text",
    "save_path": "/path/to/save/CS2_2025-06-30.json",
    "language": "zh_CN",
    "comment": "First round"
  }
]
```
---

## 字段说明：

- `game_type`：游戏种类

- `event_type`：事件类型（或 “Others”+自定义）

- `highlight_frame`：开始帧编号

- `highlight_time`：对应开始帧的秒数（浮点，单位 s）

- `duration_frames`：事件持续帧数

- `duration_seconds`：对应持续时长（s）

- `event_text`：显示/描述文本

- `save_path`：保存该事件截图或数据的文件夹路径

- `language`：语言代码（zh_CN/en_US/all）

- `comment`：备注，可选。

---
## 快速开始

1. 安装依赖：

```bash
pip install opencv-python pillow scikit-image
```
2. 运行程序：
```bash
python event_recorder/gui/main_window.py
```
3. 点击`加载配置`，选择示例 `saved/config.json`

4. 点击`加载视频`，选择需要标注的视频

5. 点击`添加事件`, 直接记录当前帧作为高光时刻，并在弹窗中填写/选择其他信息记录特定事件

6. 也可依次点击`开始标记` → `结束标记`，记录当前帧作为高光时刻，和点击间隔为持续时间，并在弹窗中填写/选择其他信息记录特定事件

7. 点击`保存事件`导出 `saved/events.json`


