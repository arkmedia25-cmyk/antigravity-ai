from unittest.mock import patch
from src.agents.cmo_agent import CmoAgent


def test_cmo_agent_process():
    agent = CmoAgent()
    with patch("src.skills.ai_client.ask_ai", return_value="CMO strategie resultaat"):
        result = agent.process("Hollanda'da supplement niche icin lead sistemi kur")
    assert isinstance(result, str)
    assert len(result) > 0
