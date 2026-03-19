import os
import json
from ai_client import ask_ai


def load_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_memory():
    current_dir = os.path.dirname(__file__)
    memory_dir = os.path.abspath(os.path.join(current_dir, "../../memory"))

    brand = load_json(os.path.join(memory_dir, "brand.json"))
    products = load_json(os.path.join(memory_dir, "products.json"))
    audience = load_json(os.path.join(memory_dir, "audience.json"))
    learned = load_json(os.path.join(memory_dir, "learned.json"))

    memory_text = f"""
=== MARKA BİLGİSİ ===
{json.dumps(brand, ensure_ascii=False, indent=2)}

=== ÜRÜNLER ===
{json.dumps(products, ensure_ascii=False, indent=2)}

=== HEDEF KİTLE ===
{json.dumps(audience, ensure_ascii=False, indent=2)}

=== ÖĞRENİLENLER ===
Onaylanan hook'lar: {learned.get('approved_hooks', [])}
Reddedilen stiller: {learned.get('rejected_styles', [])}
Onaylanan CTA'lar: {learned.get('approved_ctas', [])}
"""
    return memory_text


def load_cmo():
    current_dir = os.path.dirname(__file__)
    cmo_file = os.path.abspath(
        os.path.join(current_dir, "../../agents/cmo-agent/cmo.txt")
    )
    if not os.path.exists(cmo_file):
        raise FileNotFoundError(f"CMO dosyasi bulunamadi: {cmo_file}")
    with open(cmo_file, "r", encoding="utf-8") as f:
        return f.read()


def run_cmo(task):
    try:
        cmo_prompt = load_cmo()
        memory = load_memory()

        full_prompt = (
            f"{cmo_prompt}\n\n"
            f"=== SİSTEM HAFIZASI ===\n"
            f"{memory}\n\n"
            f"=== GÖREV ===\n"
            f"{task}\n\n"
            f"Respond in a structured way:\n"
            f"1. Summary\n"
            f"2. Strategy Options\n"
            f"3. Best Recommendation\n"
            f"4. Next Action Steps"
        )

        response = ask_ai(full_prompt)
        return response

    except Exception as e:
        return f"CMO agent hatasi: {e}"
