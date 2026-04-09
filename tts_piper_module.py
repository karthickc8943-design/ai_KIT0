"""
Piper TTS - Using Python module directly
"""

import subprocess
import os
import threading
import sys
import tempfile

# Global variable for current voice
_current_voice = "amy"

class PiperTTS:
    def __init__(self, voice="amy"):
        self.voices = {
            'amy': 'en_US-amy-medium.onnx',
            'lessac': 'en_US-lessac-medium.onnx',
            'libritts': 'en_US-libritts_r-medium.onnx'
        }
        
        voice_file = self.voices.get(voice, self.voices['amy'])
        self.voice_path = os.path.expanduser(f"~/piper_voices/{voice_file}")
        self.available = os.path.exists(self.voice_path)
        
        if self.available:
            print(f"✅ Piper TTS ready! Voice: {voice}")
        else:
            print(f"⚠️ Voice not found: {self.voice_path}")
    
    def speak(self, text):
        if not self.available:
            # Fallback to espeak
            subprocess.run(['espeak-ng', text], capture_output=True)
            return
        
        try:
            # Create a temporary file for the audio
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_path = tmp_file.name
            
            # Use piper via Python module
            cmd = [
                sys.executable, '-m', 'piper',
                '--model', self.voice_path,
                '--output_file', tmp_path
            ]
            
            # Run piper with text input
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            process.stdin.write(text.encode())
            process.stdin.close()
            process.wait()
            
            # Play the audio
            if os.path.exists(tmp_path):
                subprocess.run(['aplay', tmp_path], capture_output=True)
                os.unlink(tmp_path)
            
        except Exception as e:
            print(f"Piper error: {e}")
            subprocess.run(['espeak-ng', text], capture_output=True)
    
    def speak_async(self, text):
        thread = threading.Thread(target=self.speak, args=(text,))
        thread.daemon = True
        thread.start()

# Global TTS instance
_tts = None
_current_voice = "amy"

def get_tts(voice=None):
    global _tts, _current_voice
    if voice is not None:
        _current_voice = voice
    if _tts is None or (_tts and _tts.voice_path != _current_voice):
        _tts = PiperTTS(voice=_current_voice)
    return _tts

def say(text, async_mode=False, voice=None):
    """Speak text using Piper TTS"""
    if not text:
        return
    tts = get_tts(voice)
    if async_mode:
        tts.speak_async(text)
    else:
        tts.speak(text)

def set_voice(voice):
    """Change the voice: 'amy', 'lessac', or 'libritts'"""
    global _tts, _current_voice
    if voice in ['amy', 'lessac', 'libritts']:
        _current_voice = voice
        _tts = None  # Reset TTS to create new instance with new voice
        print(f"✅ Voice changed to: {voice}")
        # Test the new voice
        get_tts()
    else:
        print(f"⚠️ Unknown voice: {voice}. Available: amy, lessac, libritts")

def get_current_voice():
    """Get the current voice name"""
    return _current_voice

print("✅ Piper TTS module loaded!")
print("   Available voices: amy, lessac, libritts")
print("   Use set_voice('amy') to change voice")
