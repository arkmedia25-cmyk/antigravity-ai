import os
import json
import re

# Categories and Keywords
CATEGORIES = {
    "Wellness": ["wellness", "health", "sağlık", "gezondheid", "yoga", "meditation", "diet", "gezond", "workout", "fitness"],
    "Mindset": ["mindset", "motivation", "motivasyon", "discipline", "success", "başarı", "stres", "energy", "enerji"],
    "SocialMedia": ["instagram", "reels", "tiktok", "telegram", "twitter", "canva", "video", "post", "social", "viral"],
    "AI-Prompts": ["gemini", "openai", "gpt", "anthropic", "llm", "prompt", "script", "scenario", "senaryo", "senaryosu"]
}

def analyze_workflow(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        name = data.get("name", "").lower()
        nodes = data.get("nodes", [])
        
        found_content = []
        found_categories = set()
        
        # Search in name
        for cat, keywords in CATEGORIES.items():
            if any(k in name for k in keywords):
                found_categories.add(cat)
        
        # Search in nodes
        for node in nodes:
            node_type = node.get("type", "")
            node_name = node.get("name", "").lower()
            
            # Extract content from Sticky Notes
            if "stickyNote" in node_type or "stickyNote" in node_name:
                content = node.get("parameters", {}).get("content", "").lower()
                for cat, keywords in CATEGORIES.items():
                    if any(k in content for k in keywords):
                        found_categories.add(cat)
                        if content not in found_content:
                            found_content.append(content[:500]) # Sample
            
            # Extract content from LLM Prompts
            if "chainLlm" in node_type or "llm" in node_name:
                content = node.get("parameters", {}).get("text", "").lower()
                for cat, keywords in CATEGORIES.items():
                    if any(k in content for k in keywords):
                        found_categories.add(cat)
                        if content not in found_content:
                            found_content.append(content[:500]) # Sample

        if found_categories:
            return {
                "file": os.path.basename(file_path),
                "name": data.get("name", "Untitled"),
                "categories": list(found_categories),
                "score": len(found_categories) * 10 + len(found_content) * 5
            }
        return None
    except Exception:
        return None

def process_all(directory):
    gems = []
    print(f"Opening Vault at: {directory}")
    files = [f for f in os.listdir(directory) if f.endswith('.json')]
    total = len(files)
    
    for i, filename in enumerate(files):
        if i % 500 == 0:
            print(f"Scanning... {i}/{total}")
        
        res = analyze_workflow(os.path.join(directory, filename))
        if res:
            gems.append(res)
    
    # Sort by score
    gems.sort(key=lambda x: x["score"], reverse=True)
    
    report = {
        "summary": {
            "total_scanned": total,
            "gems_found": len(gems),
            "by_category": {cat: len([g for g in gems if cat in g["categories"]]) for cat in CATEGORIES}
        },
        "top_gems": gems[:100] # Take TOP 100
    }
    
    with open('gems_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"Report Generated: gems_report.json")
    print(f"Found {len(gems)} potential gems among {total} files.")

if __name__ == "__main__":
    process_all("workflows")
