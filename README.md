# Conversation Simulator

A multi-turn conversation simulator that tests Claude's responses with different user personas. Periodically asks Claude "What role are you playing?" to track role consistency.

## Setup

1. Clone the repo:
```bash
git clone https://github.com/Silveroboros-dev/conversation-simulator.git
cd conversation-simulator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set your Anthropic API key:
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

4. Run the server:
```bash
python api.py
```

5. Open http://localhost:8080 in your browser

## Usage

### Interactive Mode
1. Select a persona (Curious Student, Frustrated Developer, etc.)
2. Click "Start Session"
3. Type messages and click "Send"
4. Click "Ask Role Check" to ask Claude what role it's playing

### Automated Mode
1. Select a persona
2. Click "Start Session"
3. Set number of turns
4. Click "Run Simulation" to watch an automated conversation with periodic role checks

## Features

- 4 user personas with different conversation styles
- Interactive and automated conversation modes
- Role tracking panel showing all role check responses
- Configurable number of conversation turns

## API Endpoints

- `GET /api/config` - Get personas and settings
- `POST /api/session/create` - Start new conversation session
- `POST /api/message` - Send message and get response
- `POST /api/session/end` - End session and get summary

## Get an API Key

Get your Anthropic API key at https://console.anthropic.com/settings/keys
