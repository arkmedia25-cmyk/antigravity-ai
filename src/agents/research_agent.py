from src.agents.base_agent import BaseAgent
from src.agents.agent_utils import load_memory_context, load_agent_prompt, build_funnel_context
from src.memory.memory_manager import MemoryManager
from src.skills.ai_client import ask_ai
from src.skills.research_tools import research_tools
from src.core.protocol import SwarmMessage
import json

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="research")
        self._system_prompt = load_agent_prompt("research-agent", "research_prompt.txt")
        self.memory = MemoryManager(namespace="research")
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "google_search",
                    "description": "General web search (falls back to DuckDuckGo). Use for market trends, competitor info, and general facts.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query."}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "pubmed_search",
                    "description": "Search PubMed for clinical trials, scientific papers, and academic studies about health/ingredients.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The scientific/ingredient search query."}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_pubmed_abstract",
                    "description": "Fetch the full abstract of a scientific paper via PMID to read the actual results and conclusions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pmid": {"type": "string", "description": "The PubMed ID (PMID) of the article."}
                        },
                        "required": ["pmid"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_page_content",
                    "description": "Scrape and read the full text content of a specific URL.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "The URL to read."}
                        },
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "save_research",
                    "description": "Save a verified research finding to the permanent memory (SQLite). Always save scientific evidence here.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string", "description": "Short title/topic of the finding."},
                            "content": {"type": "string", "description": "Detailed factual content to save."}
                        },
                        "required": ["topic", "content"]
                    }
                }
            }
        ]

    def process(self, input_data: str, chat_id=None, brand: str = "glowup", context: dict = None) -> str:
        self.logger.info(f"[RESEARCH] Starting autonomous research: {input_data[:100]}")
        
        memory_context = load_memory_context()
        funnel_context = build_funnel_context(chat_id)
        
        # Initialize conversation with personality and knowledge
        messages = [
            {"role": "system", "content": f"{self._system_prompt}\n\n=== SYSTEM KNOWLEDGE ===\n{memory_context}\n{funnel_context}"},
            {"role": "user", "content": input_data}
        ]

        # Maximum 10 turns for deep research
        for i in range(10):
            self.logger.debug(f"Research loop turn {i+1}...")
            
            # Use upgraded ask_ai that handles message list
            response_msg = ask_ai(messages, tools=self.tools)
            
            # Handle Tool Calls
            if hasattr(response_msg, 'tool_calls') and response_msg.tool_calls:
                # Add assistant's tool call to history
                messages.append({
                    "role": "assistant",
                    "content": response_msg.content,
                    "tool_calls": response_msg.tool_calls
                })
                
                for tool_call in response_msg.tool_calls:
                    func_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    
                    self.logger.info(f"[TOOL] Executing tool: {func_name}({args})")
                    
                    if func_name == "google_search":
                        result = research_tools.google_search(args["query"])
                    elif func_name == "pubmed_search":
                        result = research_tools.pubmed_search(args["query"])
                    elif func_name == "get_pubmed_abstract":
                        result = research_tools.get_pubmed_abstract(args["pmid"])
                    elif func_name == "get_page_content":
                        result = research_tools.get_page_content(args["url"])
                    elif func_name == "save_research":
                        result = "SUCCESS" if research_tools.save_research(args["topic"], args["content"]) else "ALREADY_EXISTS"
                    else:
                        result = "Error: Unknown tool."

                    # Add tool result to history
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": func_name,
                        "content": json.dumps(result, ensure_ascii=False)
                    })
                
                # Continue loop to let AI digest tool results
                continue
            
            else:
                # Final answer reached update memory and return
                self.logger.info("Research complete.")
                self.memory.save("last_response", response_msg, chat_id=chat_id)
                
                return SwarmMessage(
                    sender=self.name,
                    content=response_msg,
                    status="success"
                )

        return SwarmMessage(
            sender=self.name,
            content="Araştırma süreci zaman aşımına uğradı veya çok fazla adım gerektirdi. Bulabildiklerim hafızaya işlendi.",
            status="error"
        )
