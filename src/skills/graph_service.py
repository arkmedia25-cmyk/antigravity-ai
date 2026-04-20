import sqlite3
import time
import os
import json
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class GraphService:
    """Manages relationships between entities (Research, Scripts, Videos, Budgets)."""
    
    def __init__(self, db_path: str = "data/knowledge_graph.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            # Nodes represent entities (Task, Metadata, File, Agent)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS nodes (
                    id TEXT PRIMARY KEY,
                    type TEXT NOT NULL, -- 'task', 'insight', 'asset', 'agent'
                    label TEXT,
                    data_json TEXT,
                    created_at REAL
                )
            """)
            # Edges represent relationships
            conn.execute("""
                CREATE TABLE IF NOT EXISTS edges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    relation TEXT NOT NULL, -- 'derived_from', 'produced_by', 'referenced'
                    FOREIGN KEY(source_id) REFERENCES nodes(id),
                    FOREIGN KEY(target_id) REFERENCES nodes(id)
                )
            """)

    def add_node(self, node_id: str, node_type: str, label: str, data: Optional[Dict] = None):
        """Adds or updates a node in the graph."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO nodes (id, type, label, data_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                data_json = excluded.data_json
            """, (node_id, node_type, label, json.dumps(data) if data else "{}", time.time()))

    def link(self, source_id: str, target_id: str, relation: str):
        """Creates a relationship link between two nodes."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO edges (source_id, target_id, relation)
                VALUES (?, ?, ?)
            """, (source_id, target_id, relation))

    def add_relation(self, parent_id: str, child_id: str, relation_type: str) -> bool:
        """Alias for link, compatible with the new Specialized Graph Master."""
        try:
            self.link(parent_id, child_id, relation_type)
            return True
        except Exception as e:
            logger.error(f"Graph link error: {e}")
            return False

    def query_knowledge(self, topic: str) -> List[Dict]:
        """Searches the nodes for relevant past knowledge. (Pillar 30)"""
        with sqlite3.connect(self.db_path) as conn:
            query = f"%{topic}%"
            rows = conn.execute("""
                SELECT id, type, label, data_json 
                FROM nodes 
                WHERE label LIKE ? OR data_json LIKE ?
                LIMIT 5
            """, (query, query)).fetchall()
            return [{"id": r[0], "type": r[1], "label": r[2], "data": json.loads(r[3])} for r in rows]

    def get_lineage(self, node_id: str) -> List[Dict]:
        """Traces the origin of a node (Recursive lookup)."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("""
                SELECT n.id, n.type, n.label, e.relation
                FROM nodes n
                JOIN edges e ON n.id = e.source_id
                WHERE e.target_id = ?
            """, (node_id,)).fetchall()
            return [{"parent_id": r[0], "type": r[1], "label": r[2], "relation": r[3]} for r in rows]

# Global Instance
graph_service = GraphService()
