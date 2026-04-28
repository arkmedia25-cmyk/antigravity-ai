"""
Agent sistemini başlatır.
Cron: 0 9 * * 1  (her Pazartesi 09:00)
Kullanım: python run_agents.py [--channel neonpulse sleepwave]
"""
import argparse
import sys
from pathlib import Path

# Proje kökünü path'e ekle
sys.path.insert(0, str(Path(__file__).parent))

from agents import orchestrator

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--channel", nargs="*",
        help="Belirli kanalları çalıştır (boş = tümü)"
    )
    args = parser.parse_args()

    decision = orchestrator.run(args.channel)

    print("\n=== ORKESTRATÖR KARARI ===")
    print(f"Öncelikli kanal : {decision.get('priority_channel', '?')}")
    print(f"Bu haftanın odağı: {decision.get('weekly_focus', '?')}")
    if decision.get("alerts"):
        print(f"Uyarılar: {', '.join(decision['alerts'])}")
