"""
Web Search Module for AI Toolkit
Uses DuckDuckGo HTML search with guaranteed response
"""

import requests
import re
try:
    from .core import set_response
except ImportError:
    from core import set_response

def web_search(query, max_results=5):
    """Search the web using DuckDuckGo HTML search"""
    try:
        print(f"🔍 Searching for: {query}")

        url = "https://html.duckduckgo.com/html/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        params = {'q': query}

        response = requests.post(url, data=params, headers=headers, timeout=30)

        results = []

        # Extract results
        link_pattern = r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>([^<]+)</a>'
        snippet_pattern = r'<a[^>]+class="result__snippet"[^>]*>([^<]+(?:<[^>]+>[^<]*</[^>]+>[^<]*)*)</a>'

        links = re.findall(link_pattern, response.text)
        snippets = re.findall(snippet_pattern, response.text)

        for i, (link, title) in enumerate(links[:max_results]):
            link = link.replace('&amp;', '&')
            title = re.sub(r'<[^>]+>', '', title)

            snippet = ""
            if i < len(snippets):
                snippet = re.sub(r'<[^>]+>', '', snippets[i])
                snippet = snippet.replace('&amp;', '&').replace('&quot;', '"')

            results.append({
                'title': title.strip(),
                'body': snippet.strip()[:400] if snippet else "No description available",
                'href': link
            })

        print(f"✅ Found {len(results)} results")
        return results

    except requests.exceptions.Timeout:
        print(f"⏱️ Search timed out, retrying...")
        try:
            response = requests.post(url, data=params, headers=headers, timeout=45)
            results = []
            links = re.findall(link_pattern, response.text)
            for i, (link, title) in enumerate(links[:max_results]):
                link = link.replace('&amp;', '&')
                title = re.sub(r'<[^>]+>', '', title)
                results.append({'title': title.strip(), 'body': '', 'href': link})
            print(f"✅ Retry found {len(results)} results")
            return results
        except Exception:
            print(f"❌ Retry also failed")
            return []

def search_and_respond(query):
    """Search the web. Summarize first, store link for deferred opening."""
    print(f"🌐 Smart Search activated for: {query}")

    try:
        results = web_search(query, max_results=5)

        if not results:
            return f"I searched for '{query}' but found no results, sir."

        # Build context for AI
        context = "REAL-TIME SEARCH RESULTS:\n"
        for i, result in enumerate(results[:5], 1):
            title = result.get('title', 'No title')
            body = result.get('body', '')[:300]
            href = result.get('href', '')
            context += f"• {title}: {body} (Link: {href})\n"

        system_prompt = """
        You are JARVIS, Sir Karthick's personal AI. Use the results to answer concisely.
        
        RULES:
        1. Give a concise 2-3 sentence SUMMARY. Do NOT include raw URLs in your answer.
        2. Address the user as "Sir".
        3. End your response with: "Would you like me to open the source, Sir?"
        """

        prompt = f"RESULTS:\n{context}\nUSER REQUEST: {query}\n"
        response = set_response(prompt, system=system_prompt)

        # Store the top link in the pending buffer for deferred opening
        try:
            import system_automation as sa
            top = results[0]
            sa._pending_links = [(top['title'], top['href'])]
        except Exception:
            pass

        return response if response else "I found relevant information. Would you like me to open the source, Sir?"

    except Exception as e:
        print(f"Error in search_and_respond: {e}")
        return f"I encountered an error while searching for '{query}', sir."

def needs_web_search(query):
    """Autonomous intent detector for web search necessity"""
    # Guard: 'search again' is a meta-command, not a real query
    if query.strip().lower() in ['search again', 'try again', 'retry']:
        return False
    keywords = [
        'today', 'now', 'latest', 'current', 'news', 'weather', 
        'price', 'cost', 'buy', 'link', 'website', 'address', 'number',
        'phone', 'who is', 'who was', 'where is', 'when will', 'score', 
        'match', 'vs', 'live', 'movie', 'showtimes', 'near me', 'shops'
    ]
    query_lower = query.lower()
    
    # Check for direct search requests
    if any(word in query_lower for word in ['search for', 'look up', 'google']):
        return True
        
    # Check for real-time keywords
    for keyword in keywords:
        if keyword in query_lower:
            return True
            
    return False

def smart_chat(message, auto_web=True):
    """Smart chat with automatic web search"""
    if auto_web and needs_web_search(message):
        print(f"🌐 Searching web for: {message}")
        return search_and_respond(message)
    else:
        print(f"💬 Using local AI")
        return set_response(message)

def get_best_music_link(query):
    """Specific helper to find the best playable music link"""
    # Force 'spotify' into query if not present for better results
    search_query = query if 'spotify' in query.lower() else f"{query} spotify playlist"
    results = web_search(search_query, max_results=5)
    
    if not results:
        return None, None
        
    # Prioritize deep Spotify links (playlists, tracks, etc)
    playable_patterns = ['/playlist/', '/track/', '/album/', '/artist/']
    
    for r in results:
        url = r['href'].lower()
        if 'spotify.com' in url and any(p in url for p in playable_patterns):
            return r['title'], r['href']
            
    # Second priority: Any Spotify link, then fallback
    for r in results:
        if 'spotify.com' in r['href']:
            return r['title'], r['href']
            
    return results[0]['title'], results[0]['href']

print("✅ Web Search module loaded (fixed version)")
