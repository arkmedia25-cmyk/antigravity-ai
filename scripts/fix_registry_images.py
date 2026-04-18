"""
Fix all amRegistry img URLs on the homepage — replace broken CDN links with WP uploads.
Also fix the AYW Watermelon card.
"""
import re, sys, requests
from requests.auth import HTTPBasicAuth
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

AUTH = HTTPBasicAuth('shoppingbest41', 'QmdY FAML WPzu IiK4 jewG lSD7')
BASE = 'https://amarenl.com'
WP   = f'{BASE}/wp-content/uploads/2026/04'

# registry key → WP filename
REGISTRY_IMG = {
    'edge':             'Amare-Edge-Mango.jpg',
    'mentabiotics':     'MentaBiotics.jpg',
    'ignite':           'Amare-Ignite-for-HIM.jpg',
    'ignite_her':       'Amare-Ignite-for-HER.jpg',
    'fit20':            'FIT20.png',
    'hl5':              'Amare-HL5.png',
    'edge_grape':       'Amare-Edge-Mango.jpg',
    'triangle':         'Xtreme-Triangle-of-Wellness-Level-Up-Pack.jpg',
    'energy':           'Energy-DragonFruit.jpg',
    'on':               'Amare-ON.png',
    'nitro':            'Amare-Nitro-Xtreme-56ml.png',
    'origin':           'Amare-Origin.png',
    'sunrise2':         'Amare-Sunrise-2-Pack.jpg',
    'hl5_2pack':        'Amare-HL5-2-Pack.png',
    'hlp_basic':        'Happy-Lifestyle-Pack-Basic.jpg',
    'hlp_pro':          'Happy-Lifestyle-Pack-Pro.jpg',
    'triangle2':        'Triangle-of-Wellness_2-pk.jpg',
    'triangle3':        'Triangle-of-Wellness_3-pk.jpg',
    'triangle6':        'Triangle-of-Wellness_6-pk.jpg',
    's2m_collection':   'Skin-to-Mind%E2%84%A2-Collection.jpg',
    's2m_neuday':       'Skin-to-Mind-NeuDay%E2%84%A2-Brighten-Revitalize-Serum.jpg',
    's2m_neunight':     'Skin-to-Mind-NeuNight%E2%84%A2-Restore-Renew-Serum.jpg',
    's2m_optimist':     'Skin-to-Mind-OptiMIST%E2%84%A2-Awaken-Glow-Facial-Mist.jpg',
    'biobrew':          'BioBrew%E2%84%A2-Gefermenteerd-Versterkend-Serum.jpg',
    'aha_acv':          'AHAACV-Pre-Shampoo-Hoofdhuid-Verhelderende-Spoeling.jpg',
    'clarify_serum':    'Clarify-Balancing-Serum-voor-een-vette-hoofdhuid.jpg',
    'rootist':          'Rootist-Dynamic-Pack.jpg',
    'versterk_haar':    'Versterkende-Collectie-voor-Haarherstel.jpg',
    'haar_volume':      'Haarverdikkende-Collectie-voor-Volume.jpg',
    'verdik_serum':     'Collectie-voor-vette-hoofdhuid-en-fijn-haar.jpg',
    'verdicht_shampoo': 'Verdichten-Geconcentreerde-Shampoo.jpg',
    'verdicht_cond':    'Verdichten-Geconcentreerde-Conditioner.jpg',
    'droogshampoo':     'Verduidelijk-Droogshampoo-Poeder.jpg',
    'versterik_shampoo':'Versterken-Geconcentreerde-Shampoo.jpg',
    'versterik_cond':   'Geconcentreerde-conditioner-versterken.jpg',
}


def fix_registry(raw):
    fixed = 0
    for key, filename in REGISTRY_IMG.items():
        new_url = f'{WP}/{filename}'
        # Match: 'key': { ... img:'OLD_URL' ...
        pattern = rf"('{re.escape(key)}':\s*\{{[^}}]*img:')[^']+(')"
        new_raw, n = re.subn(pattern, lambda m: m.group(1) + new_url + m.group(2), raw)
        if n:
            fixed += 1
            raw = new_raw
        else:
            print(f'  WARNING: key [{key}] not found in registry')
    print(f'Registry entries fixed: {fixed}/{len(REGISTRY_IMG)}')
    return raw


def fix_ayw_watermelon(raw):
    # Fix the AYW middle card — use the Watermelon pack image
    old = f'{WP}/Amare-Happy-Juice-Pack-Amare-EDGE-Watermelon.jpg'
    # Also catch any remaining CDN version
    cdn_pattern = r'cdn/shop/files/HappyJuicePack_EDGE_Plus_WatermelonSunset_EU\.png'
    raw, n1 = re.subn(cdn_pattern, old.split('amarenl.com/')[-1], raw)
    if n1:
        print(f'AYW Watermelon CDN fixed ({n1}x)')
    return raw


def run():
    print('Fetching page 36...')
    r = requests.get(f'{BASE}/wp-json/wp/v2/pages/36', auth=AUTH, params={'context': 'edit'})
    raw = r.json().get('content', {}).get('raw', '')
    print(f'Fetched: {len(raw)} chars')

    raw = fix_ayw_watermelon(raw)
    raw = fix_registry(raw)

    print('Deploying...')
    resp = requests.post(
        f'{BASE}/wp-json/wp/v2/pages/36',
        json={'content': raw, 'status': 'publish'},
        auth=AUTH, timeout=60
    )
    if resp.status_code == 200:
        print(f'OK -> {resp.json().get("link","?")}')
    else:
        print(f'ERR {resp.status_code}: {resp.text[:300]}')


if __name__ == '__main__':
    run()
