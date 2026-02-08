"""Core agent coordinator with Ollama LLM and MCP tools integration.

This module provides the main agent logic for:
- Natural language understanding
- Tool selection and execution
- Multi-step workflow coordination
- Response formatting
"""

import json
import requests


class MCPToolsClient:
    """Client for interacting with MCP Tools API."""

    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self._tools_cache = None

    def list_tools(self) -> list[str]:
        """Get list of available tools."""
        response = requests.get(f"{self.api_url}/tools", timeout=10)
        response.raise_for_status()
        return response.json()["tools"]

    def get_tool_metadata(self, tool_name: str = None) -> dict:
        """Get metadata for all tools or specific tool."""
        response = requests.get(f"{self.api_url}/mcp/tools/metadata", timeout=10)
        response.raise_for_status()
        data = response.json()

        if tool_name:
            # Find specific tool
            for tool in data["tools"]:
                if tool["name"] == tool_name:
                    return tool
            raise ValueError(f"Tool '{tool_name}' not found")

        return data

    def execute_tool(self, tool_name: str, args: dict) -> dict:
        """Execute a tool with given arguments."""
        response = requests.post(
            f"{self.api_url}/mcp/tools/invoke",
            json={"tool": tool_name, "args": args},
            timeout=300,  # 5 minutes for long operations
        )
        response.raise_for_status()
        return response.json()

    def get_tools_for_llm(self) -> list[dict]:
        """Format tools metadata for LLM function calling."""
        if self._tools_cache:
            return self._tools_cache

        metadata = self.get_tool_metadata()
        tools = []

        for tool in metadata["tools"]:
            tool_def = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool.get("input_schema", {"type": "object"}),
                },
            }
            tools.append(tool_def)

        self._tools_cache = tools
        return tools


class OllamaClient:
    """Client for interacting with Ollama LLM."""

    def __init__(self, api_url: str = "http://localhost:11434"):
        self.api_url = api_url

    def check_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.api_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list[str]:
        """Get list of available models."""
        response = requests.get(f"{self.api_url}/api/tags", timeout=5)
        response.raise_for_status()
        data = response.json()
        return [model["name"] for model in data.get("models", [])]

    def generate(
        self,
        prompt: str,
        model: str = "gemma:latest",
        system: str = None,
        stream: bool = False,
    ) -> str:
        """Generate text from prompt."""
        payload = {"model": model, "prompt": prompt, "stream": stream}

        if system:
            payload["system"] = system

        response = requests.post(
            f"{self.api_url}/api/generate", json=payload, timeout=300
        )
        response.raise_for_status()

        result = response.json()
        return result.get("response", "").strip()

    def chat(
        self,
        messages: list[dict],
        model: str = "gemma:latest",
        tools: list[dict] = None,
        stream: bool = False,
    ) -> dict:
        """Chat with context and optional tool use."""
        payload = {"model": model, "messages": messages, "stream": stream}

        if tools:
            payload["tools"] = tools

        response = requests.post(f"{self.api_url}/api/chat", json=payload, timeout=300)
        response.raise_for_status()

        return response.json()


