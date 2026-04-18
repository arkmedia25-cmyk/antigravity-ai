"""
Rebuild the homepage hero slider to match Amare.com reference style:
- Full-width banner
- Left product image panel (~38% width)
- Center text area (~24% width)
- Right product image panel (~38% width)
- Pill outline CTA button
- Matching background colors per slide
"""
import requests
from requests.auth import HTTPBasicAuth
import re
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

AUTH = HTTPBasicAuth('shoppingbest41', 'QmdY FAML WPzu IiK4 jewG lSD7')
BASE = 'https://amarenl.com'

NEW_SLIDER_CSS = """/* ====== HERO SLIDER (Amare.com Reference Style) ====== */
.am-hero-slider {
  position: relative; width: 100%; overflow: hidden; user-select: none;
}
.am-slides-track {
  display: flex; transition: transform 0.6s cubic-bezier(0.4,0,0.2,1); will-change: transform;
}
.am-slide {
  min-width: 100%; display: grid;
  grid-template-columns: 38% 24% 38%;
  align-items: center; min-height: 460px; overflow: hidden;
}
/* Slide 1: Happy Juice Pack — warm peach */
.am-slide-1 { background: #F5EDE4; }
/* Slide 2: Triangle of Wellness Xtreme — deep royal purple */
.am-slide-2 { background: linear-gradient(130deg, #2D1450 0%, #3E2068 100%); }
/* Slide 3: Restore — natural sage/cream */
.am-slide-3 { background: #EEF2E8; }
/* Slide 4: The Rootist — warm peach salmon (ref: Amare × Rootist banner) */
.am-slide-4 { background: linear-gradient(135deg, #F9C5A0 0%, #F5A882 55%, #F9C5A0 100%); }
/* Slide 5: Skin to Mind — soft lavender (ref: Amare Skin to Mind banner) */
.am-slide-5 { background: radial-gradient(ellipse at 18% 50%, rgba(210,170,238,0.55) 0%, transparent 52%), radial-gradient(ellipse at 82% 50%, rgba(200,168,236,0.55) 0%, transparent 52%), linear-gradient(135deg, #EDD5F5 0%, #D5CCF0 100%); }
.am-slide-left, .am-slide-right {
  height: 460px; overflow: hidden;
  display: flex; align-items: center; justify-content: center;
}
.am-slide-left img, .am-slide-right img {
  width: 100%; height: 100%; object-fit: contain; object-position: center;
  transition: transform 0.6s ease;
}
.am-slide:hover .am-slide-left img,
.am-slide:hover .am-slide-right img { transform: scale(1.05); }
.am-slide-center {
  text-align: center; padding: 48px 20px; z-index: 2;
}
.am-slide-badge {
  display: inline-block; font-size: 0.7rem; font-weight: 700;
  letter-spacing: 2.5px; text-transform: uppercase; margin-bottom: 16px; opacity: 0.72;
}
/* Light slides: 1, 3, 4, 5 */
.am-slide-1 .am-slide-badge,.am-slide-3 .am-slide-badge,.am-slide-4 .am-slide-badge,.am-slide-5 .am-slide-badge { color: #522D72; }
/* Dark slides: 2 */
.am-slide-2 .am-slide-badge { color: rgba(255,255,255,0.65); }
.am-slide h2 {
  font-family: 'Playfair Display', serif;
  font-size: clamp(1.5rem, 2.2vw, 2rem); font-weight: 900;
  line-height: 1.2; margin: 0 0 12px;
}
.am-slide-1 h2,.am-slide-3 h2,.am-slide-4 h2,.am-slide-5 h2 { color: #3a1f50; }
.am-slide-2 h2 { color: white; }
.am-slide-desc {
  font-size: 0.9rem; line-height: 1.65; margin-bottom: 28px;
  max-width: 240px; margin-left: auto; margin-right: auto;
}
.am-slide-1 .am-slide-desc,.am-slide-3 .am-slide-desc,.am-slide-4 .am-slide-desc,.am-slide-5 .am-slide-desc { color: #5a4070; }
.am-slide-2 .am-slide-desc { color: rgba(255,255,255,0.8); }
.am-slide-cta {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 11px 30px; border-radius: 50px;
  font-weight: 600; font-size: 0.88rem; text-decoration: none; transition: all 0.2s;
}
.am-slide-1 .am-slide-cta,.am-slide-3 .am-slide-cta,.am-slide-4 .am-slide-cta,.am-slide-5 .am-slide-cta {
  border: 1.5px solid #522D72; color: #522D72; background: transparent;
}
.am-slide-1 .am-slide-cta:hover,.am-slide-3 .am-slide-cta:hover,.am-slide-4 .am-slide-cta:hover,.am-slide-5 .am-slide-cta:hover {
  background: #522D72; color: white;
}
.am-slide-2 .am-slide-cta {
  border: 1.5px solid rgba(255,255,255,0.75); color: white; background: transparent;
}
.am-slide-2 .am-slide-cta:hover { background: rgba(255,255,255,0.15); }
.am-slider-arrow {
  position: absolute; top: 50%; transform: translateY(-50%);
  width: 40px; height: 40px; background: rgba(255,255,255,0.88); border: none;
  border-radius: 50%; font-size: 1.4rem; cursor: pointer; z-index: 10;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 2px 12px rgba(0,0,0,0.12); transition: all 0.2s; color: #522D72;
}
.am-slider-arrow:hover { background: white; box-shadow: 0 4px 20px rgba(0,0,0,0.18); }
.am-slider-arrow.prev { left: 20px; }
.am-slider-arrow.next { right: 20px; }
.am-slider-dots {
  position: absolute; bottom: 16px; left: 50%; transform: translateX(-50%);
  display: flex; gap: 8px; z-index: 10;
}
.am-dot {
  width: 9px; height: 9px; border-radius: 50%;
  border: 1.5px solid rgba(255,255,255,0.6); background: transparent;
  cursor: pointer; transition: all 0.2s; padding: 0;
}
.am-dot.active { background: white; border-color: white; }
@media(max-width: 900px) {
  .am-slide { grid-template-columns: 1fr; min-height: auto; }
  .am-slide-left { display: none; }
  .am-slide-right { height: 220px; }
  .am-slide-center { padding: 32px 20px; order: -1; }
}
@media(max-width: 600px) {
  .am-slide-right { height: 180px; }
  .am-slide h2 { font-size: 1.3rem; }
}"""

