"""
JARVIS Calendar Module - Complete with all functions
"""

import os
import pickle
import re
from datetime import datetime, timedelta, timezone
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

print("📅 Loading JARVIS Calendar Module (Write Enabled)...")

CREDS_FILE = os.path.expanduser("~/Desktop/Private_JARVIS/credentials.json")
TOKEN_FILE = os.path.expanduser("~/Desktop/Private_JARVIS/token_write.pickle")
SCOPES = ['https://www.googleapis.com/auth/calendar']

_service = None

def _get_service():
    global _service
    if _service is not None:
        return _service

    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    _service = build('calendar', 'v3', credentials=creds)
    return _service

def today():
    """Get today's events (from now until 11:59 PM)"""
    service = _get_service()
    
    # Current time in local timezone
    now_local = datetime.now()
    # End of today (23:59:59)
    end_of_today = datetime.combine(now_local.date(), datetime.max.time())
    
    # Convert to RFC3339 format for Google API (append local offset or use UTC 'Z')
    # Since we're comparing, using naive local time with proper UTC conversion is safest
    time_min = now_local.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
    time_max = end_of_today.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    events = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    items = events.get('items', [])
    if not items:
        return "You have no events today."

    result = []
    for event in items:
        start = event['start'].get('dateTime', event['start'].get('date'))
        if start:
            try:
                # Handle both dateTime and date-only events
                if 'T' in start:
                    dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    result.append(f"• {dt.strftime('%I:%M %p')}: {event.get('summary', 'Untitled')}")
                else:
                    result.append(f"• [All Day]: {event.get('summary', 'Untitled')}")
            except:
                result.append(f"• {event.get('summary', 'Untitled')}")

    if len(result) == 1:
        return f"You have one event today: {result[0]}"
    return f"You have {len(result)} events today:\n" + "\n".join(result)

def tomorrow():
    """Get tomorrow's events (Midnight to Midnight)"""
    service = _get_service()
    
    # Tomorrow's date
    tomorrow_date = datetime.now().date() + timedelta(days=1)
    # Start of tomorrow (00:00:00)
    start_of_tomorrow = datetime.combine(tomorrow_date, datetime.min.time())
    # End of tomorrow (23:59:59)
    end_of_tomorrow = datetime.combine(tomorrow_date, datetime.max.time())
    
    time_min = start_of_tomorrow.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
    time_max = end_of_tomorrow.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    events = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    items = events.get('items', [])
    if not items:
        return "You have no events tomorrow."

    result = []
    for event in items:
        start = event['start'].get('dateTime', event['start'].get('date'))
        if start:
            try:
                if 'T' in start:
                    dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    result.append(f"• {dt.strftime('%I:%M %p')}: {event.get('summary', 'Untitled')}")
                else:
                    result.append(f"• [All Day]: {event.get('summary', 'Untitled')}")
            except:
                result.append(f"• {event.get('summary', 'Untitled')}")

    if len(result) == 1:
        return f"You have one event tomorrow: {result[0]}"
    return f"You have {len(result)} events tomorrow:\n" + "\n".join(result)

def week():
    """Get next 7 days events"""
    service = _get_service()
    now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    future = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat().replace('+00:00', 'Z')
    events = service.events().list(
        calendarId='primary',
        timeMin=now,
        timeMax=future,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    items = events.get('items', [])
    if not items:
        return "You have no events in the next 7 days."

    result = []
    for event in items:
        start = event['start'].get('dateTime', event['start'].get('date'))
        if start:
            try:
                dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                result.append(f"• {dt.strftime('%A at %I:%M %p')}: {event.get('summary', 'Untitled')}")
            except:
                result.append(f"• {event.get('summary', 'Untitled')}")

    return "Here are your upcoming events:\n" + "\n".join(result[:10])

def next_event():
    """Get next upcoming event"""
    service = _get_service()
    now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    events = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=1,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    items = events.get('items', [])
    if not items:
        return "You have no upcoming events."

    event = items[0]
    start = event['start'].get('dateTime', event['start'].get('date'))
    if start:
        try:
            dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            return f"Your next event is at {dt.strftime('%I:%M %p')}: {event.get('summary', 'Untitled')}"
        except:
            return f"Your next event is: {event.get('summary', 'Untitled')}"
    return f"Your next event is: {event.get('summary', 'Untitled')}"

def add_to_calendar(text):
    """Create event from natural language"""
    service = _get_service()

    text_lower = text.lower()

    if 'tomorrow' in text_lower:
        event_date = datetime.now() + timedelta(days=1)
    else:
        event_date = datetime.now()

    # Extract title (remove command words)
    title = text_lower
    # Aggressively strip command prefixes and action verbs
    prefixes = [
        'create event', 'schedule', 'add event', 'remind me to', 
        'appointment', 'meeting', 'tomorrow', 'add to my calendar',
        'create an', 'add a', 'set a', 'set an', 'with the', 'with',
        'check my', 'read my', 'what is', 'show my', 'tell me about'
    ]
    for kw in sorted(prefixes, key=len, reverse=True):
        title = title.replace(kw, ' ')
    
    # Clean up excess spaces
    title = re.sub(r'\s+', ' ', title).strip()
    
    # Extract time with a more robust regex
    time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*([ap]\.?m\.?)', text_lower, re.IGNORECASE)

    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        ampm_raw = time_match.group(3).lower()
        ampm = 'am' if 'a' in ampm_raw else 'pm'

        if ampm == 'pm' and hour != 12:
            hour += 12
        elif ampm == 'am' and hour == 12:
            hour = 0

        event_date = event_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        time_display = time_match.group(0)
        # Remove time from title
        title = re.sub(r'(\d{1,2})(?::(\d{2}))?\s*([ap]\.?m\.?)', '', title, flags=re.IGNORECASE).strip()
    else:
        event_date = event_date.replace(hour=15, minute=0, second=0, microsecond=0)
        time_display = "3:00 PM"

    if not title:
        title = "Untitled Event"

    end_date = event_date + timedelta(hours=1)

    event = {
        'summary': title,
        'start': {'dateTime': event_date.isoformat(), 'timeZone': 'Asia/Singapore'},
        'end': {'dateTime': end_date.isoformat(), 'timeZone': 'Asia/Singapore'},
    }

    result = service.events().insert(calendarId='primary', body=event).execute()
    return f"✅ Event created: {title} at {time_display}"

print("✅ JARVIS Calendar Module Ready (Write Enabled)!")
print("   Functions: today(), tomorrow(), week(), next_event(), add_to_calendar()")
