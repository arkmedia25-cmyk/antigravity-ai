"""
thumbnail_animated.py
─────────────────────
Generates animated HTML thumbnails + background visuals per video clip.
  • Vertical  9:16  → YouTube Shorts / Reels thumbnail
  • Horizontal 16:9 → YouTube long video thumbnail + background

Genre themes defined in GENRES dict — each slug gets its own palette & style.
Montage pipeline can reuse the same HTML files; render_png() exports a static
PNG snapshot via Playwright when needed.

Usage:
    from thumbnail_animated import make
    result = make(genre, channel="binaural", video_duration_min=3)
    # result["vertical"]  → Path to 9:16 HTML
    # result["horizontal"]→ Path to 16:9 HTML
    # result["png_v"]     → PNG (if render=True)
    # result["png_h"]     → PNG (if render=True)
"""

from pathlib import Path
from string import Template

THUMBNAILS_DIR = Path("thumbnails")

# ── Per-genre visual themes ────────────────────────────────────────────────────
# Keys: hue_primary, hue_secondary, label, sub, pills
GENRES: dict[str, dict] = {
    # Binaural / general
    "binaural-beats": dict(
        hue1=280, hue2=260,
        label="Binaural Mind",
        sub="Binaural Frequencies",
        pills=[("α","8–12Hz","290"),("θ","4–8Hz","220"),("δ","1–4Hz","260")],
        style="neural",
    ),
    # Delta – deep sleep
    "delta-wave-sleep": dict(
        hue1=220, hue2=200,
        label="Sleep Wave Music",
        sub="Delta Wave Sleep",
        pills=[("δ","0.5–4Hz","200"),("☾","Sleep","220"),("∞","Infinite","240")],
        style="float",
    ),
    # Alpha – relaxation
    "alpha-relaxation": dict(
        hue1=300, hue2=260,
        label="Binaural Mind",
        sub="Alpha Relaxation",
        pills=[("α","8–12Hz","300"),("♡","Calm","280"),("✦","Peace","260")],
        style="ripple",
    ),
    # Theta – meditation
    "theta-meditation": dict(
        hue1=160, hue2=200,
        label="Binaural Mind",
        sub="Theta Meditation",
        pills=[("θ","4–8Hz","160"),("☯","Zen","180"),("✦","Flow","200")],
        style="geo",
    ),
    # Gamma – focus / 40 Hz
    "gamma-focus": dict(
        hue1=180, hue2=200,
        label="Binaural Mind",
        sub="40Hz Gamma Focus",
        pills=[("γ","40Hz","180"),("⚡","Focus","200"),("◈","Sharp","160")],
        style="grid",
    ),
    # Nature / ambient
    "nature-sounds": dict(
        hue1=130, hue2=160,
        label="Sleep Wave Music",
        sub="Nature & Ambient",
        pills=[("🌿","Nature","130"),("🌊","Waves","160"),("☁","Peace","180")],
        style="float",
    ),
    # Piano / classical
    "piano-ambient": dict(
        hue1=50, hue2=30,
        label="Sleep Wave Music",
        sub="Piano & Ambient",
        pills=[("♪","Piano","50"),("✦","Ambient","30"),("♩","Soft","70")],
        style="ripple",
    ),
    # White noise / brown noise
    "white-noise": dict(
        hue1=210, hue2=230,
        label="Sleep Wave Music",
        sub="White & Brown Noise",
        pills=[("~","White","210"),("♦","Brown","230"),("∿","Pink","220")],
        style="wave",
    ),
}

# Fallback for unknown slugs
_DEFAULT_GENRE = GENRES["binaural-beats"]


def _resolve_genre(slug: str) -> dict:
    """Find best matching genre config for a given slug."""
    if slug in GENRES:
        return GENRES[slug]
    for key, cfg in GENRES.items():
        if key in slug or slug in key:
            return cfg
    return _DEFAULT_GENRE


def _pills_html(pills: list) -> str:
    rows = []
    for sym, lbl, hue in pills:
        rows.append(
            f'<span class="pill" style="'
            f'border-color:oklch(0.7 0.28 {hue}/.8);'
            f'color:oklch(0.88 0.25 {hue});'
            f'background:oklch(0.7 0.28 {hue}/.12)">'
            f'{sym} {lbl}</span>'
        )
    return " ".join(rows)


