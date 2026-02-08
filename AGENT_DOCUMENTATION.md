# MCP Agent - Complete Documentation

## 🎯 Overview

The MCP Agent is an intelligent coordinator that combines:
- **Ollama LLM** for natural language understanding
- **MCP Tools** for task execution
- **Conversation memory** for context awareness
- **Multiple interfaces** (CLI, Web, Jupyter, API)

### Key Features

✅ **Natural Language Interface** - Ask questions in plain English
✅ **Automatic Tool Selection** - Agent decides which tools to use
✅ **Multi-step Workflows** - Chains multiple tool calls
✅ **Conversation Memory** - Maintains context across messages
✅ **Multiple UIs** - CLI, Web chat, Jupyter notebooks, REST API
✅ **Extensible** - Easy to add new tools and MCP servers
✅ **Local & Private** - All processing happens on your machine

---

## 🚀 Quick Start

### 1. Check System Status

```bash
python mcp_agent.py status
```

Output:
```
✓ MCP Server: Running at http://localhost:8000 (9 tools available)
✓ Ollama: Running at http://localhost:11434 (2 models available)
  • gpt-oss:20b
  • gemma:latest
```

### 2. Ask a Question (Single-Shot)

```bash
python mcp_agent.py ask "Summarize this video: https://www.youtube.com/watch?v=EmfoQWQ1DR8"
```

### 3. Start Interactive Chat

```bash
python mcp_agent.py chat
```

### 4. Start Web Interface

```bash
# Terminal 1: MCP Server (already running)
python -m uvicorn app:app --reload --port 8000

# Terminal 2: Agent Web API
python -m uvicorn agent.web_api:web_app --reload --port 8001

# Open browser: http://localhost:8001/chat
```

---

## 📚 Usage Guide

### CLI Interface

#### Commands

```bash
# Ask a question
python mcp_agent.py ask "Your question here"

# With options
python mcp_agent.py ask "Question" --model gpt-oss:20b --format markdown

# Interactive chat
python mcp_agent.py chat

# List available tools
python mcp_agent.py tools

# Check status
python mcp_agent.py status
```

#### Interactive Chat Commands

Once in chat mode:
- `/help` - Show available commands
- `/clear` - Clear conversation history
- `/tools` - List available tools
- `/history` - Show conversation history
- `/exit` or `/quit` - Exit chat

#### Examples

```bash
# Simple question
python mcp_agent.py ask "Hello, who are you?"

# Tool usage
python mcp_agent.py ask "What's the weather in London?"

# YouTube analysis
python mcp_agent.py ask "Summarize: https://youtube.com/watch?v=VIDEO_ID"

# With specific model
python mcp_agent.py ask "Explain quantum computing" --model gpt-oss:20b

# Markdown output
python mcp_agent.py ask "List 5 facts about Python" --format markdown
```

---

### Web Interface

#### Starting the Server

```bash
python -m uvicorn agent.web_api:web_app --reload --port 8001
```

#### Access Points

- **Web Chat UI**: http://localhost:8001/chat
- **REST API**: http://localhost:8001/api/ask
- **WebSocket**: ws://localhost:8001/ws
- **API Docs**: http://localhost:8001/docs

#### REST API Usage

**POST /api/ask**

```bash
curl -X POST http://localhost:8001/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the weather in Paris?",
    "model": "gemma:latest",
    "return_format": "auto"
  }'
```

Response:
```json
{
  "response": "The current weather in Paris is...",
  "tool_calls": [
    {
      "tool": "get_weather",
      "success": true
    }
  ],
  "metadata": {
    "iterations": 1,
    "success": true
  },
  "session_id": "default"
}
```

#### WebSocket Usage

```javascript
const ws = new WebSocket('ws://localhost:8001/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    query: "Summarize this video: https://...",
    format: "markdown"
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'response') {
    console.log(data.response);
  }
};
```

---

### Python API

#### Basic Usage

