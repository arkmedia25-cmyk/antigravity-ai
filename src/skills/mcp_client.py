import asyncio
import os
import sys
import json
import logging
import threading
from typing import Dict, Any, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Basic Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPBridge:
    """A synchronous bridge to the asynchronous MCP SDK with a persistent session."""
    
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
        
        # Session state
        self._session: Optional[ClientSession] = None
        self._exit_stack = None
        self._connection_lock = threading.Lock()
        
        # Ensure connection is established early
        self._run_async(self._ensure_connected())

    def _run_event_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def _run_async(self, coro):
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        try:
            return future.result(timeout=60)
        except Exception as e:
            logger.error(f"Async transition error: {e}")
            return None

    async def _ensure_connected(self):
        """Initializes the persistent MCP session if not already connected."""
        if self._session:
            return
        
        try:
            # We use a manual context manager entry here for persistence
            logger.info("Initializing persistent MCP session...")
            from contextlib import AsyncExitStack
            self._exit_stack = AsyncExitStack()
            
            read, write = await self._exit_stack.enter_async_context(stdio_client(self._server_params))
            session = await self._exit_stack.enter_async_context(ClientSession(read, write))
            
            await session.initialize()
            self._session = session
            logger.info("✅ Persistent MCP session established.")
        except Exception as e:
            logger.error(f"Failed to establish persistent MCP session: {e}")
            self._session = None

    async def _call_tool_async(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        try:
            await self._ensure_connected()
            if not self._session:
                return {"error": "MCP Session not available."}
            
            result = await self._session.call_tool(tool_name, arguments)
            return result
        except Exception as e:
            logger.error(f"MCP Tool Execution Error ({tool_name}): {e}")
            # If session is dead, clear it for next retry
            self._session = None
            return {"error": str(e)}

    async def _get_tools_async(self) -> List[Dict]:
        try:
            await self._ensure_connected()
            if not self._session:
                return []
            
            mcp_tools = await self._session.list_tools()
            
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
            self._session = None
            return []

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool synchronously."""
        return self._run_async(self._call_tool_async(tool_name, arguments))

    def get_tools(self) -> List[Dict]:
        """Fetch all available tools from the MCP server."""
        return self._run_async(self._get_tools_async())

# Global Instance for easier access
try:
    mcp_bridge = MCPBridge()
except Exception as e:
    logger.error(f"Failed to initialize MCP Bridge: {e}")
    mcp_bridge = None
