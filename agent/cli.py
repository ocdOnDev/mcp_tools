"""Command-line interface for the agent."""

import sys
from typing import Optional

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.syntax import Syntax

from agent.core import Agent

console = Console()


@click.group()
def cli():
    """MCP Agent - Intelligent assistant with tool coordination."""
    pass


@cli.command()
@click.argument("query", required=False)
@click.option("--model", "-m", default="gemma:latest", help="Ollama model to use")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["auto", "text", "json", "markdown"]),
    default="auto",
    help="Response format",
)
@click.option("--mcp-url", default="http://localhost:8000", help="MCP API URL")
@click.option("--ollama-url", default="http://localhost:11434", help="Ollama API URL")
def ask(
    query: Optional[str],
    model: str,
    format: str,
    mcp_url: str,
    ollama_url: str,
):
    """Ask the agent a question (single-shot mode)."""
    if not query:
        console.print("[red]Error:[/red] Please provide a query", style="bold")
        console.print("\nExample: mcp-agent ask 'What is the weather in Paris?'")
        sys.exit(1)

    try:
        # Initialize agent
        console.print(f"[cyan]Initializing agent with model:[/cyan] {model}")
        agent = Agent(mcp_url=mcp_url, ollama_url=ollama_url, model=model)

        # Process query
        console.print(f"\n[cyan]Processing:[/cyan] {query}\n")

        with console.status("[bold green]Thinking..."):
            result = agent.ask(query, return_format=format)

        # Display result
        _display_result(result, format)

    except ConnectionError as e:
        console.print(f"[red]Connection Error:[/red] {e}", style="bold")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        sys.exit(1)


@cli.command()
@click.option("--model", "-m", default="gemma:latest", help="Ollama model to use")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["auto", "text", "json", "markdown"]),
    default="auto",
    help="Response format",
)
@click.option("--mcp-url", default="http://localhost:8000", help="MCP API URL")
@click.option("--ollama-url", default="http://localhost:11434", help="Ollama API URL")
def chat(model: str, format: str, mcp_url: str, ollama_url: str):
    """Start interactive chat session with the agent."""
    try:
        # Initialize agent
        console.print(
            Panel.fit(
                f"[bold cyan]MCP Agent[/bold cyan]\n"
                f"Model: {model}\n"
                f"Format: {format}\n\n"
                f"Type your questions or commands.\n"
                f"Special commands:\n"
                f"  /help - Show help\n"
                f"  /clear - Clear conversation history\n"
                f"  /tools - List available tools\n"
                f"  /history - Show conversation history\n"
                f"  /exit or /quit - Exit chat",
                title="🤖 Agent Chat",
                border_style="cyan",
            )
        )

        agent = Agent(mcp_url=mcp_url, ollama_url=ollama_url, model=model)

        while True:
            # Get user input
            user_input = Prompt.ask("\n[bold green]You[/bold green]")

            if not user_input.strip():
                continue

            # Handle special commands
            if user_input.startswith("/"):
                if _handle_command(user_input, agent):
                    continue
                else:
                    break

            # Process query
            with console.status("[bold cyan]Agent is thinking..."):
                result = agent.ask(user_input, return_format=format)

            # Display result
            console.print("\n[bold cyan]Agent:[/bold cyan]")
            _display_result(result, format, in_chat=True)

    except KeyboardInterrupt:
        console.print("\n\n[yellow]Chat interrupted. Goodbye![/yellow]")
    except ConnectionError as e:
        console.print(f"\n[red]Connection Error:[/red] {e}", style="bold")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}", style="bold")
        sys.exit(1)


@cli.command()
@click.option("--mcp-url", default="http://localhost:8000", help="MCP API URL")
@click.option("--ollama-url", default="http://localhost:11434", help="Ollama API URL")
def status(mcp_url: str, ollama_url: str):
    """Check status of MCP server and Ollama."""
    import requests

    console.print("[cyan]Checking system status...[/cyan]\n")

    # Check MCP server
    try:
        response = requests.get(f"{mcp_url}/tools", timeout=5)
        if response.status_code == 200:
            tools = response.json()["tools"]
            console.print(
                f"[green]✓[/green] MCP Server: Running at {mcp_url} ({len(tools)} tools available)"
            )
        else:
            console.print("[yellow]⚠[/yellow] MCP Server: Unexpected status code")
    except Exception as e:
        console.print(f"[red]✗[/red] MCP Server: Not accessible ({e})")

    # Check Ollama
    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()["models"]
            console.print(
                f"[green]✓[/green] Ollama: Running at {ollama_url} ({len(models)} models available)"
            )
            for model in models:
                console.print(f"  • {model['name']}")
        else:
            console.print("[yellow]⚠[/yellow] Ollama: Unexpected status code")
    except Exception as e:
        console.print(f"[red]✗[/red] Ollama: Not accessible ({e})")


