"""
Core text AI functions - Super Logic Memory Edition
"""
import requests
import json
import os
import re
try:
    from IPython.display import display, Markdown
    HAS_IPYTHON = True
except ImportError:
    HAS_IPYTHON = False

try:
    from .chat_memory import get_memory
except ImportError:
    from chat_memory import get_memory

# Global configuration
_current_model = "llama3.1:latest"

def check_ollama_status():
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def set_model(model_name):
    """Set the global model"""
    global _current_model
    _current_model = model_name
    print(f"✅ Model: {model_name}")

def get_current_model():
    """Get the current model name"""
    global _current_model
    return _current_model

def _ai_call(prompt, system="", model=None, temperature=0.3):
    """Internal helper for Ollama API calls"""
    use_model = model or _current_model
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                "model": use_model,
                "system": system,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature}
            },
            timeout=120
        )
        if response.status_code == 200:
            return response.json()['response'].strip()
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"❌ AI Error: {e}"

def _extract_facts_ai(user_msg, ai_response):
    """
    Super Logic: Use AI to extract structured facts from the conversation
    """
    memory = get_memory()
    extraction_prompt = f"""
    Analyze the following conversation and extract any NEW permanent facts about the user.
    Look for: preferences, names, relationships, goals, dislikes, or important context.
    
    User: {user_msg}
    AI: {ai_response}
    
    Return ONLY a JSON list of objects with "key", "value", "category", and "importance" (1-5).
    Example: [{{"key": "hobby", "value": "chess", "category": "preference", "importance": 3}}]
    If no new facts, return [].
    """
    
    try:
        result = _ai_call(extraction_prompt, system="You are a data extraction engine. Return only JSON.")
        # Extract JSON from potential code blocks
        json_match = re.search(r'\[.*\]', result, re.DOTALL)
        if json_match:
            facts = json.loads(json_match.group())
            for fact in facts:
                memory.remember_fact(
                    fact.get('key'), 
                    fact.get('value'), 
                    fact.get('category', 'general'), 
                    fact.get('importance', 1)
                )
                # print(f"🧠 Remembered: {fact.get('key')} = {fact.get('value')}")
    except Exception as e:
        # Silent fail for background extraction
        pass

def set_response_with_memory(prompt, model=None, session_id="default"):
    """
    Super Logic Response: Retrieve -> Reason -> Respond
    """
    memory = get_memory()
    
    # 1. Retrieval Pass: Get relevant facts
    relevant_facts = memory.get_relevant_facts(prompt)
    context_str = ""
    if relevant_facts:
        context_str = "RELEVANT CONTEXT FROM MEMORY:\n"
        for f in relevant_facts:
            context_str += f"- {f['key']}: {f['value']} ({f['category']})\n"
    
    # 2. History Pass: Get recent turns
    history = memory.get_recent_context(limit=3, session_id=session_id)
    history_str = ""
    if history:
        history_str = "RECENT CONVERSATION:\n"
        for u, a in history:
            history_str += f"User: {u}\nAI: {a}\n"

    # 3. Final Logical Prompt
    system_prompt = """
    You are JARVIS, Sir Karthick's personal PC-based AI assistant.
    
    TONE & PERSONA:
    - Calm, technical, Paul Bettany style. Always address the user as "Sir".
    - NO RAMBLING. Never use "My friend", "Old chap", or informal greetings.
    - BE EXTREMELY CONCISE (1-2 sentences max).
    
    REALITY RULES:
    - YOU CANNOT: Post to Google Drive, Control cars/IoT, or use "Google Play Music" (it is discontinued).
    - YOU CAN: Search the web, control Spotify via playerctl, and manage PC tasks.
    - If you provide a link, it will open automatically.
    
    STRICT TRUTH: If you don't have a tool, say "I cannot perform that action, Sir." Do not make up system statuses.
    """
    
    full_prompt = f"""
    {context_str}
    {history_str}
    
    SYSTEM INSTRUCTIONS:
    {system_prompt}
    
    USER REQUEST: {prompt}
    
    LOGICAL RESPONSE:
    """
    
    # Generate response
    print("🧠 JARVIS is thinking...")
    ai_response = _ai_call(full_prompt, system=system_prompt, model=model)
    
    # 4. Background Learning: Extract facts from this turn
    import threading
    threading.Thread(target=_extract_facts_ai, args=(prompt, ai_response)).start()
    
    # 5. Save to History
    memory.add_conversation(prompt, ai_response, session_id)
    
    return ai_response

def set_response(prompt, model=None, system=""):
    """Simple response without full logic loop"""
    return _ai_call(prompt, system=system, model=model)

def out(prompt, model=None):
    """Get AI response with markdown formatting"""
    response = set_response_with_memory(prompt, model)
    if response and not response.startswith("❌"):
        if HAS_IPYTHON:
            display(Markdown(response))
        else:
            print(f"\n{response}\n")
    return response

# Standard utility functions
def remember_fact(key, value, category="general"):
    get_memory().remember_fact(key, value, category, importance=5)

def get_fact(key):
    res = get_memory().get_fact(key)
    return res['value'] if res else None

def route_with_ai(user_input):
    """
    JARVIS AI Command Router fallback.
    Analyzes input and returns a command dictionary.
    """
    prompt = f"""
You are JARVIS command router. Analyze: "{user_input}"

Output ONLY JSON:

· For conversation: {{"action": "chat", "message": "user message"}}
· For action commands:
  - {{"action": "open", "app": "name"}}
  - {{"action": "calendar_read", "when": "today/tomorrow"}}
  - {{"action": "calendar_write", "event": "details", "when": "today/tomorrow"}}
  - {{"action": "volume", "direction": "up/down"}}
  - {{"action": "time"}} / {{"action": "date"}} / {{"action": "joke"}} / {{"action": "screenshot"}} / {{"action": "lock"}} / {{"action": "exit"}}

Examples:
· "how are you?" → {{"action": "chat", "message": "how are you?"}}
· "what's the weather?" → {{"action": "chat", "message": "what's the weather?"}}
· "remind me to call mom" → {{"action": "calendar_write", "event": "call mom", "when": "today"}}

Response:
"""
    try:
        response = set_response(prompt, system="You are a command router. Return only valid JSON.")
        # Clean response if LLM adds markdown backticks
        clean_json = response.strip().replace('```json', '').replace('```', '')
        return json.loads(clean_json)
    except Exception as e:
        print(f"⚠️ AI Route Error: {e}")
        return {"action": "chat", "message": user_input}

def show_memory_stats():
    stats = get_memory().get_stats()
    print(f"📊 Memory: {stats['facts']} facts, {stats['conversations']} turns.")
    return stats
