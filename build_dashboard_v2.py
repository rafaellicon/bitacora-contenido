# -*- coding: utf-8 -*-
import json
import html as htmlmod
from datetime import datetime

COMBINED_PATH = r"C:\Users\rafae\Documentos\IA\Claude\GHL\dashboard\bitacora-contenido\audit_combined.json"
SUMMARY_PATH = r"C:\Users\rafae\Documentos\IA\Claude\GHL\dashboard\bitacora-contenido\audit_summary.json"
OUT_PATH = r"C:\Users\rafae\Documentos\IA\Claude\GHL\dashboard\bitacora-contenido\bitacora_contenido.html"

BRAND_FULL = {
    "ETV": "Estuvisa", "ETH": "España Te Homologa", "NAC": "Nacionalízate",
    "MNEE": "Mi Negocio en España", "C&A": "Cohen y Aguirre",
}
FORMAT_LABEL = {
    "Reel de Instagram": "Reel", "Secuencia de Instagram": "Carrusel", "Imagen de Instagram": "Imagen",
}
BRANDS = ["ETV", "ETH", "NAC", "MNEE", "C&A"]

with open(COMBINED_PATH, encoding="utf-8") as f:
    combined = json.load(f)
with open(SUMMARY_PATH, encoding="utf-8") as f:
    summary = json.load(f)

def fmt(n):
    return f"{int(n):,}".replace(",", ".")

def esc(s):
    return htmlmod.escape(s or "", quote=True)

def short_title(caption):
    line = (caption or "").split("\n")[0].strip()
    if len(line) > 88:
        line = line[:85].rstrip() + "..."
    return line or "(sin texto)"

def fmt_date(s):
    s = (s or "").strip()
    for fi in ("%m/%d/%Y %H:%M", "%m/%d/%Y"):
        try:
            d = datetime.strptime(s, fi)
            meses = ["ene","feb","mar","abr","may","jun","jul","ago","sep","oct","nov","dic"]
            return f"{d.day} {meses[d.month-1]} {d.year}"
        except ValueError:
            continue
    return s[:10]

def find_best_overall(metric):
    best = None
    for brand in BRANDS:
        for p in combined[brand]["posts"].values():
            if best is None or p[metric] > best[metric]:
                best = p
    return best

def render_stat_value(p, key):
    return f"{p[key]}%" if key == "engagement_rate" else fmt(p[key])

def render_hero(p, metric_key, metric_label, eyebrow):
    # Las otras 3 tarjetas muestran las métricas restantes del pool fijo, sin repetir la principal.
    pool = [("reach", "Alcance"), ("interactions", "Interacciones"),
            ("follows", "Seguidores"), ("engagement_rate", "Tasa")]
    others = [(k, l) for k, l in pool if k != metric_key][:3]
    gold_key = "follows"

    other_cards = ""
    for k, l in others:
        cls = " hero-stat-gold" if k == gold_key else ""
        other_cards += f"""
          <div class="hero-stat{cls}">
            <span class="hero-stat-value">{render_stat_value(p, k)}</span>
            <span class="hero-stat-label">{esc(l)}</span>
          </div>"""

    return f"""
    <section class="hero">
      <div class="hero-eyebrow">{esc(eyebrow)}</div>
      <div class="hero-grid">
        <div class="hero-main">
          <div class="hero-brand">{esc(BRAND_FULL[p['brand']])} <span class="hero-brand-code">{esc(p['brand'])}</span></div>
          <h2 class="hero-title">{esc(short_title(p['caption']))}</h2>
          <div class="hero-tags">
            <span class="tag">{esc(p['theme'])}</span>
            <span class="tag tag-format">{esc(FORMAT_LABEL.get(p['post_type'], p['post_type']))}</span>
            <span class="tag tag-date">{esc(fmt_date(p['publish_time']))}</span>
          </div>
          <a class="hero-link" href="{esc(p['permalink'])}" target="_blank" rel="noopener">Ver publicación en Instagram ↗</a>
        </div>
        <div class="hero-stats">
          <div class="hero-stat hero-stat-primary">
            <span class="hero-stat-value">{render_stat_value(p, metric_key)}</span>
            <span class="hero-stat-label">{esc(metric_label)}</span>
          </div>
          {other_cards}
        </div>
      </div>
    </section>"""

