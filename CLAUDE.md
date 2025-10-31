# MCP Tools Project Documentation

## Project Overview

**mcp_tools** is a Python-based Model Context Protocol (MCP) server that provides a web API for executing modular tools. It is built on FastAPI and exposes tools through REST endpoints, allowing agents, AI models, and other applications to call various utilities in a standardized way.

The project serves as both:
1. A **tool registry and execution server** - A FastAPI application that dynamically discovers and executes Python tools
2. A **learning resource** - Part of the Hugging Face Agents Course, with extensive notebooks and templates for building agent-based applications

## Architecture Overview

### Core Design Pattern

The architecture follows a **plugin-based microservice pattern**:

```
┌─────────────────────────────────────────────────────┐
│  FastAPI Application (app.py)                       │
├─────────────────────────────────────────────────────┤
│  • Dynamic tool discovery from /tools directory     │
│  • REST endpoints for tool invocation               │
│  • MCP-compliant metadata and invoke endpoints      │
├─────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │ Tool Module  │  │ Tool Module  │  │Tool...   │ │
│  │(Pydantic     │  │(Pydantic     │  │(Pattern) │ │
│  │schemas)      │  │schemas)      │  │          │ │
│  └──────────────┘  └──────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────┘
```

### Execution Model

Each tool follows a standardized module pattern:
- **Input/Output Schemas**: Pydantic models for type validation
- **execute() Function**: Core logic that processes input and returns output
- **Module Docstring**: Serves as tool description in API metadata

## Directory Structure

```
mcp_tools/
├── app.py                          # Main FastAPI application server
├── invoke_tool.py                  # Client library for invoking tools
├── requirements.txt                # Python dependencies
├── pyproject.toml                  # Black, Ruff, isort configuration
├── tool_registry.json              # Static tool registry/manifest
├── .pre-commit-config.yaml         # Pre-commit hooks (Black, Ruff)
├── README.MD                       # Usage examples and API documentation
│
├── tools/                          # Directory of executable tool modules
│   ├── get_weather.py              # Weather lookup via Open-Meteo API
│   ├── get_system_metrics.py       # CPU, memory, disk monitoring
│   ├── extract_pdf_text.py         # PDF text extraction (PyMuPDF)
│   ├── text_to_json.py             # JSON parsing from text
│   ├── visit_webpage.py            # Web scraping to Markdown
│   └── test_visit_webpage.py       # Test script for webpage tool
│
├── templates/                      # Agent application templates
│   └── First_agent_template/       # Hugging Face Spaces agent template
│       ├── app.py                  # Gradio web interface
│       ├── agent.json              # Agent configuration
│       ├── Gradio_UI.py            # UI components
│       ├── prompts.yaml            # System prompts
│       ├── tools/                  # Template tools
│       └── requirements.txt
│
└── notebooks/                      # Educational notebooks (Hugging Face course)
    ├── unit1/                      # Agent fundamentals
    ├── unit2/                      # Advanced topics
    │   ├── smolagents/             # smolagents framework examples
    │   ├── llama-index/            # LlamaIndex examples
    │   └── langgraph/              # LangGraph examples
    ├── bonus-unit1/                # Gemma & function calling
    ├── bonus-unit2/                # Monitoring & evaluation
    └── fr/                         # French translations
```

## Key Components

### 1. FastAPI Server (app.py)

**Purpose**: Serves as the main HTTP server for tool execution and metadata

**Key Endpoints**:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/tools` | GET | List available tool names |
| `/tools/{tool_name}` | POST | Execute a tool with input |
| `/mcp/tools/metadata` | GET | Full MCP metadata with schemas and examples |
| `/mcp/tools/invoke` | POST | MCP-style tool invocation |

**Implementation Details**:
- Uses `importlib` for dynamic module loading from the `/tools` directory
- Validates input using Pydantic models (`Input` class from tools)
- Extracts module docstrings for tool descriptions
- Supports both standard and MCP-compliant invocation styles

### 2. Tool Module Pattern

Each tool in `/tools` follows this standard structure:

```python
"""Tool description from module docstring."""

