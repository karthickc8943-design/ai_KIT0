"""
Faster-Whisper STT - 4x faster than standard Whisper
Automatically detects device sample rate and resamples to 16kHz
"""

import numpy as np
import tempfile
import os
import subprocess
import time
from faster_whisper import WhisperModel

class FasterWhisperSTT:
    def __init__(self, model_size="base", device="cuda", language="en", mic_device_index=10):
        self.model_size = model_size
        self.device = device
        self.language = language
        self.mic_device_index = mic_device_index
        compute_type = "float16" if device == "cuda" else "int8"

        print(f"Loading Faster-Whisper {model_size} on {device}...")
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        print(f"✅ Ready! (Language: {language})")

    def get_sample_rate(self):
        """Get the default sample rate for the microphone"""
        try:
            import sounddevice as sd
            dev_info = sd.query_devices(self.mic_device_index)
            return int(dev_info['default_samplerate'])
        except:
            return 48000  # fallback

    def transcribe_file(self, audio_path, language=None):
        """Transcribe an audio file"""
        lang = language or self.language

        try:
            segments, info = self.model.transcribe(
                audio_path, 
                language=lang,
                beam_size=5,
                best_of=5
            )
            text = " ".join([seg.text for seg in segments])
            return text if text else "No speech detected."
        except Exception as e:
            return f"Transcription error: {e}"

    def transcribe_mic(self, duration=5, device_index=None, language=None):
        """Record from microphone and transcribe"""
        lang = language or self.language

        try:
            import sounddevice as sd
            import soundfile as sf

            # Use provided device index or default
            mic_idx = device_index if device_index is not None else self.mic_device_index
            samplerate = self.get_sample_rate()

            print(f"🎤 Recording for {duration} seconds at {samplerate} Hz...")
            recording = sd.rec(int(duration * samplerate),
                               samplerate=samplerate,
                               channels=1,
                               dtype='float32',
                               device=mic_idx)
            sd.wait()

            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name
                sf.write(temp_path, recording, samplerate)

            # Resample to 16kHz for Whisper
            resampled_path = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
            subprocess.run(['ffmpeg', '-i', temp_path, '-ar', '16000', resampled_path, '-y'],
                          capture_output=True)

            # Transcribe
            text = self.transcribe_file(resampled_path, language=lang)

            # Clean up
            os.unlink(temp_path)
            os.unlink(resampled_path)

            return text

        except Exception as e:
            return f"Recording error: {e}"

# Create default instance
stt = FasterWhisperSTT(mic_device_index=10)

def transcribe(audio_path, language="en"):
    """Transcribe an audio file"""
    return stt.transcribe_file(audio_path, language=language)




def listen(duration=5, device_index=None, language="en"):
    """Record and transcribe - preserves wake words"""
    try:
        text = stt.transcribe_mic(duration=duration, device_index=device_index, language=language)

        if not text:
            return ""

        # Check for wake words FIRST (don't filter them)
        wake_words = ["hey jarvis", "hello jarvis", "jarvis"]
        is_wake = any(wake in text.lower() for wake in wake_words)

        if is_wake:
            return text.strip()

        # Filter if the user is repeating the exact same phrase (Whisper hallucination)
        words = text.split()
        if len(words) > 6:
            # Check for 3-word phrase repeats
            for i in range(len(words)-6):
                phrase = " ".join(words[i:i+3])
                if text.count(phrase) >= 3:
                    print(f"🎤 Filtered Stutter Hallucination: {phrase}")
                    return ""

        # Keep hallucination filtering conservative to avoid dropping real commands.
        text_clean = text.strip().lower().rstrip('.')
        exact_noise = {
            "no speech detected",
            "error",
            "transcription error",
            "recording error",
            "thanks for watching",
            "transcribed by",
        }
        if text_clean in exact_noise and not is_wake:
            print(f"🎤 Filtered Hallucination: {text[:50]}")
            return ""

        noise_substrings = ["thanks for watching", "transcribed by"]
        if any(p in text_clean for p in noise_substrings) and not is_wake:
            print(f"🎤 Filtered Hallucination: {text[:50]}")
            return ""

        # Filter ultra-short gibberish only; keep short real commands like "yes", "stop".
        if len(text.strip()) < 2 and not is_wake:
            return ""

        # Filter if too many punctuation marks (hallucination sign)
        punct_count = sum(1 for c in text if c in '.,!?;:')
        if punct_count > len(text) * 0.4:
            return ""

        return text.strip()
    except Exception as e:
        print(f"Listen error: {e}")
        return ""

def list_microphones():
    """List available input devices"""
    try:
        import sounddevice as sd
        print("\n📋 Available input devices:")
        for i, dev in enumerate(sd.query_devices()):
            if dev['max_input_channels'] > 0:
                print(f"  {i}: {dev['name']} (SR: {dev['default_samplerate']:.0f} Hz)")
        print()
    except ImportError:
        print("sounddevice not installed")

def set_mic_device(device_index):
    """Change the default microphone device"""
    global stt
    stt.mic_device_index = device_index
    print(f"✅ Microphone set to device {device_index}")

print("✅ Faster-Whisper STT module loaded!")
print("   - 4x faster than standard Whisper")
print("   - Automatic sample rate detection")
print("   - Use list_microphones() to see available devices")
