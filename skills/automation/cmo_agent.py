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
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"[WARN] JSON parse hatasi ({filepath}): {e}")
    return {}



def load_memory():
    current_dir = os.path.dirname(__file__)
    memory_dir = os.path.abspath(os.path.join(current_dir, "../../memory"))

    brand = load_json(os.path.join(memory_dir, "brand.json"))
    products = load_json(os.path.join(memory_dir, "products.json"))
    audience = load_json(os.path.join(memory_dir, "audience.json"))
    learned = load_json(os.path.join(memory_dir, "learned.json"))

    memory_text = f"""
=== MERKINFO ===
{json.dumps(brand, ensure_ascii=False, indent=2)}

=== PRODUCTEN ===
{json.dumps(products, ensure_ascii=False, indent=2)}

=== DOELGROEP ===
{json.dumps(audience, ensure_ascii=False, indent=2)}

=== GELEERDE INZICHTEN ===
Goedgekeurde hooks: {learned.get('approved_hooks', [])}
Afgewezen stijlen: {learned.get('rejected_styles', [])}
Goedgekeurde CTA's: {learned.get('approved_ctas', [])}
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
        print(f"[RAW RESPONSE] {response[:300]}")
        return response

    except Exception as e:
        print(f"[ERROR] CMO agent hatasi: {e}")
        return f"CMO agent hatasi: {e}"
