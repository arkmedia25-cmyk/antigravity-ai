from src.skills.ai_client import ask_ai

class AgentBase:
    def __init__(self, name: str, role: str, expertise: str):
        self.name = name
        self.role = role
        self.expertise = expertise

    def run_task(self, prompt: str, is_json: bool = False) -> str:
        system_prompt = f"Role: {self.role}. Expertise: {self.expertise}. Name: {self.name}."
        full_prompt = f"{system_prompt}\n\nTask: {prompt}"
        return ask_ai(full_prompt, is_json=is_json)

class ResearcherAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="The Spy",
            role="Strategic Market Researcher",
            expertise="Analyzing viral trends on YouTube, Instagram, and TikTok. Finding industry pains."
        )

class StrategistAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="The Brain",
            role="Chief Marketing Officer (CMO)",
            expertise="Converting research data into high-converting marketing funnels and content strategies."
        )

class WriterAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="The Pen",
            role="Viral Script & Content Writer",
            expertise="Writing psychological hooks and engaging short-form video scripts in Dutch."
        )

class DesignerAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="The Brush",
            role="Aesthetic Visual Designer",
            expertise="Creating high-end Canva designs and DALL-E image prompts based on brand guidelines."
        )

class ProducerAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="The Lens",
            role="Video Production Master",
            expertise="Orchestrating FFmpeg rendering, TTS synchronization, and final video quality control."
        )

class PublisherAgent(AgentBase):
    def __init__(self):
        super().__init__(
            name="The Pilot",
            role="Social Media Distribution Manager",
            expertise="Managing Meta Instagram/Facebook Graph API and automation of content publication."
        )