class Agent:
    """Intelligent agent coordinator for MCP tools and LLM interaction."""

    def __init__(
        self,
        mcp_url: str = "http://localhost:8000",
        ollama_url: str = "http://localhost:11434",
        model: str = "gemma:latest",
    ):
        self.mcp_client = MCPToolsClient(mcp_url)
        self.ollama_client = OllamaClient(ollama_url)
        self.model = model
        self.conversation_history = []
        self.system_prompt = self._build_system_prompt()

        # Verify connections
        if not self.ollama_client.check_available():
            raise ConnectionError(
                f"Cannot connect to Ollama at {ollama_url}. Is it running?"
            )

    def _build_system_prompt(self) -> str:
        """Build system prompt with available tools."""
        tools = self.mcp_client.list_tools()
        tools_str = "\n".join(f"- {tool}" for tool in tools)

        return f"""You are a helpful AI assistant with access to various tools.

Available tools:
{tools_str}

When a user asks for something that requires a tool, you should:
1. Identify which tool(s) to use
2. Determine the required parameters
3. Call the tool with proper arguments
4. Present results in a user-friendly format

For YouTube videos, you have several specialized tools:
- youtube_analyzer: Get basic metadata (title, author, thumbnail)
- youtube_transcript: Get full transcript/captions
- youtube_summary: Get AI-generated summary (uses Ollama)
- summarize_with_ollama: Summarize any text

You can also:
- Extract text from PDFs (extract_pdf_text)
- Get weather information (get_weather)
- Visit webpages and extract content (visit_webpage)
- Get system metrics (get_system_metrics)
- Parse JSON from text (text_to_json)

Always provide clear, concise responses. If a tool fails, explain why and suggest alternatives."""

    def ask(
        self, user_query: str, return_format: str = "auto", max_iterations: int = 5
    ) -> dict:
        """Process user query with tool coordination.

        Args:
            user_query: User's natural language query
            return_format: "text", "json", "markdown", or "auto"
            max_iterations: Maximum tool calls to prevent infinite loops

        Returns:
            Dictionary with response, tool_calls, and metadata
        """
        # Add user message to history
        self.conversation_history.append({"role": "user", "content": user_query})

        result = {
            "response": "",
            "tool_calls": [],
            "metadata": {"iterations": 0, "success": True, "format": return_format},
        }

        iteration = 0
        current_messages = [{"role": "system", "content": self.system_prompt}] + [
            msg for msg in self.conversation_history
        ]

        while iteration < max_iterations:
            iteration += 1

            # Check if we need to use tools
            needs_tool, tool_plan = self._analyze_query(user_query, current_messages)

            if not needs_tool:
                # Just chat normally
                response = self._chat_without_tools(current_messages)
                result["response"] = response
                result["metadata"]["iterations"] = iteration
                break

            # Execute tool based on plan
            tool_result = self._execute_tool_plan(tool_plan)
            result["tool_calls"].append(tool_result)

            # Add tool result to conversation
            tool_message = self._format_tool_result_for_llm(tool_result)
            current_messages.append(
                {"role": "assistant", "content": f"[Used tool: {tool_plan['tool']}]"}
            )
            current_messages.append({"role": "user", "content": tool_message})

            # Check if we're done or need more tools
            if tool_result["success"]:
                # Generate final response incorporating tool results
                final_response = self._generate_final_response(
                    current_messages, return_format
                )
                result["response"] = final_response
                result["metadata"]["iterations"] = iteration
                break
            else:
                # Tool failed, try to recover or inform user
                error_msg = f"Tool '{tool_plan['tool']}' failed: {tool_result.get('error', 'Unknown error')}"
                result["response"] = error_msg
                result["metadata"]["success"] = False
                result["metadata"]["iterations"] = iteration
                break

        # Add assistant response to history
        self.conversation_history.append(
            {"role": "assistant", "content": result["response"]}
        )

        return result

    def _analyze_query(
        self, user_query: str, messages: list[dict]
    ) -> tuple[bool, dict]:
        """Analyze if query needs tools and generate execution plan."""
        # Use LLM to determine if we need tools
        analysis_prompt = f"""Analyze this user query and determine if it requires using any tools.

User query: "{user_query}"

Available tools: {', '.join(self.mcp_client.list_tools())}

Respond in JSON format:
{{
    "needs_tool": true/false,
    "tool": "tool_name" (if needs_tool is true),
    "args": {{"param": "value"}} (if needs_tool is true),
    "reasoning": "why this tool is needed"
}}

Examples:
- "What's the weather in Paris?" → {{"needs_tool": true, "tool": "get_weather", "args": {{"location": "Paris"}}}}
- "Hello, how are you?" → {{"needs_tool": false}}
- "Summarize this video: https://youtube.com/..." → {{"needs_tool": true, "tool": "youtube_summary", "args": {{"url": "https://..."}}}}
"""

        response = self.ollama_client.generate(
            analysis_prompt,
            model=self.model,
            system="You are a tool planning assistant.",
        )

        try:
            plan = json.loads(response)
            return plan.get("needs_tool", False), plan
        except json.JSONDecodeError:
            # Fallback: simple pattern matching
            return self._simple_tool_detection(user_query)

    def _simple_tool_detection(self, query: str) -> tuple[bool, dict]:
        """Fallback simple pattern matching for tool detection."""
        query_lower = query.lower()

        # YouTube patterns
        if "youtube.com" in query or "youtu.be" in query:
            if "summarize" in query_lower or "summary" in query_lower:
                # Extract URL
                import re

                url_match = re.search(
                    r"https?://(?:www\.)?(?:youtube\.com|youtu\.be)/[^\s]+", query
                )
                url = url_match.group(0) if url_match else ""
                return True, {
                    "needs_tool": True,
                    "tool": "youtube_summary",
                    "args": {"url": url},
                }
            elif "transcript" in query_lower:
                import re

                url_match = re.search(
                    r"https?://(?:www\.)?(?:youtube\.com|youtu\.be)/[^\s]+", query
                )
                url = url_match.group(0) if url_match else ""
                return True, {
                    "needs_tool": True,
                    "tool": "youtube_transcript",
                    "args": {"url": url},
                }

        # Weather patterns
        if "weather" in query_lower:
            # Extract location (simple heuristic)
            words = query.split()
            location_idx = words.index("in") if "in" in words else -1
            location = (
                " ".join(words[location_idx + 1 :]) if location_idx != -1 else "London"
            )
            return True, {
                "needs_tool": True,
                "tool": "get_weather",
                "args": {"location": location.strip("?.,")},
            }

        return False, {}

    def _execute_tool_plan(self, plan: dict) -> dict:
        """Execute tool based on plan."""
        tool_name = plan.get("tool")
        args = plan.get("args", {})

        try:
            result = self.mcp_client.execute_tool(tool_name, args)
            return {
                "tool": tool_name,
                "args": args,
                "result": result.get("result", {}),
                "success": result.get("result", {}).get("success", True),
                "error": result.get("result", {}).get("error_message", ""),
            }
        except Exception as e:
            return {
                "tool": tool_name,
                "args": args,
                "result": {},
                "success": False,
                "error": str(e),
            }

    def _format_tool_result_for_llm(self, tool_result: dict) -> str:
        """Format tool result for LLM context."""
        if not tool_result["success"]:
            return f"Tool '{tool_result['tool']}' failed with error: {tool_result['error']}"

        result = tool_result["result"]

        # Format based on tool type
        tool_name = tool_result["tool"]

        if tool_name == "youtube_summary":
            return f"""Video Summary:
Title: {result.get('title', 'N/A')}
Author: {result.get('author', 'N/A')}
Summary: {result.get('summary', 'N/A')}
"""

        elif tool_name == "youtube_transcript":
            transcript = result.get("transcript", "")
            word_count = result.get("word_count", 0)
            # Truncate long transcripts
            if len(transcript) > 2000:
                transcript = transcript[:2000] + "... (truncated)"
            return f"Transcript ({word_count} words):\n{transcript}"

        elif tool_name == "get_weather":
            return f"Weather information:\n{result.get('weather', 'N/A')}"

        else:
            # Generic formatting
            return f"Tool result:\n{json.dumps(result, indent=2)}"

    def _chat_without_tools(self, messages: list[dict]) -> str:
        """Simple chat without tool use."""
        response = self.ollama_client.chat(messages, model=self.model)
        return response.get("message", {}).get("content", "")

    def _generate_final_response(self, messages: list[dict], return_format: str) -> str:
        """Generate final user-facing response."""
        # Add instruction for formatting
        format_instruction = ""
        if return_format == "markdown":
            format_instruction = "\n\nFormat your response using Markdown."
        elif return_format == "json":
            format_instruction = "\n\nFormat your response as JSON."

        messages.append(
            {
                "role": "user",
                "content": f"Based on the tool results above, provide a clear, helpful response to the user.{format_instruction}",
            }
        )

        response = self.ollama_client.chat(messages, model=self.model)
        return response.get("message", {}).get("content", "")

    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []

    def get_conversation_history(self) -> list[dict]:
        """Get current conversation history."""
        return self.conversation_history.copy()
