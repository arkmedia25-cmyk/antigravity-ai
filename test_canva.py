import sys
import os
sys.path.insert(0, os.path.abspath('src'))

# Load environment variables and settings
from config.settings import settings
from agents.canva_agent import CanvaAgent

def main():
    agent = CanvaAgent()
    print("Testing Canva Agent with template execution...")
    # Trigger the instagram design creation for the requested chat_id
    res = agent.process("instagram Ark Media Flow: Geleceğin Medya Ajansı Artık Canlı!", chat_id=812914122)
    print("\nResult Data:")
    print("-" * 40)
    print(res)
    print("-" * 40)

if __name__ == "__main__":
    main()