def render_table(posts_by_id, id_order, highlight_col):
    rows = []
    for i, pid in enumerate(id_order, start=1):
        p = posts_by_id[pid]
        def cell(key, cls=""):
            val = p[key]
            display = f"{val}%" if key == "engagement_rate" else fmt(val)
            hl = " hl" if key == highlight_col else ""
            return f'<td class="num{hl} {cls}">{display}</td>'
        rows.append(f"""
          <tr>
            <td class="col-rank">{i}</td>
            <td class="col-title">
              <div class="row-title">{esc(short_title(p['caption']))}</div>
              <div class="row-meta">
                <span class="tag">{esc(p['theme'])}</span>
                <span class="tag tag-format">{esc(FORMAT_LABEL.get(p['post_type'], p['post_type']))}</span>
              </div>
            </td>
            <td class="col-date">{esc(fmt_date(p['publish_time']))}</td>
            {cell('reach')}
            {cell('interactions')}
            {cell('engagement_rate')}
            {cell('follows', 'num-gold')}
            {cell('saves')}
            <td class="col-link"><a href="{esc(p['permalink'])}" target="_blank" rel="noopener">Ver ↗</a></td>
          </tr>""")
    return "".join(rows)

def render_brand_section(brand):
    data = combined[brand]
    posts_by_id = data["posts"]
    s = summary[brand]

    return f"""
    <section class="brand-section" id="brand-{brand.lower().replace('&','')}">
      <div class="brand-header">
        <div class="brand-name-block">
          <h3 class="brand-name">{esc(brand)}</h3>
          <div class="brand-full-name">{esc(BRAND_FULL[brand])}</div>
        </div>
        <div class="brand-summary">
          <div class="summary-stat">
            <span class="summary-value">{fmt(s['total_posts'])}</span>
            <span class="summary-label">publicaciones (1 año)</span>
          </div>
          <div class="summary-stat">
            <span class="summary-value">{fmt(s['total_reach'])}</span>
            <span class="summary-label">alcance acumulado</span>
          </div>
          <div class="summary-stat summary-stat-gold">
            <span class="summary-value">{fmt(s['total_follows'])}</span>
            <span class="summary-label">seguidores generados</span>
          </div>
        </div>
      </div>

      <div class="ranking-block">
        <h4 class="ranking-title">Top por alcance <span class="ranking-sub">— mayor exposición</span></h4>
        <div class="table-wrap">
          <table>
            <thead><tr>
              <th class="col-rank">#</th><th class="col-title">Publicación</th><th class="col-date">Fecha</th>
              <th class="num hl">Alcance</th><th class="num">Interacc.</th><th class="num">Tasa</th>
              <th class="num">Seguid.</th><th class="num">Guard.</th><th class="col-link"></th>
            </tr></thead>
            <tbody>{render_table(posts_by_id, data['by_reach'], 'reach')}</tbody>
          </table>
        </div>
      </div>

      <div class="ranking-block">
        <h4 class="ranking-title">Top por interacción <span class="ranking-sub">— mejores candidatos a campaña</span></h4>
        <div class="table-wrap">
          <table>
            <thead><tr>
              <th class="col-rank">#</th><th class="col-title">Publicación</th><th class="col-date">Fecha</th>
              <th class="num">Alcance</th><th class="num hl">Interacc.</th><th class="num hl">Tasa</th>
              <th class="num">Seguid.</th><th class="num">Guard.</th><th class="col-link"></th>
            </tr></thead>
            <tbody>{render_table(posts_by_id, data['by_interaction'], 'interactions')}</tbody>
          </table>
        </div>
      </div>
    </section>"""

brand_nav = "".join(f'<a href="#brand-{b.lower().replace("&","")}" class="nav-pill">{esc(b)}</a>' for b in BRANDS)
brand_sections = "".join(render_brand_section(b) for b in BRANDS)

best_reach = find_best_overall("reach")
best_engagement = find_best_overall("engagement_rate")

total_reach_all = sum(s["total_reach"] for s in summary.values())
total_follows_all = sum(s["total_follows"] for s in summary.values())
total_posts_all = sum(s["total_posts"] for s in summary.values())

