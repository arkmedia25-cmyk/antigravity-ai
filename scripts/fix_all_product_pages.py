"""
Fix broken CDN images on all product pages, then rebuild the Producten (all products) page.
"""
import re, sys, requests
from requests.auth import HTTPBasicAuth
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

AUTH = HTTPBasicAuth('shoppingbest41', 'QmdY FAML WPzu IiK4 jewG lSD7')
BASE = 'https://amarenl.com'
WP   = f'{BASE}/wp-content/uploads/2026/04'

# page_id → primary WP image filename
PAGE_IMG = {
    751:  'Amare-Edge-Mango.jpg',                                            # EDGE Grape (no grape in WP)
    29:   'BioBrew%E2%84%A2-Gefermenteerd-Versterkend-Serum.jpg',
    783:  'Collectie-voor-vette-hoofdhuid-en-fijn-haar.jpg',
    787:  'Geconcentreerde-conditioner-versterken.jpg',
    34:   'Amare-Xtreme-56ml-2-Pack.png',                                    # Nitro 2-Pack
    805:  'Skin-to-Mind%E2%84%A2-Collection.jpg',
    810:  'Triangle-Marketing-Pack.jpg',
    818:  'Xtreme-Triangle-of-Wellness-Level-Up-Pack.jpg',                   # Triangle duplicate
    812:  'Triangle-of-Wellness_2-pk.jpg',
    814:  'Triangle-of-Wellness_3-pk.jpg',
    816:  'Triangle-of-Wellness_6-pk.jpg',
    822:  'Verdichten-Geconcentreerde-Shampoo.jpg',
    824:  'Collectie-voor-vette-hoofdhuid-en-fijn-haar.jpg',                 # Verdikkend Serum
    793:  'Happy-Lifestyle-Pack-Pro.jpg',
    791:  'Happy-Lifestyle-Pack-Basic.jpg',
    39:   'Versterken-Geconcentreerde-Shampoo.jpg',
    35:   'Xtreme-Triangle-of-Wellness-Level-Up-Pack.jpg',                   # Level Up Pack
    32:   'Amare-ON-4-Pack.jpg',
    28:   'Verduidelijk-Droogshampoo-Poeder.jpg',
    25:   'Skin-to-Mind-NeuNight%E2%84%A2-Restore-Renew-Serum.jpg',
    24:   'Skin-to-Mind-NeuDay%E2%84%A2-Brighten-Revitalize-Serum.jpg',
    23:   'Skin-to-Mind-OptiMIST%E2%84%A2-Awaken-Glow-Facial-Mist.jpg',
    17:   'Verdichten-Geconcentreerde-Conditioner.jpg',
}

CDN_PAT = re.compile(r'src="(https?://[^"]*(?:cdn/shop/files|webassets)[^"]*)"')


def fix_page(pid, filename):
    r = requests.get(f'{BASE}/wp-json/wp/v2/pages/{pid}', auth=AUTH, params={'context': 'edit'})
    data = r.json()
    raw = data.get('content', {}).get('raw', '')
    title = data.get('title', {}).get('rendered', '?')

    new_url = f'{WP}/{filename}'
    new_raw, n = CDN_PAT.subn(f'src="{new_url}"', raw)
    if n == 0:
        print(f'  [{pid}] {title[:40]} — no CDN found (already fixed?)')
        return

    resp = requests.post(
        f'{BASE}/wp-json/wp/v2/pages/{pid}',
        json={'content': new_raw, 'status': 'publish'},
        auth=AUTH, timeout=30
    )
    status = 'OK' if resp.status_code == 200 else f'ERR {resp.status_code}'
    print(f'  [{pid}] {title[:40]} — {n}x fixed → {status}')


def run():
    print(f'Fixing {len(PAGE_IMG)} product pages...')
    for pid, filename in PAGE_IMG.items():
        fix_page(pid, filename)
    print('\nDone.')


if __name__ == '__main__':
    run()
