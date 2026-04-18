"""
Deploy all product pages to WordPress with embedded CSS.
Bridge page flow: Category page → Product page (trust) → Affiliate link (sale)
"""
import requests
from requests.auth import HTTPBasicAuth

AUTH = HTTPBasicAuth('shoppingbest41', 'QmdY FAML WPzu IiK4 jewG lSD7')
BASE = 'https://amarenl.com'

EMBEDDED_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
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
</style>
"""


def build_product_page(p):
    badge_html = f'<div class="sp-badge">{p["badge"]}</div>' if p.get("badge") else ""
    thumbs_html = ""
    for i, t in enumerate(p.get("thumbs", [])):
        active = "active" if i == 0 else ""
        thumbs_html += f'<img class="sp-thumb {active}" src="{t}" alt="Thumb {i+1}" onclick="spChangeImg(this)">'
    thumbs_block = f'<div class="sp-thumbs">{thumbs_html}</div>' if thumbs_html else ""

    why_cards = ""
    for w in p.get("why_cards", []):
        why_cards += f'<div class="sp-why-card"><div class="sp-why-icon">{w[0]}</div><h3>{w[1]}</h3><p>{w[2]}</p></div>'

    tab_cols = ""
    for t in p.get("tabs", []):
        tab_cols += f'<div class="sp-tab-block"><h3>{t[0]}</h3><p>{t[1]}</p></div>'

    return f"""{EMBEDDED_CSS}
<div class="sp-wrap">

  <div class="sp-promo">Gratis verzending vanaf €75 &nbsp;|&nbsp; 30 dagen geld-terug-garantie &nbsp;|&nbsp; 100% Natuurlijk</div>

  <div class="sp-breadcrumb">
    <a href="/">&#8592; Home</a> &nbsp;/&nbsp;
    <a href="{p['cat_url']}">{p['cat_name']}</a> &nbsp;/&nbsp;
    <span>{p['name']}</span>
  </div>

  <div class="sp-container">
    <div class="sp-top">

      <!-- IMAGE -->
      <div class="sp-gallery-wrap">
        <div class="sp-gallery">
          {badge_html}
          <img id="sp-main-img" src="{p['img']}" alt="{p['name']}">
        </div>
        {thumbs_block}
      </div>

      <!-- INFO -->
      <div class="sp-info">
        <div class="sp-stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
        <div class="sp-review-count">4.8/5 &ndash; gebaseerd op klantbeoordelingen</div>
        <h1>{p['name']}</h1>
        <p class="sp-desc">{p['desc']}</p>

        <div class="sp-buybox">
          <label class="sp-option selected" id="opt-sub" onclick="spToggle('opt-sub')">
            <input type="radio" name="sp_price" checked>
            <div class="sp-opt-body">
              <span class="sp-opt-title">Subscribe &amp; Save <span class="sp-opt-tag">BESTE WAARDE</span></span>
              <span class="sp-opt-price">{p['price_sub']}</span>
            </div>
          </label>
          <label class="sp-option" id="opt-once" onclick="spToggle('opt-once')">
            <input type="radio" name="sp_price">
            <div class="sp-opt-body">
              <span class="sp-opt-title">Eenmalige aankoop</span>
              <span class="sp-opt-price">{p['price_once']}</span>
            </div>
          </label>
          <a href="{p['affiliate']}" target="_blank" rel="noopener" class="sp-btn-main" id="sp-buy-btn">
            &#43; KOOP NU OP AMARE.COM
          </a>
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

    <!-- DETAIL TABS -->
    <div class="sp-tabs">
      <h2>Alles wat je wilt weten</h2>
      <div class="sp-tabs-grid">
        {tab_cols}
      </div>
    </div>
  </div>

  <!-- WHY AMARE -->
  <div class="sp-why">
    <div class="sp-why-inner">
      <h2>Waarom Amare?</h2>
      <p>Wetenschappelijk onderbouwde supplementen voor de gut-brain axis.</p>
      <div class="sp-why-grid">
        {why_cards}
        <div class="sp-why-card"><div class="sp-why-icon">&#127807;</div><h3>100% Natuurlijk</h3><p>Geen kunstmatige toevoegingen. Alleen klinisch geteste ingrediënten.</p></div>
        <div class="sp-why-card"><div class="sp-why-icon">&#128300;</div><h3>Klinisch Onderbouwd</h3><p>Gebaseerd op gepubliceerde wetenschappelijke studies.</p></div>
        <div class="sp-why-card"><div class="sp-why-icon">&#128737;&#65039;</div><h3>30 Dagen Garantie</h3><p>Niet tevreden? Geld terug — ook op lege verpakkingen.</p></div>
        <div class="sp-why-card"><div class="sp-why-icon">&#9889;</div><h3>Voelbaar Verschil</h3><p>Klanten rapporteren verbeteringen binnen 2–4 weken.</p></div>
      </div>
    </div>
  </div>

  <!-- CTA -->
  <div class="sp-cta">
    <h2>Klaar om te bestellen?</h2>
    <p>Koop direct via de officiële Amare webshop met onze affiliate link. Zelfde product, zelfde garantie.</p>
    <a href="{p['affiliate']}" target="_blank" rel="noopener" class="sp-cta-btn">Koop Nu op Amare.com &#8594;</a>
  </div>

