import os
import json
import re

# Ana maden sahasi
MINING_PATH = r"C:\Users\mus-1\OneDrive\Bureaublad\Ai otomasyonu"
REPORT_FILE = "hazine_raporu.md"

# Arama kriterleri (Hazine avcisi bunlara bakar)
KEYWORDS = [
    "wellness", "health", "gezondheid", "beauty", "vitamin", 
    "instagram", "reels", "tiktok", "social", "automation", 
    "agent", "openai", "claude", "api", "n8n", "workflow", "prompt"
]

def score_file(content):
    score = 0
    content_lower = content.lower()
    for kw in KEYWORDS:
        count = content_lower.count(kw)
        score += count * 5
    return score

def find_treasures():
    print(f"🚜 Cevher Avcısı v3 Kazıya Başladı: {MINING_PATH}")
    treasures = []
    
    # Rekursif tarama
    for root, dirs, files in os.walk(MINING_PATH):
        # Gereksiz klasorleri atla
        if any(x in root for x in [".git", "__pycache__", "venv", "node_modules"]):
            continue
            
        for file in files:
            file_path = os.path.join(root, file)
            # Kritik dosya turlerine bak
            if file.endswith((".py", ".json", ".md", ".txt", ".js")):
                try:
                    # Dosya onizlemesi oku
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read(10000) # Ilk 10k karakter yeterli
                        score = score_file(content)
                        
                        if score > 20: # Belirli bir barajin ustundeyse hazinedir
                            treasures.append({
                                "file": file,
                                "path": file_path,
                                "score": score,
                                "preview": content[:200].replace("\n", " ") + "..."
                            })
                except Exception:
                    continue

    # Puanlara gore sirala
    treasures.sort(key=lambda x: x["score"], reverse=True)
    return treasures[:30] # En iyi 30 hazine

def generate_report(treasures):
    print(f"📊 Hazine Raporu Hazırlanıyor: {REPORT_FILE}")
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write("# 🎭 Hazine Raporu: Ai Otomasyon Arşivi Kazısı 💎\n\n")
        f.write(f"Cevher Avcısı tarafından `{MINING_PATH}` dizininde yapılan derin kazı sonuçlarıdır.\n\n")
        f.write("## 🏆 En Değerli Bileşenler (Top 30)\n\n")
        
        for i, t in enumerate(treasures):
            f.write(f"### {i+1}. {t['file']} (Puan: {t['score']})\n")
            f.write(f"- **Konum**: `{t['path']}`\n")
            f.write(f"- **Özet**: {t['preview']}\n\n")
            f.write("---\n\n")
            
    print(f"✅ Rapor Hazır! Toplam {len(treasures)} hazine bulundu.")

if __name__ == "__main__":
    found = find_treasures()
    generate_report(found)
