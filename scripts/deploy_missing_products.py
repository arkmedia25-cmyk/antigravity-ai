"""
Deploy the 17 SHORT product pages with full embedded CSS template.
These pages had old template (no CSS) - now getting full self-contained design.
"""
import requests
from requests.auth import HTTPBasicAuth
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

AUTH = HTTPBasicAuth('shoppingbest41', 'QmdY FAML WPzu IiK4 jewG lSD7')
BASE = 'https://amarenl.com'

EMBEDDED_CSS = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
.sp-wrap{--purple:#522D72;--purple-dark:#3a1f50;--gold:#f5c048;--cream:#F8F5F1;--text:#2A2A2A;--muted:#666;--border:#e0d7c6;--green:#4CAF50;font-family:'Inter',sans-serif;color:var(--text);overflow-x:hidden}
.sp-wrap *{box-sizing:border-box}
.sp-wrap a{text-decoration:none}
.sp-promo{background:var(--green);color:#fff;text-align:center;padding:9px 16px;font-size:.82rem;font-weight:600}
.sp-breadcrumb{max-width:1200px;margin:0 auto;padding:16px 24px;font-size:.85rem;color:var(--muted)}
.sp-breadcrumb a{color:var(--purple)}
.sp-breadcrumb a:hover{text-decoration:underline}
.sp-container{max-width:1200px;margin:0 auto;padding:40px 24px 80px}
.sp-top{display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:start}
.sp-gallery-wrap{display:flex;flex-direction:column;gap:16px}
.sp-gallery{background:var(--cream);border-radius:20px;display:flex;align-items:center;justify-content:center;height:420px;padding:48px;position:relative}
.sp-gallery img{width:100%;height:100%;object-fit:contain;transition:transform .4s}
.sp-gallery:hover img{transform:scale(1.04)}
.sp-badge{position:absolute;top:20px;left:20px;background:var(--purple);color:#fff;font-size:.68rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;padding:5px 14px;border-radius:50px}
.sp-thumbs{display:flex;gap:10px;overflow-x:auto;padding-bottom:6px}
.sp-thumb{width:76px;height:76px;border-radius:10px;background:var(--cream);cursor:pointer;border:2px solid transparent;padding:4px;object-fit:contain;flex-shrink:0;transition:border-color .2s}
.sp-thumb.active{border-color:var(--purple)}
.sp-info h1{font-family:'Playfair Display',serif;font-size:clamp(1.8rem,3vw,2.6rem);font-weight:900;color:var(--purple-dark);margin:0 0 16px;line-height:1.1}
.sp-desc{font-size:1rem;color:var(--muted);line-height:1.7;margin-bottom:28px}
.sp-stars{color:#d4a017;font-size:1rem;letter-spacing:2px;margin-bottom:6px}
.sp-review-count{font-size:.82rem;color:var(--muted)}
.sp-buybox{background:#fff;border:1px solid var(--border);border-radius:16px;padding:28px;box-shadow:0 8px 24px rgba(0,0,0,.04);margin-bottom:24px}
.sp-option{display:flex;align-items:flex-start;gap:14px;padding:14px;border:1.5px solid transparent;border-radius:10px;cursor:pointer;transition:all .2s;margin-bottom:10px}
.sp-option:last-of-type{margin-bottom:0}
.sp-option.selected{border-color:var(--purple);background:#fcf9ff}
.sp-option:hover{background:#fafafa}
.sp-option input{margin-top:4px;accent-color:var(--purple);transform:scale(1.2);cursor:pointer}
.sp-opt-body{flex:1}
.sp-opt-title{font-size:1rem;font-weight:700;color:var(--text);display:block;margin-bottom:3px}
.sp-opt-price{font-size:1.3rem;font-weight:800;color:var(--purple);display:block}
.sp-opt-tag{font-size:.7rem;color:var(--green);font-weight:700;background:#f0faf0;padding:2px 8px;border-radius:50px;margin-left:6px}
.sp-btn-main{display:block;width:100%;margin-top:20px;padding:18px;border-radius:50px;border:none;background:var(--purple);color:#fff;font-size:1rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px;cursor:pointer;transition:all .2s;text-align:center;text-decoration:none;font-family:'Inter',sans-serif}
.sp-btn-main:hover{background:var(--purple-dark);transform:translateY(-3px);box-shadow:0 12px 28px rgba(82,45,114,.25);color:#fff}
.sp-benefits{padding-top:20px;border-top:1px solid var(--border);margin-top:20px}
.sp-ben{display:flex;align-items:center;gap:10px;font-size:.88rem;color:var(--muted);margin-bottom:10px}
.sp-ben-icon{font-size:1.1rem}
.sp-guarantee{background:#f0faf0;border:1px solid #c3e6cb;border-radius:10px;padding:12px 16px;font-size:.82rem;color:#276228;font-weight:600;margin-top:16px;text-align:center}
.sp-tabs{margin-top:56px;padding-top:56px;border-top:1px solid var(--border)}
.sp-tabs h2{font-family:'Playfair Display',serif;font-size:1.6rem;color:var(--purple);margin:0 0 32px}
.sp-tabs-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:40px}
.sp-tab-block h3{font-family:'Playfair Display',serif;font-size:1.1rem;color:var(--purple);margin:0 0 12px}
.sp-tab-block p{font-size:.9rem;line-height:1.7;color:var(--muted);margin:0}
.sp-why{background:var(--purple);padding:64px 24px}
.sp-why-inner{max-width:1200px;margin:0 auto}
.sp-why-inner h2{font-family:'Playfair Display',serif;font-size:clamp(1.6rem,3vw,2.4rem);color:#fff;margin:0 0 10px}
.sp-why-inner p{color:rgba(255,255,255,.75);margin:0 0 40px}
.sp-why-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:20px}
.sp-why-card{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:24px}
.sp-why-card h3{color:#fff;font-size:.95rem;font-weight:700;margin:0 0 8px}
.sp-why-card p{color:rgba(255,255,255,.72);font-size:.85rem;line-height:1.6;margin:0}
.sp-why-icon{font-size:1.8rem;margin-bottom:10px}
.sp-cta{background:var(--gold);padding:56px 24px;text-align:center}
.sp-cta h2{font-family:'Playfair Display',serif;font-size:clamp(1.6rem,3vw,2.2rem);color:var(--purple-dark);margin:0 0 12px}
.sp-cta p{color:var(--purple-dark);opacity:.8;margin:0 auto 28px;max-width:500px}
.sp-cta-btn{display:inline-block;background:var(--purple);color:#fff;padding:16px 44px;border-radius:50px;font-weight:700;font-size:1rem;text-decoration:none;transition:all .25s}
.sp-cta-btn:hover{background:var(--purple-dark);transform:translateY(-2px);color:#fff}
.sp-float-wa{position:fixed;bottom:28px;right:28px;z-index:300;background:#25D366;color:#fff;width:54px;height:54px;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 8px 24px rgba(37,211,102,.4);text-decoration:none;transition:all .3s}
.sp-float-wa:hover{transform:scale(1.1)}
@media(max-width:900px){.sp-top{grid-template-columns:1fr;gap:32px}.sp-gallery{height:320px}.sp-tabs-grid{grid-template-columns:1fr;gap:28px}}
@media(max-width:600px){.sp-gallery{height:260px;padding:24px}}
</style>"""


def build_page(name, img, price_sub, price_once, affiliate, cat_name, cat_url, badge='', desc='', tabs=None):
    if tabs is None:
        tabs = [
            ('Waarom kiezen?', f'{name} is zorgvuldig samengesteld voor optimale resultaten bij dagelijks gebruik.'),
            ('Wat is het?', f'Premium Amare product uit de {cat_name} lijn voor dagelijks gebruik en maximale effectiviteit.'),
            ('Hoe werkt het?', 'Werkzame stoffen ondersteunen uw lichaam op cellulair niveau voor duurzame, meetbare resultaten.'),
        ]
    badge_html = f'<div class="sp-badge">{badge}</div>' if badge else ''
    tab_cols = ''.join(f'<div class="sp-tab-block"><h3>{t[0]}</h3><p>{t[1]}</p></div>' for t in tabs)
    wa_name = name.replace(' ', '%20')
    return f"""{EMBEDDED_CSS}
<div class="sp-wrap">
  <div class="sp-promo">Gratis verzending vanaf &euro;75 &nbsp;|&nbsp; 30 dagen geld-terug-garantie &nbsp;|&nbsp; 100% Natuurlijk</div>
  <div class="sp-breadcrumb"><a href="/">&#8592; Home</a> &nbsp;/&nbsp; <a href="{cat_url}">{cat_name}</a> &nbsp;/&nbsp; <span>{name}</span></div>
  <div class="sp-container">
    <div class="sp-top">
      <div class="sp-gallery-wrap">
        <div class="sp-gallery">
          {badge_html}
          <img id="sp-main-img" src="{img}" alt="{name}">
        </div>
      </div>
      <div class="sp-info">
        <div class="sp-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
        <div class="sp-review-count">4.8/5 &ndash; gebaseerd op klantbeoordelingen</div>
        <h1>{name}</h1>
        <p class="sp-desc">{desc if desc else 'Ontworpen om uw algehele welzijn te ondersteunen met wetenschappelijk onderbouwde ingredienten.'}</p>
        <div class="sp-buybox">
          <label class="sp-option selected" id="opt-sub" onclick="spToggle('opt-sub')">
            <input type="radio" name="sp_price" checked>
            <div class="sp-opt-body">
              <span class="sp-opt-title">Subscribe &amp; Save <span class="sp-opt-tag">BESTE WAARDE</span></span>
              <span class="sp-opt-price">{price_sub}</span>
            </div>
          </label>
          <label class="sp-option" id="opt-once" onclick="spToggle('opt-once')">
            <input type="radio" name="sp_price">
            <div class="sp-opt-body">
              <span class="sp-opt-title">Eenmalige aankoop</span>
              <span class="sp-opt-price">{price_once}</span>
            </div>
          </label>
          <a href="{affiliate}" target="_blank" rel="noopener" class="sp-btn-main">&#43; KOOP NU OP AMARE.COM</a>
        </div>
        <div class="sp-benefits">
          <div class="sp-ben"><span class="sp-ben-icon">&#127807;</span> 100% Natuurlijke Formule</div>
          <div class="sp-ben"><span class="sp-ben-icon">&#128300;</span> Wetenschappelijk onderbouwd</div>
          <div class="sp-ben"><span class="sp-ben-icon">&#127381;</span> GMP-gecertificeerde productie</div>
          <div class="sp-ben"><span class="sp-ben-icon">&#128274;</span> Veilig &amp; getest op zuiverheid</div>
        </div>
        <div class="sp-guarantee">&#128737;&#65039; 30 Dagen Geld-Terug-Garantie &mdash; ook op lege verpakkingen!</div>
      </div>
    </div>
    <div class="sp-tabs">
      <h2>Alles wat je wilt weten</h2>
      <div class="sp-tabs-grid">{tab_cols}</div>
    </div>
  </div>
  <div class="sp-why">
    <div class="sp-why-inner">
      <h2>Waarom Amare?</h2>
      <p>Wetenschappelijk onderbouwde supplementen voor de gut-brain axis.</p>
      <div class="sp-why-grid">
        <div class="sp-why-card"><div class="sp-why-icon">&#127807;</div><h3>100% Natuurlijk</h3><p>Geen kunstmatige toevoegingen. Alleen klinisch geteste ingredienten.</p></div>
        <div class="sp-why-card"><div class="sp-why-icon">&#128300;</div><h3>Klinisch Onderbouwd</h3><p>Gebaseerd op gepubliceerde wetenschappelijke studies.</p></div>
        <div class="sp-why-card"><div class="sp-why-icon">&#128737;&#65039;</div><h3>30 Dagen Garantie</h3><p>Niet tevreden? Geld terug &mdash; ook op lege verpakkingen.</p></div>
        <div class="sp-why-card"><div class="sp-why-icon">&#9889;</div><h3>Voelbaar Verschil</h3><p>Klanten rapporteren verbeteringen binnen 2&ndash;4 weken.</p></div>
      </div>
    </div>
  </div>
  <div class="sp-cta">
    <h2>Klaar om te bestellen?</h2>
    <p>Koop direct via de officiele Amare webshop met onze affiliate link. Zelfde product, zelfde garantie.</p>
    <a href="{affiliate}" target="_blank" rel="noopener" class="sp-cta-btn">Koop Nu op Amare.com &#8594;</a>
  </div>
</div>
<a href="https://wa.me/31638732951?text=Hallo!%20Ik%20heb%20een%20vraag%20over%20{wa_name}." class="sp-float-wa" target="_blank" rel="noopener" title="WhatsApp">
  <svg width="26" height="26" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
</a>
<script>
function spToggle(id){{document.querySelectorAll('.sp-option').forEach(function(el){{el.classList.remove('selected');}});document.getElementById(id).classList.add('selected');}}
function spChangeImg(el){{document.getElementById('sp-main-img').src=el.src;document.querySelectorAll('.sp-thumb').forEach(function(t){{t.classList.remove('active');}});el.classList.add('active');}}
</script>"""


PRODUCTS = [
    {'wp_id': 17, 'name': 'Verdichten Geconcentreerde Conditioner', 'badge': '',
     'cat_name': 'Haarverzorging', 'cat_url': '/haarverzorging/',
     'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Densify_Concentrated_Conditioner_BE_800.jpg',
     'price_sub': '&#8364; 28,81', 'price_once': '&#8364; 32,99',
     'affiliate': 'https://www.amare.com/2075008/nl-nl/densify-concentrated-conditioner',
     'desc': 'Geconcentreerde conditioner die het haar verdicht en volume geeft. Ideaal voor fijn en dun haar voor zichtbaar dikker haar na elke wasbeurt.',
     'tabs': [('Waarom kiezen?', 'Speciaal voor fijn haar dat meer volume en dichtheid nodig heeft. Zichtbaar resultaat vanaf de eerste wasbeurt voor voller, dichter haar.'),
              ('Wat is het?', 'Geconcentreerde formule met volume-boosting actieve stoffen voor fijn, dun haar dat meer body en dichtheid nodig heeft.'),
              ('Hoe werkt het?', 'Actieve stoffen dringen in de haarschacht voor structurele versterking en volumeverhoging voor denser, voller haar bij elke wasbeurt.')]},
    {'wp_id': 28, 'name': 'Clarify Droogshampoo Poeder', 'badge': '',
     'cat_name': 'Haarverzorging', 'cat_url': '/haarverzorging/',
     'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Clarify_Dry_Shampoo_Powder_CZ_800.jpg',
     'price_sub': '&#8364; 29,85', 'price_once': '&#8364; 34,02',
     'affiliate': 'https://www.amare.com/2075008/nl-nl/clarify-dry-shampoo-powder',
     'desc': 'Droogshampoo in poedervorm die vet haar absorbeert en volume toevoegt. Frisse, schone look zonder water voor drukke momenten.',
     'tabs': [('Waarom kiezen?', 'Perfect voor drukke momenten wanneer je geen tijd hebt om je haar te wassen maar er toch vers en verzorgd wilt uitzien.'),
              ('Wat is het?', 'Droogshampoo poeder dat talg absorbeert en volume toevoegt voor fris, schoon haar zonder wassen.'),
              ('Hoe werkt het?', 'Absorbeert overtollig talg terwijl volume-boosters het haar direct optillen voor een frisse look binnen minuten.')]},
    {'wp_id': 32, 'name': 'Amare ON 4-Pack', 'badge': 'Voordeel',
     'cat_name': 'Energie & Focus', 'cat_url': '/energie-focus/',
     'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/ON-Raspberry-Grapefruit-4pk-EU-800.jpg',
     'price_sub': '&#8364; 98,37', 'price_once': '&#8364; 109,31',
     'affiliate': 'https://www.amare.com/2075008/nl-nl/onshots-4pack',
     'desc': 'Vier dozen ON Shots voor vier maanden dagelijkse vitaliteit. Het beste voordeel voor wie structureel wil profiteren van de voordelen van ON.',
     'tabs': [('Waarom kiezen?', 'Voordelig vier-pack voor consistente dagelijkse energie en focus over vier maanden. Bespaar meer, profiteer maximaal van Amare ON.'),
              ('Wat is het?', 'Vier dozen geconcentreerde raspberry-grapefruit shots vol vitamine B-complex en natuurlijke energizers voor dagelijks gebruik.'),
              ('Hoe werkt het?', 'Dagelijkse inname bouwt een stabiele energiebasis op voor aanhoudende vitaliteit en focus gedurende de hele dag.')]},
    {'wp_id': 34, 'name': 'Amare Nitro Xtreme 56ml 2-Pack', 'badge': 'Voordeel',
     'cat_name': 'Energie & Focus', 'cat_url': '/energie-focus/',
     'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Nitro-Xtreme-56ml-2pk-EU-800.jpg',
     'price_sub': '&#8364; 100,66', 'price_once': '&#8364; 111,84',
     'affiliate': 'https://www.amare.com/2075008/nl-nl/nitro-xtreme-56ml-2pack',
     'desc': 'Dubbele voorraad Nitro Xtreme voor twee maanden optimale doorbloeding en vitaliteit. Voordelig pakket voor serieuze health enthousiastelingen.',
     'tabs': [('Waarom kiezen?', 'Twee-pack voor consistente nitric oxide ondersteuning. Ideaal voor sportieve mensen die dagelijks maximale prestaties willen leveren.'),
              ('Wat is het?', 'Twee dozen 56ml Nitro Xtreme flesjes met krachtige nitric oxide precursors voor maximale vasculaire ondersteuning.'),
              ('Hoe werkt het?', 'Stimuleert aanmaak van stikstofmonoxide voor verbeterde vasculaire functie, betere zuurstoftoevoer en meer vitaliteit.')]},
    {'wp_id': 35, 'name': 'Triangle of Wellness Level Up Pack', 'badge': 'Premium',
     'cat_name': 'Darmgezondheid', 'cat_url': '/darmgezondheid/',
     'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Triangle-of-Wellness-Xtreme-Level-Up-HL5-EU-800.jpg',
     'price_sub': '&#8364; 176,20', 'price_once': '&#8364; 195,77',
     'affiliate': 'https://www.amare.com/2075008/nl-nl/triangle-of-wellness-levelup-pack',
     'desc': 'Het ultieme Level Up pakket: Triangle of Wellness Xtreme verrijkt met HL5 Peach Collagen. Complete mind-body-skin oplossing in een premium pakket.',
     'tabs': [('Waarom kiezen?', 'Complete holistische oplossing die gut-brain axis, energie en huidgezondheid tegelijk optimaliseert. Het beste van Amare in een pakket.'),
              ('Wat is het?', 'Triangle of Wellness Xtreme plus HL5 Peach Collagen voor complete mind, body en skin ondersteuning op wetenschappelijk niveau.'),
              ('Hoe werkt het?', 'Synergie van nootropics, probiotica, energie en collageen biedt een complete aanpak voor algeheel welzijn.')]},
    {'wp_id': 39, 'name': 'Versterken Geconcentreerde Shampoo', 'badge': '',
     'cat_name': 'Haarverzorging', 'cat_url': '/haarverzorging/',
     'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Strengthen_Concentrated_Shampoo_BE_800.jpg',
     'price_sub': '&#8364; 27,78', 'price_once': '&#8364; 30,93',
     'affiliate': 'https://www.amare.com/2075008/nl-nl/strengthen-concentrated-shampoo',
     'desc': 'Versterkende geconcentreerde shampoo voor beschadigd en breekbaar haar. Herstelt haarstructuur voor merkbaar sterker, gezonder haar na elke wasbeurt.',
     'tabs': [('Waarom kiezen?', 'Beschadigd haar heeft specifieke versterking nodig. Deze shampoo levert die versterking op cellulair niveau voor echte, meetbare resultaten.'),
              ('Wat is het?', 'Geconcentreerde versterkende shampoo met proteinen en botanicals voor diep herstel van beschadigd, breekbaar haar.'),
              ('Hoe werkt het?', 'Proteinen vullen gaten in de haarschacht op terwijl botanicals de haarwortel versterken voor structureel gezonder haar.')]},
    {'wp_id': 783, 'name': 'Collectie voor Vette Hoofdhuid en Fijn Haar', 'badge': '',
     'cat_name': 'Haarverzorging', 'cat_url': '/haarverzorging/',
     'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Collection_For_Oily_Scalp_and_Fine_Hair_EU_800x800.jpg',
     'price_sub': '&#8364; 151,55', 'price_once': '&#8364; 171,40',
     'affiliate': 'https://www.amare.com/2075008/nl-nl/collection-oily-scalp-fine-hair',
     'desc': 'Complete collectie speciaal voor vette hoofdhuid en fijn haar. Reguleert talgproductie en geeft volume voor fris, vol haar elke dag.',
     'tabs': [('Waarom kiezen?', 'Een gecombineerd probleem als vette hoofdhuid met fijn haar heeft een specifieke aanpak nodig. Deze collectie biedt de complete oplossing.'),
              ('Wat is het?', 'Complete haarverzorgingslijn met talg-regulerende en volume-boosting producten voor vette hoofdhuid en fijn haar.'),
              ('Hoe werkt het?', 'Talg-regulerende ingredienten balanceren de hoofdhuid terwijl volume-boosters het haar optillen voor dagelijks frisse, volle look.')]},
    {'wp_id': 787, 'name': 'Geconcentreerde Conditioner Versterken', 'badge': '',
     'cat_name': 'Haarverzorging', 'cat_url': '/haarverzorging/',
     'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Strengthen_Concentrated_Conditioner_BE_800.jpg',
     'price_sub': '&#8364; 28,81', 'price_once': '&#8364; 32,99',
     'affiliate': 'https://www.amare.com/2075008/nl-nl/strengthen-concentrated-conditioner',
     'desc': 'Versterkende geconcentreerde conditioner voor diepe voeding en herstel van beschadigd haar. Merkbaar soepeler en sterker haar na eerste gebruik.',
     'tabs': [('Waarom kiezen?', 'Complement aan de versterkende shampoo voor een compleet herstelritueel dat beschadigd haar van wortel tot punt herstelt.'),
              ('Wat is het?', 'Geconcentreerde conditioner met proteinen en ceramiden voor intensieve voeding en versterking van breekbaar haar.'),
              ('Hoe werkt het?', 'Ceramiden sluiten de haarschubben en proteinen vullen beschadigingen op voor soepeler, sterker en glanzender haar.')]},
    {'wp_id': 791, 'name': 'Happy Lifestyle Pack Basic', 'badge': 'Starter',
     'cat_name': 'Darmgezondheid', 'cat_url': '/darmgezondheid/',
     'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Happy-Lifestyle-Pack-Basic-EU-new-800.jpg',
     'price_sub': '&#8364; 277,68', 'price_once': '&#8364; 308,59',
     'affiliate': 'https://www.amare.com/2075008/nl-nl/happy-lifestyle-pack-basic',
     'desc': 'Het instappakket voor de Amare Happy Lifestyle. Alles wat je nodig hebt om te beginnen met de gut-brain wellness journey van Amare.',
     'tabs': [('Waarom kiezen?', 'Ideaal startpakket voor iedereen die begint met Amare. Bevat de kernproducten voor complete gut-brain ondersteuning in een pakket.'),
              ('Wat is het?', 'Complete starter collectie met Amare kernproducten voor de gut-brain axis, energie en algeheel welzijn.'),
              ('Hoe werkt het?', 'Synergie van de basisproducten optimaliseert de gut-brain communicatie voor meetbaar beter welzijn binnen 30 dagen.')]},
    {'wp_id': 793, 'name': 'Happy Lifestyle Pack Pro', 'badge': 'Pro',
     'cat_name': 'Darmgezondheid', 'cat_url': '/darmgezondheid/',
     'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Happy-Lifestyle-Pack-Pro-EU-new-800.jpg',
     'price_sub': '&#8364; 649,64', 'price_once': '&#8364; 721,83',
     'affiliate': 'https://www.amare.com/2075008/nl-nl/happy-lifestyle-pack-pro',
     'desc': 'Het complete Pro pakket voor serieuze Amare enthousiastelingen. Maximale ondersteuning voor de gut-brain axis met alle premium producten.',
     'tabs': [('Waarom kiezen?', 'Voor wie maximale resultaten wil. Het Pro pakket biedt de meest complete Amare wellness ervaring voor optimaal welzijn.'),
              ('Wat is het?', 'Uitgebreid pakket met alle premium Amare producten voor complete gut-brain, energie en skin wellness ondersteuning.'),
              ('Hoe werkt het?', 'Volledige synergie van alle Amare systemen voor maximale optimalisatie van gut-brain communicatie, energie en vitaliteit.')]},
    {'wp_id': 810, 'name': 'Triangle Marketing Pack', 'badge': 'Business',
     'cat_name': 'Darmgezondheid', 'cat_url': '/darmgezondheid/',
     'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/500QV-MarketingPack-EU-new-800.jpg',
     'price_sub': '&#8364; 511,21', 'price_once': '&#8364; 568,03',
     'affiliate': 'https://www.amare.com/2075008/nl-nl/triangle-marketing-pack',
     'desc': 'Het Triangle Marketing Pack combineert Amare topproducten voor zowel persoonlijk gebruik als het starten van je eigen Amare wellness business.',
     'tabs': [('Waarom kiezen?', 'Perfect voor Amare Brand Partners die willen starten met een sterk productportfolio voor demos en persoonlijk gebruik.'),
              ('Wat is het?', 'Combinatiepakket van Triangle of Wellness Xtreme producten ideaal voor persoonlijk gebruik en zakelijke demonstraties.'),
              ('Hoe werkt het?', 'Start je eigen Amare wellness business terwijl je zelf profiteert van de krachtige gut-brain ondersteuning van de producten.')]},
    {'wp_id': 812, 'name': 'Triangle of Wellness Xtreme 2-Pack', 'badge': 'Voordeel',
     'cat_name': 'Darmgezondheid', 'cat_url': '/darmgezondheid/',
     'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Triangle-of-Wellness-Xtreme2-EU-800_25_x2.jpg',
     'price_sub': '&#8364; 205,96', 'price_once': '&#8364; 237,99',
     'affiliate': 'https://www.amare.com/2075008/nl-nl/triangle-of-wellness-xtreme-2pack',
     'desc': 'Twee maanden complete gut-brain wellness met het Triangle of Wellness Xtreme 2-Pack. Voordelig pakket voor consistent welzijn.',
     'tabs': [('Waarom kiezen?', 'Twee maanden consistent gebruik van Triangle of Wellness Xtreme voor maximale, duurzame resultaten op gut-brain niveau.'),
              ('Wat is het?', 'Twee dozen Triangle of Wellness Xtreme voor twee maanden onafgebroken gut-brain ondersteuning en welzijn.'),
              ('Hoe werkt het?', 'Consistente dagelijkse inname bouwt een sterk fundament voor structureel betere gut-brain communicatie en algeheel welzijn.')]},
    {'wp_id': 814, 'name': 'Triangle of Wellness Xtreme 3-Pack', 'badge': 'Beste Waarde',
     'cat_name': 'Darmgezondheid', 'cat_url': '/darmgezondheid/',
     'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Triangle-of-Wellness-Xtreme2-EU-800_25_x3.jpg',
     'price_sub': '&#8364; 320,41', 'price_once': '&#8364; 373,80',
     'affiliate': 'https://www.amare.com/2075008/nl-nl/triangle-of-wellness-xtreme-3pack',
     'desc': 'Drie maanden complete wellness met het meest voordelige Triangle of Wellness Xtreme pakket. Maximale besparing, maximale resultaten.',
     'tabs': [('Waarom kiezen?', 'Drie maanden aaneengesloten gebruik is het minimum voor structurele verandering. Dit pakket biedt de beste prijs-kwaliteitverhouding.'),
              ('Wat is het?', 'Drie dozen Triangle of Wellness Xtreme voor drie maanden complete gut-brain axis ondersteuning en gezondheidsverbetering.'),
              ('Hoe werkt het?', 'Langdurige consistente inname optimaliseert het darmmicrobioom structureel voor blijvend betere mentale en fysieke gezondheid.')]},
    {'wp_id': 816, 'name': 'Triangle of Wellness Xtreme 6-Pack', 'badge': 'Maximale Besparing',
     'cat_name': 'Darmgezondheid', 'cat_url': '/darmgezondheid/',
     'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Triangle-of-Wellness-Xtreme2-EU-800_25_x6.jpg',
     'price_sub': '&#8364; 613,40', 'price_once': '&#8364; 715,63',
     'affiliate': 'https://www.amare.com/2075008/nl-nl/triangle-of-wellness-xtreme-6pack',
     'desc': 'Zes maanden complete gut-brain wellness. Het ultieme voordeel pakket voor serieuze Amare gebruikers die maximale resultaten willen.',
     'tabs': [('Waarom kiezen?', 'Zes maanden is de gouden standaard voor diepe microbioom transformatie. Dit pakket biedt maximale besparing voor dedicated gebruikers.'),
              ('Wat is het?', 'Zes dozen Triangle of Wellness Xtreme voor een half jaar onafgebroken gut-brain axis optimalisatie.'),
              ('Hoe werkt het?', 'Zes maanden consistente inname transformeert het darmmicrobioom fundamenteel voor duurzame positieve verandering op alle niveaus.')]},
    {'wp_id': 818, 'name': 'Triangle of Wellness Xtreme', 'badge': 'Populair',
     'cat_name': 'Darmgezondheid', 'cat_url': '/darmgezondheid/',
     'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Triangle-of-Wellness-Xtreme2-EU-800_25.jpg',
     'price_sub': '&#8364; 123,55', 'price_once': '&#8364; 137,27',
     'affiliate': 'https://www.amare.com/2075008/nl-nl/triangle-of-wellness-xtreme',
     'desc': 'De ultieme combinatie: mentale gezondheid + darmgezondheid + energie in een synergistisch pakket. Alles wat je lichaam nodig heeft voor compleet welzijn.',
     'tabs': [('Waarom kiezen?', 'Complete holistische gezondheidsoplossing die alle systemen in je lichaam in balans brengt voor maximaal welzijn in een pakket.'),
              ('Wat is het?', 'Bestaat uit MentaBiotics, Energy+ en EDGE nootropics voor optimale gut-brain communicatie op alle niveaus.'),
              ('Hoe werkt het?', 'Door de krachten van drie producten te bundelen ontstaat een extreem krachtige synergie voor compleet welzijn en vitaliteit.')]},
    {'wp_id': 822, 'name': 'Verdichten Geconcentreerde Shampoo', 'badge': '',
     'cat_name': 'Haarverzorging', 'cat_url': '/haarverzorging/',
     'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Densify_Concentrated_Shampoo_BE_800.jpg',
     'price_sub': '&#8364; 27,78', 'price_once': '&#8364; 30,93',
     'affiliate': 'https://www.amare.com/2075008/nl-nl/densify-concentrated-shampoo',
     'desc': 'Verdichtende geconcentreerde shampoo die het haar van binnenuit dikt. Zichtbaar voller haar met meer body en volume na elke wasbeurt.',
     'tabs': [('Waarom kiezen?', 'Fijn haar dat meer volume nodig heeft profiteert direct van de verdichtende formule. Zichtbaar verschil al bij de eerste wasbeurt.'),
              ('Wat is het?', 'Geconcentreerde verdichtende shampoo met volume-boosting peptiden voor fijn haar dat meer massa en body nodig heeft.'),
              ('Hoe werkt het?', 'Verdichtende polymeren coaten elk haartje voor meer dikte terwijl volumizers de wortels optillen voor merkbaar voller haar.')]},
    {'wp_id': 824, 'name': 'Verdikkend Serum voor Fijn Haar', 'badge': '',
     'cat_name': 'Haarverzorging', 'cat_url': '/haarverzorging/',
     'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Densifying_Serum_BE_800.jpg',
     'price_sub': '&#8364; 53,56', 'price_once': '&#8364; 59,80',
     'affiliate': 'https://www.amare.com/2075008/nl-nl/densifying-serum-thinning-hair',
     'desc': 'Geavanceerd verdikkend serum dat haarfollikels stimuleert en elk haartje dikker maakt. Behandeling voor fijn haar voor zichtbaar denser resultaat.',
     'tabs': [('Waarom kiezen?', 'Serum werkt dieper in de haarfollikel dan gewone verzorgingsproducten voor structureel dikkere, densere haren bij dagelijks gebruik.'),
              ('Wat is het?', 'Geavanceerd serum met haarverdikkende actieve stoffen voor direct zichtbare verbetering van haardichtheid en volume.'),
              ('Hoe werkt het?', 'Verdikkende actieve stoffen stimuleren haarfollikels en zwellen elk haartje van binnenuit op voor merkbaar denser haar.')]},
]


def deploy_all():
    for p in PRODUCTS:
        html = build_page(
            name=p['name'], img=p['img'],
            price_sub=p['price_sub'], price_once=p['price_once'],
            affiliate=p['affiliate'],
            cat_name=p['cat_name'], cat_url=p['cat_url'],
            badge=p.get('badge', ''), desc=p.get('desc', ''),
            tabs=p.get('tabs')
        )
        wp_content = f'<!-- wp:html -->\n{html}\n<!-- /wp:html -->'
        resp = requests.post(
            f'{BASE}/wp-json/wp/v2/pages/{p["wp_id"]}',
            json={'title': p['name'], 'content': wp_content, 'status': 'publish'},
            auth=AUTH, timeout=30
        )
        status = 'OK ' if resp.status_code == 200 else f'ERR {resp.status_code}'
        link = resp.json().get('link', '?') if resp.ok else ''
        print(f'{status} ID:{p["wp_id"]:4d} {p["name"][:45]:45s} {link}')


if __name__ == '__main__':
    deploy_all()