</div>

<!-- WhatsApp -->
<a href="https://wa.me/31638732951?text=Hallo!%20Ik%20heb%20een%20vraag%20over%20{p['name'].replace(' ', '%20')}." class="sp-float-wa" target="_blank" rel="noopener" title="WhatsApp">
  <svg width="26" height="26" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
</a>

<script>
function spToggle(id) {{
  document.querySelectorAll('.sp-option').forEach(function(el) {{ el.classList.remove('selected'); }});
  document.getElementById(id).classList.add('selected');
}}
function spChangeImg(el) {{
  document.getElementById('sp-main-img').src = el.src;
  document.querySelectorAll('.sp-thumb').forEach(function(t) {{ t.classList.remove('active'); }});
  el.classList.add('active');
}}
</script>
"""


PRODUCTS = [
    {
        'wp_id': 22, 'name': 'Restore', 'badge': 'Populair',
        'cat_name': 'Darmgezondheid', 'cat_url': '/darmgezondheid/',
        'img': 'https://amarenl.com/cdn/shop/files/Amare-Restore-EU-800.jpg',
        'thumbs': ['https://amarenl.com/cdn/shop/files/Amare-Restore-EU-800.jpg'],
        'desc': 'Restore is zorgvuldig samengesteld met vijf belangrijke enzymen, botanische extracten en 2 miljard levende bacterieculturen voor je algehele welzijn. Een unieke combinatie voor gezonde darmfunctie en optimaal welzijn.',
        'price_sub': '€ 29,70', 'price_once': '€ 33,01',
        'affiliate': 'https://www.amare.com/2075008/nl-NL/shop/restore/restore',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'Restore onderscheidt zich met een mix van 9 botanische middelen: jeneverbespoeder, paardenbloemwortelpoeder, venkelzaadpoeder en meer. Jouw darmen zullen het voelen.'),
            ('Wat het is', 'Restore is een uniek mengsel van 9 plantaardige stoffen, 5 spijsverteringsenzymen en 2 miljard levende bacterieculturen voor complete darmondersteuning.'),
            ('Hoe het werkt', 'De enzymencombinatie breekt voedingsstoffen efficiënt af, terwijl de probiotica het darmmicrobioom in balans houden en de botanicals de darmwand ondersteunen.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 12, 'name': 'Amare MentaBiotics', 'badge': 'Bestseller',
        'cat_name': 'Darmgezondheid', 'cat_url': '/darmgezondheid/',
        'img': 'https://amarenl.com/cdn/shop/files/Amare-Mentabiotics-EU-800.jpg',
        'thumbs': ['https://amarenl.com/cdn/shop/files/Amare-Mentabiotics-EU-800.jpg'],
        'desc': 'Het meest geavanceerde product voor de gut-brain axis. Combineert prebiotica, probiotica en fytobiotica in één formule die direct de verbinding tussen darmen en hersenen voedt.',
        'price_sub': '€ 71,83', 'price_once': '€ 75,61',
        'affiliate': 'https://www.amare.com/2075008/nl-NL/shop/mentabiotics/mentabiotics',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'Omdat 90% van je serotonine in je darmen wordt aangemaakt. MentaBiotics helpt je microbioom te balanceren voor betere stemming en meer energie.'),
            ('Wat het is', 'Bevat de unieke MWC-blend van Amare en klinisch geteste probiotische stammen zoals L. Rhamnosus en B. Longum voor cortisol reductie.'),
            ('Hoe het werkt', 'Prebiotica voeden goede bacteriën, probiotica herstellen balans, en fytobiotica verbeteren de communicatie via de vagus zenuw naar de hersenen.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 758, 'name': 'Amare Happy Juice Pack', 'badge': 'Bestseller',
        'cat_name': 'Darmgezondheid', 'cat_url': '/darmgezondheid/',
        'img': 'https://amarenl.com/wp-content/uploads/2026/04/Amare-Happy-Juice-Mango.jpg',
        'thumbs': ['https://amarenl.com/wp-content/uploads/2026/04/Amare-Happy-Juice-Mango.jpg',
                   'https://amarenl.com/cdn/shop/files/HappyJuicePack_EDGE_Plus_WatermelonSunset_EU.png'],
        'desc': 'De meest populaire combinatie in Nederland: EDGE+ Mango + Energy+ + MentaBiotics. Meng ze samen voor een complete gut-brain ondersteuning in één heerlijk drankje.',
        'price_sub': '€ 155,33', 'price_once': '€ 172,59',
        'affiliate': 'https://www.amare.com/2075008/nl-NL/shop/happy-juice/happy-juice-pack',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'Het Happy Juice Pack optimaliseert de verbinding tussen je darmen en je brein. Gebruikers rapporteren meer energie, minder stress en betere focus binnen 2 weken.'),
            ('Wat het is', 'Een synergetisch pakket van drie kernproducten: EDGE+ (nootropics), Energy+ (vitaliteit) en MentaBiotics (gut-brain axis).'),
            ('Hoe het werkt', 'Door de drie producten te mengen in één glas creëer je een krachtige drank die direct neurotransmitters en darmgezondheid optimaliseert.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 754, 'name': 'Amare EDGE+ (Mango)', 'badge': 'Bestseller',
        'cat_name': 'Mentale Fitheid', 'cat_url': '/mentale-fitheid/',
        'img': 'https://amarenl.com/cdn/shop/files/Amare-Edge-Plus-Mango-EU-800.jpg',
        'thumbs': ['https://amarenl.com/cdn/shop/files/Amare-Edge-Plus-Mango-EU-800.jpg',
                   'https://amarenl.com/cdn/shop/files/Amare-Edge-Watermelon-EU-800.jpg'],
        'desc': 'Nootropics voor scherpe focus en aanhoudende motivatie zonder jittery gevoel of crash. De mentale boost die je dagelijks routine transformeert.',
        'price_sub': '€ 77,28', 'price_once': '€ 81,35',
        'affiliate': 'https://www.amare.com/2075008/nl-NL/shop/edge/edge-plus',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'EDGE+ geeft je de mentale voorsprong in een drukke wereld. Scherpe focus zonder de crash van cafeïne-alleen producten.'),
            ('Wat het is', 'Een blend van krachtige nootropics en botanische extracten in een heerlijke mangosmaak voor dagelijks gebruik.'),
            ('Hoe het werkt', 'De ingrediënten stimuleren neuro-plasticiteit en focus via gezonde neurotransmitter-ondersteuning de hele dag lang.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 751, 'name': 'Amare EDGE Grape (cafeïnevrij)', 'badge': '',
        'cat_name': 'Mentale Fitheid', 'cat_url': '/mentale-fitheid/',
        'img': 'https://amarenl.com/cdn/shop/files/EDGE_Grape_Caffeinfree_EU-800.jpg',
        'thumbs': ['https://amarenl.com/cdn/shop/files/EDGE_Grape_Caffeinfree_EU-800.jpg'],
        'desc': 'Alle mentale helderheid van EDGE, maar dan zonder cafeïne. Ideaal voor avondgebruik of voor mensen die gevoelig zijn voor cafeïne.',
        'price_sub': '€ 77,28', 'price_once': '€ 81,35',
        'affiliate': 'https://www.amare.com/2075008/nl-NL/shop/edge/edge-grape',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'Bevordert helderheid en focus zonder nerveus gevoel of verstoring van je slaappatroon. Druivendrank voor elk moment.'),
            ('Wat het is', 'Dezelfde krachtige nootropics als EDGE+, maar volledig zonder cafeïne voor een rustigere maar toch gefocuste ervaring.'),
            ('Hoe het werkt', 'Ingrediënten reguleren neurotransmitters op een natuurlijk niveau voor kalme maar productieve mentale helderheid.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 31, 'name': 'Amare Energy+', 'badge': '',
        'cat_name': 'Energie & Focus', 'cat_url': '/energie-focus/',
        'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Amare-Energy-Dragonfruit-EU-800.jpg',
        'thumbs': ['https://amarecdn.azureedge.net/webassets/web/prod/products/Amare-Energy-Dragonfruit-EU-800.jpg'],
        'desc': 'Natuurlijk duurzame energie met dragonfruit smaak. Ondersteunt focus en vitaliteit zonder crash of jittery gevoel gedurende de hele dag.',
        'price_sub': '€ 55,48', 'price_once': '€ 59,84',
        'affiliate': 'https://www.amare.com/2075008/nl-nl/EnergyPlus',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'Energy+ geeft een natuurlijke boost die de hele dag aanhoudt. Geen suikercrash, geen kunstmatige stimulanten — alleen pure energie.'),
            ('Wat het is', 'Een blend van botanische extracten en adaptogens in dragonfruit smaak voor dagelijkse energieondersteuning.'),
            ('Hoe het werkt', 'Ondersteunt cellulaire energieproductie via mitochondriën voor langdurige vitaliteit op cellulair niveau.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 21, 'name': 'Amare ON Shots', 'badge': '',
        'cat_name': 'Energie & Focus', 'cat_url': '/energie-focus/',
        'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/ON-Raspberry-Grapefruit-EU-800.jpg',
        'thumbs': ['https://amarecdn.azureedge.net/webassets/web/prod/products/ON-Raspberry-Grapefruit-EU-800.jpg'],
        'desc': 'Compacte shots voor dagelijkse vitaliteit en snelle focus. Heerlijke raspberry-grapefruit smaak voor een directe boost op elk moment van de dag.',
        'price_sub': '€ 27,41', 'price_once': '€ 30,45',
        'affiliate': 'https://www.amare.com/2075008/nl-NL/onshots',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'ON is perfect voor drukke momenten wanneer je snel een boost nodig hebt, waar je ook bent. Compact en krachtig.'),
            ('Wat het is', 'Geconcentreerde shots met raspberry-grapefruit smaak, vol vitamine B-complex en natuurlijke energizers.'),
            ('Hoe het werkt', 'Actieve ingrediënten worden snel opgenomen voor onmiddellijke vitaliteit en mentale helderheid.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 26, 'name': 'Amare Nitro Xtreme 56ml', 'badge': '',
        'cat_name': 'Energie & Focus', 'cat_url': '/energie-focus/',
        'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Nitro-Xtreme-56ml-EU-800.jpg',
        'thumbs': ['https://amarecdn.azureedge.net/webassets/web/prod/products/Nitro-Xtreme-56ml-EU-800.jpg'],
        'desc': 'Krachtige nitric oxide booster in een handige 56ml flesje. Verbetert doorbloeding, vitaliteit en uithoudingsvermogen voor optimale dagelijkse prestaties.',
        'price_sub': '€ 53,74', 'price_once': '€ 59,71',
        'affiliate': 'https://www.amare.com/2075008/nl-nl/kyani-nitro-xtreme-56ml',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'Nitro Xtreme ondersteunt de bloedsomloop en het uithoudingsvermogen voor optimale prestaties — zowel mentaal als fysiek.'),
            ('Wat het is', 'Geconcentreerde 56ml formule met krachtige nitric oxide precursors voor maximale vasculaire ondersteuning.'),
            ('Hoe het werkt', 'Stimuleert aanmaak van stikstofmonoxide voor verbeterde vasculaire functie, betere zuurstoftoevoer en meer vitaliteit.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 9, 'name': 'Amare Ignite (for HIM)', 'badge': '',
        'cat_name': 'Darmgezondheid', 'cat_url': '/darmgezondheid/',
        'img': 'https://amarenl.com/cdn/shop/files/Ignite-Him-EU-800.jpg',
        'thumbs': ['https://amarenl.com/cdn/shop/files/Ignite-Him-EU-800.jpg'],
        'desc': 'Een supplement speciaal samengesteld voor mannen met een mix van op de natuur gebaseerde kruiden gecombineerd met zink voor vitaliteit en seksueel welzijn.',
        'price_sub': '€ 67,47', 'price_once': '€ 75,10',
        'affiliate': 'https://www.amare.com/2075008/nl-NL/shop/ignite/ignite-for-him',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'Helpt bij het behouden van gezonde energieniveaus en ondersteunt een actieve, vitale levensstijl voor mannen.'),
            ('Wat het is', 'Een mix van op de natuur gebaseerde kruiden gecombineerd met zink speciaal voor mannelijke vitaliteit.'),
            ('Hoe het werkt', 'Ondersteunt de natuurlijke bloedsomloop, hormonale harmonie en dagelijkse focus voor mannen.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 10, 'name': 'Amare Ignite (for HER)', 'badge': '',
        'cat_name': 'Darmgezondheid', 'cat_url': '/darmgezondheid/',
        'img': 'https://amarenl.com/cdn/shop/files/AmareIgnite_forHER.jpg',
        'thumbs': ['https://amarenl.com/cdn/shop/files/AmareIgnite_forHER.jpg'],
        'desc': 'Een supplement speciaal samengesteld voor vrouwen met een mix van kruiden, fytonutriënten en mineralen voor optimale vrouwelijke vitaliteit en welzijn.',
        'price_sub': '€ 67,47', 'price_once': '€ 75,10',
        'affiliate': 'https://www.amare.com/2075008/nl-NL/shop/ignite/ignite-for-her',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'Ondersteunt de vrouwelijke fysiologische balans en hormonale gezondheid voor optimale dagelijkse vitaliteit.'),
            ('Wat het is', 'Een holistische blend gericht op de specifieke behoeften van vrouwen met fytonutriënten en mineralen.'),
            ('Hoe het werkt', 'Fytonutriënten en mineralen optimaliseren hormoonbalans en ondersteunen seksueel welzijn op natuurlijke wijze.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 327, 'name': 'FIT20', 'badge': '',
        'cat_name': 'Darmgezondheid', 'cat_url': '/darmgezondheid/',
        'img': 'https://amarenl.com/cdn/shop/files/FIT20_EiwitPoederVoorTraining_Herstel.png',
        'thumbs': ['https://amarenl.com/cdn/shop/files/FIT20_EiwitPoederVoorTraining_Herstel.png'],
        'desc': 'De perfecte manier om je lichaam van brandstof te voorzien vóór, tijdens en na de fysieke activiteit. Bevat 21 aminozuren voor optimale spierondersteuning.',
        'price_sub': '€ 48,01', 'price_once': '€ 53,34',
        'affiliate': 'https://www.amare.com/2075008/nl-NL/shop',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'Ondersteunt spierherstel en spieropbouw na de training met 21 essentiele aminozuren voor optimale resultaten.'),
            ('Wat het is', 'Krachtig eiwitpoeder verrijkt met collageen voor flexibele gewrichten en gezonde weefsels na intensieve training.'),
            ('Hoe het werkt', 'Aminozuren herstellen spierschade, terwijl collageenpeptiden de structuur van je lichaam ondersteunen voor sneller herstel.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 760, 'name': 'Amare HL5 Peach Collagen', 'badge': '',
        'cat_name': 'Huidverzorging', 'cat_url': '/huidverzorging/',
        'img': 'https://amarenl.com/cdn/shop/files/AmareHL5.png',
        'thumbs': ['https://amarenl.com/cdn/shop/files/AmareHL5.png'],
        'desc': 'Dagelijkse collageenondersteuning met frisse perziksmaak. Voedt huid, haar en nagels van binnenuit voor zichtbaar jonger uitziende huid.',
        'price_sub': '€ 68,62', 'price_once': '€ 72,23',
        'affiliate': 'https://www.amare.com/2075008/nl-NL/shop',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'Voorkomt tekenen van veroudering door het lichaam te voorzien van goed opneembaar gehydrolyseerd collageen.'),
            ('Wat het is', 'Gehydrolyseerd collageen in vloeibare form voor maximale absorptie, in een heerlijke perziksmaak.'),
            ('Hoe het werkt', 'Collageenpeptiden stimuleren de eigen productie in de diepere huidlagen voor langdurig zichtbaar resultaat.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 14, 'name': 'Triangle of Wellness Xtreme', 'badge': 'Populair',
        'cat_name': 'Darmgezondheid', 'cat_url': '/darmgezondheid/',
        'img': 'https://amarenl.com/cdn/shop/files/XtremeTriangleofWellness.jpg',
        'thumbs': ['https://amarenl.com/cdn/shop/files/XtremeTriangleofWellness.jpg'],
        'desc': 'De ultieme combinatie: mentale gezondheid + darmgezondheid + energie in één synergistisch pakket. Alles wat je lichaam nodig heeft voor volledig welzijn.',
        'price_sub': '€ 123,55', 'price_once': '€ 130,05',
        'affiliate': 'https://www.amare.com/2075008/nl-NL/shop',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'Complete holistische gezondheidsoplossing die alle systemen in je lichaam in balans brengt voor maximaal welzijn.'),
            ('Wat het is', 'Bestaat uit MentaBiotics, Energy+ en EDGE noötropica voor optimale gut-brain communicatie op alle niveaus.'),
            ('Hoe het werkt', 'Door de krachten van drie producten te bundelen ontstaat een extreem krachtige synergie voor compleet welzijn.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 805, 'name': 'Skin to Mind™ Collection', 'badge': 'Nieuw',
        'cat_name': 'Huidverzorging', 'cat_url': '/huidverzorging/',
        'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/SkinToMind_Collection_800.jpg',
        'thumbs': ['https://amarecdn.azureedge.net/webassets/web/prod/products/SkinToMind_Collection_800.jpg'],
        'desc': 'De eerste huidverzorgingslijn die de mind-skin connectie centraal stelt. Complete collectie voor zichtbaar stralende, gezonde huid van binnenuit én buitenaf.',
        'price_sub': '€ 195,83', 'price_once': '€ 217,74',
        'affiliate': 'https://www.amare.com/2075008/nl-nl/skin-mind-collection',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'De eerste huidverzorgingslijn die de mind-skin connectie centraal stelt voor diepere, langdurige huidresultaten.'),
            ('Wat het is', 'Complete collectie: NeuDay serum, NeuNight serum en OptiMIST facial mist voor dag en nacht.'),
            ('Hoe het werkt', 'Formules werken op de huid-hersen-as voor een holistische aanpak van huidgezondheid zichtbaar in 4 weken.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 24, 'name': 'Skin to Mind NeuDay™ Serum', 'badge': '',
        'cat_name': 'Huidverzorging', 'cat_url': '/huidverzorging/',
        'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/NueDay_800.jpg',
        'thumbs': ['https://amarecdn.azureedge.net/webassets/web/prod/products/NueDay_800.jpg'],
        'desc': 'Dagelijks brightening serum dat huid verlicht en revitaliseert voor een stralende, gezonde gloed. Brighten + Revitalize voor een egale teint.',
        'price_sub': '€ 87,58', 'price_once': '€ 97,95',
        'affiliate': 'https://www.amare.com/2075008/nl-nl/skin-mind-neuday',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'NeuDay verlicht de huid van binnenuit en beschermt overdag tegen oxidatieve stress voor een egale teint.'),
            ('Wat het is', 'Dagserum met brightening actieve stoffen en antioxidanten voor een stralende, egale huidteint.'),
            ('Hoe het werkt', 'Brightening peptiden werken samen met antioxidanten voor zichtbaar egale huid in 4 weken dagelijks gebruik.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 25, 'name': 'Skin to Mind NeuNight™ Serum', 'badge': '',
        'cat_name': 'Huidverzorging', 'cat_url': '/huidverzorging/',
        'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/NueNight_800.jpg',
        'thumbs': ['https://amarecdn.azureedge.net/webassets/web/prod/products/NueNight_800.jpg'],
        'desc': 'Intensief nachtserum dat tijdens de slaap de huid herstelt en vernieuwt. Restore + Renew voor zichtbaar jongere, gladder huid in de ochtend.',
        'price_sub': '€ 97,89', 'price_once': '€ 108,84',
        'affiliate': 'https://www.amare.com/2075008/nl-NL/shop-all',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'NeuNight werkt terwijl je slaapt — de meest actieve herstelperiode van je huid voor maximaal resultaat.'),
            ('Wat het is', 'Intensief nachtserum met herstellende peptiden en ceramiden voor nachtelijke celvernieuwing.'),
            ('Hoe het werkt', 'Stimuleert nachtelijke celregeneratie en verhoogt huidbarrièrefunctie voor strakker, gladder huidresultaat.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 23, 'name': 'Skin to Mind OptiMIST™', 'badge': 'Nieuw',
        'cat_name': 'Huidverzorging', 'cat_url': '/huidverzorging/',
        'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/OptiMist_800.jpg',
        'thumbs': ['https://amarecdn.azureedge.net/webassets/web/prod/products/OptiMist_800.jpg'],
        'desc': 'Verfrissende gezichtsmist die de huid wakker maakt en een stralende glow geeft. Awaken + Glow voor direct zichtbaar stralende huid op elk moment.',
        'price_sub': '€ 51,50', 'price_once': '€ 58,02',
        'affiliate': 'https://www.amare.com/2075008/nl-nl/skin-mind-optimist',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'OptiMIST is de snelste manier om je huid te verfrissen en een gezonde gloed te creëren, altijd en overal.'),
            ('Wat het is', 'Lichte gezichtsmist met hydraterende en glow-enhancing actieve stoffen voor alle huidtypen.'),
            ('Hoe het werkt', 'Fijne nevel zet onmiddellijk in op hydratatie en lichtreflectie voor direct zichtbaar huidresultaat.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 803, 'name': 'Rootist Dynamic Pack', 'badge': 'Bestseller',
        'cat_name': 'Haarverzorging', 'cat_url': '/haarverzorging/',
        'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Rootist_Dynamic_Pack_800_Hero_DU.jpg',
        'thumbs': ['https://amarecdn.azureedge.net/webassets/web/prod/products/Rootist_Dynamic_Pack_800_Hero_DU.jpg'],
        'desc': 'Compleet haarverzorgingspakket dat haarwortels versterkt, uitval vermindert en haardikte vergroot. De complete oplossing voor denser, sterker haar.',
        'price_sub': '€ 96,80', 'price_once': '€ 107,63',
        'affiliate': 'https://www.amare.com/2075008/nl-nl/rootist-dynamic-pack',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'Gezond haar begint bij sterke wortels. Rootist pakt haaruitval bij de bron aan voor zichtbaar denser haar.'),
            ('Wat het is', 'Dynamisch pakket met producten gericht op versterking van haarfollikel en vermindering van haaruitval.'),
            ('Hoe het werkt', 'Werkzame stoffen stimuleren haarfollikel-activiteit voor meer haargroei en aantoonbaar minder uitval.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 29, 'name': 'BioBrew™ Gefermenteerd Versterkend Serum', 'badge': '',
        'cat_name': 'Haarverzorging', 'cat_url': '/haarverzorging/',
        'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/BioBrew_Serum_BE_800.jpg',
        'thumbs': ['https://amarecdn.azureedge.net/webassets/web/prod/products/BioBrew_Serum_BE_800.jpg'],
        'desc': 'Gefermenteerd haarserum dat haarsterkte en -glans verbetert. Op de natuur gebaseerde formule voor merkbaar sterker, glanzend haar.',
        'price_sub': '€ 30,88', 'price_once': '€ 35,05',
        'affiliate': 'https://www.amare.com/2075008/nl-nl/biobrew-fermented-strengthening-serum',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'Gefermenteerde ingrediënten zijn beter opneembaar en werken dieper in de haarstructuur voor echt resultaat.'),
            ('Wat het is', 'Versterkend serum op basis van gefermenteerde botanicals voor structureel sterkere, glanzende haren.'),
            ('Hoe het werkt', 'Gefermenteerde actieve stoffen dringen diep in de haarschacht voor structurele versterking van binnenuit.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 27, 'name': 'Clarify Balancing Serum', 'badge': '',
        'cat_name': 'Haarverzorging', 'cat_url': '/haarverzorging/',
        'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Clarify_Balancing_Serum_BE_800.jpg',
        'thumbs': ['https://amarecdn.azureedge.net/webassets/web/prod/products/Clarify_Balancing_Serum_BE_800.jpg'],
        'desc': 'Balanceert de vette hoofdhuid en vermindert overtollig talg voor een gezondere haarbasis. De oplossing voor vet, plat haar.',
        'price_sub': '€ 44,28', 'price_once': '€ 49,48',
        'affiliate': 'https://www.amare.com/2075008/nl-nl/clarify-balancing-serum-oily-scalp',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'Een gezonde hoofdhuid is de basis voor gezond haar. Dit serum brengt de talgproductie in balans.'),
            ('Wat het is', 'Licht, niet-vettig serum met talg-regulerende actieve stoffen voor de vette, onbalansen hoofdhuid.'),
            ('Hoe het werkt', 'Reguleert talgproductie en kalmeert de hoofdhuid voor minder vet haar en een frissere, gezondere basis.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 37, 'name': 'AHA+ACV Pre-Shampoo Spoeling', 'badge': '',
        'cat_name': 'Haarverzorging', 'cat_url': '/haarverzorging/',
        'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/AHA_ACV_Pre_Shampoo_BE_800.jpg',
        'thumbs': ['https://amarecdn.azureedge.net/webassets/web/prod/products/AHA_ACV_Pre_Shampoo_BE_800.jpg'],
        'desc': 'Reinigt en verlicht de hoofdhuid met AHA en appelazijn. Een frisse, schone start die de haarbasis optimaal voorbereidt voor behandeling.',
        'price_sub': '€ 28,81', 'price_once': '€ 32,99',
        'affiliate': 'https://www.amare.com/2075008/nl-nl/pre-shampoo-clarifying-rinse',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'Een gezonde hoofdhuid begint met de juiste reiniging. Deze pre-shampoo verwijdert ophoping voor optimale haargroei.'),
            ('Wat het is', 'Pre-shampoo behandeling met alpha-hydroxy zuren en appelazijn voor diepgereinigde, gebalanceerde hoofdhuid.'),
            ('Hoe het werkt', 'AHA-zuren exfoliëren dode huidcellen terwijl appelazijn de pH balans herstelt voor een gezonde haarbasis.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 828, 'name': 'Versterkende Collectie voor Haarherstel', 'badge': '',
        'cat_name': 'Haarverzorging', 'cat_url': '/haarverzorging/',
        'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Strenghtening_Collection_for_Hair_Repair_EU_800x800.jpg',
        'thumbs': ['https://amarecdn.azureedge.net/webassets/web/prod/products/Strenghtening_Collection_for_Hair_Repair_EU_800x800.jpg'],
        'desc': 'Alles-in-één collectie voor beschadigd haar. Herstelt, voedt en beschermt van wortel tot punt voor merkbaar sterker, glanzend haar.',
        'price_sub': '€ 110,47', 'price_once': '€ 125,36',
        'affiliate': 'https://www.amare.com/2075008/nl-nl/collection-hair-repair',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'Beschadigd haar heeft een complete herstelroutine nodig. Deze collectie levert een volledig systeem.'),
            ('Wat het is', 'Complete collectie met shampoo, conditioner en serum speciaal voor beschadigd, breekbaar haar.'),
            ('Hoe het werkt', 'Proteïnen en ceramiden herbouwen de haarstructuur terwijl botanicals het haar beschermen tegen verdere schade.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 789, 'name': 'Haarverdikkende Collectie voor Volume', 'badge': '',
        'cat_name': 'Haarverzorging', 'cat_url': '/haarverzorging/',
        'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Densifying_Collection_for_Volume_EU_800x800.jpg',
        'thumbs': ['https://amarecdn.azureedge.net/webassets/web/prod/products/Densifying_Collection_for_Volume_EU_800x800.jpg'],
        'desc': 'Complete collectie voor meer volume en dichtheid bij fijn of dun haar. Zichtbaar dikker haar met elke wasbeurt.',
        'price_sub': '€ 132,02', 'price_once': '€ 148,87',
        'affiliate': 'https://www.amare.com/2075008/nl-nl/collection-densifying-for-volume',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'Fijn haar heeft een gerichte volume-routine nodig. Deze collectie levert zichtbaar dikker haar.'),
            ('Wat het is', 'Volledige haarverzorgingslijn met volume-boosting actieve stoffen voor fijn en dun haar.'),
            ('Hoe het werkt', 'Volumizende polymeren en bodifying stoffen geven haar zichtbaar meer massa, lift en dichtheid.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 20, 'name': 'Amare Origin (Chocolate)', 'badge': '',
        'cat_name': 'Darmgezondheid', 'cat_url': '/darmgezondheid/',
        'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Origin-Chocolate-EU-800.jpg',
        'thumbs': ['https://amarecdn.azureedge.net/webassets/web/prod/products/Origin-Chocolate-EU-800.jpg'],
        'desc': '100% veganistische eiwitshake met 23g eiwit per portie. Romige chocoladesmaak voor optimaal spierherstel en spieropbouw na elke training.',
        'price_sub': '€ 40,00', 'price_once': '€ 44,45',
        'affiliate': 'https://www.amare.com/2075008/nl-NL/kyani-origin-chocolate',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'Origin is de perfecte post-workout shake die je spieren voedt en je lichaam optimaal laat herstellen.'),
            ('Wat het is', 'Complete, macronutriënten uitgebalanceerde shake op basis van plantaardige eiwitten van superieure kwaliteit.'),
            ('Hoe het werkt', '21 aminozuren en 23g plantaardig eiwit ondersteunen spierherstel en -opbouw voor maximale sportprestaties.'),
        ],
        'why_cards': []
    },
    {
        'wp_id': 13, 'name': 'Amare Sunrise 2-Pack', 'badge': '',
        'cat_name': 'Energie & Focus', 'cat_url': '/energie-focus/',
        'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Sunrise-2pk-EU-800.jpg',
        'thumbs': ['https://amarecdn.azureedge.net/webassets/web/prod/products/Sunrise-2pk-EU-800.jpg'],
        'desc': 'Twee maanden dagelijkse zon-voeding. Rijke omega-vetzuren, vitamine D en krachtige antioxidanten voor een krachtige, gezonde ochtendstart.',
        'price_sub': '€ 85,78', 'price_once': '€ 95,31',
        'affiliate': 'https://www.amare.com/2075008/nl-nl/sunrise-2pack',
        'tabs': [
            ('Waarom je het leuk zult vinden', 'Sunrise is jouw dagelijkse dosis zonlicht in een flesje — essentiële voedingsstoffen voor elke ochtend.'),
            ('Wat het is', 'Essentiële omega-vetzuren, vitamine D en krachtige antioxidanten voor twee maanden dagelijks gebruik.'),
            ('Hoe het werkt', 'Combinatie van omegas en vitamine D ondersteunt hart, hersenen en immuunsysteem voor algeheel welzijn.'),
        ],
        'why_cards': []
    },
]


def deploy_all():
    for p in PRODUCTS:
        html = build_product_page(p)
        wp_content = f'<!-- wp:html -->\n{html}\n<!-- /wp:html -->'
        resp = requests.post(
            f'{BASE}/wp-json/wp/v2/pages/{p["wp_id"]}',
            json={'title': p['name'], 'content': wp_content, 'status': 'publish'},
            auth=AUTH, timeout=30
        )
        if resp.status_code == 200:
            link = resp.json().get('link', 'N/A')
            print(f'OK  ID:{p["wp_id"]:4d} {p["name"][:40]:40s} -> {link}')
        else:
            print(f'ERR ID:{p["wp_id"]:4d} {p["name"][:40]:40s} -> {resp.status_code}')


if __name__ == '__main__':
    deploy_all()