@cli.command()
@click.option("--mcp-url", default="http://localhost:8000", help="MCP API URL")
def tools(mcp_url: str):
    """List all available tools with descriptions."""
    from agent.core import MCPToolsClient

    try:
        client = MCPToolsClient(mcp_url)
        metadata = client.get_tool_metadata()

        console.print(
            Panel.fit(
                f"[bold cyan]Available Tools[/bold cyan]\n"
                f"Found {len(metadata['tools'])} tools",
                border_style="cyan",
            )
        )

        for tool in metadata["tools"]:
            console.print(f"\n[bold green]{tool['name']}[/bold green]")
            console.print(f"  {tool['description']}")

            # Show input parameters
            if "input_schema" in tool and "properties" in tool["input_schema"]:
                console.print("  [dim]Parameters:[/dim]")
                for param, details in tool["input_schema"]["properties"].items():
                    param_type = details.get("type", "any")
                    required = (
                        param in tool["input_schema"].get("required", [])
                        if "input_schema" in tool
                        else False
                    )
                    req_str = "[red]*[/red]" if required else "[dim](optional)[/dim]"
                    console.print(f"    • {param}: {param_type} {req_str}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}", style="bold")
        sys.exit(1)


def _display_result(result: dict, format: str, in_chat: bool = False):
    """Display agent result based on format."""
    response = result["response"]
    tool_calls = result.get("tool_calls", [])

    # Show tool calls if any
    if tool_calls and not in_chat:
        console.print("\n[dim]Tool calls:[/dim]")
        for call in tool_calls:
            tool_name = call["tool"]
            success = call["success"]
            status_icon = "[green]✓[/green]" if success else "[red]✗[/red]"
            console.print(f"  {status_icon} {tool_name}")
            if not success:
                console.print(f"    [red]Error: {call.get('error', 'Unknown')}[/red]")

    # Display response
    console.print()
    if format == "markdown":
        md = Markdown(response)
        console.print(md)
    elif format == "json":
        syntax = Syntax(response, "json", theme="monokai", line_numbers=False)
        console.print(syntax)
    else:
        console.print(response)

    # Show metadata
    if not in_chat:
        metadata = result.get("metadata", {})
        console.print(
            f"\n[dim]Iterations: {metadata.get('iterations', 0)} | "
            f"Success: {metadata.get('success', True)}[/dim]"
        )


def _handle_command(command: str, agent: Agent) -> bool:
    """Handle special chat commands. Returns True to continue, False to exit."""
    cmd = command.lower().strip()

    if cmd in ["/exit", "/quit", "/q"]:
        console.print("\n[yellow]Goodbye![/yellow]")
        return False

    elif cmd == "/help":
        console.print(
            Panel.fit(
                "[bold]Available Commands:[/bold]\n\n"
                "/help - Show this help message\n"
                "/clear - Clear conversation history\n"
                "/tools - List available tools\n"
                "/history - Show conversation history\n"
                "/exit, /quit, /q - Exit chat",
                title="Help",
                border_style="cyan",
            )
        )

    elif cmd == "/clear":
        agent.reset_conversation()
        console.print("[green]Conversation history cleared[/green]")

    elif cmd == "/tools":
        tools = agent.mcp_client.list_tools()
        console.print("\n[bold cyan]Available Tools:[/bold cyan]")
        for tool in tools:
            console.print(f"  • {tool}")

    elif cmd == "/history":
        history = agent.get_conversation_history()
        if not history:
            console.print("[yellow]No conversation history yet[/yellow]")
        else:
            console.print("\n[bold cyan]Conversation History:[/bold cyan]")
            for i, msg in enumerate(history):
                role = msg["role"]
                content = msg["content"]
                role_color = "green" if role == "user" else "cyan"
                console.print(f"\n[{role_color}]{role.capitalize()}:[/{role_color}]")
                console.print(content)

    else:
        console.print(f"[red]Unknown command:[/red] {command}")
        console.print("[dim]Type /help for available commands[/dim]")

    return True


if __name__ == "__main__":
    cli()
