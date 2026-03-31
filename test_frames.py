import sys, os
sys.path.append(os.path.join(os.getcwd(), "src"))

from skills.video_skill import THEMES, _build_hook, _build_sentence_frame, _build_cta

theme = THEMES["glow"]

# Realistic test sentences (as AI would generate them)
test_sentences = [
    "Wist jij dat een glas water voor het ontbijt je stofwisseling met 30% kan verhogen?",
    "Drie minuten bewegen na elke maaltijd helpt je bloedsuiker stabiel te houden.",
    "Slaap voor middernacht is twee keer zo herstellend voor je hormonen dan erna.",
]

print("Generating Hook...")
h = _build_hook(theme)
print(h)

print("Generating sentence frames...")
for i, s in enumerate(test_sentences):
    p = _build_sentence_frame(s, theme, i)
    print(p)

print("Generating CTA...")
c = _build_cta(theme)
print(c)
