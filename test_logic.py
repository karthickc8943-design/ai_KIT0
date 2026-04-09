"""
Verification of 'Super Logic Memory'
"""
import time
from core import set_response_with_memory, show_memory_stats

def test_logic_memory():
    print("🚀 Initializing Logic Test...")
    
    # 1. Fact Injection
    msg1 = "My wife's birthday is October 24th and she loves orchids."
    print(f"\nUser: {msg1}")
    resp1 = set_response_with_memory(msg1)
    print(f"JARVIS: {resp1}")
    
    time.sleep(2) # Wait for background threads
    show_memory_stats()
    
    # 2. Logic Challenge
    msg2 = "What should I get for the special occasion in late October?"
    print(f"\nUser: {msg2}")
    resp2 = set_response_with_memory(msg2)
    print(f"JARVIS: {resp2}")
    
    if "orchid" in resp2.lower():
        print("\n✅ LOGIC PASS: JARVIS correctly recalled the orchid preference!")
    else:
        print("\n❌ LOGIC FAIL: JARVIS forgot the preference.")

if __name__ == "__main__":
    test_logic_memory()
