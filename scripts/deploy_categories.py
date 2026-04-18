"""
Deploy category pages to WordPress.
Each category page = product grid filtered to that category + links to individual product pages → affiliate links.
Bridge page flow: Homepage → Category → Product detail → Amare affiliate link
"""
import requests
from requests.auth import HTTPBasicAuth

AUTH = HTTPBasicAuth('shoppingbest41', 'QmdY FAML WPzu IiK4 jewG lSD7')
BASE = 'https://amarenl.com'

CATEGORY_PAGES = {
    41: {
        'title': 'Darmgezondheid',
        'label': 'Darmgezondheid',
        'sub': 'Ondersteun je darmen en gut-brain axis met wetenschappelijk onderbouwde supplementen.',
        'products': [
            {
                'name': 'Amare Happy Juice Pack (Mango)',
                'desc': 'EDGE+ Mango + Energy+ + MentaBiotics. Complete gut-brain ondersteuning in één drankje.',
                'img': 'https://amarenl.com/wp-content/uploads/2026/04/Amare-Happy-Juice-Mango.jpg',
                'page': '/happy-juice-pack/',
                'affiliate': 'https://www.amare.com/2075008/nl-NL/shop/happy-juice/happy-juice-pack',
                'price_sub': '€155,33',
                'price_once': '€172,59',
                'badge': 'Bestseller'
            },
            {
                'name': 'Amare MentaBiotics',
                'desc': 'Uniek prebiotica, probiotica en fytobiotica complex dat de gut-brain-axis direct voedt.',
                'img': 'https://amarenl.com/cdn/shop/files/Amare-Mentabiotics-EU-800.jpg',
                'page': '/mentabiotics-3/',
                'affiliate': 'https://www.amare.com/2075008/nl-NL/shop/mentabiotics/mentabiotics',
                'price_sub': '€71,83',
                'price_once': '€75,61',
                'badge': ''
            },
            {
                'name': 'Restore',
                'desc': 'Spijsverteringsenzymen, probiotica en botanicals die de darmbarrière herstellen.',
                'img': 'https://amarenl.com/cdn/shop/files/Amare-Restore-EU-800.jpg',
                'page': '/restore/',
                'affiliate': 'https://www.amare.com/2075008/nl-NL/shop/restore/restore',
                'price_sub': '€29,70',
                'price_once': '€33,01',
                'badge': ''
            },
            {
                'name': 'Triangle of Wellness Xtreme',
                'desc': 'Mentale gezondheid + darmgezondheid + energie in één synergistisch pakket.',
                'img': 'https://amarenl.com/cdn/shop/files/XtremeTriangleofWellness.jpg',
                'page': '/triangle-of-wellness-xtreme/',
                'affiliate': 'https://www.amare.com/2075008/nl-NL/shop',
                'price_sub': '€123,55',
                'price_once': '€130,05',
                'badge': 'Populair'
            },
            {
                'name': 'Happy Juice Pack (Watermelon)',
                'desc': 'EDGE+ Watermelon + Energy+ + MentaBiotics. Frisse variant van de complete dagstart.',
                'img': 'https://amarenl.com/cdn/shop/files/HappyJuicePack_EDGE_Plus_WatermelonSunset_EU.png',
                'page': '/happy-juice-pack/',
                'affiliate': 'https://www.amare.com/2075008/nl-NL/shop/happy-juice/happy-juice-pack',
                'price_sub': '€155,33',
                'price_once': '€172,59',
                'badge': 'Nieuw'
            },
        ]
    },
    42: {
        'title': 'Mentale Fitheid',
        'label': 'Mentale Fitheid',
        'sub': 'Scherpe focus, aanhoudende motivatie en mentale helderheid voor productieve dagen.',
        'products': [
            {
                'name': 'Amare EDGE+ Mango',
                'desc': 'Nootropics + cafeïne voor scherpe focus en motivatie. Geen jittery gevoel.',
                'img': 'https://amarenl.com/cdn/shop/files/Amare-Edge-Plus-Mango-EU-800.jpg',
                'page': '/amare-edge-mango-2/',
                'affiliate': 'https://www.amare.com/2075008/nl-NL/shop/edge/edge-plus',
                'price_sub': '€77,28',
                'price_once': '€81,35',
                'badge': 'Bestseller'
            },
            {
                'name': 'Amare EDGE+ Watermelon',
                'desc': 'Frisse watermeloen smaak, dezelfde krachtige nootropics. Perfect voor sportieve momenten.',
                'img': 'https://amarenl.com/cdn/shop/files/Amare-Edge-Watermelon-EU-800.jpg',
                'page': '/amare-edge-mango-2/',
                'affiliate': 'https://www.amare.com/2075008/nl-NL/shop/edge/edge-plus-watermelon',
                'price_sub': '€77,28',
                'price_once': '€81,35',
                'badge': 'Nieuw'
            },
            {
                'name': 'Amare EDGE Grape (cafeïnevrij)',
                'desc': 'Alle mentale helderheid zonder cafeïne. Ideaal voor avond of bij gevoeligheid.',
                'img': 'https://amarenl.com/cdn/shop/files/EDGE_Grape_Caffeinfree_EU-800.jpg',
                'page': '/amare-edge-grape/',
                'affiliate': 'https://www.amare.com/2075008/nl-NL/shop/edge/edge-grape',
                'price_sub': '€77,28',
                'price_once': '€81,35',
                'badge': ''
            },
            {
                'name': 'Amare Energy+',
                'desc': 'Natuurlijk duurzame energie met dragonfruit smaak. Focus zonder crash.',
                'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Amare-Energy-Dragonfruit-EU-800.jpg',
                'page': '/energy-pom/',
                'affiliate': 'https://www.amare.com/2075008/nl-nl/EnergyPlus',
                'price_sub': '€55,48',
                'price_once': '€59,84',
                'badge': ''
            },
            {
                'name': 'Amare MentaBiotics',
                'desc': 'Uniek gut-brain complex. 90% van serotonine wordt in je darmen aangemaakt.',
                'img': 'https://amarenl.com/cdn/shop/files/Amare-Mentabiotics-EU-800.jpg',
                'page': '/mentabiotics-3/',
                'affiliate': 'https://www.amare.com/2075008/nl-NL/shop/mentabiotics/mentabiotics',
                'price_sub': '€71,83',
                'price_once': '€75,61',
                'badge': ''
            },
        ]
    },
    43: {
        'title': 'Energie & Focus',
        'label': 'Energie &amp; Focus',
        'sub': 'Natuurlijke energieboosters voor meer vitaliteit, doorzettingsvermogen en dagelijkse prestaties.',
        'products': [
            {
                'name': 'Amare ON Shots',
                'desc': 'Compacte shots voor dagelijkse vitaliteit en snelle focus. Raspberry-grapefruit.',
                'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/ON-Raspberry-Grapefruit-EU-800.jpg',
                'page': '/onshots/',
                'affiliate': 'https://www.amare.com/2075008/nl-NL/onshots',
                'price_sub': '€27,41',
                'price_once': '€30,45',
                'badge': ''
            },
            {
                'name': 'Amare Energy+',
                'desc': 'Langdurige energie met dragonfruit smaak. Ondersteunt focus en vitaliteit zonder crash.',
                'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Amare-Energy-Dragonfruit-EU-800.jpg',
                'page': '/energy-pom/',
                'affiliate': 'https://www.amare.com/2075008/nl-nl/EnergyPlus',
                'price_sub': '€55,48',
                'price_once': '€59,84',
                'badge': 'Populair'
            },
            {
                'name': 'Amare Sunrise 2-Pack',
                'desc': 'Twee maanden dagelijkse ochtend-voeding. Omega\'s, vitamine D en antioxidanten.',
                'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Sunrise-2pk-EU-800.jpg',
                'page': '/sunrise-2pack/',
                'affiliate': 'https://www.amare.com/2075008/nl-nl/sunrise-2pack',
                'price_sub': '€85,78',
                'price_once': '€95,31',
                'badge': ''
            },
            {
                'name': 'Amare Nitro Xtreme 56ml',
                'desc': 'Nitric oxide booster voor betere doorbloeding en uithoudingsvermogen.',
                'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Nitro-Xtreme-56ml-EU-800.jpg',
                'page': '/nitro-xtreme/',
                'affiliate': 'https://www.amare.com/2075008/nl-nl/kyani-nitro-xtreme-56ml',
                'price_sub': '€53,74',
                'price_once': '€59,71',
                'badge': ''
            },
            {
                'name': 'Amare EDGE+ Mango',
                'desc': 'Nootropics voor scherpe focus en aanhoudende motivatie de hele dag.',
                'img': 'https://amarenl.com/cdn/shop/files/Amare-Edge-Plus-Mango-EU-800.jpg',
                'page': '/amare-edge-mango-2/',
                'affiliate': 'https://www.amare.com/2075008/nl-NL/shop/edge/edge-plus',
                'price_sub': '€77,28',
                'price_once': '€81,35',
                'badge': ''
            },
        ]
    },
    44: {
        'title': 'Huidverzorging',
        'label': 'Huidverzorging',
        'sub': 'Premium huidverzorging die de mind-skin connectie verbetert voor zichtbaar stralende huid.',
        'products': [
            {
                'name': 'Skin to Mind™ Collection',
                'desc': 'Complete huidverzorgingslijn die de connectie tussen huid en geest verbetert.',
                'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/SkinToMind_Collection_800.jpg',
                'page': '/skin-to-mind/',
                'affiliate': 'https://www.amare.com/2075008/nl-nl/skin-mind-collection',
                'price_sub': '€195,83',
                'price_once': '€217,74',
                'badge': 'Bestseller'
            },
            {
                'name': 'Skin to Mind NeuDay™ Serum',
                'desc': 'Dagelijks serum dat huid verlicht en revitaliseert. Brighten + Revitalize.',
                'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/NueDay_800.jpg',
                'page': '/neuday/',
                'affiliate': 'https://www.amare.com/2075008/nl-nl/skin-mind-neuday',
                'price_sub': '€87,58',
                'price_once': '€97,95',
                'badge': ''
            },
            {
                'name': 'Skin to Mind NeuNight™ Serum',
                'desc': 'Nachtserum dat tijdens slaap huid herstelt en vernieuwt. Restore + Renew.',
                'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/NueNight_800.jpg',
                'page': '/neunight/',
                'affiliate': 'https://www.amare.com/2075008/nl-NL/shop-all',
                'price_sub': '€97,89',
                'price_once': '€108,84',
                'badge': ''
            },
            {
                'name': 'Skin to Mind OptiMIST™',
                'desc': 'Verfrissende gezichtsmist. Awaken + Glow voor directe stralende huid.',
                'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/OptiMist_800.jpg',
                'page': '/optimist/',
                'affiliate': 'https://www.amare.com/2075008/nl-nl/skin-mind-optimist',
                'price_sub': '€51,50',
                'price_once': '€58,02',
                'badge': 'Nieuw'
            },
            {
                'name': 'Amare HL5 Peach Collagen',
                'desc': 'Dagelijkse collageen ondersteuning met perziksmaak. Huid, haar en nagels.',
                'img': 'https://amarenl.com/cdn/shop/files/AmareHL5.png',
                'page': '/amare-hl5-peach-collagen/',
                'affiliate': 'https://www.amare.com/2075008/nl-NL/shop',
                'price_sub': '€68,62',
                'price_once': '€72,23',
                'badge': ''
            },
        ]
    },
    45: {
        'title': 'Haarverzorging',
        'label': 'Haarverzorging',
        'sub': 'Wetenschappelijk onderbouwde haarverzorging voor sterker, dikker en gezonder haar.',
        'products': [
            {
                'name': 'Rootist Dynamic Pack',
                'desc': 'Compleet pakket dat haarwortels versterkt, uitval vermindert en dichtheid vergroot.',
                'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Rootist_Dynamic_Pack_800_Hero_DU.jpg',
                'page': '/rootist-dynamic-pack-2/',
                'affiliate': 'https://www.amare.com/2075008/nl-nl/rootist-dynamic-pack',
                'price_sub': '€96,80',
                'price_once': '€107,63',
                'badge': 'Bestseller'
            },
            {
                'name': 'Haarverdikkende Collectie voor Volume',
                'desc': 'Complete collectie voor meer volume en dichtheid bij fijn of dun haar.',
                'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Densifying_Collection_for_Volume_EU_800x800.jpg',
                'page': '/haarverdikkende-collectie-voor-volume-2/',
                'affiliate': 'https://www.amare.com/2075008/nl-nl/collection-densifying-for-volume',
                'price_sub': '€132,02',
                'price_once': '€148,87',
                'badge': ''
            },
            {
                'name': 'Versterkende Collectie voor Haarherstel',
                'desc': 'Alles-in-één voor beschadigd haar. Herstelt, voedt en beschermt van wortel tot punt.',
                'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Strenghtening_Collection_for_Hair_Repair_EU_800x800.jpg',
                'page': '/versterkende-collectie-voor-haarherstel-2/',
                'affiliate': 'https://www.amare.com/2075008/nl-nl/collection-hair-repair',
                'price_sub': '€110,47',
                'price_once': '€125,36',
                'badge': ''
            },
            {
                'name': 'BioBrew™ Gefermenteerd Versterkend Serum',
                'desc': 'Gefermenteerd haarserum dat haarsterkte en -glans verbetert. Natuur-gebaseerd.',
                'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/BioBrew_Serum_BE_800.jpg',
                'page': '/biobrew-serum/',
                'affiliate': 'https://www.amare.com/2075008/nl-nl/biobrew-fermented-strengthening-serum',
                'price_sub': '€30,88',
                'price_once': '€35,05',
                'badge': ''
            },
            {
                'name': 'Clarify Balancing Serum',
                'desc': 'Balanceert de vette hoofdhuid en vermindert overtollig talg voor gezonder haar.',
                'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/Clarify_Balancing_Serum_BE_800.jpg',
                'page': '/clarify-serum/',
                'affiliate': 'https://www.amare.com/2075008/nl-nl/clarify-balancing-serum-oily-scalp',
                'price_sub': '€44,28',
                'price_once': '€49,48',
                'badge': ''
            },
            {
                'name': 'AHA+ACV Pre-Shampoo Spoeling',
                'desc': 'Reinigt en verlicht de hoofdhuid met AHA en appelazijn voor een frisse basis.',
                'img': 'https://amarecdn.azureedge.net/webassets/web/prod/products/AHA_ACV_Pre_Shampoo_BE_800.jpg',
                'page': '/pre-shampoo/',
                'affiliate': 'https://www.amare.com/2075008/nl-nl/pre-shampoo-clarifying-rinse',
                'price_sub': '€28,81',
                'price_once': '€32,99',
                'badge': ''
            },
        ]
    },
}


