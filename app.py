from fastapi import FastAPI, HTTPException, Body, Request
from importlib import import_module
from inspect import getdoc
import os
import pkgutil
from typing import Optional

app = FastAPI(title="MCP Tool Server")

TOOLS_DIR = "tools"


@app.get("/tools")
def list_tools():
    """List all available tools."""
    files = [f[:-3] for f in os.listdir(TOOLS_DIR) if f.endswith(".py")]
    return {"tools": files}


@app.post("/tools/{tool_name}")
async def run_tool(tool_name: str, body: Optional[dict] = Body(default={})):
    """Execute the given tool with provided input JSON."""
    try:
        module = import_module(f"{TOOLS_DIR}.{tool_name}")
        if hasattr(module, "Input"):
            input_data = module.Input(**(body or {}))
            result = module.execute(input_data)
        else:
            result = module.execute()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/mcp/tools/metadata")
def mcp_metadata():
    """Return full MCP metadata with schemas and examples."""
    tools_metadata = []

    for _, name, _ in pkgutil.iter_modules([TOOLS_DIR]):
        module = import_module(f"{TOOLS_DIR}.{name}")
        entry = {
            "name": name,
            "description": getdoc(module) or f"MCP tool: {name}",
        }

        # Schemas
        if hasattr(module, "Input"):
            entry["input_schema"] = module.Input.schema()
        if hasattr(module, "Output"):
            entry["output_schema"] = module.Output.schema()

        # Example input/output
        if hasattr(module, "ExampleInput"):
            try:
                example_in = module.ExampleInput
                entry["example_input"] = (
                    example_in.dict() if hasattr(example_in, "dict") else example_in
                )
            except Exception:
                pass
        if hasattr(module, "ExampleOutput"):
            try:
                example_out = module.ExampleOutput
                entry["example_output"] = (
                    example_out.dict() if hasattr(example_out, "dict") else example_out
                )
            except Exception:
                pass

        tools_metadata.append(entry)

    return {"mcp_version": "0.2", "tools": tools_metadata}


@app.post("/mcp/tools/invoke")
async def invoke_tool(request: Request):
    """Execute a tool via MCP-style payload: {"tool": "name", "args": {...}}"""
    try:
        data = await request.json()
        tool_name = data.get("tool")
        args = data.get("args", {})

        if not tool_name:
            raise HTTPException(status_code=400, detail="Missing 'tool' field")

        module = import_module(f"{TOOLS_DIR}.{tool_name}")

        if hasattr(module, "Input"):
            input_data = module.Input(**args)
            result = module.execute(input_data)
        else:
            result = module.execute()

        return {"tool": tool_name, "success": True, "result": result}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
