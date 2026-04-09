import subprocess
import threading

class EspeakTTS:
    def __init__(self, voice='en-us', speed=150, pitch=50, volume=200):
        self.voice = voice
        self.speed = speed
        self.pitch = pitch
        self.volume = volume

    def speak(self, text):
        cmd = [
            'espeak-ng',
            '-v', self.voice,
            '-s', str(self.speed),
            '-p', str(self.pitch),
            '-a', str(self.volume),
            text
        ]
        subprocess.run(cmd)

    def speak_async(self, text):
        threading.Thread(target=self.speak, args=(text,)).start()

tts = EspeakTTS()

def say(text, async_mode=False):
    if async_mode:
        tts.speak_async(text)
    else:
        tts.speak(text)

print("✅ Enhanced espeak-ng TTS loaded – improved voice quality")
