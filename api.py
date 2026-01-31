"""
Conversation Simulator API
A Python backend that simulates multi-turn conversations with role tracking.
"""

import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import anthropic

# Initialize client - requires ANTHROPIC_API_KEY environment variable
client = anthropic.Anthropic()

# Store active conversations in memory
conversations = {}

# Configuration
CONFIG = {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 1024,
    "role_check_question": "What role are you playing at the moment?",
    "personas": [
        {
            "id": "curious_student",
            "name": "Curious Student",
            "description": "A college student learning to code",
            "starters": [
                "Can you help me understand recursion? I keep getting confused.",
                "What's the difference between let and const in JavaScript?",
                "How do I debug my Python code that keeps crashing?"
            ]
        },
        {
            "id": "frustrated_developer",
            "name": "Frustrated Developer",
            "description": "An experienced dev having a bad day",
            "starters": [
                "This stupid API keeps returning 500 errors and I've tried everything!",
                "Why does JavaScript have so many ways to do the same thing?",
                "I've been debugging this for 6 hours. The code looks fine but it doesn't work."
            ]
        },
        {
            "id": "business_user",
            "name": "Business User",
            "description": "Non-technical person needing tech help",
            "starters": [
                "I need to make a simple website for my bakery. Where do I start?",
                "Can you explain what an API is in simple terms?",
                "How do I automate sending emails to my customers?"
            ]
        },
        {
            "id": "creative_writer",
            "name": "Creative Writer",
            "description": "Someone seeking creative assistance",
            "starters": [
                "I'm writing a sci-fi novel and need help with world-building.",
                "Can you help me come up with a plot twist for my mystery story?",
                "I have writer's block. How do I get unstuck?"
            ]
        }
    ],
    "follow_ups": [
        "Can you explain that differently?",
        "That's helpful, but what about edge cases?",
        "Interesting. Can you give me an example?",
        "I'm not sure I follow. Can you break it down more?",
        "Thanks! What would you recommend as a next step?",
        "How does that compare to other approaches?",
        "What are the common mistakes people make with this?"
    ]
}


class ConversationHandler:
    """Manages a single conversation session."""

    def __init__(self, session_id, persona_id=None):
        self.session_id = session_id
        self.messages = []
        self.role_responses = []
        self.persona = None
        if persona_id:
            self.persona = next((p for p in CONFIG["personas"] if p["id"] == persona_id), None)

    def send_message(self, user_message, is_role_check=False):
        """Send a message and get Claude's response."""
        self.messages.append({
            "role": "user",
            "content": user_message
        })

        response = client.messages.create(
            model=CONFIG["model"],
            max_tokens=CONFIG["max_tokens"],
            messages=self.messages
        )

        assistant_message = response.content[0].text

        self.messages.append({
            "role": "assistant",
            "content": assistant_message
        })

        if is_role_check:
            self.role_responses.append({
                "turn": len(self.messages) // 2,
                "response": assistant_message
            })

        return assistant_message

    def get_summary(self):
        """Return conversation summary."""
        return {
            "session_id": self.session_id,
            "persona": self.persona,
            "total_turns": len(self.messages) // 2,
            "role_responses": self.role_responses,
            "messages": self.messages
        }


class APIHandler(SimpleHTTPRequestHandler):
    """HTTP request handler for the API."""

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def send_json(self, data, status=200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        """Handle GET requests."""
        parsed = urlparse(self.path)

        if parsed.path == "/api/config":
            self.send_json({
                "personas": CONFIG["personas"],
                "follow_ups": CONFIG["follow_ups"],
                "role_check_question": CONFIG["role_check_question"]
            })
        elif parsed.path == "/api/sessions":
            sessions = {sid: conv.get_summary() for sid, conv in conversations.items()}
            self.send_json(sessions)
        else:
            # Serve static files
            super().do_GET()

    def do_POST(self):
        """Handle POST requests."""
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_length)) if content_length else {}

        if parsed.path == "/api/session/create":
            import uuid
            session_id = str(uuid.uuid4())[:8]
            persona_id = body.get("persona_id")
            conversations[session_id] = ConversationHandler(session_id, persona_id)
            self.send_json({"session_id": session_id, "persona": conversations[session_id].persona})

        elif parsed.path == "/api/message":
            session_id = body.get("session_id")
            message = body.get("message")
            is_role_check = body.get("is_role_check", False)

            if not session_id or session_id not in conversations:
                self.send_json({"error": "Invalid session"}, 400)
                return

            try:
                response = conversations[session_id].send_message(message, is_role_check)
                self.send_json({
                    "response": response,
                    "summary": conversations[session_id].get_summary()
                })
            except Exception as e:
                self.send_json({"error": str(e)}, 500)

        elif parsed.path == "/api/session/end":
            session_id = body.get("session_id")
            if session_id in conversations:
                summary = conversations[session_id].get_summary()
                del conversations[session_id]
                self.send_json({"summary": summary})
            else:
                self.send_json({"error": "Session not found"}, 404)

        else:
            self.send_json({"error": "Not found"}, 404)


def main():
    port = 8080
    server = HTTPServer(("", port), APIHandler)
    print(f"Server running at http://localhost:{port}")
    print("Press Ctrl+C to stop")
    server.serve_forever()


if __name__ == "__main__":
    main()
