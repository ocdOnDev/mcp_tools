"""FastAPI web interface for the agent with WebSocket support."""

import json
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from agent.core import Agent

# Create FastAPI app
web_app = FastAPI(title="MCP Agent Web API", version="1.0.0")

# Configure CORS
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active agent sessions
agent_sessions = {}


class QueryRequest(BaseModel):
    query: str
    model: str = "gemma:latest"
    return_format: str = "auto"
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    response: str
    tool_calls: list[dict]
    metadata: dict
    session_id: str


@web_app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "MCP Agent Web API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/ask": "Ask the agent a question",
            "GET /api/tools": "List available tools",
            "GET /api/status": "Get system status",
            "WebSocket /ws": "WebSocket for real-time chat",
            "GET /chat": "Web-based chat UI",
        },
    }


@web_app.post("/api/ask", response_model=QueryResponse)
async def ask_agent(request: QueryRequest):
    """Ask the agent a question (REST API)."""
    try:
        # Get or create agent session
        session_id = request.session_id or "default"

        if session_id not in agent_sessions:
            agent_sessions[session_id] = Agent(model=request.model)

        agent = agent_sessions[session_id]

        # Process query
        result = agent.ask(request.query, return_format=request.return_format)

        return QueryResponse(
            response=result["response"],
            tool_calls=result.get("tool_calls", []),
            metadata=result.get("metadata", {}),
            session_id=session_id,
        )

    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")


@web_app.get("/api/tools")
async def list_tools():
    """List all available tools."""
    from agent.core import MCPToolsClient

    try:
        client = MCPToolsClient()
        metadata = client.get_tool_metadata()
        return metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tools: {e}")


@web_app.get("/api/status")
async def get_status():
    """Get system status."""
    import requests

    status = {"mcp_server": "unknown", "ollama": "unknown"}

    # Check MCP server
    try:
        response = requests.get("http://localhost:8000/tools", timeout=5)
        if response.status_code == 200:
            tools = response.json()["tools"]
            status["mcp_server"] = {
                "status": "running",
                "tools_count": len(tools),
            }
    except Exception:
        status["mcp_server"] = {"status": "offline"}

    # Check Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()["models"]
            status["ollama"] = {
                "status": "running",
                "models": [m["name"] for m in models],
            }
    except Exception:
        status["ollama"] = {"status": "offline"}

    return status


@web_app.post("/api/reset/{session_id}")
async def reset_session(session_id: str):
    """Reset conversation history for a session."""
    if session_id in agent_sessions:
        agent_sessions[session_id].reset_conversation()
        return {"message": f"Session {session_id} reset successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")


@web_app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()

    # Create agent for this WebSocket session
    agent = Agent()
    session_id = f"ws_{id(websocket)}"

    try:
        await websocket.send_json(
            {
                "type": "connected",
                "message": "Connected to MCP Agent",
                "session_id": session_id,
            }
        )

        while True:
            # Receive message
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                query = message.get("query", "")
                return_format = message.get("format", "auto")

                if not query:
                    await websocket.send_json(
                        {"type": "error", "message": "Empty query"}
                    )
                    continue

                # Handle special commands
                if query.startswith("/"):
                    await _handle_ws_command(query, agent, websocket)
                    continue

                # Send thinking status
                await websocket.send_json({"type": "thinking"})

                # Process query
                result = agent.ask(query, return_format=return_format)

                # Send result
                await websocket.send_json(
                    {
                        "type": "response",
                        "response": result["response"],
                        "tool_calls": result.get("tool_calls", []),
                        "metadata": result.get("metadata", {}),
                    }
                )

            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
            except Exception as e:
                await websocket.send_json(
                    {"type": "error", "message": f"Error: {str(e)}"}
                )

    except WebSocketDisconnect:
        # Clean up session
        pass


async def _handle_ws_command(command: str, agent: Agent, websocket: WebSocket):
    """Handle WebSocket commands."""
    cmd = command.lower().strip()

    if cmd == "/clear":
        agent.reset_conversation()
        await websocket.send_json(
            {"type": "info", "message": "Conversation history cleared"}
        )

    elif cmd == "/tools":
        tools = agent.mcp_client.list_tools()
        await websocket.send_json(
            {"type": "info", "message": f"Available tools: {', '.join(tools)}"}
        )

    elif cmd == "/history":
        history = agent.get_conversation_history()
        await websocket.send_json({"type": "history", "history": history})

    else:
        await websocket.send_json(
            {"type": "error", "message": f"Unknown command: {command}"}
        )


