import json
import logging
import os
import sys
import numpy as np
from typing import List, Dict, Optional

# Ensure root is in path
_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_FILE_DIR, "..", ".."))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from mcp.server.fastmcp import FastMCP
from src.skills.ai_client import ask_ai
from src.skills.graph_service import graph_service

logger = logging.getLogger(__name__)

def register_knowledge_tools(mcp: FastMCP):
    """Registers advanced RAG and Knowledge suites."""

    @mcp.tool()
    def generate_embeddings(text: str) -> str:
        """
        Converts text into a semantic vector representation. (Pillar 32)
        Note: In real-world, calls OpenAI/Local embedding model.
        """
        # Simulated embedding for portable architecture
        # Real impl would use ai_client.get_embeddings(text)
        vector = np.random.uniform(-1, 1, 1536).tolist() 
        return json.dumps({"text_snippet": text[:50], "vector_dim": 1536, "vector": vector})

    @mcp.tool()
    def search_vector_memory(query: str, top_k: int = 3) -> str:
        """
        Performs a semantic search across the Vector DB. (Pillar 31)
        Connects current query to past research and knowledge.
        """
        # This will be connected to a persistent Chroma/SQLite-VSS store in next steps
        results = [
            {"id": "doc_1", "score": 0.92, "content": "Benefits of cold exposure for mitochondria."},
            {"id": "doc_2", "score": 0.85, "content": "Wim Hof method breathing techniques for focus."}
        ]
        return json.dumps({"query": query, "results": results[:top_k]})

    @mcp.tool()
    def build_context_window(task_id: str, query: str) -> str:
        """
        The 'Ultimate Context' builder. (Pillar 33) 
        Merges Graph Lineage, Vector Search results, and Prompt Templates.
        """
        # 1. Get Graph Memory
        graph_mem = graph_service.get_lineage(task_id)
        
        # 2. Get Semantic Memory (Vector)
        vec_mem = json.loads(search_vector_memory(query))
        
        context = {
            "task_id": task_id,
            "origin_lineage": graph_mem,
            "related_research": vec_mem.get("results"),
            "timestamp": "2026-04-16",
            "instruction_depth": "Master-Level"
        }
        return json.dumps(context)

logger.info("Knowledge tools registered successfully.")
