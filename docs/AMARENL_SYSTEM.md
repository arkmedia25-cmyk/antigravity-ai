# AmarreNL.com — Bridge Site & SEO Blog Documentatie

> Site: https://amarenl.com
> Doel: Affiliate bridge site + organisch SEO-verkeer + e-mailleads verzamelen
> Laatste update: 2026-04-20

---

## Overzicht

amarenl.com heeft twee functies:
1. **Productpagina's** — bezoekers doorsturen naar Amare.com met affiliate ID
2. **SEO Blog** — dagelijks artikel over voedingsstoffen → e-mailleads verzamelen

---

## WordPress Configuratie

| Instelling | Waarde |
|---|---|
| Site URL | https://amarenl.com |
| WP gebruiker | shoppingbest41 |
| App password | In `.env` als `WP_APP_PASSWORD` |
| Affiliate ID | 2075008 |
| Affiliate URL formaat | `https://www.amare.com/2075008/nl-nl/[slug]` |

---

## Blog Automatisering (dagelijks 10:00)

### Bestanden
| Bestand | Functie |
|---|---|
| `scripts/article_writer_amarenl.py` | Artikel genereren + publiceren |
| `scripts/daily_article_writer_amarenl.py` | Dagelijkse scheduler |
| `article_amarenl_state.json` | Voortgang state bestand |

### Cron
```bash
0 10 * * * cd /root/antigravity-ai && venv/bin/python3 scripts/daily_article_writer_amarenl.py >> logs/article_amarenl.log 2>&1
```

Log bekijken:
```bash
tail -f /root/antigravity-ai/logs/article_amarenl.log
```

### Artikel Type
- **Taal**: 100% Nederlands
- **Onderwerp**: Voedingsstoffen & ingrediënten (calcium, omega-3, vitamine D/E/B/C, collageen, probiotica, adaptogenen...)
- **Structuur**: Wat is het? / Tekort symptomen / Lead CTA / Aanvullen / Amare product link / FAQ / Conclusie
- **CTA**: €8 kortingscode modal (links naar homepage lead capture)

### Artikel Wachtrij (15 onderwerpen, herhaalt na voltooiing)

| # | Key | Onderwerp |
|---|---|---|
| 1 | magnesium_slaap | Magnesium en slaapproblemen |
| 2 | vitamine_d_tekort | Vitamine D tekort Nederland |
| 3 | omega3_hersenen | Omega-3 en hersengezondheid |
| 4 | collageen_huid | Collageen voor huid & haar |
| 5 | probiotica_darm | Probiotica voor darmen |
| 6 | vitamine_b_energie | B-vitamines en energie |
| 7 | adaptogenen_stress | Adaptogenen tegen stress |
| 8 | gut_brain_stemming | Darm-hersen verbinding |
| 9 | vitamine_e_huid | Vitamine E voor huid |
| 10 | vitamine_c_immuun | Vitamine C en immuniteit |
| 11 | zink_testosteron | Zink en testosteron |
| 12 | calcium_botten | Calcium voor botten |
| 13 | mct_energie | MCT voor energie |
| 14 | ijzer_vermoeidheid | IJzer tekort en moeheid |
| 15 | prebiotica_vezels | Prebiotica vs probiotica |

---

## Productpagina's

### Actieve Pagina's (WP IDs)

| WP ID | Slug | Product | Affiliate URL |
|---|---|---|---|
| 36 | homepage | — | — |
| 760 | hl5-peach-collagen | HL5 Collageen | nl-nl/hl5-peach |
| 982 | hl5-2pack | HL5 2-Pack | nl-nl/hl5-peach-2pack |
| 754 | edge-plus-mango | Edge Plus Mango | nl-nl/amareedge-plus-mango |
| 751 | edge-plus-watermelon | Edge Plus Watermeloen | nl-nl/amareedge-plus-watermelon |
| 758 | happy-juice-pack | Happy Juice Pack | nl-nl/amareedge-plus-mango |
| 9 | ignite-him | Ignite for Him | nl-nl/ignite-for-him |
| 10 | ignite-her | Ignite for Her | nl-nl/ignite-for-her |
| 22 | restore | Restore | nl-nl/restore |
| 12 | mentabiotics | MentaBiotics | nl-nl/mentabiotics |
| 14 | triangle-xtreme | Triangle Xtreme | nl-nl/triangle-of-wellness-xtreme |
| 327 | fit20 | Fit20 | nl-nl/fit20 |
| 25 | neunight-serum | NeuNight Serum | nl-nl/skin-mind-neunight |
| 1008 | amare-triangle-xtreme-3pack | Triangle 3-Pack | nl-nl/triangle-of-wellness-xtreme-3pack |