@web_app.get("/chat", response_class=HTMLResponse)
async def chat_ui():
    """Serve the web chat UI."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MCP Agent Chat</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            .chat-container {
                width: 90%;
                max-width: 800px;
                height: 90vh;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            .chat-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                font-size: 24px;
                font-weight: bold;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .status {
                font-size: 12px;
                padding: 4px 8px;
                border-radius: 12px;
                background: rgba(255,255,255,0.2);
            }
            .status.connected { background: #10b981; }
            .status.connecting { background: #f59e0b; }
            .status.disconnected { background: #ef4444; }
            .chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #f9fafb;
            }
            .message {
                margin-bottom: 16px;
                display: flex;
                flex-direction: column;
            }
            .message.user {
                align-items: flex-end;
            }
            .message.agent {
                align-items: flex-start;
            }
            .message-content {
                max-width: 70%;
                padding: 12px 16px;
                border-radius: 18px;
                word-wrap: break-word;
            }
            .message.user .message-content {
                background: #667eea;
                color: white;
            }
            .message.agent .message-content {
                background: white;
                color: #1f2937;
                border: 1px solid #e5e7eb;
            }
            .message-label {
                font-size: 12px;
                color: #6b7280;
                margin-bottom: 4px;
                padding: 0 8px;
            }
            .thinking {
                display: flex;
                gap: 4px;
                padding: 12px 16px;
                background: white;
                border-radius: 18px;
                width: fit-content;
            }
            .thinking span {
                width: 8px;
                height: 8px;
                background: #667eea;
                border-radius: 50%;
                animation: bounce 1.4s infinite ease-in-out;
            }
            .thinking span:nth-child(1) { animation-delay: -0.32s; }
            .thinking span:nth-child(2) { animation-delay: -0.16s; }
            @keyframes bounce {
                0%, 80%, 100% { transform: scale(0); }
                40% { transform: scale(1); }
            }
            .chat-input-container {
                padding: 20px;
                background: white;
                border-top: 1px solid #e5e7eb;
            }
            .chat-input {
                width: 100%;
                padding: 12px 16px;
                border: 2px solid #e5e7eb;
                border-radius: 24px;
                font-size: 14px;
                outline: none;
                transition: border-color 0.3s;
            }
            .chat-input:focus {
                border-color: #667eea;
            }
            .tool-call {
                font-size: 12px;
                color: #6b7280;
                padding: 8px;
                background: #f3f4f6;
                border-radius: 8px;
                margin-top: 8px;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                <span>🤖 MCP Agent</span>
                <span class="status connecting" id="status">Connecting...</span>
            </div>
            <div class="chat-messages" id="messages">
                <div class="message agent">
                    <div class="message-label">Agent</div>
                    <div class="message-content">
                        Hello! I'm your MCP Agent. I can help you with:<br>
                        • Summarizing YouTube videos<br>
                        • Getting weather information<br>
                        • Extracting PDF text<br>
                        • And much more!<br><br>
                        Just ask me anything!
                    </div>
                </div>
            </div>
            <div class="chat-input-container">
                <input
                    type="text"
                    class="chat-input"
                    id="input"
                    placeholder="Type your message..."
                    autocomplete="off"
                >
            </div>
        </div>

        <script>
            const messagesContainer = document.getElementById('messages');
            const input = document.getElementById('input');
            const status = document.getElementById('status');

            let ws;
            let isThinking = false;

            function connect() {
                ws = new WebSocket('ws://localhost:8001/ws');

                ws.onopen = () => {
                    status.textContent = 'Connected';
                    status.className = 'status connected';
                };

                ws.onclose = () => {
                    status.textContent = 'Disconnected';
                    status.className = 'status disconnected';
                    setTimeout(connect, 3000);
                };

                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    handleMessage(data);
                };
            }

            function handleMessage(data) {
                if (data.type === 'thinking') {
                    showThinking();
                } else if (data.type === 'response') {
                    removeThinking();
                    addMessage('agent', data.response);
                    if (data.tool_calls && data.tool_calls.length > 0) {
                        const lastMessage = messagesContainer.lastElementChild;
                        const toolInfo = document.createElement('div');
                        toolInfo.className = 'tool-call';
                        toolInfo.textContent = `Used tools: ${data.tool_calls.map(t => t.tool).join(', ')}`;
                        lastMessage.querySelector('.message-content').appendChild(toolInfo);
                    }
                } else if (data.type === 'error') {
                    removeThinking();
                    addMessage('agent', `❌ ${data.message}`);
                } else if (data.type === 'info') {
                    addMessage('agent', data.message);
                }
            }

            function addMessage(role, content) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${role}`;

                const label = document.createElement('div');
                label.className = 'message-label';
                label.textContent = role === 'user' ? 'You' : 'Agent';

                const contentDiv = document.createElement('div');
                contentDiv.className = 'message-content';
                contentDiv.innerHTML = content.replace(/\\n/g, '<br>');

                messageDiv.appendChild(label);
                messageDiv.appendChild(contentDiv);
                messagesContainer.appendChild(messageDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }

            function showThinking() {
                if (isThinking) return;
                isThinking = true;

                const thinkingDiv = document.createElement('div');
                thinkingDiv.className = 'message agent';
                thinkingDiv.id = 'thinking';

                const label = document.createElement('div');
                label.className = 'message-label';
                label.textContent = 'Agent';

                const thinkingContent = document.createElement('div');
                thinkingContent.className = 'thinking';
                thinkingContent.innerHTML = '<span></span><span></span><span></span>';

                thinkingDiv.appendChild(label);
                thinkingDiv.appendChild(thinkingContent);
                messagesContainer.appendChild(thinkingDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }

            function removeThinking() {
                const thinking = document.getElementById('thinking');
                if (thinking) {
                    thinking.remove();
                    isThinking = false;
                }
            }

            function sendMessage() {
                const message = input.value.trim();
                if (!message) return;

                addMessage('user', message);
                input.value = '';

                ws.send(JSON.stringify({
                    query: message,
                    format: 'auto'
                }));
            }

            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });

            connect();
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(web_app, host="0.0.0.0", port=8001)
