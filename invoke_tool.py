import requests
import json


def invoke_tool(tool_name, args, base_url="http://localhost:8080"):
    """
    Calls the local MCP endpoint to invoke a tool.

    Example:
        invoke_tool("get_weather", {"location": "Amsterdam"})
    """
    url = f"{base_url}/mcp/tools/invoke"
    payload = {"tool": tool_name, "args": args}
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        raise RuntimeError(
            f"Tool call failed ({response.status_code}): {response.text}"
        )

    return response.json()