html_doc = f"""<title>Bitácora de Contenido</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #EEF1F6; --surface: #FFFFFF; --surface-2: #F5F7FA; --text: #161A22; --text-muted: #5B6472;
    --border: #DCE1E9; --accent: #2B4C8C; --accent-soft: #E4EAF6; --gold: #A9781F; --gold-soft: #F3E7CE;
    --font-display: 'Fraunces', Georgia, 'Times New Roman', serif;
    --font-body: 'IBM Plex Sans', -apple-system, Segoe UI, sans-serif;
    --font-mono: 'IBM Plex Mono', 'SFMono-Regular', Consolas, monospace;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) {{
      --bg: #10141C; --surface: #171D28; --surface-2: #1D2430; --text: #E7EAF0; --text-muted: #8B95A6;
      --border: #262E3D; --accent: #7FA0DE; --accent-soft: #223251; --gold: #E0B15F; --gold-soft: #3A2E17;
    }}
  }}
  :root[data-theme="dark"] {{
    --bg: #10141C; --surface: #171D28; --surface-2: #1D2430; --text: #E7EAF0; --text-muted: #8B95A6;
    --border: #262E3D; --accent: #7FA0DE; --accent-soft: #223251; --gold: #E0B15F; --gold-soft: #3A2E17;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{ background: var(--bg); color: var(--text); font-family: var(--font-body); font-size: 15px; line-height: 1.55; -webkit-font-smoothing: antialiased; }}
  a {{ color: var(--accent); }}
  a:focus-visible, button:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
  .page {{ max-width: 1180px; margin: 0 auto; padding: 48px 24px 96px; }}
  .masthead {{ margin-bottom: 32px; }}
  .masthead-eyebrow {{ font-family: var(--font-mono); font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-muted); margin-bottom: 10px; }}
  .masthead h1 {{ font-family: var(--font-display); font-weight: 600; font-size: clamp(32px, 5vw, 46px); margin: 0 0 10px; text-wrap: balance; letter-spacing: -0.01em; }}
  .masthead p {{ margin: 0; color: var(--text-muted); max-width: 62ch; font-size: 15.5px; }}
  .totals-strip {{ display: flex; gap: 28px; flex-wrap: wrap; margin-top: 24px; padding-top: 20px; border-top: 1px solid var(--border); }}
  .totals-strip .t-item {{ display: flex; flex-direction: column; gap: 2px; }}
  .totals-strip .t-value {{ font-family: var(--font-mono); font-weight: 600; font-size: 20px; font-variant-numeric: tabular-nums; }}
  .totals-strip .t-label {{ font-size: 12.5px; color: var(--text-muted); }}
  nav.brand-nav {{ display: flex; gap: 8px; flex-wrap: wrap; margin: 28px 0 40px; }}
  .nav-pill {{ font-family: var(--font-mono); font-size: 13px; padding: 7px 14px; border-radius: 999px; border: 1px solid var(--border); color: var(--text); text-decoration: none; background: var(--surface); transition: border-color .15s ease, background .15s ease; }}
  .nav-pill:hover {{ border-color: var(--accent); background: var(--accent-soft); }}
  .hero {{ background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 28px 30px; margin-bottom: 28px; }}
  .hero-eyebrow {{ font-family: var(--font-mono); font-size: 11.5px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--gold); margin-bottom: 16px; font-weight: 600; }}
  .hero-grid {{ display: grid; grid-template-columns: 1.4fr 1fr; gap: 32px; align-items: center; }}
  .hero-brand {{ font-family: var(--font-mono); font-size: 13px; color: var(--text-muted); margin-bottom: 8px; }}
  .hero-brand-code {{ color: var(--accent); font-weight: 600; }}
  .hero-title {{ font-family: var(--font-display); font-weight: 600; font-size: clamp(20px, 2.6vw, 27px); margin: 0 0 16px; text-wrap: balance; line-height: 1.25; }}
  .hero-tags {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 18px; }}
  .hero-link {{ font-size: 14px; font-weight: 600; text-decoration: none; }}
  .hero-link:hover {{ text-decoration: underline; }}
  .hero-stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  .hero-stat {{ background: var(--surface-2); border-radius: 10px; padding: 14px 16px; display: flex; flex-direction: column; gap: 4px; }}
  .hero-stat-value {{ font-family: var(--font-mono); font-weight: 600; font-size: 22px; font-variant-numeric: tabular-nums; }}
  .hero-stat-label {{ font-size: 12px; color: var(--text-muted); }}
  .hero-stat-primary .hero-stat-value {{ color: var(--accent); }}
  .hero-stat-gold {{ background: var(--gold-soft); }}
  .hero-stat-gold .hero-stat-value {{ color: var(--gold); }}
  .heroes-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 48px; }}
  .heroes-row .hero {{ margin-bottom: 0; }}
  .tag {{ display: inline-block; font-size: 11.5px; padding: 3px 9px; border-radius: 999px; border: 1px solid var(--border); color: var(--text-muted); background: var(--surface-2); white-space: nowrap; }}
  .tag-format {{ font-family: var(--font-mono); }}
  .brand-section {{ margin-bottom: 60px; scroll-margin-top: 20px; }}
  .brand-header {{ display: flex; justify-content: space-between; align-items: flex-end; flex-wrap: wrap; gap: 18px; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 2px solid var(--border); }}
  .brand-name {{ font-family: var(--font-display); font-weight: 600; font-size: 30px; margin: 0; letter-spacing: -0.01em; }}
  .brand-full-name {{ color: var(--text-muted); font-size: 13.5px; margin-top: 2px; }}
  .brand-summary {{ display: flex; gap: 24px; flex-wrap: wrap; }}
  .summary-stat {{ display: flex; flex-direction: column; gap: 2px; text-align: right; }}
  .summary-value {{ font-family: var(--font-mono); font-weight: 600; font-size: 18px; font-variant-numeric: tabular-nums; }}
  .summary-label {{ font-size: 11.5px; color: var(--text-muted); }}
  .summary-stat-gold .summary-value {{ color: var(--gold); }}
  .ranking-block {{ margin-bottom: 26px; }}
  .ranking-title {{ font-family: var(--font-body); font-size: 14px; font-weight: 600; margin: 0 0 10px; }}
  .ranking-sub {{ font-weight: 400; color: var(--text-muted); font-size: 13px; }}
  .table-wrap {{ overflow-x: auto; border: 1px solid var(--border); border-radius: 12px; background: var(--surface); }}
  table {{ width: 100%; border-collapse: collapse; min-width: 820px; }}
  thead th {{ text-align: left; font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); font-weight: 600; padding: 12px 14px; border-bottom: 1px solid var(--border); position: sticky; top: 0; background: var(--surface); }}
  thead th.hl {{ color: var(--accent); }}
  tbody tr {{ border-bottom: 1px solid var(--border); }}
  tbody tr:last-child {{ border-bottom: none; }}
  tbody tr:hover {{ background: var(--surface-2); }}
  td {{ padding: 11px 14px; vertical-align: top; }}
  .col-rank {{ font-family: var(--font-mono); color: var(--text-muted); width: 32px; }}
  .col-title {{ min-width: 230px; }}
  .row-title {{ font-weight: 500; margin-bottom: 6px; line-height: 1.4; }}
  .row-meta {{ display: flex; gap: 6px; flex-wrap: wrap; }}
  .col-date {{ color: var(--text-muted); font-size: 13px; white-space: nowrap; }}
  th.num, td.num {{ text-align: right; font-family: var(--font-mono); font-variant-numeric: tabular-nums; white-space: nowrap; }}
  td.num.hl {{ color: var(--accent); font-weight: 600; }}
  .num-gold {{ color: var(--gold); font-weight: 600; }}
  .col-link {{ text-align: right; white-space: nowrap; }}
  .col-link a {{ font-size: 13px; font-weight: 600; text-decoration: none; }}
  .col-link a:hover {{ text-decoration: underline; }}
  footer.page-footer {{ margin-top: 64px; padding-top: 20px; border-top: 1px solid var(--border); color: var(--text-muted); font-size: 12.5px; }}
  @media (max-width: 900px) {{ .heroes-row {{ grid-template-columns: 1fr; }} }}
  @media (max-width: 760px) {{
    .hero-grid {{ grid-template-columns: 1fr; }}
    .hero-stats {{ grid-template-columns: repeat(4, 1fr); }}
    .brand-header {{ align-items: flex-start; }}
    .brand-summary {{ gap: 16px; }}
  }}
</style>

<div class="page">
  <header class="masthead">
    <div class="masthead-eyebrow">Auditoría de contenido orgánico &middot; sep 2025&ndash;ago 2026 (1 año)</div>
    <h1>Bitácora de Contenido</h1>
    <p>Reels, carruseles y fotos publicados en Instagram por las 5 marcas. Cada marca trae dos rankings — por alcance (mayor exposición) y por interacción (mejor candidato a campaña) — con tema, formato, fecha y enlace a la publicación original.</p>
    <div class="totals-strip">
      <div class="t-item"><span class="t-value">{fmt(total_posts_all)}</span><span class="t-label">publicaciones analizadas</span></div>
      <div class="t-item"><span class="t-value">{fmt(total_reach_all)}</span><span class="t-label">alcance acumulado</span></div>
      <div class="t-item"><span class="t-value">{fmt(total_follows_all)}</span><span class="t-label">seguidores generados</span></div>
    </div>
  </header>

  <nav class="brand-nav">{brand_nav}</nav>

  <div class="heroes-row">
    {render_hero(best_reach, 'reach', 'Alcance', 'Mayor alcance del periodo')}
    {render_hero(best_engagement, 'engagement_rate', 'Tasa de interacción', 'Mayor tasa de interacción del periodo')}
  </div>

  {brand_sections}

  <footer class="page-footer">
    Fuente: Meta Business Suite &middot; Estadísticas de contenido, exportado el 1 sep 2026. Interacción = me gusta + comentarios + compartidos + guardados. Tasa = interacción / alcance. Alcance/interacciones orgánicas no están disponibles vía la API pública con el permiso actual — estos datos vienen directamente de la interfaz de Business Suite. Temas clasificados automáticamente a partir del texto de cada publicación.
  </footer>
</div>
"""

with open(OUT_PATH, "w", encoding="utf-8") as f:
    f.write(html_doc)

print("Generado:", OUT_PATH, "-", len(html_doc), "caracteres")
