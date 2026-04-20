import os
import sys
import logging
from mcp.server.fastmcp import FastMCP

# Add root directory to sys.path safely
_FILE_DIR = os.path.dirname(os.path.abspath(__file__)) # src/mcp
_PROJECT_ROOT = os.path.abspath(os.path.join(_FILE_DIR, "..", ".."))

if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import importlib
import glob
from src.mcp.servers.prompt_evolution import register_prompt_evolution_tools
from src.mcp.servers.graph_db import register_graph_db_tools
from src.mcp.servers.knowledge import register_knowledge_tools
from src.mcp.servers.frontier import register_frontier_tools

import sys

# Configure Logging to stderr (Crucial for MCP Stdio compatibility)
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Global FastMCP Hub
mcp = FastMCP("Antigravity-OS")

# Register Architecture Suites
# Register Standalone Phase 5/6 Suites
register_prompt_evolution_tools(mcp)
register_graph_db_tools(mcp)
register_knowledge_tools(mcp)
register_frontier_tools(mcp)

# Dynamically Register All Specialized Expert Servers (Phase 7)
specialized_dir = os.path.join(_FILE_DIR, "servers", "specialized")
for file_path in glob.glob(os.path.join(specialized_dir, "*.py")):
    basename = os.path.basename(file_path)
    if basename == "__init__.py":
        continue
    module_name = basename[:-3]
    try:
        module = importlib.import_module(f"src.mcp.servers.specialized.{module_name}")
        if hasattr(module, "register"):
            module.register(mcp)
            logger.info(f"✅ Registered specialized expert: {module_name}")
        else:
            logger.warning(f"⚠️ Expert {module_name} missing 'register' function.")
    except Exception as e:
        logger.error(f"❌ Failed to load specialized expert {module_name}: {e}")

@mcp.resource("system://health")
def get_health() -> str:
    """Returns the current operational status of the OS hub."""
    return "Status: Online | Middleware Phase: 1 (Core OS) | Complexity: 25 Pillars"

if __name__ == "__main__":
    logger.info("Antigravity MCP OS Hub starting up...")
    mcp.run()