NEW_SLIDER_HTML = """<section class="am-hero-slider" id="amHeroSlider">
    <div class="am-slides-track" id="amSlidesTrack">

      <!-- Slide 1: Happy Juice Pack — warm peach bg -->
      <div class="am-slide am-slide-1">
        <div class="am-slide-left">
          <img src="https://amarenl.com/wp-content/uploads/2026/04/Amare-Happy-Juice-Mango-set.jpg" alt="Happy Juice Pack set" loading="eager">
        </div>
        <div class="am-slide-center">
          <span class="am-slide-badge">&#10022; Bestseller Pakket</span>
          <h2>Amare Happy<br>Juice Pack</h2>
          <p class="am-slide-desc">Combineer EDGE+, Energy+ en MentaBiotics voor een complete gut-brain boost</p>
          <a href="https://www.amare.com/2075008/nl-NL/shop/happy-juice/happy-juice-pack" target="_blank" rel="noopener" class="am-slide-cta">Nu winkelen &#8594;</a>
        </div>
        <div class="am-slide-right">
          <img src="https://amarenl.com/wp-content/uploads/2026/04/Amare-Happy-Juice-Pack-Amare-EDGE-Watermelon.jpg" alt="Happy Juice Pack Watermelon" loading="eager">
        </div>
      </div>

      <!-- Slide 2: Triangle of Wellness Xtreme — deep purple bg -->
      <div class="am-slide am-slide-2">
        <div class="am-slide-left">
          <img src="https://amarenl.com/wp-content/uploads/2026/04/Triangle-of-Wellness.jpg" alt="Triangle of Wellness Xtreme">
        </div>
        <div class="am-slide-center">
          <span class="am-slide-badge">&#9650; Complete Wellness</span>
          <h2>Triangle of<br>Wellness Xtreme&#8482;</h2>
          <p class="am-slide-desc">Mentale gezondheid + darmgezondheid + energie in een synergistisch pakket</p>
          <a href="https://www.amare.com/2075008/nl-nl/triangle-of-wellness-xtreme" target="_blank" rel="noopener" class="am-slide-cta">Nu winkelen &#8594;</a>
        </div>
        <div class="am-slide-right">
          <img src="https://amarenl.com/wp-content/uploads/2026/04/Xtreme-Triangle-of-Wellness-Level-Up-Pack.jpg" alt="Triangle of Wellness Xtreme pack">
        </div>
      </div>

      <!-- Slide 3: Restore — natural sage/cream bg -->
      <div class="am-slide am-slide-3">
        <div class="am-slide-left">
          <img src="https://amarenl.com/wp-content/uploads/2026/04/Restore.jpg" alt="Amare Restore">
        </div>
        <div class="am-slide-center">
          <span class="am-slide-badge">&#127807; Darmgezondheid</span>
          <h2>Amare<br>Restore&#8482;</h2>
          <p class="am-slide-desc">Spijsverteringsenzymen, probiotica en botanicals die de darmbarriere herstellen</p>
          <a href="https://www.amare.com/2075008/nl-NL/shop/restore/restore" target="_blank" rel="noopener" class="am-slide-cta">Nu winkelen &#8594;</a>
        </div>
        <div class="am-slide-right">
          <img src="https://amarenl.com/wp-content/uploads/2026/04/Restore-1.jpg" alt="Restore supplement">
        </div>
      </div>

      <!-- Slide 4: The Rootist — warm peach salmon (ref: Amare × Rootist banner) -->
      <div class="am-slide am-slide-4">
        <div class="am-slide-left">
          <img src="https://amarenl.com/wp-content/uploads/2026/04/Collectie-voor-vette-hoofdhuid-en-fijn-haar.jpg" alt="The Rootist Haar Collectie">
        </div>
        <div class="am-slide-center">
          <span class="am-slide-badge">&#9752; Haar &amp; Hoofdhuid</span>
          <h2>The Rootist&#8482;</h2>
          <p class="am-slide-desc">Ontketen het volledige potentieel van je haar met de Amare &#215; The Rootist collectie</p>
          <a href="https://www.amare.com/2075008/nl-NL/shop/the-rootist" target="_blank" rel="noopener" class="am-slide-cta">Nu winkelen &#8594;</a>
        </div>
        <div class="am-slide-right">
          <img src="https://amarenl.com/wp-content/uploads/2026/04/Haarverdikkende-Collectie-voor-Volume.jpg" alt="The Rootist Volume Collectie">
        </div>
      </div>

      <!-- Slide 5: Skin to Mind — soft lavender (ref: Amare Skin to Mind banner) -->
      <div class="am-slide am-slide-5">
        <div class="am-slide-left">
          <img src="https://amarenl.com/wp-content/uploads/2026/04/Skin-to-Mind%E2%84%A2-Collection.jpg" alt="Skin to Mind Collectie">
        </div>
        <div class="am-slide-center">
          <span class="am-slide-badge">&#10024; Huidverzorging</span>
          <h2>Het nieuwe tijdperk<br>van huidverzorging</h2>
          <p class="am-slide-desc">NIEUWE Skin to Mind&#8482; huidverzorging gebaseerd op neurowetenschap</p>
          <a href="https://www.amare.com/2075008/nl-NL/shop/skin-to-mind" target="_blank" rel="noopener" class="am-slide-cta">Nu winkelen &#8594;</a>
        </div>
        <div class="am-slide-right">
          <img src="https://amarenl.com/wp-content/uploads/2026/04/Skin-to-Mind-OptiMIST%E2%84%A2-Awaken-Glow-Facial-Mist.jpg" alt="Skin to Mind OptiMIST Serum">
        </div>
      </div>

    </div><!-- end slides-track -->

    <button class="am-slider-arrow prev" onclick="amMoveSlide(-1)" aria-label="Vorige">&#8249;</button>
    <button class="am-slider-arrow next" onclick="amMoveSlide(1)" aria-label="Volgende">&#8250;</button>

    <div class="am-slider-dots" id="amSliderDots">
      <button class="am-dot active" onclick="amGoSlide(0)"></button>
      <button class="am-dot" onclick="amGoSlide(1)"></button>
      <button class="am-dot" onclick="amGoSlide(2)"></button>
      <button class="am-dot" onclick="amGoSlide(3)"></button>
      <button class="am-dot" onclick="amGoSlide(4)"></button>
    </div>
  </section>"""