# ── Compact shared CSS (injected into both layouts) ────────────────────────────
_BASE_CSS = """
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
body{background:#000;display:flex;align-items:center;justify-content:center;min-height:100vh;font-family:'Outfit',sans-serif}
.stage{position:relative;overflow:hidden;border-radius:14px}
.bg{position:absolute;inset:0}
.ring{position:absolute;top:50%;left:50%;border-radius:50%;border:1px solid;transform-origin:center}
.orb{position:absolute;top:50%;left:50%;border-radius:50%;animation:pulse 3s ease-in-out infinite}
@keyframes pulse{0%,100%{transform:translate(-50%,-50%) scale(1)}50%{transform:translate(-50%,-50%) scale(1.07)}}
.wave-row{position:absolute;left:0;right:0;height:50px;overflow:hidden}
.wave-svg{width:200%;height:100%;animation:wscroll 2.8s linear infinite}
@keyframes wscroll{from{transform:translateX(0)}to{transform:translateX(-50%)}}
.bars{position:absolute;left:50%;transform:translateX(-50%);display:flex;align-items:flex-end;gap:3px}
.bar{border-radius:3px 3px 0 0;animation:bdance var(--d,.8s) ease-in-out infinite alternate;transform-origin:bottom}
@keyframes bdance{from{transform:scaleY(.15);opacity:.5}to{transform:scaleY(1);opacity:1}}
.pills{position:absolute;left:50%;transform:translateX(-50%);display:flex;gap:7px;flex-wrap:wrap;justify-content:center}
.pill{padding:3px 10px;border-radius:20px;border:1px solid;font-size:9px;font-family:'Space Mono',monospace;letter-spacing:.04em;white-space:nowrap;animation:pglow 3s ease-in-out infinite alternate}
@keyframes pglow{from{opacity:.6}to{opacity:1;filter:drop-shadow(0 0 5px currentColor)}}
.channel{position:absolute;top:32px;left:50%;transform:translateX(-50%);font-family:'Space Mono',monospace;font-size:10px;letter-spacing:.3em;text-transform:uppercase;white-space:nowrap;animation:fdown 1s ease-out both}
.title-block{position:absolute;text-align:center;padding:0 20px;animation:fup 1.2s ease-out .2s both}
.title{font-weight:900;line-height:1.05;letter-spacing:-.02em;background-clip:text;-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-wrap:balance}
.sub{font-weight:200;text-transform:uppercase;letter-spacing:.14em}
.corner{position:absolute;width:18px;height:18px;border-style:solid}
.corner-tl{top:12px;left:12px;border-width:2px 0 0 2px;border-radius:4px 0 0 0}
.corner-tr{top:12px;right:12px;border-width:2px 2px 0 0;border-radius:0 4px 0 0}
.corner-bl{bottom:12px;left:12px;border-width:0 0 2px 2px;border-radius:0 0 0 4px}
.corner-br{bottom:12px;right:12px;border-width:0 2px 2px 0;border-radius:0 0 4px 0}
.scan{position:absolute;inset:0;background:repeating-linear-gradient(to bottom,transparent 0 3px,rgba(0,0,0,.07) 3px 4px);pointer-events:none}
.particle{position:absolute;border-radius:50%;filter:blur(1px);animation:fup2 var(--d,6s) linear infinite;opacity:0}
@keyframes fup2{0%{opacity:0;transform:translateY(0)}10%{opacity:.7}90%{opacity:.3}100%{opacity:0;transform:translateY(-350px)}}
@keyframes fdown{from{opacity:0;transform:translateX(-50%) translateY(-12px)}to{opacity:1;transform:translateX(-50%) translateY(0)}}
@keyframes fup{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
"""

_FONTS = '<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@200;400;700;900&family=Space+Mono&display=swap" rel="stylesheet">'

