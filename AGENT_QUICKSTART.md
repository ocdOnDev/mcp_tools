# MCP Agent - Quick Start Guide

## 🚀 Get Started in 60 Seconds

### 1. Check Everything is Running

```bash
python mcp_agent.py status
```

Expected output:
```
✓ MCP Server: Running at http://localhost:8000 (9 tools available)
✓ Ollama: Running at http://localhost:11434 (2 models available)
```

---

### 2. Try It Out!

#### Option A: Single Question

```bash
python mcp_agent.py ask "What's the weather in Paris?"
```

#### Option B: Interactive Chat

```bash
python mcp_agent.py chat
```

Then type:
```
You> Summarize this video: https://www.youtube.com/watch?v=EmfoQWQ1DR8
Agent> [Generates summary using youtube_summary tool]

You> What were the main points?
Agent> [Responds with context from previous message]

You> /exit
```

#### Option C: Web Chat UI

```bash
# Start web server
python -m uvicorn agent.web_api:web_app --reload --port 8001

# Open browser
# http://localhost:8001/chat
```

---

## 📋 Common Commands

### CLI Commands

```bash
# Get help
python mcp_agent.py --help

# Ask with specific model
python mcp_agent.py ask "Question" --model gpt-oss:20b

# Ask with markdown output
python mcp_agent.py ask "List 5 Python tips" --format markdown

# List available tools
python mcp_agent.py tools

# Start interactive chat
python mcp_agent.py chat
```

### In Chat Mode

- `/help` - Show commands
- `/clear` - Clear history
- `/tools` - List tools
- `/exit` - Exit chat

---

## 💡 Example Queries

### Simple Chat
```
"Hello, who are you?"
"Explain quantum computing in simple terms"
"Tell me a joke about programming"
```

### Tool Usage
```
"What's the weather in Tokyo?"
"Summarize: https://www.youtube.com/watch?v=VIDEO_ID"
"Get the transcript of this video: https://youtube.com/..."
"What are my system metrics?"
```

### Multi-Step
```
"What's the capital of France and what's the weather there?"
"Compare the topics in these two videos: [url1] [url2]"
```

---

## 🎯 Quick Tips

1. **Faster responses**: Use `--model gemma:latest` (default)
2. **Better quality**: Use `--model gpt-oss:20b`
3. **Clear context**: Type `/clear` in chat mode
4. **See history**: Type `/history` in chat mode
5. **List tools**: `python mcp_agent.py tools`

---

## 🐍 Python Usage

```python
from agent.core import Agent

# Initialize
agent = Agent()

# Ask
result = agent.ask("What's the weather in London?")
print(result['response'])

# Chat with context
agent.ask("What's the capital of France?")
agent.ask("What's the weather there?")  # Knows "there" = Paris

# Reset
agent.reset_conversation()
```

---

## 🌐 Web API

```bash
# Start server
python -m uvicorn agent.web_api:web_app --reload --port 8001

# Test API
curl -X POST http://localhost:8001/api/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is 2+2?"}'
```

---

## 📊 Interfaces Comparison

| Interface | Best For | Command |
|-----------|----------|---------|
| **CLI Ask** | Single questions | `python mcp_agent.py ask "..."` |
| **CLI Chat** | Back-and-forth conversation | `python mcp_agent.py chat` |
| **Web Chat** | Visual, shareable | http://localhost:8001/chat |
| **REST API** | Integration with apps | POST /api/ask |
| **WebSocket** | Real-time applications | ws://localhost:8001/ws |
| **Jupyter** | Research, exploration | Open `notebooks/agent_demo.ipynb` |
| **Python** | Programmatic access | `from agent.core import Agent` |

---

## 🆘 Troubleshooting

### "Cannot connect to Ollama"
```bash
ollama serve
```

### "Cannot connect to MCP Server"
```bash
python -m uvicorn app:app --reload --port 8000
```

### Slow responses
```bash
# Use faster model
python mcp_agent.py ask "..." --model gemma:latest
```

---

## 📚 Learn More

- **Full Documentation**: [AGENT_DOCUMENTATION.md](AGENT_DOCUMENTATION.md)
- **YouTube Tools**: [YOUTUBE_TOOLS_DOCUMENTATION.md](YOUTUBE_TOOLS_DOCUMENTATION.md)
- **Examples**: `notebooks/agent_demo.ipynb`

---

## ✅ Next Steps

1. ✅ Try the web chat: http://localhost:8001/chat
2. ✅ Test with your own YouTube videos
3. ✅ Explore different models
4. ✅ Check out the Jupyter notebook
5. ✅ Read full documentation

**Happy chatting!** 🎉
