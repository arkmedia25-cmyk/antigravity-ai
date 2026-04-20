import asyncio
import os
import sys
import json
import logging
import threading
from typing import Dict, Any, List, Optional

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    _MCP_AVAILABLE = True
except ImportError:
    _MCP_AVAILABLE = False

# Basic Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPBridge:
    """A synchronous bridge to the asynchronous MCP SDK."""
    
    def __init__(self):
        # Point to the server.py inside src/mcp/
        server_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mcp", "server.py")
        self._server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_path],
            env=os.environ.copy()
        )
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()

    def _run_event_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def _run_async(self, coro):
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        try:
            return future.result(timeout=8)
        except Exception as e:
            logger.warning(f"MCP timeout/error (skipping): {e}")
            return None

    async def _call_tool_async(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        try:
            async with stdio_client(self._server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments)
                    return result
        except Exception as e:
            logger.error(f"MCP Tool Execution Error ({tool_name}): {e}")
            return {"error": str(e)}

    async def _get_tools_async(self) -> List[Dict]:
        try:
            async with stdio_client(self._server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    mcp_tools = await session.list_tools()
                    
                    formatted_tools = []
                    for tool in mcp_tools.tools:
                         formatted_tools.append({
                            "type": "function",
                            "function": {
                                "name": tool.name,
                                "description": tool.description,
                                "parameters": tool.inputSchema
                            }
                        })
                    return formatted_tools
        except Exception as e:
            logger.error(f"MCP Discovery Error: {e}")
            return []

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool synchronously."""
        return self._run_async(self._call_tool_async(tool_name, arguments))

    def get_tools(self) -> List[Dict]:
        """Fetch all available tools from the MCP server."""
        return self._run_async(self._get_tools_async())

# Global Instance for easier access
if not _MCP_AVAILABLE:
    logger.warning("MCP module not installed — mcp_bridge disabled. AI calls will use direct API.")
    mcp_bridge = None
else:
    try:
        mcp_bridge = MCPBridge()
    except Exception as e:
        logger.error(f"Failed to initialize MCP Bridge: {e}")
        mcp_bridge = None
