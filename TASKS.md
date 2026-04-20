# Antigravity Agency OS — Taak & Bug Tracker

> Laatste update: 2026-04-20 (avond)
> Gebruik `/tasks` skill om dit bestand te lezen en bij te werken via Claude.

---

## 🔴 ACTIEF (In Progress)

| ID | Taak | Bestand/Systeem | Eigenaar |
|---|---|---|---|
| T-001 | Server .env updaten met MAILERLITE_API_KEY | DO Server `.env` | Musa |
| T-002 | Yoast SEO meta handmatig invullen nieuwe pagina's | amarenl.com WP Admin | Musa |

---

## 🟡 GEPLAND (Todo)

| ID | Taak | Bestand/Systeem | Prioriteit |
|---|---|---|---|
| T-003 | amarenl.com blog cron testen (10:00 run) | `scripts/daily_article_writer_amarenl.py` | Hoog |
| T-004 | MailerLite welkomstmail flow aanmaken | mailerlite.com dashboard | Middel |
| T-005 | Google Search Console + Analytics controleren via Site Kit | amarenl.com WP Admin → Site Kit | Hoog |
| T-006 | Blog → Ürün sayfası iç linkler ekle | `scripts/article_writer_amarenl.py` | Hoog |
| T-007 | Article schema (FAQ + Article JSON-LD) blog makaleleri | `scripts/article_writer_amarenl.py` | Middel |
| T-008 | Instagram auto-publish testen (pub_ callback) | `src/interfaces/telegram/handler.py` | Middel |
| T-009 | MailerLite welkomstmail automatie aanmaken | mailerlite.com dashboard | Middel |
| T-010 | Canva OAuth 400 error diagnosticeren | `skills/heygen/` | Laag |
| T-011 | SQLite WAL mode inschakelen (concurrent writes) | `src/memory/memory_manager.py` | Laag |

---

## ✅ VOLTOOID (Afgerond)

| ID | Taak | Datum | Notities |
|---|---|---|---|
| ✅ | Bot video pipeline — 10+ bugs opgelost | 2026-04-20 | Brand routing, MCP timeout, Markdown parse, Ken Burns |
| ✅ | amarenl.com bridge site audit & fix | 2026-04-20 | 12 affiliate links, 4 nieuwe pagina's aangemaakt |
| ✅ | SEO/GEO optimalisatie amarenl.com pagina's | 2026-04-20 | JSON-LD schema, meta descriptions |
| ✅ | MailerLite lead capture homepage | 2026-04-20 | AJAX handler, groep "Amare NL Leads" aangemaakt |
| ✅ | Daily article writer cron — amarereview.nl | 2026-04-20 | Elke dag 09:00 via cron |
| ✅ | Daily article writer cron — amarenl.com | 2026-04-20 | Elke dag 10:00 via cron |
| ✅ | 2GB swap geheugen DO server | 2026-04-20 | OOM kills opgelost |
| ✅ | amarenl.com custom footer | 2026-04-20 | Mor/altın tasarım, MailerLite form, disclaimer |
| ✅ | amarenl.com /blog sayfası + menu linki | 2026-04-20 | WP blog index ayarlı, Hoofdmenu'ye eklendi |
| ✅ | WPCode plugin kurulumu | 2026-04-20 | Tüm sayfalara script enjeksiyonu için |

---

## 🐛 BEKENDE BUGS

| ID | Bug | Bestand | Status |
|---|---|---|---|
| B-001 | MCP bridge beschikbaar maar niet geconfigureerd | `src/skills/mcp_client.py` | Omzeild (use_mcp=False) |
| B-002 | Canva OAuth token exchange 400 error | `skills/heygen/` | Open |
| B-003 | memory.db in src/ — gewist bij redeploy | `src/memory/memory_manager.py` | Open |

---

## 📋 SYSTEEM OVERZICHT

| Systeem | Status | Cron |
|---|---|---|
| Telegram Bot | ✅ Online (PM2) | — |
| Video Pipeline | ✅ Werkt | 08:00 / 12:30 / 20:15 / 22:00 |
| amarereview.nl artikelen | ✅ Actief | 09:00 dagelijks |
| amarenl.com artikelen | ✅ Actief | 10:00 dagelijks |
| MailerLite lead capture | ✅ Actief | — |
| amarenl.com footer | ✅ Actief (homepage) | — |
| amarenl.com /blog | ✅ Actief | — |
| Google Site Kit | ⚠️ Kurulu, bağlantı kontrol edilmeli | — |
