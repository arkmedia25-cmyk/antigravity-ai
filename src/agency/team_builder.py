import os
import glob
import importlib
import inspect
from typing import List, Dict
from src.agents.base_agent import BaseAgent

class TeamBuilder:
    """Implementation of Phase 1: Agent Discovery from Team Builder skill."""
    
    def __init__(self, agents_dir: str = "src/agents"):
        self.project_root = os.getcwd()
        self.agents_dir = os.path.join(self.project_root, agents_dir)
        self.agents_metadata = {}

    def discover_agents(self) -> Dict[str, dict]:
        """Scans the agents directory and extracts metadata."""
        agent_files = glob.glob(os.path.join(self.agents_dir, "*_agent.py"))
        
        for file_path in agent_files:
            file_name = os.path.basename(file_path)
            module_name = f"src.agents.{file_name[:-3]}"
            
            try:
                module = importlib.import_module(module_name)
                # Find classes that inherit from BaseAgent
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, BaseAgent) and obj is not BaseAgent:
                        # Extract domain from filename prefix (e.g. sales_agent.py -> Sales)
                        domain = file_name.split("_")[0].capitalize()
                        description = obj.__doc__ or "No description available."
                        
                        self.agents_metadata[name] = {
                            "name": name,
                            "domain": domain,
                            "description": description.strip().split("\n")[0],
                            "module": module_name,
                            "class": name
                        }
            except Exception as e:
                print(f"Error loading agent {module_name}: {e}")
                
        return self.agents_metadata

    def get_team_menu(self) -> str:
        """Returns a string representation of available domains and agents."""
        if not self.agents_metadata:
            self.discover_agents()
            
        domains = {}
        for agent in self.agents_metadata.values():
            d = agent["domain"]
            if d not in domains:
                domains[d] = []
            domains[d].append(agent["name"])
            
        menu = "Available Agent Domains:\n"
        for i, (domain, agents) in enumerate(domains.items(), 1):
            menu += f"{i}. {domain} — {', '.join(agents)}\n"
            
        return menu

# Global instance
team_builder = TeamBuilder()
