import asyncio
import atexit
import json
import signal
import sys

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent as MCPTextContent, ImageContent as MCPImageContent

from .manager import BackendManager


server = Server("scicompute")
manager = BackendManager()
_shutdown_requested = False


def _cleanup():
    global _shutdown_requested
    if _shutdown_requested:
        return
    _shutdown_requested = True
    manager.stop_all()


@atexit.register
def _atexit_cleanup():
    _cleanup()


def _signal_handler(signum, frame):
    _cleanup()
    sys.exit(0)


signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGHUP, _signal_handler)


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="compute",
            description="Execute scientific computing code. Supports multiple backends (mathematica, matlab, sympy, julia). Use 'backend' parameter to specify, or leave empty for auto-select.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Code to execute in the selected backend"
                    },
                    "backend": {
                        "type": "string",
                        "description": "Backend name (mathematica, matlab, sympy, julia, numpy). Default: auto"
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="list_backends",
            description="List all available computing backends and their capabilities",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="stop",
            description="Stop backend to clear variables and free memory. Use when you want a clean slate or the backend is misbehaving. The backend will restart automatically when needed.",
            inputSchema={
                "type": "object",
                "properties": {
                    "backend": {
                        "type": "string",
                        "description": "Backend name (e.g., 'octave', 'mathematica'). Leave empty to stop all."
                    }
                }
            }
        ),
        Tool(
            name="doc",
            description="Query documentation for a symbol. Returns usage information and options. Useful when you need to understand how to use a function.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Symbol name to query (e.g., 'Plot', 'NDSolve', 'Import')"
                    },
                    "backend": {
                        "type": "string",
                        "description": "Backend name (default: mathematica)"
                    }
                },
                "required": ["symbol"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list:
    if name == "compute":
        code = arguments.get("code", "")
        backend = arguments.get("backend")
        
        result = manager.compute(code, backend)
        
        content = []
        for item in result.content:
            if isinstance(item, dict):
                item_type = item.get("type")
                if item_type == "text":
                    content.append(MCPTextContent(type="text", text=item.get("text", "")))
                elif item_type == "image":
                    content.append(MCPImageContent(
                        type="image",
                        data=item.get("data", ""),
                        mimeType=item.get("mimeType", "image/png")
                    ))
                elif item_type == "error":
                    content.append(MCPTextContent(type="text", text=f"Error: {item.get('message', '')}"))
            else:
                if hasattr(item, 'type'):
                    if item.type == "text":
                        content.append(MCPTextContent(type="text", text=item.text))
                    elif item.type == "image":
                        content.append(MCPImageContent(type="image", data=item.data, mimeType=item.mimeType))
                    elif item.type == "error":
                        content.append(MCPTextContent(type="text", text=f"Error: {item.message}"))
        
        return content
    
    elif name == "list_backends":
        backends = manager.list_available()
        text = json.dumps(backends, indent=2)
        return [MCPTextContent(type="text", text=text)]
    
    elif name == "stop":
        backend = arguments.get("backend")
        result = manager.stop(backend)
        return [MCPTextContent(type="text", text=json.dumps(result))]

    elif name == "doc":
        symbol = arguments.get("symbol", "")
        backend = arguments.get("backend", "mathematica")
        
        result = manager.doc(symbol, backend)
        
        content = []
        for item in result.content:
            if isinstance(item, dict):
                item_type = item.get("type")
                if item_type == "text":
                    content.append(MCPTextContent(type="text", text=item.get("text", "")))
                elif item_type == "error":
                    content.append(MCPTextContent(type="text", text=f"Error: {item.get('message', '')}"))
            else:
                if hasattr(item, 'type'):
                    if item.type == "text":
                        content.append(MCPTextContent(type="text", text=item.text))
                    elif item.type == "error":
                        content.append(MCPTextContent(type="text", text=f"Error: {item.message}"))
        
        return content
    
    return [MCPTextContent(type="text", text=f"Unknown tool: {name}")]


async def run():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()