def build_category_html(cat):
    cards_html = ''
    for p in cat['products']:
        badge_html = f'<div class="ac-badge">{p["badge"]}</div>' if p.get('badge') else ''
        cards_html += f'''
        <a class="ac-card" href="{p["page"]}">
          <div class="ac-img-wrap">
            {badge_html}
            <img src="{p["img"]}" alt="{p["name"]}" onerror="this.style.opacity=0">
          </div>
          <div class="ac-body">
            <div class="ac-name">{p["name"]}</div>
            <div class="ac-desc">{p["desc"]}</div>
            <div class="ac-price-row">
              <span class="ac-price">{p["price_sub"]}</span>
              <span class="ac-price-old">{p["price_once"]}</span>
              <span class="ac-save">Subscribe &amp; Save</span>
            </div>
          </div>
          <div class="ac-btn">Meer informatie &rsaquo;</div>
          <div class="ac-guarantee">&#128737;&#65039; 30 dagen geld-terug-garantie</div>
        </a>'''

    return f'''<!-- wp:html -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<style>
.ac-wrap {{ font-family: "Inter", sans-serif; color: #2A2A2A; overflow-x: hidden; }}
.ac-wrap * {{ box-sizing: border-box; }}
.ac-hero {{
  background: linear-gradient(120deg, #ddd0ee 0%, #c8b8de 100%);
  padding: 64px 24px 48px;
  text-align: center;
}}
.ac-hero-label {{
  font-size: 0.72rem; font-weight: 700; letter-spacing: 3px;
  text-transform: uppercase; color: #522D72; opacity: 0.7; margin-bottom: 12px;
}}
.ac-hero h1 {{
  font-family: "Playfair Display", serif;
  font-size: clamp(2rem, 5vw, 3.2rem);
  font-weight: 900; color: #3a1f50; margin: 0 0 16px;
}}
.ac-hero p {{ color: #5a4a6a; font-size: 1rem; line-height: 1.7; max-width: 600px; margin: 0 auto; }}
.ac-breadcrumb {{
  max-width: 1200px; margin: 0 auto; padding: 16px 24px;
  font-size: 0.82rem; color: #666;
}}
.ac-breadcrumb a {{ color: #522D72; text-decoration: none; }}
.ac-breadcrumb a:hover {{ text-decoration: underline; }}
.ac-grid-wrap {{
  max-width: 1200px; margin: 0 auto; padding: 40px 24px 80px;
}}
.ac-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 28px;
}}
.ac-card {{
  background: white; border: 1px solid #e8e2da; border-radius: 16px;
  overflow: hidden; text-decoration: none; color: inherit;
  display: flex; flex-direction: column;
  transition: all 0.25s; cursor: pointer;
}}
.ac-card:hover {{ box-shadow: 0 16px 40px rgba(82,45,114,0.13); transform: translateY(-5px); }}
.ac-img-wrap {{
  position: relative; height: 240px; background: #F8F5F1;
  display: flex; align-items: center; justify-content: center; overflow: hidden;
}}
.ac-img-wrap img {{
  width: 100%; height: 100%; object-fit: contain; padding: 20px;
  transition: transform 0.35s;
}}
.ac-card:hover .ac-img-wrap img {{ transform: scale(1.05); }}
.ac-badge {{
  position: absolute; top: 12px; left: 12px;
  background: #522D72; color: white;
  font-size: 0.68rem; font-weight: 700; padding: 4px 12px;
  border-radius: 50px; text-transform: uppercase;
}}
.ac-body {{ padding: 20px 20px 12px; flex-grow: 1; }}
.ac-name {{
  font-family: "Playfair Display", serif;
  font-size: 1.05rem; font-weight: 700; color: #522D72;
  margin-bottom: 8px; line-height: 1.3;
}}
.ac-desc {{ font-size: 0.84rem; color: #666; line-height: 1.6; margin-bottom: 14px; }}
.ac-price-row {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
.ac-price {{ font-size: 1.1rem; font-weight: 800; color: #522D72; }}
.ac-price-old {{ font-size: 0.82rem; color: #999; text-decoration: line-through; }}
.ac-save {{ font-size: 0.72rem; color: #4CAF50; font-weight: 700;
  background: #f0faf0; padding: 2px 8px; border-radius: 50px; }}
.ac-btn {{
  margin: 0 20px; padding: 13px;
  background: #522D72; color: white;
  text-align: center; font-weight: 700; font-size: 0.88rem;
  border-radius: 8px; transition: background 0.2s;
}}
.ac-card:hover .ac-btn {{ background: #3a1f50; }}
.ac-guarantee {{
  text-align: center; padding: 8px 16px 14px;
  font-size: 0.68rem; color: #2e7d32; font-weight: 600;
}}
.ac-cta-strip {{
  background: #522D72; padding: 48px 24px; text-align: center;
}}
.ac-cta-strip h2 {{
  font-family: "Playfair Display", serif;
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  color: white; margin: 0 0 12px;
}}
.ac-cta-strip p {{ color: rgba(255,255,255,0.8); margin: 0 auto 28px; max-width: 500px; }}
.ac-cta-link {{
  display: inline-block; background: white; color: #3a1f50;
  padding: 14px 36px; border-radius: 50px; font-weight: 700;
  text-decoration: none; font-size: 0.95rem; transition: all 0.25s;
}}
.ac-cta-link:hover {{ background: #f0eaf7; transform: translateY(-2px); }}
@media (max-width: 600px) {{
  .ac-grid {{ grid-template-columns: 1fr; }}
}}
</style>

<div class="ac-wrap">

  <div class="ac-hero">
    <div class="ac-hero-label">Amare Global Nederland</div>
    <h1>{cat["label"]}</h1>
    <p>{cat["sub"]}</p>
  </div>

  <div class="ac-breadcrumb">
    <a href="/">&#8592; Terug naar Home</a> &nbsp;/&nbsp; {cat["label"]}
  </div>

  <div class="ac-grid-wrap">
    <div class="ac-grid">
      {cards_html}
    </div>
  </div>

  <div class="ac-cta-strip">
    <h2>Alle Producten Bekijken?</h2>
    <p>Ontdek het volledige Amare assortiment en vind het supplement dat bij jou past.</p>
    <a href="/" class="ac-cta-link">&#8592; Terug naar het assortiment</a>
  </div>

</div>
<!-- /wp:html -->'''


def deploy():
    for page_id, cat in CATEGORY_PAGES.items():
        html = build_category_html(cat)
        resp = requests.post(
            f'{BASE}/wp-json/wp/v2/pages/{page_id}',
            json={'title': cat['title'], 'content': html, 'status': 'publish'},
            auth=AUTH, timeout=30
        )
        if resp.status_code == 200:
            print(f"OK  ID:{page_id} {cat['title']} -> {resp.json().get('link')}")
        else:
            print(f"ERR ID:{page_id} {cat['title']} -> {resp.status_code} {resp.text[:200]}")


if __name__ == '__main__':
    deploy()
