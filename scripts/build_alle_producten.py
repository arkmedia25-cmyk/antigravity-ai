"""
1. Deploy Alle Producten page (ID 40) with all 39 products + category filter.
2. Update homepage am-pcard divs to link directly to individual product pages.
"""
import re, sys, requests
from requests.auth import HTTPBasicAuth
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

AUTH = HTTPBasicAuth('shoppingbest41', 'QmdY FAML WPzu IiK4 jewG lSD7')
BASE = 'https://amarenl.com'
WP   = f'{BASE}/wp-content/uploads/2026/04'

# registry key → WP product page slug
KEY_TO_SLUG = {
    'happyjuice':        '/happy-juice-pack/',
    'edge':              '/amare-edge-mango-2/',
    'restore':           '/restore/',
    'mentabiotics':      '/mentabiotics-3/',
    'ignite':            '/ignite-for-him/',
    'ignite_her':        '/ignite-for-her/',
    'fit20':             '/fit20/',
    'hl5':               '/amare-hl5-peach-collagen/',
    'edge_grape':        '/amare-edge-grape/',
    'triangle':          '/triangle-of-wellness-xtreme/',
    'energy':            '/energy-pom/',
    'on':                '/onshots/',
    'nitro':             '/nitro-xtreme/',
    'origin':            '/origin-chocolate/',
    'sunrise2':          '/sunrise-2pack/',
    'hl5_2pack':         '/amare-hl5-peach-collagen/',
    'hlp_basic':         '/happy-lifestyle-pack-basic-2/',
    'hlp_pro':           '/happy-lifestyle-pack-pro-2/',
    'triangle2':         '/triangle-of-wellness-xtreme-2-pack/',
    'triangle3':         '/triangle-of-wellness-xtreme-3-pack/',
    'triangle6':         '/triangle-of-wellness-xtreme-6-pack/',
    's2m_collection':    '/skin-to-mind/',
    's2m_neuday':        '/neuday/',
    's2m_neunight':      '/neunight/',
    's2m_optimist':      '/optimist/',
    'biobrew':           '/biobrew-serum/',
    'aha_acv':           '/pre-shampoo/',
    'clarify_serum':     '/clarify-serum/',
    'rootist':           '/rootist-dynamic-pack-2/',
    'versterk_haar':     '/versterkende-collectie-voor-haarherstel-2/',
    'haar_volume':       '/haarverdikkende-collectie-voor-volume-2/',
    'verdik_serum':      '/verdikkend-serum-voor-fijn-haar/',
    'verdicht_shampoo':  '/verdichten-geconcentreerde-shampoo/',
    'verdicht_cond':     '/densify-conditioner/',
    'droogshampoo':      '/dry-shampoo/',
    'versterik_shampoo': '/strengthen-conditioner/',
    'versterik_cond':    '/geconcentreerde-conditioner-versterken-2/',
}

CAT_LABELS = {
    'start':       'Starter Pakket',
    'darm':        'Darmgezondheid',
    'mentaal':     'Mentale Fitheid',
    'mentaalwelzijn': 'Mentaal Welzijn',
    'essentieel':  'Essentieel',
    'huid':        'Huidverzorging',
    'haar':        'Haarverzorging',
    'gewicht':     'Gewicht',
    'lichaam':     'Lichaam & Kracht',
    'seksueel':    'Seksueel Welzijn',
}