_JS = """
(function(){
  const B=document.getElementById('bars');
  const D=[.6,.8,.5,.9,.7,1,.65,.75,.55,.85,.7,.9,.6,.8,.55,.95,.7,.5,.8,.65,.75,.6];
  const DL=[0,.1,.2,.05,.3,.15,.4,.25,.35,.1,.45,.2,.05,.3,.15,.4,.25,0,.35,.1,.2,.3];
  for(let i=0;i<22;i++){const b=document.createElement('div');b.className='bar';b.style.setProperty('--d',D[i%D.length]+'s');b.style.animationDelay=DL[i%DL.length]+'s';B.appendChild(b);}
  const S=document.getElementById('stage');
  for(let i=0;i<14;i++){const p=document.createElement('div');p.className='particle';const sz=Math.random()*3+1;p.style.cssText=`width:${sz}px;height:${sz}px;left:${10+Math.random()*80}%;bottom:${Math.random()*35}%;--d:${4+Math.random()*5}s;animation-delay:${Math.random()*5}s;background:${PCLR}`;S.appendChild(p);}
  const svg=document.getElementById('nsvg');
  const W=svg.viewBox.baseVal.width,H=svg.viewBox.baseVal.height,cx=W/2,cy=H*.42;
  const ns=[];
  for(let i=0;i<12;i++){const a=(i/12)*Math.PI*2,r=90+(i%3)*28;ns.push({x:cx+Math.cos(a)*r,y:cy+Math.sin(a)*r});}
  ns.push({x:W*.15,y:H*.22},{x:W*.85,y:H*.22},{x:W*.12,y:H*.72},{x:W*.88,y:H*.72});
  for(let i=0;i<ns.length;i++)for(let j=i+1;j<ns.length;j++){const dx=ns[i].x-ns[j].x,dy=ns[i].y-ns[j].y,d=Math.sqrt(dx*dx+dy*dy);if(d<160){const l=document.createElementNS('http://www.w3.org/2000/svg','line');l.setAttribute('x1',ns[i].x);l.setAttribute('y1',ns[i].y);l.setAttribute('x2',ns[j].x);l.setAttribute('y2',ns[j].y);const op=(1-d/160)*.35;l.setAttribute('stroke',LCLR.replace('OP',op));l.setAttribute('stroke-width','0.7');svg.appendChild(l);}}
  ns.forEach(n=>{const c=document.createElementNS('http://www.w3.org/2000/svg','circle');c.setAttribute('cx',n.x);c.setAttribute('cy',n.y);c.setAttribute('r','2');c.setAttribute('fill',NCLR);svg.appendChild(c);});
})();
"""


def _html(
    *,
    title_html: str,
    sub: str,
    label: str,
    pills_html: str,
    hue1: int,
    hue2: int,
    w: int,
    h: int,
    bar_h: int,
    font_sz: int,
    sub_sz: int,
    title_bottom: int,
    pills_bottom: int,
    bars_bottom: int,
    wave_bottom: int,
) -> str:
    orb_sz = min(w, h) * 0.38
    orb_off = orb_sz / 2
    ring1 = orb_sz * 1.7
    ring2 = orb_sz * 1.3
    corner_clr = f"oklch(0.6 0.25 {hue1}/.7)"
    p_clr = f"oklch(0.8 0.3 {hue1})"
    l_clr = f"oklch(0.65 0.3 {hue1} / OP)"
    n_clr = f"oklch(0.75 0.3 {hue1}/.7)"

    bars_css = f"height:{bar_h}px;bottom:{bars_bottom}px;"
    bar_item_css = f"width:4px;background:linear-gradient(to top,oklch(0.55 0.3 {hue2}),oklch(0.75 0.35 {hue1}))"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{label}</title>
{_FONTS}
<style>
{_BASE_CSS}
.stage{{width:{w}px;height:{h}px;box-shadow:0 0 60px oklch(0.55 0.3 {hue1}/.4)}}
.bg{{background:
  radial-gradient(ellipse 65% 55% at 50% 38%,oklch(0.18 0.18 {hue1}) 0%,transparent 70%),
  radial-gradient(ellipse 80% 55% at 50% 88%,oklch(0.12 0.14 {hue2}) 0%,transparent 60%),
  oklch(0.05 0.04 {hue1})}}
.ring1{{width:{ring1:.0f}px;height:{ring1:.0f}px;margin:-{ring1/2:.0f}px 0 0 -{ring1/2:.0f}px;
  border-color:oklch(0.5 0.22 {hue1}/.28);animation:spin1 20s linear infinite}}
.ring2{{width:{ring2:.0f}px;height:{ring2:.0f}px;margin:-{ring2/2:.0f}px 0 0 -{ring2/2:.0f}px;
  border-color:oklch(0.5 0.22 {hue2}/.2);animation:spin1 13s linear infinite reverse}}
