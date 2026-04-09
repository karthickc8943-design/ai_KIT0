"""
Permanent Memory System for AI Chat - Enhanced Logic Version
Corrected Schema with Unique Keys
"""

import sqlite3
import json
import os
import re
from datetime import datetime
from pathlib import Path

class ChatMemory:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.expanduser("~/ai_memory/chat_memory.db")
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self.init_database()
        self.migrate_database()
    
    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # New schema: fact_key is PRIMARY to ensure "INSERT OR REPLACE" works as intended
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    fact_key TEXT UNIQUE, 
                    fact_value TEXT, 
                    category TEXT, 
                    importance INTEGER DEFAULT 1, 
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    user_message TEXT, 
                    ai_response TEXT, 
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, 
                    session_id TEXT
                )
            """)
            conn.commit()

    def migrate_database(self):
        """Handle schema migration safely"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Check if we have the old UNIQUE(fact_key, fact_value) constraint
                # In SQLite, the easiest way to update a constraint is to recreate the table
                cursor.execute("PRAGMA table_info(user_facts)")
                cols = cursor.fetchall()
                # If we have an 'id' but no unique constraint on 'fact_key', we need to fix it
                # For simplicity in this dev environment, we'll ensure fact_key is unique
                cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_fact_key ON user_facts(fact_key)")
                conn.commit()
        except Exception as e:
            print(f"⚠️ Migration note: {e}")

    def remember_fact(self, key, value, category="general", importance=1):
        """Store or update a fact in the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Using REPLACE here now works because fact_key is UNIQUE
            cursor.execute("""
                INSERT OR REPLACE INTO user_facts 
                (fact_key, fact_value, category, importance, timestamp) 
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (key.lower(), value, category, importance))
            conn.commit()
    
    def get_fact(self, key):
        """Retrieve a specific fact by key"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Order by timestamp to get the latest just in case
            cursor.execute("""
                SELECT fact_value, category FROM user_facts 
                WHERE fact_key = ? 
                ORDER BY timestamp DESC LIMIT 1
            """, (key.lower(),))
            result = cursor.fetchone()
            if result:
                return {"value": result[0], "category": result[1]}
            return None
    
    def get_all_facts(self):
        """Get all stored facts"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT fact_key, fact_value, category FROM user_facts ORDER BY importance DESC, timestamp DESC")
            return [{"key": r[0], "value": r[1], "category": r[2]} for r in cursor.fetchall()]

    def get_relevant_facts(self, query, limit=10):
        """Keyword-based semantic retrieval with recent-first priority"""
        words = re.findall(r'\w+', query.lower())
        stopwords = {'the', 'and', 'was', 'for', 'you', 'with', 'have', 'from', 'what', 'where', 'when', 'how'}
        keywords = [w for w in words if len(w) > 2 and w not in stopwords]
        
        if not keywords:
            return self.get_all_facts()[:limit]

        results = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for kw in keywords:
                cursor.execute("""
                    SELECT fact_key, fact_value, category 
                    FROM user_facts 
                    WHERE fact_key LIKE ? OR fact_value LIKE ?
                    ORDER BY importance DESC, timestamp DESC
                """, (f'%{kw}%', f'%{kw}%'))
                for r in cursor.fetchall():
                    fact = {"key": r[0], "value": r[1], "category": r[2]}
                    if fact not in results:
                        results.append(fact)
        
        return results[:limit]
    
    def add_conversation(self, user_message, ai_response, session_id="default"):
        """Save a conversation turn to history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversation_history 
                (user_message, ai_response, session_id, timestamp) 
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (user_message, ai_response, session_id))
            conn.commit()
    
    def get_recent_context(self, limit=5, session_id="default"):
        """Retrieve recent conversation history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_message, ai_response 
                FROM conversation_history 
                WHERE session_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (session_id, limit))
            results = cursor.fetchall()
            return list(reversed(results))
    
    def get_stats(self):
        """Get database statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM user_facts")
            facts_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM conversation_history")
            conv_count = cursor.fetchone()[0]
            return {"facts": facts_count, "conversations": conv_count}

_memory = None

def get_memory():
    global _memory
    if _memory is None:
        _memory = ChatMemory()
    return _memory

print("🧠 Logic Memory System active.")