def extract_products(raw):
    """Extract all 39 product cards from homepage raw content."""
    blocks = re.split(r'(?=<div class="am-pcard")', raw)
    products = []
    for block in blocks:
        if not block.startswith('<div class="am-pcard"'):
            continue
        cat  = re.search(r'data-cat="([^"]+)"', block)
        key  = re.search(r"amOpenDetail\('([^']+)'\)", block)
        name = re.search(r'am-pcard-name[^>]*>(.*?)</div>', block, re.DOTALL)
        img  = re.search(r'<img[^>]+src="([^"]+)"', block)
        desc = re.search(r'am-pcard-desc[^>]*>(.*?)</div>', block, re.DOTALL)
        price= re.search(r'am-price-new[^>]*>(.*?)</span>', block)
        aff  = re.search(r'href="(https://www\.amare\.com[^"]+)"', block)
        if not key:
            continue
        products.append({
            'key':   key.group(1),
            'cats':  cat.group(1).split() if cat else [],
            'name':  re.sub(r'<[^>]+>', '', name.group(1)).strip() if name else '',
            'img':   img.group(1) if img else '',
            'desc':  re.sub(r'<[^>]+>', '', desc.group(1)).strip() if desc else '',
            'price': price.group(1) if price else '',
            'aff':   aff.group(1) if aff else '#',
            'slug':  KEY_TO_SLUG.get(key.group(1), '#'),
        })
    return products