```python
from agent.core import Agent

# Initialize agent
agent = Agent(model="gemma:latest")

# Ask a question
result = agent.ask("What's the weather in Paris?")
print(result['response'])

# With format
result = agent.ask("List 5 Python tips", return_format="markdown")
print(result['response'])
```

#### Advanced Usage

```python
# Custom configuration
agent = Agent(
    mcp_url="http://localhost:8000",
    ollama_url="http://localhost:11434",
    model="gpt-oss:20b"
)

# Ask with metadata
result = agent.ask("Summarize: https://youtube.com/...")

print(f"Response: {result['response']}")
print(f"Tools used: {[t['tool'] for t in result['tool_calls']]}")
print(f"Iterations: {result['metadata']['iterations']}")

# View conversation
history = agent.get_conversation_history()
for msg in history:
    print(f"{msg['role']}: {msg['content']}")

# Reset conversation
agent.reset_conversation()
```

#### Direct Tool Access

```python
# Use MCP client directly
from agent.core import MCPToolsClient

client = MCPToolsClient()

# List tools
tools = client.list_tools()

# Execute tool
result = client.execute_tool(
    "youtube_summary",
    {
        "url": "https://youtube.com/...",
        "summary_length": "brief"
    }
)
```

---

### Jupyter Notebook

See [`notebooks/agent_demo.ipynb`](notebooks/agent_demo.ipynb) for interactive examples.

```python
from agent.core import Agent
from IPython.display import Markdown, display

agent = Agent()

# Ask question
result = agent.ask("What's the weather in Tokyo?")
display(Markdown(result['response']))

# YouTube summary
result = agent.ask("Summarize: https://youtube.com/...")
display(Markdown(result['response']))
```

---

## 🏗️ Architecture

### System Overview

```
┌────────────────────────────────────────────────┐
│              User Interfaces                   │
│  CLI │ Web Chat │ REST API │ Jupyter │ WS     │
└──────────────────┬─────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────────────┐
│           Agent Coordinator                    │
│  - Query Analysis                              │
│  - Tool Selection                              │
│  - Workflow Orchestration                      │
│  - Context Management                          │
└──────┬─────────────────────────┬──────────────┘
       │                         │
       ▼                         ▼
┌─────────────┐         ┌──────────────┐
│ Ollama LLM  │         │  MCP Tools   │
│  (Planning) │         │  (Execution) │
└─────────────┘         └──────────────┘
```

### Component Breakdown

#### 1. Agent Core (`agent/core.py`)
- **Agent**: Main coordinator class
- **MCPToolsClient**: MCP API wrapper
- **OllamaClient**: Ollama API wrapper

#### 2. CLI Interface (`agent/cli.py`)
- Click-based command-line interface
- Rich formatting for beautiful output
- Interactive chat mode

#### 3. Web API (`agent/web_api.py`)
- FastAPI REST endpoints
- WebSocket for real-time chat
- Embedded web UI

#### 4. Jupyter Support (`notebooks/agent_demo.ipynb`)
- Interactive widgets
- Rich display formatting
- Educational examples

---

## 🧠 How It Works

### Query Processing Flow

1. **User Input**: User asks a question in natural language
2. **Analysis**: Agent analyzes if tools are needed
3. **Planning**: If tools needed, determine which tools and parameters
4. **Execution**: Execute tools via MCP API
5. **Synthesis**: LLM generates final response incorporating tool results
6. **Output**: Response formatted based on user preference

### Tool Selection

The agent uses two methods:

#### 1. LLM-Based (Primary)
```python
# Agent asks LLM to analyze query
analysis_prompt = """
Analyze this query and determine if it needs tools:
"What's the weather in Paris?"

Available tools: get_weather, youtube_summary, ...

Respond in JSON:
{
  "needs_tool": true,
  "tool": "get_weather",
  "args": {"location": "Paris"}
}
"""
```

#### 2. Pattern Matching (Fallback)
```python
# Simple patterns for common cases
if "youtube.com" in query and "summarize" in query:
    return use_tool("youtube_summary", {"url": extracted_url})

if "weather" in query:
    return use_tool("get_weather", {"location": extracted_location})
```