def update_homepage():
    print("Fetching homepage...")
    r = requests.get(f'{BASE}/wp-json/wp/v2/pages/36', auth=AUTH, params={'context': 'edit'})
    raw = r.json().get('content', {}).get('raw', '')
    print(f"Page fetched: {len(raw)} chars")

    # Replace slider CSS
    css_start = raw.find('/* ====== HERO SLIDER')
    css_end = raw.find('/* ====== AMARE YOUR WAY', css_start)
    if css_start == -1 or css_end == -1:
        print("ERROR: Could not find slider CSS boundaries")
        return

    new_raw = raw[:css_start] + NEW_SLIDER_CSS + '\n\n' + raw[css_end:]
    print(f"CSS replaced: {css_end - css_start} -> {len(NEW_SLIDER_CSS)} chars")

    # Replace slider HTML
    html_start = new_raw.find('<section class="am-hero-slider"')
    # Find the closing </section> that is followed by AMARE YOUR WAY
    import re as _re
    m = _re.search(r'</section>\s*\n+\s*<!--\s*={4,}\s*AMARE YOUR WAY', new_raw[html_start:])
    if not m:
        print(f"ERROR: Could not find slider HTML end (start:{html_start})")
        return
    html_end = html_start + m.start()

    new_raw = new_raw[:html_start] + NEW_SLIDER_HTML + '\n\n  ' + new_raw[html_end + len('</section>'):]
    print(f"HTML replaced, new total: {len(new_raw)} chars")

    # Fix amTotal JS variable to match actual slide count (6)
    import re as _re2
    new_raw, n = _re2.subn(r'amTotal\s*=\s*\d+', 'amTotal = 5', new_raw, count=1)
    if n:
        print("JS amTotal patched -> 5")
    else:
        print("WARNING: amTotal not found in page, slider JS may be stale")

    # Deploy
    print("Deploying...")
    resp = requests.post(
        f'{BASE}/wp-json/wp/v2/pages/36',
        json={'content': new_raw, 'status': 'publish'},
        auth=AUTH, timeout=60
    )
    if resp.status_code == 200:
        link = resp.json().get('link', '?')
        print(f"OK -> {link}")
    else:
        print(f"ERR {resp.status_code}: {resp.text[:200]}")


if __name__ == '__main__':
    update_homepage()
