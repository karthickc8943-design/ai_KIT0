import re
import json

class FastPatternMatcher:
    def __init__(self):
        # Patterns based on the requirements table
        self.patterns = [
            (r"(?:check|show|open|what's (?:on )?my)\s+(?:my\s+)?calend[ae]r", lambda m: {"action": "calendar_read", "when": "today"}),
            # Tomorrow — handles typos: tommarow, tomarrow, tommorow, tomorro
            (r".*\btom+[ao]r+o[ow]\b.*", lambda m: {"action": "calendar_read", "when": "tomorrow"}),
            (r".*\b(?:play|launch|open).*\b(?:game|steam)\b.*", lambda m: {"action": "open", "app": "steam"}),
            (r".*\b(?:play|song|music|track|skip|pause|resume|next|previous|suggest|playlist)\b.*", self.handle_music),
            (r"(?:my schedule|what are my events)", lambda m: {"action": "calendar_read", "when": "today"}),
            (r"(?:tell me a joke|make me laugh|funny)", lambda m: {"action": "joke"}),
            (r"(?:thank you|thanks|appreciate it)", lambda m: {"action": "thank"}),
            (r"(?:take screenshot|capture screen)", lambda m: {"action": "screenshot"}),
            (r"(?:lock screen|lock computer)", lambda m: {"action": "lock"}),
            (r"(?:volume up|increase volume)", lambda m: {"action": "volume", "direction": "up"}),
            (r"(?:volume down|decrease volume)", lambda m: {"action": "volume", "direction": "down"}),
            (r"(?:goodbye|bye|exit|quit)", lambda m: {"action": "exit"}),
            # Link control — must be BEFORE generic 'open' to catch 'open it/that/the link'
            (r"(?:open (?:it|that|the link|the url)|visit (?:it|the link|that)|yes[,!]? (?:open|show|visit)|show me (?:it|the link)|go to (?:it|the link))", lambda m: {"action": "open_link"}),
            # Standalone confirmations after JARVIS asks to open source
            (r"^(?:yes|yeah|yep|yup|sure|ok|okay|open it|ok the link|yes please|go ahead)$", lambda m: {"action": "open_link"}),
            (r"(?:close (?:it|that|the tab|the browser|the window)|no thanks|never mind|skip it)", lambda m: {"action": "close_tab"}),
            (r'\b(?:open|launch|start|run)\b\s+(.+)', self.handle_open),
            # Web search — fast-matched before AI to prevent misrouting
            (r"(?:search (?:about|for)|look up|research|who is|what is|tell me about)\s+(.+)", self.handle_web_search),
            (r"(?:generate image|draw|create image|make an image of|picture of)\s+(.+)", self.handle_image_gen),
            (r"(?:create event|schedule)\s+(.+)", self.handle_calendar_write),
        ]

    def handle_image_gen(self, match):
        prompt = match.group(1).strip()
        return {"action": "image_gen", "prompt": prompt}

    def handle_web_search(self, match):
        query = match.group(0).strip()
        return {"action": "web_search", "query": query}

    def handle_music(self, match):
        query = match.group(0).lower().strip()
        return {"action": "music", "query": query}

    def handle_open(self, match):
        app = match.group(1).lower().strip()
        # Clean common filler words
        app = app.replace("the ", "").replace("for me", "").strip()
        return {"action": "open", "app": app}

    def handle_calendar_write(self, match):
        content = match.group(1).lower().strip()
        when = "today"
        if "tomorrow" in content:
            when = "tomorrow"
            content = content.replace("tomorrow", "").strip()
        return {"action": "calendar_write", "event": content, "when": when}

    def match(self, text):
        text = text.lower().strip()
        for pattern, handler in self.patterns:
            m = re.search(pattern, text)
            if m:
                return handler(m)
        return None

class HybridRouter:
    def __init__(self, ai_router_func):
        self.fast = FastPatternMatcher()
        self.ai_fallback = ai_router_func

    def route(self, text):
        # 1. Try Fast Router
        command = self.fast.match(text)
        if command:
            return command, "⚡ Fast pattern match"
        
        # 2. Try AI Router fallback
        command = self.ai_fallback(text)
        return command, "🧠 AI fallback used"

# For testing
if __name__ == "__main__":
    def mock_ai(text):
        return {"action": "chat", "message": text}
    
    router = HybridRouter(mock_ai)
    test_cases = [
        "open chrome",
        "tell me the time",
        "my schedule",
        "lock computer",
        "How's the weather?"
    ]
    
    for tc in test_cases:
        cmd, method = router.route(tc)
        print(f"Input: {tc} -> {method} -> {cmd}")