### Conversation Memory

```python
conversation_history = [
    {"role": "user", "content": "What's the capital of France?"},
    {"role": "assistant", "content": "The capital of France is Paris."},
    {"role": "user", "content": "What's the weather there?"},  # "there" refers to Paris
    {"role": "assistant", "content": "The weather in Paris is..."}
]
```

---

## 🛠️ Configuration

### Environment Variables

```bash
# MCP Server URL
export MCP_URL="http://localhost:8000"

# Ollama URL
export OLLAMA_URL="http://localhost:11434"

# Default model
export DEFAULT_MODEL="gemma:latest"
```

### Model Selection

```bash
# Fast responses
--model gemma:latest

# Better quality
--model gpt-oss:20b

# Other models (if installed)
--model llama3
--model mistral
```

### Output Formats

- `auto` - Agent decides (default)
- `text` - Plain text
- `markdown` - Formatted markdown
- `json` - Structured JSON

---

## 🔧 Extending the Agent

### Adding New Tools

Tools are automatically discovered from the MCP server. To add a new tool:

1. Create tool in `/tools` directory (see existing tools)
2. Restart MCP server
3. Agent automatically picks it up

### Integrating MCP Servers

To connect to external MCP servers:

```python
# Custom MCP server
agent = Agent(mcp_url="http://other-server:8000")

# Multiple servers (future feature)
agent.add_mcp_server("http://server1:8000")
agent.add_mcp_server("http://server2:8000")
```

### Custom Tool Selection Logic

Edit `agent/core.py`:

```python
def _analyze_query(self, query):
    # Your custom logic here
    if "my_custom_pattern" in query:
        return True, {
            "tool": "my_custom_tool",
            "args": {...}
        }

    # Fall back to default
    return super()._analyze_query(query)
```

---

## 📊 Performance

### Response Times

| Query Type | Model | Time |
|------------|-------|------|
| Simple chat | gemma | 1-2s |
| Weather | gemma | 3-5s |
| YouTube summary (5min) | gemma | 10-15s |
| YouTube summary (5min) | gpt-oss:20b | 30-45s |

### Resource Usage

| Model | RAM | VRAM |
|-------|-----|------|
| gemma:latest | ~6 GB | ~5 GB |
| gpt-oss:20b | ~14 GB | ~12 GB |

---

## 🔍 Troubleshooting

### Agent won't start

**Error**: "Cannot connect to Ollama"

**Solution**:
```bash
# Check Ollama is running
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

**Error**: "Cannot connect to MCP Server"

**Solution**:
```bash
# Start MCP server
python -m uvicorn app:app --reload --port 8000

# Test connection
curl http://localhost:8000/tools
```

### Tool not working

```bash
# Check tool is available
python mcp_agent.py tools

# Test tool directly
curl -X POST http://localhost:8000/mcp/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{"tool": "TOOL_NAME", "args": {...}}'
```

### Slow responses

- Use faster model: `--model gemma:latest`
- Reduce summary length: `summary_length: "brief"`
- Check system resources (RAM/VRAM)

### Memory issues

```bash
# Use smaller model
--model gemma:latest

# Clear conversation history
/clear  # in chat mode

# Or in Python
agent.reset_conversation()
```

---

## 💡 Use Cases

### 1. YouTube Analysis

```bash
# Quick summary
python mcp_agent.py ask "Summarize: https://youtube.com/..."

# Detailed analysis
python mcp_agent.py ask "What are the main topics in this video: https://..."

# Compare videos
python mcp_agent.py ask "Compare these videos: [url1] and [url2]"
```

### 2. Research Assistant

```bash
# Weather
python mcp_agent.py ask "What's the weather in Tokyo and should I bring an umbrella?"

# Web research
python mcp_agent.py ask "Visit https://example.com and summarize the main points"
```

### 3. Document Processing

```bash
# PDF extraction
python mcp_agent.py ask "Extract text from /path/to/file.pdf and summarize it"
```

### 4. System Monitoring

```bash
# Check system
python mcp_agent.py ask "What are my system metrics?"
```

---

## 🎓 Examples

### Example 1: Video Research

```python
agent = Agent()

