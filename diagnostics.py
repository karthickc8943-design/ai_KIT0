"""
JARVIS System Diagnostics - Comprehensive Module Test
"""

import sys
import os
import time

# Add ai1 toolkit to path
toolkit_path = os.path.dirname(os.path.abspath(__file__))
if toolkit_path not in sys.path:
    sys.path.append(toolkit_path)

print("🚀 JARVIS SYSTEM DIAGNOSTICS")
print("="*50)

def test_core():
    print("\n[1/6] Core AI & Ollama...")
    try:
        from core import check_ollama_status, set_response
        if check_ollama_status():
            print("  ✅ Ollama: ONLINE")
            resp = set_response("Say 'Diagnostics pass'")
            print(f"  ✅ AI Response: {resp}")
            return True
        else:
            print("  ❌ Ollama: OFFLINE")
            return False
    except Exception as e:
        print(f"  ❌ Core Error: {e}")
        return False

def test_memory():
    print("\n[2/6] Logic Memory System...")
    try:
        from chat_memory import get_memory
        m = get_memory()
        test_key = "diagnostic_run"
        test_val = str(time.time())
        m.remember_fact(test_key, test_val, "system", 1)
        res = m.get_fact(test_key)
        if res and res['value'] == test_val:
            print(f"  ✅ Fact Storage/Recall: SUCCESS")
            return True
        else:
            print("  ❌ Memory Recall: FAILED")
            return False
    except Exception as e:
        print(f"  ❌ Memory Error: {e}")
        return False

def test_automation():
    print("\n[3/6] Automation & Fuzzy Matching...")
    try:
        from system_automation import execute_command
        # Test 1: Typo matching
        match1 = execute_command("open cluade")
        if match1 and "Claude" in match1:
            print("  ✅ Fuzzy Typo Match (open cluade): SUCCESS")
        else:
            print("  ❌ Fuzzy Match: FAILED")
            return False
        
        # Test 2: Strict requirement matching
        # "whats up" should NOT trigger WhatsApp now
        match2 = execute_command("whats up")
        if match2 is None:
            print("  ✅ Strict Prefix Check (whats up): SUCCESS (No trigger)")
        else:
            print(f"  ❌ Strict Prefix Check: FAILED (Accidental trigger: {match2})")
            return False
        return True
    except Exception as e:
        print(f"  ❌ Automation Error: {e}")
        return False

def test_voice():
    print("\n[4/6] Audio Systems (STT/TTS)...")
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        input_devs = [d for d in devices if d['max_input_channels'] > 0]
        if input_devs:
            print(f"  ✅ Microphones Found: {len(input_devs)}")
        else:
            print("  ❌ No Microphones Found")
        
        from tts_jarvis import say
        print("  🔊 Testing Voice Output (Alan)...")
        say("System diagnostics in progress.")
        return True
    except Exception as e:
        print(f"  ❌ Audio Error: {e}")
        return False

def test_calendar():
    print("\n[5/6] Calendar Integration...")
    try:
        from jarvis_calendar import today
        res = today()
        if res and "today" in res.lower():
            print(f"  ✅ Calendar: WORKING ({res[:30]}...)")
            return True
        return False
    except Exception as e:
        print(f"  ❌ Calendar Error: {e}")
        return False

def test_vision():
    print("\n[6/6] Vision & Video Modules...")
    try:
        from video_analysis import analyze_video
        from image import describe_image
        print("  ✅ Imports: SUCCESS")
        return True
    except Exception as e:
        print(f"  ❌ Vision Imports Error: {e}")
        return False

if __name__ == "__main__":
    results = {
        "Core": test_core(),
        "Memory": test_memory(),
        "Automation": test_automation(),
        "Audio": test_voice(),
        "Calendar": test_calendar(),
        "Vision": test_vision()
    }
    
    print("\n" + "="*50)
    print("📋 FINAL TEST SUMMARY")
    for k, v in results.items():
        status = "PASSED" if v else "FAILED"
        print(f"  • {k:10}: {status}")
    print("="*50)
    
    if all(results.values()):
        print("\n✅ ALL SYSTEMS NOMINAL. Ready for deployment, sir.")
    else:
        print("\n⚠️ SYSTEM ISSUES DETECTED. Please check logs above.")
