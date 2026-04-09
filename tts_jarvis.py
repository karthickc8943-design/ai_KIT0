"""
JARVIS TTS - Alan Voice (British Male)
"""

import subprocess
import os
import threading
import sys
import tempfile

class JarvisTTS:
    def __init__(self, voice="alan"):
        self.voices = {
            'alan': 'en_GB-alan-medium.onnx',
            'ryan': 'en_GB-ryan-medium.onnx',
            'dan': 'en_US-dan-medium.onnx',
            'lessac': 'en_US-lessac-medium.onnx'
        }

        voice_file = self.voices.get(voice, self.voices['alan'])
        self.voice_path = os.path.expanduser(f"~/piper_voices/{voice_file}")
        self.voice_name = voice
        self.available = os.path.exists(self.voice_path)

        if self.available:
            print(f"✅ JARVIS Voice ready! Voice: {voice}")
        else:
            print(f"⚠️ Voice not found: {self.voice_path}")

    def speak(self, text):
        if not self.available:
            subprocess.run(['espeak-ng', text], capture_output=True)
            return

        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_path = tmp_file.name

            cmd = [sys.executable, '-m', 'piper', '--model', self.voice_path, '--output_file', tmp_path]
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            process.stdin.write(text.encode())
            process.stdin.close()
            process.wait()

            if os.path.exists(tmp_path):
                subprocess.run(['aplay', tmp_path], capture_output=True)
                os.unlink(tmp_path)

        except Exception as e:
            print(f"JARVIS error: {e}")
            subprocess.run(['espeak-ng', text], capture_output=True)

    def speak_async(self, text):
        thread = threading.Thread(target=self.speak, args=(text,))
        thread.daemon = True
        thread.start()

_tts = None
_current_voice = "alan"

def get_tts(voice=None):
    global _tts, _current_voice
    if voice is not None:
        _current_voice = voice
    if _tts is None:
        _tts = JarvisTTS(voice=_current_voice)
    return _tts

def say(text, async_mode=False, voice=None):
    if not text:
        return
    tts = get_tts(voice)
    if async_mode:
        tts.speak_async(text)
    else:
        tts.speak(text)

def set_voice(voice):
    global _tts, _current_voice
    if voice in ['alan', 'ryan', 'dan', 'lessac']:
        _current_voice = voice
        _tts = None
        print(f"✅ Voice changed to: {voice}")
        get_tts()

print("✅ JARVIS TTS module loaded (Alan voice)!")