def build_alle_producten_page(products):
    cats_seen = sorted(set(c for p in products for c in p['cats']))

    # Build filter buttons
    filter_btns = '<button class="apf-btn active" onclick="apFilter(\'all\',this)">Alles</button>\n'
    for c in cats_seen:
        label = CAT_LABELS.get(c, c.title())
        filter_btns += f'      <button class="apf-btn" onclick="apFilter(\'{c}\',this)">{label}</button>\n'

    # Build product cards
    cards_html = ''
    for p in products:
        cat_str = ' '.join(p['cats'])
        badge = ''
        if 'start' in p['cats'] or 'essentieel' in p['cats']:
            badge = '<span class="ap-badge ap-badge-pop">Bestseller</span>'
        elif 'huid' in p['cats'] or 'haar' in p['cats']:
            badge = '<span class="ap-badge ap-badge-new">Nieuw</span>'

        cards_html += f'''
        <a class="ap-card" href="{p['slug']}" data-cat="{cat_str}">
          {badge}
          <div class="ap-card-img">
            <img src="{p['img']}" alt="{p['name']}" loading="lazy" onerror="this.style.display=\'none\'">
          </div>
          <div class="ap-card-body">
            <span class="ap-card-cat">{' · '.join(CAT_LABELS.get(c,c.title()) for c in p['cats'][:2])}</span>
            <div class="ap-card-name">{p['name']}</div>
            <p class="ap-card-desc">{p['desc'][:100]}{'...' if len(p['desc'])>100 else ''}</p>
          </div>
          <div class="ap-card-footer">
            <span class="ap-card-price">{p['price']}</span>
            <span class="ap-card-btn">Bekijken →</span>
          </div>
        </a>'''

    return f'''<!-- wp:html -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
.ap-wrap {{ font-family:"Inter",sans-serif; color:#2A2A2A; overflow-x:hidden; }}
.ap-wrap * {{ box-sizing:border-box; }}
.ap-hero {{
  background: linear-gradient(130deg, #3a1f50 0%, #522D72 100%);
  padding: 64px 24px 48px; text-align: center;
}}
.ap-hero-label {{
  font-size:0.72rem; font-weight:700; letter-spacing:3px;
  text-transform:uppercase; color:rgba(255,255,255,0.6); margin-bottom:12px;
}}
.ap-hero h1 {{
  font-family:"Playfair Display",serif;
  font-size:clamp(2rem,5vw,3.2rem); font-weight:900;
  color:white; margin:0 0 12px;
}}
.ap-hero p {{ color:rgba(255,255,255,0.8); font-size:1rem; margin:0; }}
.ap-filter-bar {{
  background:#F8F5F1; border-bottom:1px solid #e0d7c6;
  padding:16px 24px; overflow-x:auto; white-space:nowrap;
  display:flex; gap:8px; max-width:1280px; margin:0 auto;
}}
.apf-btn {{
  padding:8px 18px; border-radius:50px; font-size:0.82rem; font-weight:600;
  border:1.5px solid #e0d7c6; background:white; color:#522D72;
  cursor:pointer; transition:all 0.2s; white-space:nowrap;
}}
.apf-btn.active {{ background:#522D72; color:white; border-color:#522D72; }}
.apf-btn:hover {{ border-color:#522D72; }}
.ap-count {{
  max-width:1280px; margin:0 auto; padding:24px 24px 0;
  font-size:0.85rem; color:#666;
}}
.ap-grid {{
  max-width:1280px; margin:0 auto;
  display:grid; grid-template-columns:repeat(auto-fill,minmax(260px,1fr));
  gap:24px; padding:20px 24px 80px;
}}
.ap-card {{
  background:white; border:1px solid #e8e2da; border-radius:14px;
  overflow:hidden; display:flex; flex-direction:column;
  text-decoration:none; color:inherit; position:relative;
  transition:all 0.25s;
}}
.ap-card:hover {{ transform:translateY(-5px); box-shadow:0 16px 40px rgba(82,45,114,0.12); border-color:rgba(82,45,114,0.25); }}
.ap-badge {{
  position:absolute; top:12px; left:12px; z-index:2;
  padding:3px 10px; border-radius:50px; font-size:0.68rem; font-weight:700;
}}
.ap-badge-pop {{ background:#522D72; color:white; }}
.ap-badge-new {{ background:#7c4dbd; color:white; }}
.ap-card-img {{
  height:210px; background:#F8F5F1;
  display:flex; align-items:center; justify-content:center; overflow:hidden;
}}
.ap-card-img img {{ width:100%; height:100%; object-fit:contain; padding:16px; transition:transform 0.3s; }}
.ap-card:hover .ap-card-img img {{ transform:scale(1.04); }}
.ap-card-body {{ padding:16px 18px 10px; flex-grow:1; }}
.ap-card-cat {{
  font-size:0.68rem; font-weight:700; letter-spacing:1.5px;
  text-transform:uppercase; color:#522D72; display:block; margin-bottom:6px;
}}
.ap-card-name {{
  font-family:"Playfair Display",serif; font-size:1rem; font-weight:700;
  color:#2A2A2A; margin-bottom:8px; line-height:1.3;
}}
.ap-card-desc {{ font-size:0.82rem; color:#666; line-height:1.55; }}
.ap-card-footer {{
  padding:12px 18px; border-top:1px solid #f0ebe4;
  background:#FAFAFA; display:flex; align-items:center;
  justify-content:space-between; gap:8px;
}}
.ap-card-price {{ font-size:1.1rem; font-weight:800; color:#522D72; }}
.ap-card-btn {{
  background:#522D72; color:white; padding:8px 16px;
  border-radius:50px; font-weight:700; font-size:0.8rem;
}}
.ap-card.hidden {{ display:none; }}
@media(max-width:600px) {{
  .ap-grid {{ grid-template-columns:repeat(auto-fill,minmax(160px,1fr)); gap:16px; }}
  .ap-card-img {{ height:160px; }}
}}
</style>

<div class="ap-wrap">
  <div class="ap-hero">
    <div class="ap-hero-label">&#9733; Amare NL</div>
    <h1>Alle Producten</h1>
    <p>Wetenschappelijk onderbouwde supplementen en verzorging voor een holistische levensstijl</p>
  </div>

  <div class="ap-filter-bar">
    {filter_btns}
  </div>

  <div class="ap-count" id="apCount">{len(products)} producten</div>

  <div class="ap-grid" id="apGrid">
    {cards_html}
  </div>
</div>

<script>
(function(){{
  function apFilter(cat, btn) {{
    document.querySelectorAll('.apf-btn').forEach(function(b){{ b.classList.remove('active'); }});
    btn.classList.add('active');
    var cards = document.querySelectorAll('.ap-card');
    var count = 0;
    cards.forEach(function(c) {{
      var cats = c.dataset.cat || '';
      var show = cat === 'all' || cats.split(' ').indexOf(cat) !== -1;
      c.classList.toggle('hidden', !show);
      if(show) count++;
    }});
    document.getElementById('apCount').textContent = count + ' producten';
  }}
  window.apFilter = apFilter;
}})();
</script>
<!-- /wp:html -->'''