### Affiliate Link Formaat
```
✅ WERKT:  https://www.amare.com/2075008/nl-nl/[slug]
❌ 404:    https://www.amare.com/2075008/nl-NL/shop/[cat]/[slug]
```

---

## MailerLite Lead Capture

### Hoe het werkt
1. Bezoeker opent homepage → modal verschijnt na 3 seconden
2. Bezoeker vult e-mail in + klikt "Claim Mijn €8 Korting →"
3. JavaScript stuurt AJAX call naar WP (`wp-admin/admin-ajax.php`)
4. PHP handler (functions.php) roept MailerLite API aan
5. E-mail wordt toegevoegd aan groep "Amare NL Leads"

### MailerLite Configuratie
| Instelling | Waarde |
|---|---|
| Groep | Amare NL Leads |
| Groep ID | 185294849333790257 |
| API Key | In `.env` als `MAILERLITE_API_KEY` |
| WP optie | `amare_ml_key` (opgeslagen in WP database) |

### PHP Handler (functions.php)
- AJAX action: `amare_subscribe`
- Werkt voor niet-ingelogde bezoekers (`wp_ajax_nopriv_`)
- API token uit `get_option('amare_ml_key')`

### Leads Bekijken
→ mailerlite.com → Subscribers → Groep "Amare NL Leads"

---

## SEO Strategie

- **Blog onderwerpen**: informatief (voedingsstoffen) → trekt organisch verkeer
- **Productpagina's**: transactioneel (kopen, bestellen)
- **Lead magneet**: €8 kortingscode modal → e-mail verzamelen
- **Interne links**: blog artikelen linken naar productpagina's

---

## Scripts & Tools

| Script | Gebruik |
|---|---|
| `scripts/audit_affiliate_urls.py` | Controleer alle affiliate links |
| `scripts/fix_affiliate_links.py` | Fix specifieke links |
| `scripts/fix_all_affiliate_from_excel.py` | Sync vanuit Excel |
| `scripts/add_schema_markup.py` | JSON-LD schema toevoegen |
| `scripts/create_hl5_2pack.py` | HL5 2-Pack pagina aangemaakt |

Excel bron: `amare_bridge_site/astra_integration/products/AmareNL product lijst.xlsx`

---

## Veelvoorkomende Problemen

### Affiliate link geeft 404
- Gebruik altijd klein: `nl-nl/` (niet `nl-NL/shop/...`)
- Controleer via: `python3 scripts/audit_affiliate_urls.py`

### MailerLite subscribe werkt niet
- Test: `curl -X POST https://amarenl.com/wp-admin/admin-ajax.php -d "action=amare_subscribe&email=test@test.com"`
- Check functions.php → `amare_ml_subscribe` functie aanwezig?
- Check WP optie: `get_option('amare_ml_key')` niet leeg?

### Blog artikel wordt niet gepubliceerd
- Check logs: `tail /root/antigravity-ai/logs/article_amarenl.log`
- Test: `venv/bin/python3 scripts/daily_article_writer_amarenl.py`

---

## SEO/GEO Trafik Stratejisi

**Funnel:**
```
Google Arama → Blog Makalesi (/blog)
    → İlgili ürün sayfasına iç link
    → Satın al (affiliate) VEYA email bırak (€8 korting)
```

**Lokasyon sinyalleri:** "Nederland", "Amsterdam", "Utrecht" gibi geo terimler makalelere eklenmeli.

**Schema:** Article + FAQ JSON-LD her blog makalesine eklenmeli.

**Site Kit:** Google Analytics + Search Console bağlantısı — WP Admin → Site Kit kontrol et.

---

## Footer

- Homepage'e eklenmiş (ID: 36)
- Tasarım: mor (#3a1f50) + altın (#f5c048)
- İçerik: Snelle links / €8 korting form / Disclaimer
- MailerLite bağlı — footer formdan da lead toplanıyor

---

## Todo / Verbeterpunten

- [ ] Google Search Console + Analytics — Site Kit üzerinden kontrol
- [ ] Blog makaleleri → ürün sayfası iç linkler
- [ ] Article + FAQ schema makalelere ekle
- [ ] MailerLite welkomstmail flow aanmaken
- [ ] Yoast SEO meta handmatig invullen nieuwe pagina's (free plan)
- [ ] Featured images toevoegen aan blog artikelen
- [ ] A/B test modal: €8 korting vs gratis gids
- [ ] Fase 2: AI trend-based artikel generatie (na voltooiing vaste lijst)