# Get summary
result = agent.ask(
    "Summarize this video and tell me the key takeaways: "
    "https://www.youtube.com/watch?v=VIDEO_ID"
)
print(result['response'])

# Follow-up
result = agent.ask("What were the main technical concepts discussed?")
print(result['response'])
```

### Example 2: Multi-Tool Workflow

```python
# Agent automatically chains tools
result = agent.ask(
    "Get the weather in the capital of France"
)
# Agent will:
# 1. Understand "capital of France" = Paris
# 2. Call get_weather("Paris")
# 3. Format response
```

### Example 3: Batch Processing

```python
videos = [
    "https://youtube.com/watch?v=VIDEO1",
    "https://youtube.com/watch?v=VIDEO2",
    "https://youtube.com/watch?v=VIDEO3"
]

summaries = []
for video in videos:
    result = agent.ask(f"Brief summary: {video}")
    summaries.append(result['response'])

# Compare
result = agent.ask(
    f"I have these summaries: {summaries}. "
    "What are the common themes?"
)
```

---

## 🔐 Security & Privacy

### Data Handling

✅ **All local processing** - LLM runs on your machine
✅ **No external API calls** - Except for fetching YouTube transcripts
✅ **No data logging** - Conversation history stored in memory only
✅ **No tracking** - No analytics or telemetry

### Network Connections

The agent only connects to:
1. **Localhost MCP server** (your machine)
2. **Localhost Ollama** (your machine)
3. **YouTube** (only when fetching transcripts)
4. **External APIs** (only when explicitly requested by tools like weather)

---

## 📝 API Reference

### Agent Class

```python
Agent(
    mcp_url: str = "http://localhost:8000",
    ollama_url: str = "http://localhost:11434",
    model: str = "gemma:latest"
)
```

#### Methods

**ask(query, return_format="auto", max_iterations=5)**
- `query`: User's natural language question
- `return_format`: "auto", "text", "markdown", or "json"
- `max_iterations`: Max tool calls to prevent loops
- Returns: `dict` with response, tool_calls, metadata

**reset_conversation()**
- Clears conversation history

**get_conversation_history()**
- Returns: `list[dict]` of messages

### MCPToolsClient Class

```python
MCPToolsClient(api_url: str = "http://localhost:8000")
```

#### Methods

**list_tools() -> list[str]**
**get_tool_metadata(tool_name=None) -> dict**
**execute_tool(tool_name: str, args: dict) -> dict**

### OllamaClient Class

```python
OllamaClient(api_url: str = "http://localhost:11434")
```

#### Methods

**check_available() -> bool**
**list_models() -> list[str]**
**generate(prompt: str, model: str, system: str) -> str**
**chat(messages: list[dict], model: str, tools: list[dict]) -> dict**

---

## 🚀 Next Steps

### Immediate

1. ✅ Test all interfaces (CLI, Web, Jupyter)
2. ✅ Try different models
3. ✅ Explore available tools

### Short-term

- Add more tools to MCP server
- Customize agent prompts
- Build custom workflows
- Connect to external MCP servers

### Long-term

- Multi-agent coordination
- Persistent memory (database)
- Advanced planning algorithms
- Tool marketplace integration

---

## 📞 Support

### Getting Help

1. Check this documentation
2. Review examples in `notebooks/`
3. Test with `python mcp_agent.py status`
4. Check logs for errors

### Common Issues

See [Troubleshooting](#-troubleshooting) section above.

---

## 📄 License

This agent system is part of the MCP Tools project.

---

## 🎉 Conclusion

You now have a complete, production-ready agent system that can:

✅ Chat naturally in multiple interfaces
✅ Automatically select and use tools
✅ Maintain conversation context
✅ Handle complex multi-step workflows
✅ Integrate with external MCP servers
✅ Run 100% locally with full privacy

**Start experimenting and building amazing AI-powered workflows!**
