"""
AI Toolkit - Complete Interface
"""

from .core import *
from .image import *
from .file_mgmt import *
from .upload import *
from .chat_memory import get_memory
from .tts_jarvis import say, set_voice
from .system_automation import execute_command
from .web_search import smart_chat, needs_web_search
from .faster_whisper_stt import transcribe, listen, list_microphones
from .video_analysis import analyze_video, analyze_video_short, analyze_video_medium, analyze_video_detailed

__all__ = [
    'set_model', 'set_response', 'smart_chat', 'check_ollama_status',
    'describe_image', 'ask_about_image', 'extract_text_from_image',
    'transcribe', 'listen', 'list_microphones',
    'say', 'set_voice', 'execute_command',
    'upload_to_ai', 'list_ai_files', 'read_ai_file',
    'analyze_video', 'analyze_video_short', 'analyze_video_medium', 'analyze_video_detailed',
    'get_memory'
]

print("✅ AI Toolkit loaded with JARVIS voice and system automation!")