@keyframes spin1{{to{{transform:rotate(360deg)}}}}
.orb{{width:{orb_sz:.0f}px;height:{orb_sz:.0f}px;margin:-{orb_off:.0f}px 0 0 -{orb_off:.0f}px;
  background:radial-gradient(circle at 40% 35%,oklch(0.65 0.35 {hue1}) 0%,oklch(0.45 0.3 {hue2}) 30%,oklch(0.22 0.18 {hue2}) 60%,oklch(0.1 0.08 {hue1}) 100%);
  box-shadow:0 0 35px oklch(0.6 0.35 {hue1}/.8),0 0 70px oklch(0.5 0.3 {hue2}/.4),0 0 130px oklch(0.4 0.25 {hue1}/.18)}}
.wave-row{{bottom:{wave_bottom}px}}
.bars{{{bars_css}}}
.bar{{{bar_item_css}}}
.pills{{bottom:{pills_bottom}px}}
.title-block{{bottom:{title_bottom}px;left:0;right:0}}
.title{{font-size:{font_sz}px;background:linear-gradient(150deg,oklch(.95 .05 {hue1}) 0%,oklch(.85 .25 {hue1}) 40%,oklch(.72 .32 {hue2}) 100%)}}
.sub{{font-size:{sub_sz}px;color:oklch(0.65 0.15 {hue1});margin-top:6px}}
.channel{{color:oklch(0.7 0.2 {hue1})}}
.corner{{border-color:{corner_clr}}}
</style>
</head>
<body>
<div class="stage" id="stage">
  <div class="bg"></div>
  <div class="corner corner-tl"></div><div class="corner corner-tr"></div>
  <div class="corner corner-bl"></div><div class="corner corner-br"></div>
  <svg id="nsvg" class="neural-svg" viewBox="0 0 {w} {h}" style="position:absolute;inset:0;width:100%;height:100%;opacity:.45"></svg>
  <div class="ring ring1"></div>
  <div class="ring ring2"></div>
  <div class="orb"></div>
  <div class="wave-row">
    <svg class="wave-svg" viewBox="0 0 810 50" preserveAspectRatio="none">
      <defs>
        <linearGradient id="wg"><stop offset="0%" stop-color="transparent"/>
          <stop offset="15%" stop-color="oklch(0.65 0.3 {hue1})"/>
          <stop offset="85%" stop-color="oklch(0.65 0.3 {hue2})"/>
          <stop offset="100%" stop-color="transparent"/></linearGradient>
        <filter id="gl"><feGaussianBlur stdDeviation="1.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
      </defs>
      <path d="M0,25 L25,25 L30,8 L35,42 L40,4 L45,46 L50,12 L55,38 L60,22 L65,25 L85,25 L95,18 L105,32 L115,14 L125,36 L130,25 L150,25 L155,9 L160,41 L165,5 L170,45 L175,15 L180,35 L185,24 L190,25 L215,25 L225,17 L235,33 L240,25 L260,25 L265,8 L270,42 L275,4 L280,46 L285,12 L290,38 L295,22 L300,25 L320,25 L330,18 L340,32 L350,14 L360,36 L365,25 L385,25 L390,9 L395,41 L400,5 L405,45 L410,15 L415,35 L420,24 L425,25 L450,25 L460,17 L470,33 L475,25 L495,25 L500,8 L505,42 L510,4 L515,46 L520,12 L525,38 L530,22 L535,25 L555,25 L565,18 L575,32 L585,14 L595,36 L600,25 L620,25 L625,9 L630,41 L635,5 L640,45 L645,15 L650,35 L655,24 L660,25 L685,25 L695,17 L705,33 L715,25 L810,25"
        fill="none" stroke="url(#wg)" stroke-width="1.5" filter="url(#gl)"/>
    </svg>
  </div>
  <div class="bars" id="bars"></div>
  <div class="pills">{pills_html}</div>
  <div class="channel">{label}</div>
  <div class="title-block">
    <div class="title">{title_html}</div>
    <div class="sub">{sub}</div>
  </div>
  <div class="scan"></div>
