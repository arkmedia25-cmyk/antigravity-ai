import os
import sys
from dotenv import load_dotenv

# Project Root adding for internal imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.agency.orchestrator import agency

def generate_morning_launch():
    """Generates the first autonomous content strategy for the next morning."""
    print("🌅 [STARTUP] Generating Morning Launch Package for @GlowUpNL...")
    
    # Topic from current high-velocity trends
    topic = "Gut-Brain Connection & Energy Levels for busy mothers"
    
    result = agency.run_full_autonomous_loop(topic)
    
    # Save the 'Ready to Launch' package to memory
    output_dir = "memory/ready_for_launch"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, "morning_strategy.txt"), "w", encoding="utf-8") as f:
        f.write(f"=== MORNING LAUNCH PACKAGE ===\n")
        f.write(f"Topic: {topic}\n")
        f.write(f"Researcher Data: {result.get('research_data', 'Analyzing...')}\n")
        f.write(f"Script: {result.get('script_package', {})}\n")
        f.write(f"Design Prompt: {result.get('design_prompt', '')}\n")
        
    print(f"\n✅ [SUCCESS] Morning package generated in {output_dir}/morning_strategy.txt")

if __name__ == "__main__":
    load_dotenv()
    generate_morning_launch()
