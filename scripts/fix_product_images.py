"""
Fix all product card images on the homepage.
Replaces broken CDN URLs with correct WP media (wp-content/uploads) URLs.
Also fixes the 3 Amare Your Way featured cards.
"""
import re, sys, requests
from requests.auth import HTTPBasicAuth
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

AUTH = HTTPBasicAuth('shoppingbest41', 'QmdY FAML WPzu IiK4 jewG lSD7')
BASE = 'https://amarenl.com'
WP  = f'{BASE}/wp-content/uploads/2026/04'

# card product name  →  WP media filename
IMAGE_MAP = {
    'Amare Happy Juice Mango':                      'Amare-Happy-Juice-Mango.jpg',
    'Amare Happy Juice Pack \u2013 EDGE+ Watermelon': 'Amare-Happy-Juice-Pack-Amare-EDGE-Watermelon.jpg',
    'Amare Edge+ Mango':                            'Amare-Edge-Mango.jpg',
    'Amare EDGE+\u2122 Watermelon':                 'Amare-EDGE%E2%84%A2-Watermelon.jpg',
    'Restore':                                      'Restore.jpg',
    'Amare MentaBiotics':                           'MentaBiotics.jpg',
    'Amare Ignite (for HIM)':                       'Amare-Ignite-for-HIM.jpg',
    'Amare Ignite (for HER)':                       'Amare-Ignite-for-HER.jpg',
    'FIT20':                                        'FIT20.png',
    'Amare HL5 Peach Collagen':                     'Amare-HL5.png',
    'Amare EDGE Grape (cafe\xefnevrij)':             'Amare-Edge-Mango.jpg',
    'Triangle of Wellness Xtreme':                  'Xtreme-Triangle-of-Wellness-Level-Up-Pack.jpg',
    'Amare Energy+':                                'Energy-DragonFruit.jpg',
    'Amare ON':                                     'Amare-ON.png',
    'Amare Nitro Xtreme 56ml':                      'Amare-Nitro-Xtreme-56ml.png',
    'Amare Origin':                                 'Amare-Origin.png',
    'Amare Sunrise 2-Pack':                         'Amare-Sunrise-2-Pack.jpg',
    'Amare HL5 2-Pack':                             'Amare-HL5-2-Pack.png',
    'Happy Lifestyle Pack Basic':                   'Happy-Lifestyle-Pack-Basic.jpg',
    'Happy Lifestyle Pack Pro':                     'Happy-Lifestyle-Pack-Pro.jpg',
    'Triangle of Wellness Xtreme\u2122 2-Pack':     'Triangle-of-Wellness_2-pk.jpg',
    'Triangle of Wellness Xtreme\u2122 3-Pack':     'Triangle-of-Wellness_3-pk.jpg',
    'Triangle of Wellness Xtreme\u2122 6-Pack':     'Triangle-of-Wellness_6-pk.jpg',
    'Skin to Mind\u2122 Collection':                'Skin-to-Mind%E2%84%A2-Collection.jpg',
    'Skin to Mind NeuDay\u2122 Serum':              'Skin-to-Mind-NeuDay%E2%84%A2-Brighten-Revitalize-Serum.jpg',
    'Skin to Mind NeuNight\u2122 Serum':            'Skin-to-Mind-NeuNight%E2%84%A2-Restore-Renew-Serum.jpg',
    'Skin to Mind OptiMIST\u2122':                  'Skin-to-Mind-OptiMIST%E2%84%A2-Awaken-Glow-Facial-Mist.jpg',
    'BioBrew\u2122 Gefermenteerd Versterkend Serum':'BioBrew%E2%84%A2-Gefermenteerd-Versterkend-Serum.jpg',
    'AHA+ACV Pre-Shampoo Spoeling':                 'AHAACV-Pre-Shampoo-Hoofdhuid-Verhelderende-Spoeling.jpg',
    'Clarify Balancing Serum':                      'Clarify-Balancing-Serum-voor-een-vette-hoofdhuid.jpg',
    'Rootist Dynamic Pack':                         'Rootist-Dynamic-Pack.jpg',
    'Versterkende Collectie voor Haarherstel':       'Versterkende-Collectie-voor-Haarherstel.jpg',
    'Haarverdikkende Collectie voor Volume':         'Haarverdikkende-Collectie-voor-Volume.jpg',
    'Verdikkend Serum voor Fijn Haar':               'Collectie-voor-vette-hoofdhuid-en-fijn-haar.jpg',
    'Verdichten Geconcentreerde Shampoo':            'Verdichten-Geconcentreerde-Shampoo.jpg',
    'Verdichten Geconcentreerde Conditioner':        'Verdichten-Geconcentreerde-Conditioner.jpg',
    'Verduidelijk Droogshampoo Poeder':              'Verduidelijk-Droogshampoo-Poeder.jpg',
    'Versterken Geconcentreerde Shampoo':            'Versterken-Geconcentreerde-Shampoo.jpg',
    'Versterken Geconcentreerde Conditioner':        'Geconcentreerde-conditioner-versterken.jpg',
}


def patch_card_img(card_html):
    """Replace img src in a single am-pcard block using the product name."""
    name_m = re.search(r'am-pcard-name[^>]*>(.*?)</div>', card_html, re.DOTALL)
    if not name_m:
        return card_html, None
    name = re.sub(r'<[^>]+>', '', name_m.group(1)).strip()
    filename = IMAGE_MAP.get(name)
    if not filename:
        return card_html, f'NO MATCH: {name}'
    new_url = f'{WP}/{filename}'
    new_card = re.sub(
        r'(<img[^>]+src=")[^"]+(")',
        lambda m: m.group(1) + new_url + m.group(2),
        card_html, count=1
    )
    return new_card, None


def fix_ayw_watermelon(raw):
    """Fix the Happy Juice Watermelon card in the Amare Your Way section."""
    old = 'cdn/shop/files/HappyJuicePack_EDGE_Plus_WatermelonSunset_EU.png'
    new = f'{WP}/Amare-Happy-Juice-Pack-Amare-EDGE-Watermelon.jpg'
    if old in raw:
        raw = raw.replace(old, new, 1)
        print('AYW Watermelon card image fixed')
    return raw


def run():
    print('Fetching homepage...')
    r = requests.get(f'{BASE}/wp-json/wp/v2/pages/36', auth=AUTH, params={'context': 'edit'})
    raw = r.json().get('content', {}).get('raw', '')
    print(f'Fetched: {len(raw)} chars')

    # Fix AYW section
    raw = fix_ayw_watermelon(raw)

    # Find and patch each am-pcard
    fixed = 0
    errors = []

    def replacer(m):
        nonlocal fixed
        new_card, err = patch_card_img(m.group(0))
        if err:
            errors.append(err)
        else:
            fixed += 1
        return new_card

    raw = re.sub(
        r'<div class="am-pcard".*?(?=<div class="am-pcard"|</div>\s*</div>\s*</div>\s*<!-- ====)',
        replacer,
        raw,
        flags=re.DOTALL
    )

    print(f'Cards patched: {fixed}')
    if errors:
        print(f'Unmatched ({len(errors)}):')
        for e in errors:
            print(f'  {e}')

    print('Deploying...')
    resp = requests.post(
        f'{BASE}/wp-json/wp/v2/pages/36',
        json={'content': raw, 'status': 'publish'},
        auth=AUTH, timeout=60
    )
    if resp.status_code == 200:
        print(f'OK -> {resp.json().get("link","?")}')
    else:
        print(f'ERR {resp.status_code}: {resp.text[:200]}')


if __name__ == '__main__':
    run()
