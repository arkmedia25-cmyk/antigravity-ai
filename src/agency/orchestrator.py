from src.agency.agents import ResearcherAgent, StrategistAgent, WriterAgent, DesignerAgent, ProducerAgent, PublisherAgent
import json

class AgencyOrchestrator:
    def __init__(self):
        self.researcher = ResearcherAgent()
        self.strategist = StrategistAgent()
        self.writer = WriterAgent()
        self.designer = DesignerAgent()
        self.producer = ProducerAgent()
        self.publisher = PublisherAgent()

    def run_full_autonomous_loop(self, base_topic: str):
        """Runs the entire agency pipeline from research to publication readiness."""
        print(f"🎬 [ORCHESTRATOR] Starting autonomous loop for topic: {base_topic}")
        
        # Phase 1: Research Viral Trends
        research_data = self.researcher.run_task(f"Find the most viral trend or hook for {base_topic} in health & wellness.")
        print(f"🔍 [RESEARCH] Complete: {research_data[:100]}...")
        
        # Phase 2: Create Strategy
        strategy = self.strategist.run_task(f"Based on this research: {research_data}, create a 3-step marketing funnel and hook for @GlowUpNL.")
        print(f"🧠 [STRATEGY] Complete: {strategy[:100]}...")
        
        # Phase 3: Write Viral Script
        script_package = self.writer.run_task(f"Using this strategy: {strategy}, write a 30-sec Instagram Reel script in Dutch. Include Hook, Content, and CTA.", is_json=True)
        print(f"✍️ [WRITER] Complete: {script_package.get('title', 'No Title')}")
        
        # Phase 4: Prepare Visuals & Design
        design_prompt = self.designer.run_task(f"Based on this script: {script_package}, generate a high-end DALL-E image prompt for a vertical Reel background.")
        print(f"🎨 [DESIGNER] Complete: {design_prompt[:100]}...")
        
        # Phase 5: Production & Rendering (Handled by skills)
        print("🎥 [PRODUCER] Video generation logic triggered...")
        
        return {
            "status": "ready_for_review",
            "script_package": script_package,
            "design_prompt": design_prompt
        }

# Global Orchestrator Instance
agency = AgencyOrchestrator()
