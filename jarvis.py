#!/usr/bin/env python3
"""
JARVIS - The All-in-One Voice Assistant Controller
"""
import time
import os
import sys

# Import local modules
try:
    from .core import set_response, set_response_with_memory
    from .tts_jarvis import say, set_voice
    from .faster_whisper_stt import listen, transcribe
    from .system_automation import execute_command
    from .web_search import smart_chat, needs_web_search
    from .chat_memory import get_memory
    from .jarvis_calendar import today as calendar_today, add_to_calendar
except ImportError:
    # If run as a script directly
    from core import set_response, set_response_with_memory
    from tts_jarvis import say, set_voice
    from faster_whisper_stt import listen, transcribe
    from system_automation import execute_command
    from web_search import smart_chat, needs_web_search
    from chat_memory import get_memory
    from jarvis_calendar import today as calendar_today, add_to_calendar

from .command_router import HybridRouter
from .core import route_with_ai

# Initialize Global Router
router = HybridRouter(route_with_ai)

def process_query(text):
    """
    Hybrid Routing logic for JARVIS
    """
    if not text or len(text.strip()) < 2:
        return None

    print(f"\n✅ Heard: {text}")
    
    # Run the Hybrid Router
    command, tag = router.route(text)
    print(tag) # Shows ⚡ Fast pattern match or 🧠 AI fallback used
    
    # Execute via SystemAutomation
    response = get_automation().execute_json_command(command)
    
    if response:
        print(f"🤖 JARVIS: {response}")
        # Don't auto-open links — user must say 'open it' explicitly
        return response
    
    return None

def auto_open_links(text):
    """Automatically detect and open URLs in JARVIS's response"""
    import re
    import webbrowser
    links = re.findall(r'https?://[^\s()\]]+', text)
    if links:
        print(f"🚀 JARVIS: Opening link: {links[0]}")
        webbrowser.open(links[0])

def main():
    print("="*60)
    print("🤖 JARVIS VOICE ASSISTANT STARTING")
    print("="*60)

    # Set initial voice
    set_voice("alan")
    
    # Optional greeting
    greeting = "Systems online, sir. How can I assist you today?"
    print(f"JARVIS: {greeting}")
    say(greeting, async_mode=True)

    # Main Loop
    try:
        while True:
            # Using simple wake word detection logic
            # In a real scenario, this would be the detector.start()
            # For this version, we'll use the 'listen' function directly for a trial
            
            print("\n🎙️ Listening for 'Jarvis'...")
            # Silence music before listening to prevent interference
            subprocess.run(['playerctl', 'pause'], capture_output=True)
            
            user_input = listen(duration=4)
            
            if user_input:
                if "jarvis" in user_input.lower():
                    clean_input = user_input.lower().replace("jarvis", "").strip()
                    
                    if not clean_input:
                        ack = "Yes, sir?"
                        print(f"JARVIS: {ack}")
                        # Keep music paused for the next command
                        say(ack)
                        clean_input = listen(duration=5)
                    
                    if clean_input:
                        response = process_query(clean_input)
                        if response:
                            say(response)
                            # Music will resume via the 'say' function completion logic or manual resume
                            if any(word in clean_input for word in ['stop', 'pause']):
                                pass # Don't resume if they said stop
                            else:
                                subprocess.run(['playerctl', 'play'], capture_output=True)
                else:
                    # Resume music if no wake word detected
                    subprocess.run(['playerctl', 'play'], capture_output=True)
            else:
                # Resume music if no speech heard
                subprocess.run(['playerctl', 'play'], capture_output=True)
            
            time.sleep(0.1)

    except KeyboardInterrupt:
        subprocess.run(['playerctl', 'play'], capture_output=True) # Ensure music restored
        print("\n👋 Shutting down, sir. Have a pleasant day.")
        say("Shutting down, sir. Have a pleasant day.")
        sys.exit(0)

if __name__ == "__main__":
    main()
