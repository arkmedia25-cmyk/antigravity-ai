# AmarereView.nl — Blog Automatisering Documentatie

> Site: https://amarereview.nl
> Doel: Organisch SEO-verkeer genereren via productreviews → doorverwijzen naar amarenl.com affiliate links
> Laatste update: 2026-04-20

---

## Overzicht

Elke dag om **09:00** wordt automatisch één Nederlands artikel gepubliceerd op amarereview.nl.
Het artikel is een eerlijke productreview over een Amare supplement.

### Wat wordt gepubliceerd?
- ~900 woorden Nederlandse productreview
- HTML opmaak (geen Markdown)
- SEO-geoptimaliseerd (Yoast focus keyword + meta description)
- Affiliate CTA knoppen (30-dagen garantie blok)
- JSON-LD schema markup (Review + AggregateRating)

---

## Bestanden

| Bestand | Functie |
|---|---|
| `scripts/article_writer.py` | Artikel genereren + publiceren op WP |
| `scripts/daily_article_writer.py` | Dagelijkse scheduler, bijhoudt voortgang |
| `article_writer_state.json` | State bestand: welke artikelen al geschreven |

---

## Hoe Werkt Het?

### 1. State management
`article_writer_state.json` houdt bij welke producten al geschreven zijn:
```json
{
  "completed": ["restore", "on_shots", "happy_juice_kopen"],
  "last_run": "2026-04-20T09:25:31"
}
```
Als alle producten geschreven zijn → cyclus begint opnieuw.

### 2. Artikel generatie
- AI schrijft review via OpenAI GPT-4o
- Structuur: Wat is het? / Ervaringen / Ingrediënten / Voor- & nadelen / Prijs / Conclusie
- Affiliate link: `https://www.amare.com/2075008/nl-NL/[slug]`
- 30-dagen garantie blok wordt automatisch ingevoegd

### 3. WordPress publicatie
- API: `https://amarereview.nl/wp-json/wp/v2/posts`
- Auth: `arkmedia25@gmail.com` + app password
- Status: direct `publish`
- Als slug al bestaat → artikel wordt bijgewerkt (niet gedupliceerd)

---

## Cron Schedule

```bash
# Actieve cron op DO server
0 9 * * * cd /root/antigravity-ai && venv/bin/python3 scripts/daily_article_writer.py >> logs/article_cron.log 2>&1
```

Log bekijken:
```bash
tail -f /root/antigravity-ai/logs/article_cron.log
```

---

## Product Wachtrij (21 artikelen)

| # | Product Key | Status |
|---|---|---|
| 1 | restore | ✅ |
| 2 | on_shots | ✅ |
| 3 | origin | ✅ |
| 4 | ignite_him | ✅ |
| 5 | ignite_her | ✅ |
| 6 | hl5 | ✅ |
| 7 | happy_juice_kopen | ✅ |
| 8 | happy_juice_bijwerkingen | ⏳ |
| 9 | amare_vs_concurrenten | ⏳ |
| 10 | gut_brain | ⏳ |
| 11 | happy_juice | ⏳ |
| 12 | sunrise | ⏳ |
| 13 | sunset | ⏳ |
| 14 | edge | ⏳ |
| 15 | triangle | ⏳ |
| 16 | mentabiotics | ⏳ |
| 17 | nitro_xtreme | ⏳ |
| 18 | fit20 | ⏳ |
| 19 | skin_to_mind | ⏳ |
| 20 | rootist | ⏳ |
| 21 | edge_mango | ⏳ |

---

## Handmatig Artikel Schrijven

```bash
# Eén specifiek product
cd /root/antigravity-ai
venv/bin/python3 scripts/daily_article_writer.py

# Of direct
venv/bin/python3 scripts/article_writer.py happy_juice
```

---

## WordPress Configuratie

| Instelling | Waarde |
|---|---|
| Site URL | https://amarereview.nl |
| WP gebruiker | arkmedia25@gmail.com |
| App password | In `.env` als `WP_REVIEW_APP_PASS` |
| Post type | `posts` (blog artikelen) |
| Affiliate ID | 2075008 |

---

## Veelvoorkomende Problemen

### Artikel wordt niet gepubliceerd
1. Check logs: `tail /root/antigravity-ai/logs/article_cron.log`
2. Controleer `.env` op `OPENAI_API_KEY`
3. Test handmatig: `venv/bin/python3 scripts/article_writer.py restore`

### Dubbele artikelen
- Script controleert slug voor publicatie → update bestaande indien aanwezig
- Geen duplicaten mogelijk

### Yoast SEO meta werkt niet
- Free Yoast registreert `_yoast_wpseo_*` niet via REST API
- Handmatig invullen via WP Admin → Bericht bewerken → Yoast blok onderaan

---

## SEO Strategie

- **Focus keywords**: "[product] ervaringen", "[product] review", "[product] kopen nederland"
- **Interne links**: elk artikel linkt naar amarenl.com productpagina
- **Schema markup**: Review + AggregateRating JSON-LD (add_schema_markup.py gedraaid)
- **Google indexering**: google_index_notify.py stuurt ping na publicatie

---

## Todo / Verbeterpunten

- [ ] Yoast SEO meta handmatig invullen voor nieuwe artikelen
- [ ] Google Search Console koppelen voor rankingdata
- [ ] Interne linkstructuur verbeteren (pillar content → productreviews)
- [ ] Featured images automatisch genereren via Pexels/Canva
- [ ] E-mail lead capture toevoegen aan amarereview.nl (zoals amarenl.com)