</div>
<script>
const PCLR='{p_clr}';
const LCLR='{l_clr}';
const NCLR='{n_clr}';
{_JS}
</script>
</body>
</html>"""


def _split_title(title: str, chars: int = 16) -> str:
    words = title.split()
    mid = max(1, len(words) // 2)
    l1, l2 = " ".join(words[:mid]), " ".join(words[mid:])
    return f"{l1}<br>{l2}" if l2 else l1


def make_vertical(genre: dict, channel: str, video_duration_min: int, out_dir: Path) -> Path:
    """9:16 – 405×720 for Shorts / Reels thumbnail + background."""
    cfg = _resolve_genre(genre.get("slug", ""))
    slug = genre.get("slug", "track")
    raw = genre.get("title", "Deep Focus").format(duration=video_duration_min, year=2025)

    html = _html(
        title_html=_split_title(raw, 14),
        sub=cfg["sub"],
        label=channel or cfg["label"],
        pills_html=_pills_html(cfg["pills"]),
        hue1=cfg["hue1"], hue2=cfg["hue2"],
        w=405, h=720,
        bar_h=36, font_sz=34, sub_sz=11,
        title_bottom=48, pills_bottom=88, bars_bottom=128, wave_bottom=175,
    )
    path = out_dir / f"{slug}_vertical.html"
    path.write_text(html, encoding="utf-8")
    print(f"[thumb-anim] vertical → {path}")
    return path


def make_horizontal(genre: dict, channel: str, video_duration_min: int, out_dir: Path) -> Path:
    """16:9 – 1280×720 for YouTube thumbnail + background."""
    cfg = _resolve_genre(genre.get("slug", ""))
    slug = genre.get("slug", "track")
    raw = genre.get("title", "Deep Focus").format(duration=video_duration_min, year=2025)

    html = _html(
        title_html=_split_title(raw, 22),
        sub=cfg["sub"],
        label=channel or cfg["label"],
        pills_html=_pills_html(cfg["pills"]),
        hue1=cfg["hue1"], hue2=cfg["hue2"],
        w=1280, h=720,
        bar_h=44, font_sz=64, sub_sz=18,
        title_bottom=60, pills_bottom=120, bars_bottom=170, wave_bottom=220,
    )
    path = out_dir / f"{slug}_horizontal.html"
    path.write_text(html, encoding="utf-8")
    print(f"[thumb-anim] horizontal → {path}")
    return path


def render_png(html_path: Path, out_png: Path, w: int, h: int) -> Path:
    """Render HTML → PNG via Playwright. pip install playwright && playwright install chromium"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise ImportError("Run: pip install playwright && playwright install chromium")
    out_png.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        page = br.new_page(viewport={"width": w, "height": h})
        page.goto(html_path.resolve().as_uri())
        page.wait_for_timeout(1500)
        page.locator(".stage").screenshot(path=str(out_png))
        br.close()
    print(f"[thumb-anim] PNG → {out_png}")
    return out_png


def make(
    genre: dict,
    channel: str = "binaural",
    video_duration_min: int = 1,
    out_dir: Path | None = None,
    render: bool = False,
) -> dict:
    """
    Generate animated thumbnails for one video clip.
    Returns dict: {vertical, horizontal, png_v, png_h}
    """
    save = out_dir or THUMBNAILS_DIR
    save.mkdir(parents=True, exist_ok=True)

    v = make_vertical(genre, channel, video_duration_min, save)
    h = make_horizontal(genre, channel, video_duration_min, save)

    png_v = png_h = None
    if render:
        slug = genre.get("slug", "track")
        try:
            png_v = render_png(v, save / f"{slug}_vertical.png",   405,  720)
            png_h = render_png(h, save / f"{slug}_horizontal.png", 1280, 720)
        except Exception as e:
            print(f"[thumb-anim] PNG skipped: {e}")

    return {"vertical": v, "horizontal": h, "png_v": png_v, "png_h": png_h}


# ── CLI test ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import webbrowser, sys
    slug = sys.argv[1] if len(sys.argv) > 1 else "delta-wave-sleep"
    g = {"slug": slug, "title": "{duration}H Deep Sleep Music"}
    r = make(g, channel="Sleep Wave Music", video_duration_min=3)
    webbrowser.open(r["vertical"].resolve().as_uri())
    webbrowser.open(r["horizontal"].resolve().as_uri())
    print("Opened both formats.")