def update_homepage_links(raw, products):
    """Replace onclick=amOpenDetail with direct product page links on homepage cards."""
    count = 0
    for p in products:
        slug = p['slug']
        if slug == '#':
            continue
        # Find div class="am-pcard" with this key and make it a link
        old_open = f'<div class="am-pcard" data-cat="{" ".join(p["cats"])}" onclick="amOpenDetail(\'{p["key"]}\')">'
        new_open = f'<a class="am-pcard" data-cat="{" ".join(p["cats"])}" href="{slug}">'
        if old_open in raw:
            raw = raw.replace(old_open, new_open, 1)
            # Close tag: the div's closing </div></div></div> → </a>
            # This is complex; instead just add href attribute and keep div
            # Revert and use onclick+href approach
            raw = raw.replace(new_open, old_open, 1)  # revert

        # Simpler: add href to the am-pcard-btn (the Koop Nu button)
        # Find btn for this product and add/update href
        # The btn already has the affiliate href — change it to WP page
        # Actually keep affiliate on btn, just make clicking the image/title go to product page
        # Simplest valid approach: wrap card in <a> but change div→a
        pass

    # Better approach: replace onclick with href navigation via JS inline
    for p in products:
        slug = p['slug']
        if slug == '#':
            continue
        cats_str = ' '.join(p['cats'])
        old = f'<div class="am-pcard" data-cat="{cats_str}" onclick="amOpenDetail(\'{p["key"]}\')">'
        new = f'<a class="am-pcard" data-cat="{cats_str}" href="{slug}">'
        if old in raw:
            raw = raw.replace(old, new, 1)
            count += 1

    if count:
        # Close tags: am-pcard was </div></div></div> pattern ending at pcard-guarantee
        # Need to change each card's closing </div> (the outermost am-pcard div) to </a>
        # Pattern: </div><!-- end pcard or just the last </div> before next am-pcard or grid end
        # Use regex to fix closing tags
        raw = re.sub(
            r'(</div>\s*</div>\s*</div>)\s*(?=<a class="am-pcard"|</div><!-- end shop grid)',
            lambda m: '</div></div></a>\n        ',
            raw
        )
        # Also fix the CSS: am-pcard needs display:flex as block-level anchor
        raw = raw.replace(
            '.am-pcard { background: white;',
            '.am-pcard { background: white; display:flex;',
            1
        )

    print(f'Homepage card links updated: {count}/39')
    return raw


def run():
    print('Fetching homepage...')
    r = requests.get(f'{BASE}/wp-json/wp/v2/pages/36', auth=AUTH, params={'context': 'edit'})
    raw = r.json().get('content', {}).get('raw', '')

    products = extract_products(raw)
    print(f'Extracted {len(products)} products')

    # 1. Build and deploy Alle Producten page
    print('\nBuilding Alle Producten page...')
    page_html = build_alle_producten_page(products)
    resp = requests.post(
        f'{BASE}/wp-json/wp/v2/pages/40',
        json={'content': page_html, 'status': 'publish', 'title': 'Alle Producten'},
        auth=AUTH, timeout=60
    )
    if resp.status_code == 200:
        print(f'Alle Producten deployed → {resp.json().get("link","?")}')
    else:
        print(f'Alle Producten ERR {resp.status_code}: {resp.text[:150]}')

    # 2. Update homepage card links
    print('\nUpdating homepage card links...')
    new_raw = update_homepage_links(raw, products)
    resp2 = requests.post(
        f'{BASE}/wp-json/wp/v2/pages/36',
        json={'content': new_raw, 'status': 'publish'},
        auth=AUTH, timeout=60
    )
    if resp2.status_code == 200:
        print(f'Homepage deployed → {resp2.json().get("link","?")}')
    else:
        print(f'Homepage ERR {resp2.status_code}: {resp2.text[:150]}')


if __name__ == '__main__':
    run()
