"""
Advanced System Automation Module for JARVIS
Fuzzy Matching + Conda Jupyter + Chrome App Mode
"""

import subprocess
import os
import datetime
import webbrowser
import re
import time
import difflib

# Module-level pending links buffer — stores last suggested link from web search
_pending_links = []  # list of (title, url) tuples

class SystemAutomation:
    def __init__(self):
        # Full App Mapping from User Desktop Image
        # Using exact Chrome App IDs for standalone window mode
        self.app_data = {
            'whatsapp': {
                'aliases': ['wa', 'whats app', 'whatsapp web'],
                'cmd': lambda: subprocess.Popen(['gtk-launch', 'chrome-hnpfjngllnobngcgfapefoaidbinmjnm-Default.desktop']),
                'msg': "Opening WhatsApp Web as an application, sir."
            },
            'ai assistant': {
                'aliases': ['assistant', 'jarvis web', 'ai chat'],
                'cmd': lambda: subprocess.Popen(['gtk-launch', 'chrome-bodfgilihmnhkjbneidhhcghbdhmknfd-Default.desktop']),
                'msg': "Launching your AI Assistant, sir."
            },
            'claude': {
                'aliases': ['claude ai', 'anthropic'],
                'cmd': lambda: subprocess.Popen(['gtk-launch', 'chrome-fmpnliohjhemenmnlpbfagaolkdacoja-Default.desktop']),
                'msg': "Opening Claude AI, sir."
            },
            'calendar': {
                'aliases': ['google calendar', 'my schedule', 'events'],
                'cmd': lambda: subprocess.Popen(['gtk-launch', 'chrome-kjbdgfilnfhdoflbpgamdcdgpehopbep-Default.desktop']),
                'msg': "Accessing your Google Calendar, sir."
            },
            'chatgpt': {
                'aliases': ['chat gpt', 'openai'],
                'cmd': lambda: subprocess.Popen(['gtk-launch', 'chrome-cadlkienfkclaiaibeoongdcgmdikeeg-Default.desktop']),
                'msg': "Opening ChatGPT, sir."
            },
            'coursera': {
                'aliases': ['courses', 'online learning'],
                'cmd': lambda: subprocess.Popen(['gtk-launch', 'chrome-lfdckbmfhdfakhogapfafjnanjficeae-Default.desktop']),
                'msg': "Opening Coursera, sir."
            },
            'github': {
                'aliases': ['git hub', 'repo'],
                'cmd': lambda: subprocess.Popen(['gtk-launch', 'chrome-mjoklplbddabcmpepnokjaffbmgbkkgg-Default.desktop']),
                'msg': "Opening GitHub, sir."
            },
            'openclaw': {
                'aliases': ['claw', 'open claw control'],
                'cmd': lambda: subprocess.Popen(['gtk-launch', 'chrome-eiomhnigcaelngkndeaaefnbjkmbkbha-Default.desktop']),
                'msg': "Accessing OpenClaw Control, sir."
            },
            'spotify': {
                'aliases': ['music', 'songs'],
                'cmd': lambda: subprocess.Popen(['spotify']),
                'msg': "Starting Spotify, sir."
            },
            'jupyter notebook': {
                'aliases': ['notebook', 'jupyter'],
                'cmd': lambda: subprocess.Popen(['bash', '-c', 'source ~/anaconda3/bin/activate base && jupyter notebook']),
                'msg': "Launching Jupyter Notebook in the Conda base environment, sir."
            },
            'jupyterlab': {
                'aliases': ['jupyter lab', 'lab'],
                'cmd': lambda: subprocess.Popen(['bash', '-c', 'source ~/anaconda3/bin/activate base && jupyter lab']),
                'msg': "Launching JupyterLab in the Conda base environment, sir."
            },
            'deepseek': {
                'aliases': ['deep seek', 'deepai'],
                'cmd': lambda: subprocess.Popen(['gtk-launch', 'chrome-kchcjjnjedekomllcloakpmknchiaakf-Default.desktop']),
                'msg': "Opening DeepSeek, sir."
            },
            'chaoxing': {
                'aliases': ['study portal', 'academic portal'],
                'cmd': lambda: subprocess.Popen(['gtk-launch', 'chrome-lffkaknapijdinnhcobkifbbmcmngdha-Default.desktop']),
                'msg': "Opening Chaoxing portal, sir."
            },
            'text editor': {
                'aliases': ['editor', 'notepad', 'gedit', 'gnome text editor'],
                'cmd': lambda: subprocess.Popen(['gnome-text-editor']),
                'msg': "Opening Text Editor, sir."
            },
            'libreoffice writer': {
                'aliases': ['writer', 'word', 'libreoffice'],
                'cmd': lambda: subprocess.Popen(['lowriter']),
                'msg': "Opening LibreOffice Writer, sir."
            },
            'chess': {
                'aliases': ['play chess', 'gnome chess'],
                'cmd': lambda: subprocess.Popen(['gnome-chess']),
                'msg': "Setting up the board for Chess, sir."
            },
            'youtube': {
                'aliases': ['yt', 'videos', 'you tube'],
                'cmd': lambda: subprocess.Popen(['gtk-launch', 'chrome-agimnkijcaahngcdmfeangaknmldooml-Default.desktop']),
                'msg': "Opening YouTube, sir."
            },
            'vlc': {
                'aliases': ['vlc media player', 'player', 'movies'],
                'cmd': lambda: subprocess.Popen(['vlc']),
                'msg': "Launching VLC Media Player, sir."
            },
            'file manager': {
                'aliases': ['nautilus', 'files', 'explorer', 'file manager', 'file system'],
                'cmd': lambda: subprocess.Popen(['nautilus']),
                'msg': "Opening File Manager, sir."
            },
            'antigravity': {
                'aliases': ['anti gravity', 'gravity app'],
                'cmd': lambda: subprocess.Popen(['gtk-launch', 'antigravity.desktop']),
                'msg': "Opening Antigravity, sir."
            },
            'clocks': {
                'aliases': ['clock', 'alarms', 'gnome clocks'],
                'cmd': lambda: subprocess.Popen(['gnome-clocks']),
                'msg': "Opening Clocks, sir."
            },
            'calculator': {
                'aliases': ['calc', 'math', 'gnome calculator'],
                'cmd': lambda: subprocess.Popen(['gnome-calculator']),
                'msg': "Opening Calculator, sir."
            },
            'chrome': {
                'aliases': ['google chrome', 'browser', 'web browser', 'internet', 'chromium'],
                'cmd': lambda: subprocess.Popen(['/snap/bin/chromium']),
                'msg': "Opening Chromium, sir."
            },
            'brave': {
                'aliases': ['brave browser'],
                'cmd': lambda: subprocess.Popen(['brave-browser']),
                'msg': "Opening Brave Browser, sir."
            },
            'firefox': {
                'aliases': ['fire fox', 'mozilla'],
                'cmd': lambda: subprocess.Popen(['firefox']),
                'msg': "Launching Firefox, sir."
            },
            'steam': {
                'aliases': ['games', 'gaming'],
                'cmd': lambda: subprocess.Popen(['steam']),
                'msg': "Launching Steam, sir."
            },
            'vscode': {
                'aliases': ['vs code', 'visual studio code', 'code'],
                'cmd': lambda: subprocess.Popen(['code']),
                'msg': "Opening Visual Studio Code, sir."
            },
            'telegram': {
                'aliases': ['telegram web', 'tg'],
                'cmd': lambda: subprocess.Popen(['gtk-launch', 'chrome-majiogicmcnmdhhlgmkahaleckhjbmlk-Default.desktop']),
                'msg': "Opening Telegram Web, sir."
            },
            'terminal': {
                'aliases': ['shell', 'bash', 'console'],
                'cmd': lambda: subprocess.Popen(['gnome-terminal']),
                'msg': "Opening terminal, sir."
            }
        }

        # Build a reverse lookup for difflib (flattens aliases)
        self.all_names = {}
        for app, info in self.app_data.items():
            self.all_names[app] = app
            for alias in info['aliases']:
                self.all_names[alias] = app

        # Special logic commands
        self.queries = {
            'screenshot': self.take_screenshot,
            'lock': self.lock_screen,
            'time': self.get_time,
            'date': self.get_date,
            'status': self.get_status,
            'coding': self.coding_setup,
            'volume': self.handle_volume,
            'music': self.handle_music,
            'song': self.handle_music,
            'track': self.handle_music,
            'skip': self.handle_music,
            'pause': self.handle_music,
            'stop': self.handle_music,
            'resume': self.handle_music,
            'next': self.handle_music,
            'previous': self.handle_music,
            'convert': self.handle_conversion,
        }

    def find_best_match(self, input_text):
        """Fuzzy matches the input to a known application name or alias"""
        input_text = input_text.lower().strip()
        
        # Guard against tiny filler words that cause false matches
        if len(input_text) < 3 or input_text in ['it', 'this', 'that', 'the']:
            return None
            
        names = list(self.all_names.keys())
        # Use a stricter cutoff (0.7) to avoid weak matches like 'it' -> 'gedit'
        matches = difflib.get_close_matches(input_text, names, n=1, cutoff=0.7)
        
        if matches:
            actual_app_key = self.all_names[matches[0]]
            return self.app_data[actual_app_key]
        return None

    def take_screenshot(self, query=""):
        try:
            import pyautogui
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.expanduser(f"~/Pictures/screenshot_{timestamp}.png")
            pyautogui.screenshot().save(path)
            return f"Screenshot saved to Pictures, sir."
        except: return "Failed to capture screenshot."

    def lock_screen(self, query=""):
        subprocess.run(['xdg-screensaver', 'lock'])
        return "System locked, sir."

    def get_time(self, query=""):
        return f"The current time is {datetime.datetime.now().strftime('%I:%M %p')}, sir."

    def get_date(self, query=""):
        return f"Today is {datetime.datetime.now().strftime('%B %d, %Y')}, sir."

    def handle_volume(self, query=""):
        if 'up' in query:
            subprocess.run(['amixer', 'set', 'Master', '10%+'])
            return "Volume increased, sir."
        elif 'down' in query:
            subprocess.run(['amixer', 'set', 'Master', '10%-'])
            return "Volume decreased, sir."
        elif 'mute' in query:
            subprocess.run(['amixer', 'set', 'Master', 'mute'])
            return "Sound muted, sir."
        elif 'unmute' in query:
            subprocess.run(['amixer', 'set', 'Master', 'unmute'])
            return "Sound restored, sir."
        elif 'set' in query:
            # Try to find a number
            match = re.search(r'\d+', query)
            if match:
                vol = match.group(0)
                subprocess.run(['amixer', 'set', 'Master', f'{vol}%'])
                return f"Volume set to {vol} percent, sir."
        return "Adjusting volume, sir."

    def handle_music(self, query=""):
        """Controls Spotify and other media via playerctl"""
        # Typo correction for 'truck' -> 'track'
        if 'truck' in query: query = query.replace('truck', 'track')
        
        if 'pause' in query or 'stop' in query:
            subprocess.run(['playerctl', 'pause'])
            return "Music paused, sir."
        elif 'next' in query or 'skip' in query or 'skip the track' in query:
            subprocess.run(['playerctl', 'next'])
            return "Skipping to the next track, sir."
        elif 'previous' in query or 'back' in query:
            subprocess.run(['playerctl', 'previous'])
            return "Returning to previous track, sir."
        elif 'play' in query or 'resume' in query or 'suggest' in query:
            # If the query is a suggestion or play request (e.g. "play any malayalam song")
            if 'suggest' in query or ('play' in query and len(query.split()) >= 3 and not any(w in query for w in ['resume', 'track'])):
                from web_search import get_best_music_link
                topic = query.lower()
                # Remove command words and filler words
                for word in ['play', 'suggest', 'song', 'songs', 'music', 'okey', 'ok', 'me', 'a', 'it', 'the', 'please', 'any', 'some', 'and', 'good', 'great', 'best', 'top', 'give', 'put', 'on']:
                    topic = re.sub(rf'\b{word}\b', '', topic)
                topic = ' '.join(topic.split())  # collapse multiple spaces
                
                if not topic: topic = "popular songs 2026"
                
                print(f"🎵 JARVIS: Looking for a suggestion: {topic}...")
                title, url = get_best_music_link(topic)
                
                if url:
                    print(f"🚀 JARVIS: Auto-launching: {url}")
                    webbrowser.open(url)
                    return f"I've located a popular {topic} playlist for you, Sir. Playing '{title}' now."
                else: 
                    return "I couldn't find a suitable music suggestion at the moment, Sir."

            subprocess.run(['playerctl', 'play'])
            return "Resuming playback, sir."
        elif ('what' in query or 'current' in query) and ('play' in query or 'song' in query or 'track' in query):
            try:
                title = subprocess.check_output(['playerctl', 'metadata', 'title'], text=True).strip()
                artist = subprocess.check_output(['playerctl', 'metadata', 'artist'], text=True).strip()
                return f"The current track is {title} by {artist}, sir."
            except:
                return "I couldn't retrieve the track information, sir."
        
        return "Controlling playback, sir."

    def get_status(self, query=""):
        try:
            from core import check_ollama_status
        except ImportError:
            from .core import check_ollama_status
        ollama = "Online" if check_ollama_status() else "Offline"
        return f"System nominal, sir. AI Engine: {ollama}. Memory: Logical."

    def handle_conversion(self, query=""):
        """Voice trigger for file conversion instructions"""
        formats = ['pdf', 'png', 'jpg', 'webp', 'csv', 'xlsx']
        target = None
        for f in formats:
            if f in query.lower():
                target = f
                break
        
        if target:
            return f"I can certainly help you convert that to {target.upper()}, sir. Please upload the file to the 'File Converter' tab in my dashboard, and I will handle the rest."
        return "I can convert documents to PDF, images between formats, and spreadsheets to Excel. Please use the 'File Converter' tab in my interface for file processing."

    def coding_setup(self, query=""):
        """Launches full coding environment"""
        self.app_data['vscode']['cmd']()
        self.app_data['spotify']['cmd']()
        self.app_data['deepseek']['cmd']()
        return "Coding environment established, sir. Good luck."

    def process_command(self, text):
        text_lower = text.lower().strip()

        # Clean wake words
        for wake in ['jarvis', 'hey jarvis', 'hello jarvis']:
            text_lower = text_lower.replace(wake, '').strip()

        if not text_lower: return None

        # 1. Handle special queries (time, screenshot, etc.)
        for key, func in self.queries.items():
            if key in text_lower:
                return func(text_lower)

        # 2. Handle 'Open' commands
        if 'open' in text_lower or 'launch' in text_lower or 'start' in text_lower:
            # Extract possible app name
            target = text_lower.replace('open', '').replace('launch', '').replace('start', '').strip()
            if target:
                match = self.find_best_match(target)
                if match:
                    match['cmd']()
                    return match['msg']

        return None

    def execute_json_command(self, command):
        """Standardized JSON execution layer"""
        action = command.get('action')
        if not action: return None

        if action == "open_link":
            global _pending_links
            if _pending_links:
                title, url = _pending_links[0]
                webbrowser.open(url)
                _pending_links = []
                return f"Opening '{title}' now, sir."
            # No pending link — treat 'yes' as conversational, fall through
            return None

        elif action == "close_tab":
            # Best-effort: try xdotool, then wmctrl, then just quietly acknowledge
            try:
                subprocess.run(['xdotool', 'key', 'ctrl+w'], capture_output=True, check=True)
            except (FileNotFoundError, subprocess.CalledProcessError):
                try:
                    subprocess.run(['wmctrl', '-c', ':ACTIVE:'], capture_output=True)
                except FileNotFoundError:
                    pass  # Neither tool available — just clear the buffer silently
            _pending_links = []
            return "Understood, sir. We'll leave that for now."

        elif action == "open":
            app = command.get('app', '')
            match = self.find_best_match(app)
            if match:
                match['cmd']()
                return match['msg']
            return f"I couldn't find an application called {app}, sir."

        elif action == "time": return self.get_time()
        elif action == "date": return self.get_date()
        
        elif action == "calendar_read":
            when = command.get('when', 'today')
            if when == 'tomorrow':
                from jarvis_calendar import tomorrow
                return tomorrow()
            from jarvis_calendar import today as calendar_today
            return calendar_today()

        elif action == "calendar_write":
            from jarvis_calendar import add_to_calendar
            event = command.get('event', '')
            when = command.get('when', 'today')
            # Existing add_to_calendar often takes full text, but we can adapt
            return add_to_calendar(f"{event} {when}")

        elif action == "joke": return self.get_joke()
        elif action == "thank": return "You're most welcome, sir. Happy to be of service."
        elif action == "music": return self.handle_music(command.get('query', ''))
        elif action == "screenshot": return self.take_screenshot()
        elif action == "lock": return self.lock_screen()
        
        elif action == "volume":
            direction = command.get('direction', '')
            return self.handle_volume(f"volume {direction}")
            
        elif action == "exit":
            print("System shutting down...")
            os._exit(0)
            
        elif action == "image_gen":
            prompt = command.get('prompt', '')
            # We use a simplified version of the generate_image_api here
            # For the full Gradio experience, we'll keep the Gradio version in ai_chat.py
            # but this allows voice/terminal to also generate images.
            import requests, urllib.parse, io
            from PIL import Image
            encoded_prompt = urllib.parse.quote(prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512"
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    img = Image.open(io.BytesIO(response.content))
                    save_path = os.path.expanduser(f"~/ai_files/image_{int(time.time())}.png")
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    img.save(save_path)
                    return f"✅ Image generated and saved to: {save_path}, sir."
                return "I encountered an error with the image generation service, sir."
            except Exception as e: return f"Error generating image: {e}"

        elif action == "web_search":
            from web_search import search_and_respond
            query = command.get('query', '')
            print(f"🌐 JARVIS: Autonomous search activated for '{query}'...")
            return search_and_respond(query)

        elif action == "chat":
            # For chat actions, we pass it back to the AI with a brevity constraint
            try:
                from core import set_response_with_memory
            except ImportError:
                from .core import set_response_with_memory
                
            from web_search import needs_web_search, search_and_respond
            msg = command.get('message', '')
            
            # Smart fallback: even if AI said 'chat', if it looks like a question needing web, search it
            if needs_web_search(msg):
                return search_and_respond(msg)
                
            return set_response_with_memory(msg)

        return None

    def get_joke(self, query=""):
        import random
        jokes = [
            "Why did the web developer walk out of a restaurant? Because of the table layout, sir.",
            "A SQL query walks into a bar, walks up to two tables, and asks, 'Can I join you?'",
            "There are 10 types of people in the world: those who understand binary, and those who don't.",
            "Why do programmers always mix up Halloween and Christmas? Because Oct 31 == Dec 25, sir.",
            "An optimist says 'The glass is half full.' A pessimist says 'The glass is half empty.' A programmer says 'The glass is twice as large as it needs to be.'"
        ]
        return random.choice(jokes)

_automation = None

def get_automation():
    global _automation
    if _automation is None: _automation = SystemAutomation()
    return _automation

def execute_command(text):
    return get_automation().process_command(text)
