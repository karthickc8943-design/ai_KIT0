"""
Wake Word Detection Module for AI Assistant
Uses OpenWakeWord (free, open-source alternative to Porcupine)
"""

import numpy as np
import threading
import time
import tempfile
import os
import sounddevice as sd
import soundfile as sf
from collections import deque

class WakeWordDetector:
    """
    Always-on wake word detection
n    Supports multiple wake words and continuous listening
    """
    
    # Default wake words that work well
    DEFAULT_WAKE_WORDS = ["hey jarvis", "hey computer", "jarvis"]
    
    def __init__(self, wake_words=None, sensitivity=0.7):
        """
        Initialize wake word detector
        
        Args:
            wake_words: List of wake words to detect (default: ["hey jarvis"])
            sensitivity: Detection threshold 0.0-1.0 (higher = more sensitive)
        """
        self.wake_words = wake_words or ["hey jarvis"]
        self.sensitivity = sensitivity
        self.listening = False
        self.callback = None
        self.audio_buffer = deque(maxlen=16000)  # 1 second at 16kHz
        
        # Model paths (will download on first run)
        self.model_path = os.path.expanduser("~/.cache/openwakeword")
        os.makedirs(self.model_path, exist_ok=True)
        
        self._detector = None
        self._thread = None
        
    def _load_model(self):
        """Load openwakeword model"""
        try:
            from openwakeword import Model
            
            # Download default models if not exists
            model_paths = []
            for wake_word in self.wake_words:
                model_file = os.path.join(self.model_path, f"{wake_word}.tflite")
                if not os.path.exists(model_file):
                    print(f"📥 Downloading model for '{wake_word}'...")
                    # Download from HuggingFace
                    import urllib.request
                    url = f"https://huggingface.co/datasets/rhasspy/openwakeword-models/resolve/main/{wake_word}.tflite"
                    try:
                        urllib.request.urlretrieve(url, model_file)
                        print(f"✅ Downloaded {wake_word}")
                    except Exception as e:
                        print(f"⚠️ Could not download {wake_word}: {e}")
                        # Use microwakeword as fallback
                        return self._load_microwakeword()
                model_paths.append(model_file)
            
            self._detector = Model(wakeword_models=model_paths)
            print(f"✅ Loaded wake word models: {self.wake_words}")
            return True
            
        except ImportError:
            print("⚠️ openwakeword not installed, trying microwakeword...")
            return self._load_microwakeword()
        except Exception as e:
            print(f"❌ Error loading wake word model: {e}")
            return False
    
    def _load_microwakeword(self):
        """Fallback to microwakeword (lighter, built-in models)"""
        try:
            import microwakeword
            
            # Use built-in models
            self._detector = microwakeword.MicroWakeWord(
                wakeword_models=["alexa", "hey jarvis"]
            )
            print("✅ Loaded microwakeword with built-in models")
            return True
        except ImportError:
            print("❌ Neither openwakeword nor microwakeword installed")
            print("   Install with: pip install openwakeword microwakeword")
            return False
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Process audio chunks"""
        if status:
            print(f"Audio status: {status}")
        
        # Convert to mono and add to buffer
        audio_data = indata[:, 0] if len(indata.shape) > 1 else indata
        self.audio_buffer.extend(audio_data)
        
        # Process when we have enough data
        while len(self.audio_buffer) >= 1600:  # 100ms chunks
            chunk = np.array([self.audio_buffer.popleft() for _ in range(1600)])
            self._process_chunk(chunk)
    
    def _process_chunk(self, audio_chunk):
        """Process audio chunk for wake word detection"""
        if self._detector is None:
            return
        
        try:
            # Detection logic depends on the library
            prediction = self._detector.predict(audio_chunk)
            
            # Check if any wake word detected
            if isinstance(prediction, dict):
                for wake_word, score in prediction.items():
                    if score > self.sensitivity:
                        self._on_wake_word_detected(wake_word, score)
            elif isinstance(prediction, (list, np.ndarray)):
                for i, score in enumerate(prediction):
                    if score > self.sensitivity:
                        self._on_wake_word_detected(self.wake_words[i], score)
            elif prediction > self.sensitivity:
                # Single output
                self._on_wake_word_detected(self.wake_words[0], prediction)
                
        except Exception as e:
            # Suppress frequent errors
            pass
    
    def _on_wake_word_detected(self, wake_word, confidence):
        """Handle wake word detection"""
        print(f"\n🎙️ Wake word detected: '{wake_word}' (confidence: {confidence:.2f})")
        
        if self.callback:
            try:
                self.callback(wake_word, confidence)
            except Exception as e:
                print(f"❌ Callback error: {e}")
    
    def start(self, callback=None, device=None):
        """
        Start listening for wake word
        
        Args:
            callback: Function to call when wake word detected
                     Signature: callback(wake_word, confidence)
            device: Microphone device index (None for default)
        """
        if self.listening:
            print("⚠️ Already listening")
            return False
        
        # Load model
        if not self._load_model():
            print("❌ Failed to load wake word model")
            return False
        
        self.callback = callback
        self.listening = True
        
        try:
            # Start audio stream
            self._stream = sd.InputStream(
                samplerate=16000,
                channels=1,
                dtype=np.float32,
                blocksize=1600,  # 100ms chunks
                callback=self._audio_callback,
                device=device
            )
            self._stream.start()
            
            print(f"🎙️ Listening for: {', '.join(self.wake_words)}")
            print(f"   Say one of the wake words to activate...")
            return True
            
        except Exception as e:
            print(f"❌ Error starting audio stream: {e}")
            self.listening = False
            return False
    
    def stop(self):
        """Stop listening"""
        self.listening = False
        if hasattr(self, '_stream'):
            self._stream.stop()
            self._stream.close()
        print("🛑 Wake word detection stopped")
    
    def is_listening(self):
        """Check if currently listening"""
        return self.listening


class WakeWordAssistant:
    """
    Integration class that connects wake word to your AI assistant
    """
    
    def __init__(self, ai_response_func, tts_func, stt_func):
        """
        Initialize wake word assistant
        
        Args:
            ai_response_func: Function to get AI response (takes text, returns text)
            tts_func: Text-to-speech function
            stt_func: Speech-to-text function (listen from mic)
        """
        self.ai_response = ai_response_func
        self.tts = tts_func
        self.stt = stt_func
        self.detector = WakeWordDetector()
        self.conversation_active = False
        
    def _on_wake_word(self, wake_word, confidence):
        """Handle wake word detection"""
        if self.conversation_active:
            return  # Already in conversation
        
        self.conversation_active = True
        
        # Play acknowledgment sound
        print("🔔 Wake word detected!")
        self.tts("Yes? I'm listening.")
        
        # Record and process user query
        try:
            print("🎤 Recording your question...")
            user_text = self.stt(duration=5)
            print(f"You said: {user_text}")
            
            # Get AI response
            response = self.ai_response(user_text)
            print(f"AI: {response}")
            
            # Speak response
            self.tts(response)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.tts("Sorry, I didn't catch that.")
        
        finally:
            self.conversation_active = False
            print("🎙️ Ready for next wake word...")
    
    def start_daemon(self, device=None):
        """Start the wake word daemon"""
        print("="*50)
        print("🚀 Wake Word Assistant Starting")
        print("="*50)
        
        # Start wake word detection
        if self.detector.start(callback=self._on_wake_word, device=device):
            print("\n✅ Assistant is running!")
            print("   Say 'Hey Jarvis' to activate")
            print("   Press Ctrl+C to stop")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Shutting down...")
                self.detector.stop()
        else:
            print("❌ Failed to start wake word detection")


# Simple wake word using VAD + Whisper (no model download required)
class SimpleWakeWord:
    """
    Lightweight wake word detection using Whisper + keyword matching
    No external models needed - uses your existing Whisper setup
    """
    
    def __init__(self, wake_word="jarvis", threshold=0.6):
        """
        Initialize simple wake word detector
        
        Args:
            wake_word: Word to detect (default: "jarvis")
            threshold: Similarity threshold (0.0-1.0)
        """
        self.wake_word = wake_word.lower()
        self.threshold = threshold
        self.listening = False
        self.callback = None
        
    def _similarity(self, text1, text2):
        """Simple word similarity check"""
        # Exact match
        if text1 == text2:
            return 1.0
        # Contains
        if text1 in text2 or text2 in text1:
            return 0.8
        # Levenshtein distance could be added here
        return 0.0
    
    def start(self, stt_func, callback=None, device=None):
        """
        Start listening with Whisper-based detection
        
        Args:
            stt_func: Your existing listen() function from faster_whisper_stt
            callback: Function to call when wake word detected
            device: Microphone device
        """
        self.listening = True
        self.callback = callback
        
        print(f"🎙️ Listening for '{self.wake_word}'...")
        print("   (Using Whisper for transcription)")
        
        while self.listening:
            try:
                # Listen for 2 seconds
                print("\n👂 Listening...", end="", flush=True)
                text = stt_func(duration=2, device_index=device, language="en")
                
                if text and text != "No speech detected.":
                    text_lower = text.lower().strip()
                    similarity = self._similarity(self.wake_word, text_lower)
                    
                    if similarity >= self.threshold:
                        print(f"\n🎙️ Wake word detected! (heard: '{text}')")
                        if self.callback:
                            self.callback(self.wake_word, similarity)
                    else:
                        print(f" (heard: '{text}')", end="")
                        
            except Exception as e:
                if "No speech" not in str(e):
                    print(f"\n⚠️ {e}")
                continue
    
    def stop(self):
        """Stop listening"""
        self.listening = False
        print("\n🛑 Stopped")


# Factory function for easy setup
def create_wake_word_detector(method="simple", **kwargs):
    """
    Create wake word detector with chosen method
    
    Args:
        method: "simple" (Whisper-based) or "advanced" (OpenWakeWord)
        **kwargs: Options for the detector
    
    Returns:
        WakeWordDetector instance
    """
    if method == "simple":
        return SimpleWakeWord(**kwargs)
    else:
        return WakeWordDetector(**kwargs)


print("✅ Wake Word module loaded!")
print("   Usage:")
print("   - Simple: from ai.wake_word import SimpleWakeWord")
print("   - Advanced: from ai.wake_word import WakeWordDetector")
print("   - Integration: from ai.wake_word import WakeWordAssistant")
