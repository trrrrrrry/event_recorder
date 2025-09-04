# Video Event Marker

## Project Overview

Event Recorder is a video event annotation tool built with Python and Tkinter. Key features:

- `Load Video`: Supports common video formats (`MP4`/`MOV`/`AVI`).

- `Load/Save Events`: Reads and writes event records in `JSON` format.

- `Load Config`: Loads game types, event types, and optional texts from `config.json`.

- `Add Event`: Provides a three-step flow — `“Add Event”`, `“Start Marking”`, `“End Marking” `— to record the event’s start/end frames and fill in metadata; the `“End Marking”` button is enabled only after clicking `“Start Marking”`.

- `Optional Text`: In the dialog, users can select from the preset `event_texts` list or manually enter custom text.

- `Export Format`: After annotation, generates a structured  `JSON` file for downstream analysis or model training.

---

项目结构

```bash
event_recorder/
├── core/
│   ├── video_core.py       # Core for video loading and frame reading
│   └── event_logic.py      # Event list management: create/read/update/delete and save
├── gui/
│   ├── main_window.py      # Main UI: Tkinter window, buttons, video preview rendering, progress bar
│   └── event_dialog.py     # Event dialog: enter/select event details
├── saved/
│   ├── config.json         # Example configuration file (see below)
│   └── events.json         # Event records exported after annotation
├── config.py               # Global settings (default save paths, etc.)
└── README.md               # This file
```
---
Configuration file example (config.json)
Put this in event_recorder/saved/config.json to populate the dropdown options:
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
- `game_types`: Game types; select from fixed values in a dropdown.

- `event_types`: Event types; dropdown includes “Others” for manual input.

- `event_texts`: Optional display text; dual-mode (dropdown or manual input).

- `overlays`: Annotation boxes and text to display throughout.

---
## export file example (events.json):
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

## Field Description

- `game_type`: Game category.
- `event_type`: Event type (or `"Others"` + custom).
- `highlight_frame`: Start frame index.
- `highlight_time`: Time at the start frame (float, in seconds).
- `duration_frames`: Event duration in frames.

- `duration_seconds`: Corresponding duration (in seconds).
- `event_text`: Display/description text.
- `save_path`: Folder path to save screenshots or data for this event.
- `language`: Language code (`zh_CN` / `en_US` / `all`).
- `comment`: Remarks; optional.

---
## Quick Start

1. Install dependencies:

```bash
pip install opencv-python pillow scikit-image
```

2. Run the program:

```bash
python event_recorder/gui/main_window.py
```

3. Click `Load Config` and select the sample `saved/config.json`.

4. Click `Load Video` and choose the video to annotate.

5. Click `Add Event` to record the current frame as the highlight moment, then fill/select additional details in the popup to record the specific event.

6. Alternatively, click `Start Marking` → `End Marking` in sequence to record the current frame as the highlight moment and use the interval between clicks as the duration; then fill/select additional details in the popup to record the specific event.

7. Click `Save Events` to export `saved/events.json`.