from pydantic import BaseModel

class Input(BaseModel):
    # Define input schema
    field: type

class Output(BaseModel):
    # Define output schema
    result: type

# Optional: Example data
class ExampleInput(Input):
    field = value

class ExampleOutput(Output):
    result = value

def execute(input_data: Input) -> Output:
    """Main execution logic."""
    # Implementation
    return Output(...)
```

### 3. Available Tools

#### get_weather.py
- **Purpose**: Retrieves weather information for locations
- **API**: Open-Meteo (free, no API key required)
- **Input**: `location` (string)
- **Output**: `weather` (formatted weather string)
- **Features**: 
  - Geocoding via Open-Meteo
  - WMO weather code interpretation
  - Detailed metrics (temp, humidity, wind, precipitation)

#### get_system_metrics.py
- **Purpose**: Monitors system resources
- **Dependency**: psutil
- **Input**: None (no input required)
- **Output**: CPU, memory, disk usage percentages
- **Use Case**: System health monitoring

#### extract_pdf_text.py
- **Purpose**: Extracts text from PDF files
- **Dependency**: PyMuPDF (fitz)
- **Input**: `file_path` (string)
- **Output**: `text` (extracted text content)
- **Use Case**: Document processing, content ingestion

#### text_to_json.py
- **Purpose**: Parses text into JSON format
- **Method**: Uses Python's json.loads()
- **Input**: `text` (string)
- **Output**: `json_data` (parsed dict)
- **Error Handling**: Returns error details in JSON

#### visit_webpage.py
- **Purpose**: Fetches and converts web pages to Markdown
- **Dependencies**: requests, markdownify
- **Input**: `url` (string)
- **Output**: `markdown_content` (formatted markdown)
- **Features**:
  - HTML to Markdown conversion
  - Content truncation (max 10K chars)
  - Timeout handling (20 seconds)
  - Error recovery

### 4. Client Library (invoke_tool.py)

**Purpose**: Python wrapper for calling tools programmatically

**Function**: `invoke_tool(tool_name, args, base_url)`
- Constructs MCP-style payload
- Makes HTTP POST request to `/mcp/tools/invoke`
- Returns parsed JSON response
- Raises RuntimeError on failure

**Example Usage**:
```python
from invoke_tool import invoke_tool

result = invoke_tool("get_weather", {"location": "Amsterdam"})
```

### 5. Tool Registry (tool_registry.json)

Static manifest listing available tools with basic metadata:
- Tool name
- Description
- (Can be extended with input/output schemas)

## Dependencies and Technology Stack

### Core Dependencies
- **fastapi**: Web framework for building REST APIs
- **uvicorn**: ASGI server for running FastAPI applications
- **pydantic**: Data validation and settings management using Python type annotations

### Tool-Specific Dependencies
- **psutil**: System and process monitoring library
- **PyMuPDF (fitz)**: PDF text extraction
- **requests**: HTTP client library
- **markdownify**: HTML to Markdown converter

### Development Tools
- **black**: Code formatter (line length: 88)
- **ruff**: Fast Python linter
- **isort**: Import sorting
- **pre-commit**: Git hooks framework

### Python Version
- Target: Python 3.11
- Configuration in `.python-version` and `pyproject.toml`

## Design Patterns and Conventions

### 1. Standardized Tool Interface

All tools implement a consistent contract:
```python
# Required: Module docstring for description
# Required: Input class (if tool accepts arguments)
# Required: Output class (return type)
# Required: execute() function with proper signature
```

### 2. Pydantic for Schema Management

- Input/Output validation
- Automatic JSON schema generation via `.schema()`
- Type safety and IDE autocomplete
- Example data via optional ExampleInput/ExampleOutput classes

### 3. Dynamic Discovery

The FastAPI app uses `pkgutil.iter_modules()` to automatically discover tools:
- No registration needed - just add a `.py` file to `/tools`
- Module name becomes the tool name
- Docstring becomes the description

### 4. Error Handling

Tools are responsible for their own error handling:
- Try-except blocks within tool logic
- Return error information in Output
- Server catches unhandled exceptions and returns HTTP 400

### 5. External API Integration

Tools use public APIs without authentication:
- Open-Meteo for weather (no API key)
- Generic HTTP requests for web scraping
- Enables tool reusability without credential management

## API Usage Patterns

### Standard REST API
```bash
# Execute tool
curl -X POST http://localhost:8080/tools/get_weather \
  -H "Content-Type: application/json" \
  -d '{"location": "Amsterdam"}'

