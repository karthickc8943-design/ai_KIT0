AI0730 - JARVIS Modern Local AI Assistant

JARVIS is a local-first AI assistant designed for daily productivity workflows, featuring a modern chat interface, voice interaction, automation tools, and multimodal capabilities.


---

Features

1) Modern Chat Interface

ChatGPT-style UI (modern_chat.py)

Compact input row with:

message box

attach icon (📎)

send button


In-chat previews for generated images and converted files

Auto task detection badge (Detected: ...)



---

2) AI Routing and System Actions

Fast pattern-based routing with AI fallback (command_router.py, core.py)

System automation (system_automation.py) including:

Opening desktop applications

Media controls

Calendar actions

Screenshot, lock, time/date, jokes




---

3) Voice Assistant Behavior

Integrated voice controls in UI

Wake/sleep conversation loop

Features:

Wake phrase activation

Continuous conversation while active

Auto sleep after silence timeout

Manual sleep/shutdown phrases




---

4) Local Image Generation (ComfyUI)

Fully local image generation via ComfyUI

Workflow:

Health check (/system_stats)

Queue prompt (/prompt)

Poll results (/history/{prompt_id})

Fetch image (/view)




---

5) File Intelligence

Supports:

.txt, .docx, .csv, .xlsx, code files


PDF processing:

Direct text extraction

OCR fallback for scanned PDFs (if supported tools installed)




---

6) YouTube and Web Summarization

YouTube:

Transcript → summary

Multi-fallback (API + yt-dlp)


Web:

URL fetch → text extraction → summary




---

Project Structure

ai1/
├── __init__.py
├── chat_memory.py
├── command_router.py
├── core.py
├── faster_whisper_stt.py
├── file_converter.py
├── file_mgmt.py
├── image.py
├── jarvis.py
├── jarvis_calendar.py
├── system_automation.py
├── tts_jarvis.py
├── upload.py
├── video_analysis.py
├── web_search.py
└── README.md

Entry Scripts

modern_chat.py → primary UI

ai_chat.py → legacy UI and shared functions



---

Environment and Requirements

Recommended Platform

Linux (Ubuntu-based preferred)

NVIDIA GPU (optional, recommended)

Python (Conda environment recommended)



---

Core Python Packages

gradiorequests
pillow
pytesseract
PyPDF2
python-docx
pandas
faster-whisper
youtube-transcript-api
yt-dlp
torch
torchvision
torchaudio
torchsde


---

System Tools (Recommended)

ffmpeg
tesseract-ocr
poppler-utils (pdftoppm)


---

Setup

1) Clone Repository

git clone https://github.com/karthickc8943-design/ai0730.git
cd ai0730


---

2) Install Dependencies

python -m pip install gradio requests pillow pytesseract PyPDF2 python-docx pandas faster-whisper youtube-transcript-api yt-dlp

If facing network/DNS issues:

python -m pip install <package> -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn


---

3) Setup ComfyUI

cd ~/ComfyUI
python main.py --listen 127.0.0.1 --port 8188

Optional:

export COMFYUI_URL="http://127.0.0.1:8188"


---

Running the Application

python modern_chat.py

Open in browser:

http://localhost:7866


---

Auto Mode Behavior

The assistant automatically detects intent from text and attachments.

Examples:

generate an image of ... → image generation

Upload image + analyze image text → OCR

Upload PDF + summarize short → file summary

summarize this youtube video <url> → video summary

<url> → web article summary


Detected task is shown in UI badge.


---

Voice Behavior

Starts in sleep mode

Activates on wake phrase

Ignores input while sleeping

Supports follow-up conversation

Auto sleep after inactivity

Manual sleep and shutdown supported



---

Local Image Generation Notes

Uses ComfyUI locally

Default model:


v1-5-pruned-emaonly.safetensors

If different, update the checkpoint name in workflow configuration.


---

Troubleshooting

ComfyUI Connection Error

Failed to establish connection: 127.0.0.1:8188

Fix:

curl http://127.0.0.1:8188/system_stats


---

Missing Dependencies

python -m pip install torchvision torchaudio torchsde


---

Transformers Version Issues

python -m pip install --force-reinstall --no-cache-dir "transformers==4.57.3" "huggingface-hub==0.36.2"


---

YouTube Transcript Issues

API blocked → fallback to yt-dlp

If both fail → captions unavailable



---

Security and Privacy

Designed for local usage

Image generation runs locally via ComfyUI

External requests used for web and YouTube features