# Get metadata
curl -X GET http://localhost:8080/tools/metadata
```

### MCP-Compliant API
```bash
# Get full metadata with schemas
curl -X GET http://localhost:8080/mcp/tools/metadata

# Invoke tool with MCP payload
curl -X POST http://localhost:8080/mcp/tools/invoke \
  -H "Content-Type: application/json" \
  -d '{"tool": "get_weather", "args": {"location": "Amsterdam"}}'
```

## Educational Components

### Agent Templates
The `templates/First_agent_template/` provides a complete agent application using:
- **Gradio**: Web UI framework
- **smolagents**: Agent library
- Pre-built prompts and configurations
- Deploy-ready for Hugging Face Spaces

### Course Materials
The `notebooks/` directory contains extensive Jupyter notebooks covering:
- Agent fundamentals (Unit 1)
- Framework comparisons (Unit 2):
  - smolagents
  - LlamaIndex
  - LangGraph
- Advanced topics (Bonus units)
- Multilingual support (French translations in `fr/`)

## Development Workflow

### Code Quality
- **Formatting**: Black (skip string normalization)
- **Linting**: Ruff for fast code quality checks
- **Import Management**: isort with Black profile
- **Git Hooks**: Pre-commit framework enforces standards

### Running the Server
```bash
# Start development server
uvicorn app:app --host 0.0.0.0 --port 8080

# Start alternative server
uvicorn app:app2 --host 0.0.0.0 --port 8181
```

## Component Interactions

### Request Flow - Tool Execution
```
HTTP Request
    ↓
FastAPI Route Handler
    ↓
Dynamic Module Import (importlib)
    ↓
Input Validation (Pydantic)
    ↓
Tool execute() Function
    ↓
Output Construction (Pydantic)
    ↓
JSON Response
```

### Integration Pattern
```
External Client/Agent
    ↓
invoke_tool.py (Python wrapper)
    ↓
HTTP POST to /mcp/tools/invoke
    ↓
FastAPI (app.py)
    ↓
Tool Module Execution
    ↓
Response JSON
```

## Recent Development History

1. **Initial Commit (1fe29ee)**: Project foundation with basic structure
2. **MCP Web Interface (d884a96)**: Added Flask app and tool registry
3. **Weather Integration (303d923)**: Connected weather.py to Open-Meteo API

## Extensibility

### Adding New Tools

1. Create new Python file in `/tools/` directory
2. Implement standard tool pattern:
   - Module docstring
   - Pydantic Input/Output classes
   - execute() function
3. Tool automatically available via REST API
4. (Optional) Update `tool_registry.json` for static documentation

### Deployment Considerations

- **Stateless Design**: No server state, can be horizontally scaled
- **Timeout Management**: Individual tools have their own timeouts (e.g., 20s for web requests)
- **Error Isolation**: Tool failures don't crash the server
- **Schema Validation**: Pydantic prevents invalid inputs from reaching tool logic

## Summary

mcp_tools is a well-structured, extensible tool execution platform that:
- Provides standardized REST and MCP-compliant APIs for tool execution
- Uses dynamic discovery for zero-configuration tool registration
- Employs Pydantic for robust schema management and validation
- Integrates with public APIs for real-world functionality
- Serves as an educational resource for building agent-based applications
- Follows Python best practices with pre-commit hooks and code quality standards
