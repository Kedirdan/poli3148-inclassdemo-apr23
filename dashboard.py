"""Generate the POLI 3148 dashboard as a single standalone HTML file.

Reads `data/processed/vdem_europe.csv`, produces `docs/index.html` —
the single output, served by GitHub Pages from the `/docs` folder.

Design: clean white background, Inter typography, teal accent, red/green data
encoding. Prominent AI-generated-demo disclaimer.
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

ROOT = Path(__file__).parent
CSV = ROOT / "data" / "processed" / "vdem_europe.csv"
OUT = ROOT / "docs" / "index.html"            # single output · served by GitHub Pages

# ─── Palette (clean, light, high-contrast) ──────────────────────────────────
BG = "#FFFFFF"
INK = "#0F172A"          # slate-900
INK_MUTED = "#475569"    # slate-600
GRID_COLOR = "#E2E8F0"   # slate-200
AXIS_COLOR = "#94A3B8"   # slate-400

TEAL = "#0D9488"         # teal-600 — primary accent
BLUE = "#2563EB"         # blue-600 — liberal democracy
RED = "#DC2626"          # red-600 — decline / autocracy
GREEN = "#059669"        # emerald-600 — improvement
AMBER = "#F59E0B"        # amber-500 — electoral democracy
DARK = "#1F2937"         # slate-800 — closed autocracy
ORANGE = "#EA580C"       # orange-600 — warm highlight
INDIGO = "#4F46E5"       # indigo-600

REGIME_COLORS = {
    0: DARK,    # Closed autocracy
    1: RED,     # Electoral autocracy
    2: AMBER,   # Electoral democracy
    3: BLUE,    # Liberal democracy
}
REGIME_NAMES = {
    0: "Closed autocracy",
    1: "Electoral autocracy",
    2: "Electoral democracy",
    3: "Liberal democracy",
}

GRID_AXIS = dict(gridcolor=GRID_COLOR, linecolor=AXIS_COLOR,
                 zerolinecolor=GRID_COLOR, tickfont=dict(color=INK_MUTED, size=12),
                 title_font=dict(color=INK_MUTED, size=13))


def base_layout(title: str, **overrides) -> dict:
    layout = dict(
        paper_bgcolor=BG,
        plot_bgcolor=BG,
        font=dict(family="'Inter', -apple-system, system-ui, sans-serif",
                  color=INK, size=13),
        margin=dict(l=60, r=30, t=80, b=55),
        hoverlabel=dict(bgcolor=BG, bordercolor=INK,
                        font=dict(family="'Inter', sans-serif", color=INK, size=13)),
        legend=dict(bgcolor="rgba(255,255,255,0.92)",
                    bordercolor=GRID_COLOR, borderwidth=1,
                    font=dict(color=INK, size=12)),
        title=dict(text=title,
                   font=dict(family="'Inter', sans-serif", color=INK, size=17, weight=600),
                   x=0.01, xanchor="left", y=0.97),
    )
    layout.update(overrides)
    return layout


# ─── Data ───────────────────────────────────────────────────────────────────
df = pd.read_csv(CSV)
df["year"] = df["year"].astype(int)

WEST = ["United Kingdom", "France", "Germany", "Italy", "Netherlands", "Belgium",
        "Luxembourg", "Denmark", "Sweden", "Norway", "Finland", "Iceland",
        "Ireland", "Austria", "Switzerland", "Spain", "Portugal", "Greece",
        "Cyprus", "Malta"]
EAST = ["Poland", "Czechia", "Slovakia", "Hungary", "Romania", "Bulgaria",
        "Albania", "German Democratic Republic"]
POST_COMMUNIST = ["Poland", "Czechia", "Slovakia", "Hungary", "Slovenia",
                  "Estonia", "Latvia", "Lithuania",
                  "Romania", "Bulgaria", "Croatia", "Serbia",
                  "Albania", "North Macedonia",
                  "Russia", "Ukraine", "Belarus", "Moldova"]


# ─── Chart 1: Rise and Fall 1900-1945 ───────────────────────────────────────
def chart_rise_and_fall() -> str:
    d = df[(df["year"] >= 1900) & (df["year"] <= 1945)]
    median = d.groupby("year")["v2x_polyarchy"].median()
    q25 = d.groupby("year")["v2x_polyarchy"].quantile(0.25)
    q75 = d.groupby("year")["v2x_polyarchy"].quantile(0.75)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(q75.index) + list(q25.index[::-1]),
        y=list(q75.values) + list(q25.values[::-1]),
        fill="toself", fillcolor="rgba(13,148,136,0.12)",
        line=dict(width=0), hoverinfo="skip",
        name="Interquartile range", showlegend=True))
    fig.add_trace(go.Scatter(
        x=median.index, y=median.values, mode="lines",
        line=dict(color=TEAL, width=3),
        name="European median",
        hovertemplate="<b>%{x}</b><br>Median polyarchy: %{y:.3f}<extra></extra>"))

    collapse = {
        "Germany": RED, "Italy": ORANGE, "Spain": AMBER,
        "Latvia": INDIGO, "Estonia": BLUE,
    }
    for country, color in collapse.items():
        sub = df[(df["country_name"] == country) &
                 (df["year"] >= 1900) & (df["year"] <= 1945)]
        fig.add_trace(go.Scatter(
            x=sub["year"], y=sub["v2x_polyarchy"], mode="lines",
            line=dict(color=color, width=1.6, dash="dot"), opacity=0.85,
            name=country,
            hovertemplate=f"<b>{country}</b> %{{x}}<br>Polyarchy: %{{y:.3f}}<extra></extra>"))

    for year, label in [(1922, "Mussolini"), (1933, "Nazi rise"), (1939, "WWII")]:
        fig.add_vline(x=year, line=dict(color=INK_MUTED, width=0.7, dash="dash"))
        fig.add_annotation(x=year, y=1.02, yref="paper", text=label,
                           showarrow=False, font=dict(size=11, color=INK_MUTED),
                           bgcolor="rgba(255,255,255,0.95)", borderpad=3)

    fig.update_layout(**base_layout(
        "European electoral-democracy index, 1900–1945",
        xaxis=dict(title="Year", **GRID_AXIS),
        yaxis=dict(title="Polyarchy (0–1)", range=[0, 1], **GRID_AXIS),
        height=480, hovermode="x unified",
    ))
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id="chart1",
                       config={"displayModeBar": False})


# ─── Chart 2: Divided Continent 1945-1989 ───────────────────────────────────
def chart_divided_continent() -> str:
    d = df[(df["year"] >= 1945) & (df["year"] <= 1990)]
    west_mean = d[d["country_name"].isin(WEST)].groupby("year")["v2x_polyarchy"].mean()
    east_mean = d[d["country_name"].isin(EAST)].groupby("year")["v2x_polyarchy"].mean()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(west_mean.index) + list(east_mean.index[::-1]),
        y=list(west_mean.values) + list(east_mean.values[::-1]),
        fill="toself", fillcolor="rgba(100,116,139,0.08)",
        line=dict(width=0), hoverinfo="skip", showlegend=False))

    fig.add_trace(go.Scatter(
        x=west_mean.index, y=west_mean.values, mode="lines",
        line=dict(color=BLUE, width=3), name="Western Europe",
        hovertemplate="<b>West %{x}</b><br>Mean polyarchy: %{y:.3f}<extra></extra>"))
    fig.add_trace(go.Scatter(
        x=east_mean.index, y=east_mean.values, mode="lines",
        line=dict(color=RED, width=3), name="Eastern bloc",
        hovertemplate="<b>East %{x}</b><br>Mean polyarchy: %{y:.3f}<extra></extra>"))

    for country, color in {"Spain": AMBER, "Portugal": ORANGE, "Greece": TEAL}.items():
        sub = df[(df["country_name"] == country) &
                 (df["year"] >= 1945) & (df["year"] <= 1990)]
        fig.add_trace(go.Scatter(
            x=sub["year"], y=sub["v2x_polyarchy"], mode="lines",
            line=dict(color=color, width=1.8, dash="dot"), opacity=0.95,
            name=f"{country} (dictatorship)",
            hovertemplate=f"<b>{country} %{{x}}</b><br>Polyarchy: %{{y:.3f}}<extra></extra>"))

    for year, label in [(1956, "Hungary '56"), (1968, "Prague Spring"),
                        (1974, "Portugal/Greece"), (1975, "Spain"),
                        (1989, "Berlin Wall")]:
        fig.add_vline(x=year, line=dict(color=INK_MUTED, width=0.6, dash="dash"))
        fig.add_annotation(x=year, y=1.02, yref="paper", text=label,
                           showarrow=False, font=dict(size=10, color=INK_MUTED),
                           bgcolor="rgba(255,255,255,0.95)", borderpad=2)

    fig.update_layout(**base_layout(
        "The 40-year gap: West vs East, 1945–1990",
        xaxis=dict(title="Year", **GRID_AXIS),
        yaxis=dict(title="Polyarchy (0–1)", range=[0, 1], **GRID_AXIS),
        height=480, hovermode="x unified",
    ))
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id="chart2",
                       config={"displayModeBar": False})


# ─── Chart 3: Third Wave 1989-2010 (spaghetti) ──────────────────────────────
def chart_third_wave() -> str:
    d = df[(df["country_name"].isin(POST_COMMUNIST)) &
           (df["year"] >= 1989) & (df["year"] <= 2010)].copy()

    heroes = {
        "Estonia": BLUE, "Czechia": TEAL, "Slovenia": INDIGO,
        "Poland": GREEN, "Hungary": ORANGE,
        "Ukraine": AMBER,
        "Russia": RED, "Belarus": DARK,
    }

    fig = go.Figure()
    # Draw background countries first so hero trajectories sit on top
    for country in POST_COMMUNIST:
        if country in heroes:
            continue
        sub = d[d["country_name"] == country]
        fig.add_trace(go.Scatter(
            x=sub["year"], y=sub["v2x_polyarchy"], mode="lines",
            line=dict(color="#CBD5E1", width=1), opacity=0.7,
            name=country, legendgroup="other", showlegend=False,
            hovertemplate=f"<b>{country} %{{x}}</b><br>Polyarchy: %{{y:.3f}}<extra></extra>"))

    for country, color in heroes.items():
        sub = d[d["country_name"] == country]
        fig.add_trace(go.Scatter(
            x=sub["year"], y=sub["v2x_polyarchy"], mode="lines",
            line=dict(color=color, width=2.8),
            name=country,
            hovertemplate=f"<b>{country} %{{x}}</b><br>Polyarchy: %{{y:.3f}}<extra></extra>"))

    fig.add_hline(y=0.5, line=dict(color=INK_MUTED, width=0.8, dash="dash"))
    fig.add_annotation(x=1990, y=0.52, text="≈ democracy threshold",
                       showarrow=False,
                       font=dict(size=11, color=INK_MUTED),
                       xanchor="left")

    fig.update_layout(**base_layout(
        "Post-communist trajectories, 1989–2010",
        xaxis=dict(title="Year", **GRID_AXIS),
        yaxis=dict(title="Polyarchy (0–1)", range=[0, 1], **GRID_AXIS),
        height=500, hovermode="closest",
    ))
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id="chart3",
                       config={"displayModeBar": False})


# ─── Chart 4: Backsliding Wave 2010-2024 (dumbbell) ─────────────────────────
def chart_backsliding() -> str:
    d2010 = df[df["year"] == 2010][["country_name", "v2x_libdem"]].set_index("country_name")
    d2024 = df[df["year"] == 2024][["country_name", "v2x_libdem"]].set_index("country_name")
    merged = d2010.join(d2024, lsuffix="_2010", rsuffix="_2024").dropna()
    merged["delta"] = merged["v2x_libdem_2024"] - merged["v2x_libdem_2010"]
    merged = merged.sort_values("delta")

    fig = go.Figure()
    for country, row in merged.iterrows():
        color = RED if row["delta"] < 0 else GREEN
        width = 3 if abs(row["delta"]) > 0.1 else 1.6
        fig.add_trace(go.Scatter(
            x=[row["v2x_libdem_2010"], row["v2x_libdem_2024"]],
            y=[country, country],
            mode="lines+markers",
            line=dict(color=color, width=width),
            marker=dict(size=[9, 12], color=["#94A3B8", color],
                        line=dict(color=BG, width=1)),
            hovertemplate=(f"<b>{country}</b><br>2010: {row['v2x_libdem_2010']:.3f}"
                           f"<br>2024: {row['v2x_libdem_2024']:.3f}"
                           f"<br>Δ {row['delta']:+.3f}<extra></extra>"),
            showlegend=False))

    fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines+markers",
                             line=dict(color=RED, width=3),
                             marker=dict(color=RED, size=11),
                             name="Declined 2010 → 2024"))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="lines+markers",
                             line=dict(color=GREEN, width=3),
                             marker=dict(color=GREEN, size=11),
                             name="Improved 2010 → 2024"))
    fig.add_trace(go.Scatter(x=[None], y=[None], mode="markers",
                             marker=dict(color="#94A3B8", size=9),
                             name="2010 value"))

    fig.update_layout(**base_layout(
        "Liberal-democracy change, 2010 → 2024",
        xaxis=dict(title="Liberal Democracy Index (v2x_libdem, 0–1)",
                   range=[0, 1], **GRID_AXIS),
        yaxis=dict(title="", categoryorder="array", categoryarray=list(merged.index),
                   **GRID_AXIS),
        height=max(720, 20 * len(merged)),
    ))
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id="chart4",
                       config={"displayModeBar": False})


# ─── Chart 5: 2024 Typology scatter ─────────────────────────────────────────
def chart_typology() -> str:
    latest = df[df["year"] == 2024].dropna(
        subset=["v2x_polyarchy", "v2x_libdem", "v2x_regime"]).copy()
    latest["regime_label"] = latest["v2x_regime"].astype(int).map(REGIME_NAMES)

    # Permanent labels only for extreme / signal countries — rest hover-only
    label_countries = {
        "Denmark", "Norway", "Sweden", "Germany", "France",
        "Hungary", "Poland", "Serbia", "Türkiye", "Russia", "Belarus",
        "Ukraine", "United Kingdom", "Italy", "Greece",
    }

    fig = go.Figure()
    for regime_code in [3, 2, 1, 0]:
        sub = latest[latest["v2x_regime"].astype(int) == regime_code]
        if len(sub) == 0:
            continue
        text_labels = [c if c in label_countries else "" for c in sub["country_name"]]
        fig.add_trace(go.Scatter(
            x=sub["v2x_polyarchy"], y=sub["v2x_libdem"],
            mode="markers+text",
            text=text_labels,
            textposition="top center",
            textfont=dict(size=11, color=INK),
            customdata=list(zip(
                sub["country_name"],
                sub["v2x_freexp_altinf"],
                sub["v2x_rule"],
                sub["v2xcs_ccsi"])),
            marker=dict(size=14, color=REGIME_COLORS[regime_code],
                        line=dict(color=BG, width=1.5), opacity=0.95),
            name=REGIME_NAMES[regime_code],
            hovertemplate=("<b>%{customdata[0]}</b><br>"
                           "Polyarchy: %{x:.3f}<br>"
                           "Liberal dem: %{y:.3f}<br>"
                           "Freedom of expression: %{customdata[1]:.3f}<br>"
                           "Rule of law: %{customdata[2]:.3f}<br>"
                           "Civil society: %{customdata[3]:.3f}<extra></extra>")))

    median_x = latest["v2x_polyarchy"].median()
    median_y = latest["v2x_libdem"].median()
    fig.add_vline(x=median_x, line=dict(color="#CBD5E1", width=0.8, dash="dash"))
    fig.add_hline(y=median_y, line=dict(color="#CBD5E1", width=0.8, dash="dash"))

    fig.update_layout(**base_layout(
        "Europe 2024: electoral × liberal democracy",
        xaxis=dict(title="Electoral Democracy (polyarchy)",
                   range=[0, 1], **GRID_AXIS),
        yaxis=dict(title="Liberal Democracy (libdem)", range=[0, 1], **GRID_AXIS),
        height=620,
    ))
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id="chart5",
                       config={"displayModeBar": False})


# ─── HTML assembly ──────────────────────────────────────────────────────────
PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Long Century of European Democracy · POLI 3148 AI Demo</title>
<meta name="robots" content="noindex">
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg: #FFFFFF;
    --bg-soft: #F8FAFC;
    --bg-warn: #FEF3C7;
    --ink: #0F172A;
    --ink-muted: #475569;
    --ink-subtle: #94A3B8;
    --border: #E2E8F0;
    --border-strong: #CBD5E1;
    --accent: #0D9488;
    --accent-dark: #0F766E;
    --accent-bg: #F0FDFA;
    --warn: #B45309;
    --warn-border: #F59E0B;
    --red: #DC2626;
    --blue: #2563EB;
    --green: #059669;
  }}
  * {{ box-sizing: border-box; }}
  html {{ scroll-behavior: smooth; }}
  body {{
    margin: 0; padding: 0;
    background: var(--bg); color: var(--ink);
    font-family: 'Inter', -apple-system, system-ui, 'Helvetica Neue', sans-serif;
    font-weight: 400;
    line-height: 1.65;
    font-size: 16px;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
  }}

  /* ── Disclaimer banner (top, always visible, prominent) ── */
  .disclaimer {{
    background: #FEE2E2;
    border-top: 3px solid #DC2626;
    border-bottom: 3px solid #DC2626;
    padding: 18px 24px;
    color: #991B1B;
    font-size: 15px;
    line-height: 1.55;
    text-align: center;
  }}
  .disclaimer strong {{ color: #7F1D1D; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; }}
  .disclaimer .detail {{
    display: block;
    color: #991B1B;
    font-size: 13.5px;
    margin-top: 6px;
    font-weight: 500;
  }}
  .disclaimer.sticky {{
    position: sticky; top: 0; z-index: 200;
  }}

  /* ── Inline section reminder (before each §) ── */
  .section-warn {{
    background: #FEF3C7;
    border-left: 4px solid #F59E0B;
    padding: 10px 16px;
    margin: 0 0 18px;
    color: #78350F;
    font-size: 13.5px;
    line-height: 1.5;
    font-style: italic;
  }}
  .section-warn strong {{ color: #78350F; font-weight: 600; font-style: normal; }}

  /* ── Sticky top nav ── */
  nav.top {{
    position: sticky; top: 0; z-index: 100;
    background: rgba(255,255,255,0.97);
    backdrop-filter: saturate(180%) blur(8px);
    -webkit-backdrop-filter: saturate(180%) blur(8px);
    border-bottom: 1px solid var(--border);
    padding: 12px 24px;
    display: flex; align-items: center; justify-content: space-between;
    gap: 16px;
  }}
  nav.top .brand {{
    font-weight: 600; font-size: 14px;
    color: var(--ink);
    letter-spacing: -0.01em;
    white-space: nowrap;
  }}
  nav.top .brand span.tag {{
    display: inline-block;
    padding: 2px 7px; margin-left: 8px;
    border-radius: 4px;
    background: var(--accent-bg); color: var(--accent-dark);
    font-size: 11px; font-weight: 600; letter-spacing: 0.03em;
    text-transform: uppercase;
  }}
  nav.top .links {{
    display: flex; gap: 8px; flex-wrap: wrap; align-items: center;
  }}
  nav.top .links a {{
    color: var(--ink-muted); text-decoration: none;
    padding: 6px 10px; border-radius: 6px;
    font-size: 13px; font-weight: 500;
    transition: background 120ms, color 120ms;
    white-space: nowrap;
  }}
  nav.top .links a:hover {{
    background: var(--bg-soft); color: var(--ink);
  }}
  nav.top .links a.accent {{
    color: var(--accent-dark);
  }}
  @media (max-width: 720px) {{
    nav.top {{ padding: 10px 16px; flex-direction: column; align-items: flex-start; gap: 8px; }}
    nav.top .links {{
      width: 100%; overflow-x: auto;
      padding-bottom: 4px;
      scrollbar-width: none;
    }}
    nav.top .links::-webkit-scrollbar {{ display: none; }}
  }}

  .container {{ max-width: 1080px; margin: 0 auto; padding: 56px 32px 120px; }}

  /* ── Hero ── */
  header.hero {{
    text-align: center;
    padding: 40px 0 56px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 56px;
  }}
  header.hero .eyebrow {{
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--accent-dark);
    background: var(--accent-bg);
    padding: 5px 12px;
    border-radius: 20px;
    letter-spacing: 0.05em;
    margin-bottom: 20px;
  }}
  header.hero h1 {{
    font-size: 52px;
    font-weight: 700;
    line-height: 1.08;
    letter-spacing: -0.025em;
    margin: 0 0 18px;
    color: var(--ink);
  }}
  header.hero .subtitle {{
    font-size: 22px;
    font-weight: 400;
    color: var(--ink-muted);
    margin: 0 auto 32px;
    max-width: 680px;
    line-height: 1.4;
  }}
  header.hero .meta {{
    display: inline-flex;
    gap: 20px;
    flex-wrap: wrap; justify-content: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--ink-subtle);
  }}
  header.hero .meta span strong {{ color: var(--ink-muted); font-weight: 500; }}

  .interaction-hint {{
    display: flex; gap: 24px; flex-wrap: wrap; justify-content: center;
    margin: 36px auto 0;
    padding: 18px 24px;
    max-width: 720px;
    background: var(--bg-soft);
    border: 1px solid var(--border);
    border-radius: 10px;
    font-size: 14px;
    color: var(--ink-muted);
  }}
  .interaction-hint span {{ display: inline-flex; gap: 8px; align-items: center; }}
  .interaction-hint svg {{ width: 16px; height: 16px; color: var(--accent); flex-shrink: 0; }}

  /* ── Section ── */
  section {{
    margin: 72px 0;
    scroll-margin-top: 80px;
  }}
  section .section-header {{
    border-top: 1px solid var(--border);
    padding-top: 40px;
    margin-bottom: 32px;
  }}
  section .section-num {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: var(--accent-dark);
    font-weight: 600;
    letter-spacing: 0.05em;
    margin-bottom: 10px;
  }}
  section h2 {{
    font-size: 34px;
    font-weight: 700;
    line-height: 1.18;
    letter-spacing: -0.02em;
    margin: 0 0 12px;
    color: var(--ink);
  }}
  section .section-subtitle {{
    font-size: 18px;
    color: var(--ink-muted);
    margin: 0 0 12px;
    line-height: 1.5;
  }}

  .chart {{
    background: var(--bg);
    padding: 12px 0;
    margin: 28px 0;
  }}
  .analysis {{
    background: var(--bg-soft);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    padding: 24px 28px;
    margin: 24px 0;
  }}
  .analysis p {{
    margin: 0 0 14px;
    color: var(--ink);
    line-height: 1.7;
    font-size: 16px;
  }}
  .analysis p:last-child {{ margin-bottom: 0; }}
  .analysis strong {{ color: var(--ink); font-weight: 600; }}
  .analysis em {{ color: var(--ink-muted); font-style: italic; }}

  .callout {{
    background: var(--bg);
    border: 1px solid var(--border);
    padding: 16px 20px;
    margin: 18px 0 0;
    font-size: 14px;
    color: var(--ink-muted);
    border-radius: 6px;
  }}
  .callout .label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--accent-dark);
    font-weight: 600;
    display: block;
    margin-bottom: 6px;
  }}

  /* ── Footer ── */
  footer {{
    margin-top: 100px;
    padding-top: 40px;
    border-top: 1px solid var(--border);
    color: var(--ink-muted);
    font-size: 14px;
    line-height: 1.7;
  }}
  footer .footer-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 32px;
    margin-bottom: 32px;
  }}
  footer h3 {{
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--ink);
    margin: 0 0 14px;
  }}
  footer p {{ margin: 0 0 10px; }}
  footer a {{
    color: var(--accent-dark);
    text-decoration: none;
    border-bottom: 1px solid transparent;
  }}
  footer a:hover {{ border-bottom-color: var(--accent-dark); }}
  footer code {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    background: var(--bg-soft);
    padding: 2px 6px;
    border-radius: 3px;
    color: var(--ink);
  }}
  footer .final-notice {{
    background: var(--bg-warn);
    border-left: 3px solid var(--warn-border);
    padding: 16px 20px;
    border-radius: 6px;
    color: var(--warn);
    font-size: 14px;
    margin-top: 24px;
  }}

  /* ── Back-to-top button ── */
  .to-top {{
    position: fixed; bottom: 24px; right: 24px;
    width: 44px; height: 44px;
    border-radius: 50%;
    background: var(--ink);
    color: var(--bg);
    display: flex; align-items: center; justify-content: center;
    border: none; cursor: pointer;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
    opacity: 0; pointer-events: none;
    transition: opacity 200ms, transform 200ms;
    z-index: 90;
  }}
  .to-top.visible {{ opacity: 1; pointer-events: auto; }}
  .to-top:hover {{ transform: translateY(-2px); }}
  .to-top svg {{ width: 18px; height: 18px; }}

  @media (max-width: 720px) {{
    .container {{ padding: 32px 18px 80px; }}
    header.hero {{ padding: 24px 0 40px; }}
    header.hero h1 {{ font-size: 34px; }}
    header.hero .subtitle {{ font-size: 17px; }}
    section h2 {{ font-size: 26px; }}
    section .section-subtitle {{ font-size: 16px; }}
    .analysis {{ padding: 18px 20px; }}
    .analysis p {{ font-size: 15px; }}
    .interaction-hint {{ flex-direction: column; gap: 10px; text-align: left; }}
    .to-top {{ bottom: 16px; right: 16px; width: 40px; height: 40px; }}
  }}

  /* ── Print ── */
  @media print {{
    nav.top, .to-top {{ display: none; }}
    .disclaimer {{ position: static; }}
    body {{ font-size: 11pt; }}
    .analysis {{ border: 1px solid #999; background: none; }}
  }}
</style>
</head>
<body>

<div class="disclaimer" role="alert">
  <strong>🚫 AI-generated content · Do NOT cite · Do NOT reference · Purely a GitHub Pages demonstration</strong>
  <span class="detail">Everything on this page — the narrative, the numbers cited in the text, the section framing, the country groupings, the interpretations — was written by an AI assistant. Nothing here has been peer-reviewed or verified by a political scientist. This page exists <strong>solely</strong> to illustrate the technical workflow of publishing an HTML file to GitHub Pages for POLI 3148 · Week 13 Lab. For authoritative claims about European democracy, go to the <a href="https://v-dem.net/" style="color:#991B1B;text-decoration:underline;">V-Dem Institute</a> directly.</span>
</div>

<nav class="top" aria-label="Section navigation">
  <div class="brand">
    The Long Century of European Democracy
    <span class="tag">AI Demo</span>
  </div>
  <div class="links">
    <a href="#s1">§1 Rise &amp; Fall</a>
    <a href="#s2">§2 Divided</a>
    <a href="#s3">§3 Third Wave</a>
    <a href="#s4">§4 Backsliding</a>
    <a href="#s5">§5 Typology</a>
  </div>
</nav>

<div class="container">

<header class="hero">
  <div class="eyebrow">POLI 3148 · In-Class Demo · Apr 23, 2026</div>
  <h1>The Long Century of<br>European Democracy</h1>
  <p class="subtitle">Five Acts of European Democracy · 1900–2024</p>
  <div class="meta">
    <span><strong>Data:</strong> V-Dem v16 (Mar 2026)</span>
    <span><strong>Scope:</strong> 42 states × 125 years</span>
    <span><strong>Obs:</strong> 4,110 country-years</span>
  </div>
  <div class="interaction-hint" role="note">
    <span>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6.5 6.5h11a3 3 0 0 1 3 3v7a3 3 0 0 1-3 3h-11a3 3 0 0 1-3-3v-7a3 3 0 0 1 3-3z"/><path d="M12 12 8 8m4 4 4-4m-4 4v7"/></svg>
      Hover any chart for details
    </span>
    <span>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 9h10M7 13h6M7 17h4"/></svg>
      Click legend items to filter
    </span>
    <span>
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3M8 11h6M11 8v6"/></svg>
      Drag to zoom, double-click to reset
    </span>
  </div>
</header>

<section id="s1">
  <div class="section-header">
    <div class="section-num">§1 · 1900–1945</div>
    <h2>Rise and Fall</h2>
    <p class="section-subtitle">Europe built democracy in the 1920s, then dismantled it in the 1930s.</p>
  </div>
  <div class="section-warn"><strong>AI-generated, unverified:</strong> the narrative, numbers, and framing below were produced by an AI for a GitHub Pages demonstration. Do not cite.</div>
  <div class="chart">{chart1}</div>
  <div class="analysis">
    <p>Europe's electoral-democracy index (V-Dem <em>polyarchy</em>) peaked at <strong>0.595 in 1923</strong> — post-WWI franchise expansions had pushed the continent to its highest democratic level yet. Over the next 16 years, that median fell to <strong>0.206 by 1939</strong>, and to <strong>0.118 in 1942</strong>. The interwar collapse was not gradual — it was a cascade.</p>
    <p>The countries that fell hardest were not the oldest democracies but the newer ones born from WWI: <strong>Latvia</strong> fell from 0.745 in 1924 to 0.136 in 1939 (Δ -0.609), <strong>Germany</strong> from 0.646 (1921) to 0.071 (1939), <strong>Lithuania</strong> from 0.583 (1923) to 0.120 (1939), <strong>Estonia</strong> from 0.707 (1927) to 0.278 (1939). Italy's collapse began earliest (Mussolini, 1922); Spain's came latest (civil war, 1936–39).</p>
    <div class="callout">
      <span class="label">Why it matters</span>
      The interwar collapse is the counter-example every democratic-backsliding scholar cites. V-Dem's numerical rendering shows how <em>fast</em> democratic institutions can be hollowed out — in the Baltic states, less than one electoral cycle per 0.1 index point lost.
    </div>
  </div>
</section>

<section id="s2">
  <div class="section-header">
    <div class="section-num">§2 · 1945–1990</div>
    <h2>A Divided Continent</h2>
    <p class="section-subtitle">The 40-year Cold War gap between the two Europes.</p>
  </div>
  <div class="section-warn"><strong>AI-generated, unverified:</strong> the narrative, numbers, and framing below were produced by an AI for a GitHub Pages demonstration. Do not cite.</div>
  <div class="chart">{chart2}</div>
  <div class="analysis">
    <p>Between 1950 and 1988, Western Europe's mean polyarchy score held at <strong>0.746</strong> (range 0.67–0.86), while the Eastern bloc flatlined at <strong>0.161</strong> (range 0.15–0.17). The ratio was roughly <strong>4.6 to 1</strong>, sustained for 40 consecutive years — arguably the most stable bifurcation in modern political history.</p>
    <p>The exceptions sit inside the Western average: <strong>Spain</strong> scored just 0.069 under Franco in 1950, <strong>Portugal</strong> 0.119 under Salazar in 1966, and <strong>Greece</strong> 0.074 under the Colonels in 1968. By 1990, after the Third Wave had swept them up, all three had surged past 0.86 — a reminder that "Western Europe" was not uniformly democratic until the late 1970s.</p>
    <p>Moments like the <strong>1956 Hungarian Uprising</strong> and the <strong>1968 Prague Spring</strong> register as small bumps in the Eastern bloc line — attempts at liberalisation immediately crushed. They would remain minor footnotes for another two decades, until 1989 made them retrospective preludes.</p>
  </div>
</section>

<section id="s3">
  <div class="section-header">
    <div class="section-num">§3 · 1989–2010</div>
    <h2>The Third Wave's European Chapter</h2>
    <p class="section-subtitle">Post-communist trajectories diverge from a shared starting line.</p>
  </div>
  <div class="section-warn"><strong>AI-generated, unverified:</strong> the narrative, numbers, and framing below were produced by an AI for a GitHub Pages demonstration. Do not cite.</div>
  <div class="chart">{chart3}</div>
  <div class="analysis">
    <p>Starting from a near-identical floor in 1989, post-communist Europe produced five distinct trajectories within two decades:</p>
    <p><strong>Front-runners:</strong> <strong>Czechia</strong> leapt from 0.146 to 0.883 (Δ +0.737, the largest 21-year gain anywhere on the continent), <strong>Slovenia</strong> from 0.248 to 0.872, <strong>Estonia</strong> from a mid-range start to 0.83+. <strong>Steady risers:</strong> Poland (+0.513), Hungary (+0.543), Lithuania, Latvia. <strong>Late bloomers:</strong> Romania and Bulgaria (~+0.49 each), slower initial gains but crossed the democratic threshold before EU accession in 2007.</p>
    <p><strong>Oscillators:</strong> Ukraine moved between 0.48 and 0.58 repeatedly (Orange Revolution, then reversal, then Maidan). <strong>Backsliders and blockers:</strong> Russia declined from 0.498 in 1992 to 0.306 in 2010 (Δ -0.192); Belarus fell from 0.565 to 0.226 (Δ -0.339) under Lukashenko.</p>
    <div class="callout">
      <span class="label">The core puzzle</span>
      Countries that entered 1989 with virtually identical V-Dem scores produced outcomes ranging from consolidated liberal democracy to closed autocracy. Institutional inheritance, geography, and external anchors (EU accession conditionality) explain part of the variance, but not all — which is why this period remains the most-studied case in comparative democratisation.
    </div>
  </div>
</section>

<section id="s4">
  <div class="section-header">
    <div class="section-num">§4 · 2010–2024</div>
    <h2>The Backsliding Wave</h2>
    <p class="section-subtitle">Decline between 2010 and 2024 affects old democracies and new.</p>
  </div>
  <div class="section-warn"><strong>AI-generated, unverified:</strong> the narrative, numbers, and framing below were produced by an AI for a GitHub Pages demonstration. Do not cite.</div>
  <div class="chart">{chart4}</div>
  <div class="analysis">
    <p>Between 2010 and 2024, the majority of European states recorded declines in the Liberal Democracy Index. The ten steepest:</p>
    <p><strong>Hungary</strong> -0.352 (0.677 → 0.325, the sharpest drop in the EU), <strong>Serbia</strong> -0.278, <strong>Türkiye</strong> -0.251, <strong>Greece</strong> -0.247, <strong>Poland</strong> -0.214 (partly reversed after 2023), <strong>Slovenia</strong> -0.166, <strong>Slovakia</strong> -0.162, <strong>Croatia</strong> -0.123, <strong>Romania</strong> -0.101, <strong>Italy</strong> -0.088.</p>
    <p>Improvers are few and modest: <strong>Montenegro</strong> +0.089, <strong>Kosovo</strong> +0.085, <strong>Latvia</strong> +0.055. No European country gained more than one-tenth of an index point in this period — which makes the magnitude of the top declines (0.2–0.35) starker.</p>
    <p>Crucially, decline is not confined to new democracies. Greece — a founding EU member — lost a quarter-point in liberal-democracy score. Italy's decline (-0.088) is smaller but signals that even "consolidated" democracies are no longer static assets.</p>
  </div>
</section>

<section id="s5">
  <div class="section-header">
    <div class="section-num">§5 · 2024</div>
    <h2>A Regime Typology</h2>
    <p class="section-subtitle">Where every European state sits on V-Dem's two-dimensional map today.</p>
  </div>
  <div class="section-warn"><strong>AI-generated, unverified:</strong> the narrative, numbers, and framing below were produced by an AI for a GitHub Pages demonstration. Do not cite.</div>
  <div class="chart">{chart5}</div>
  <div class="analysis">
    <p>The scatter uses V-Dem's Regimes of the World classification to group 42 European states into four categories:</p>
    <p><strong>Liberal democracies (19):</strong> Denmark, Finland, Sweden, Norway, Germany, Netherlands, Switzerland, Estonia, Ireland, France, Iceland, Luxembourg, Belgium, Austria, Spain, Italy, Latvia, Czechia, Cyprus. <strong>Electoral democracies (17):</strong> Portugal, Lithuania, Slovenia, Slovakia, Greece, United Kingdom, Poland, Croatia, Malta, Romania, Bulgaria, Montenegro, North Macedonia, Albania, Kosovo, Bosnia and Herzegovina, Moldova. <strong>Electoral autocracies (5):</strong> Hungary, Serbia, Ukraine, Türkiye, Russia. <strong>Closed autocracies (1):</strong> Belarus.</p>
    <p>The presence of <strong>Hungary</strong> in the electoral-autocracy category is politically remarkable: it is the first EU member state ever to be classified below the democratic threshold by V-Dem (first occurred 2019). <strong>Ukraine</strong> appears in the same category, but its trajectory is very different — its 2024 score reflects wartime institutional disruption rather than a consolidated autocratic turn.</p>
    <p>The median European state in 2024 scores <strong>0.784 on polyarchy</strong> and <strong>0.670 on liberal democracy</strong>. The range is <strong>0.160 (Belarus) to 0.917 (Denmark)</strong> — a spread of 0.76 index points, the largest within any single continent in the V-Dem data.</p>
  </div>
</section>

<footer>
  <div class="footer-grid">
    <div>
      <h3>Data Source</h3>
      <p>V-Dem Country-Year Dataset, <strong>version 16</strong> (March 2026), V-Dem Institute, University of Gothenburg.</p>
      <p>DOI: <a href="https://doi.org/10.23696/vdemds26">10.23696/vdemds26</a></p>
      <p>Licence: <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a></p>
    </div>
    <div>
      <h3>Indicators Used</h3>
      <p><code>v2x_polyarchy</code> — electoral democracy<br>
      <code>v2x_libdem</code> — liberal democracy<br>
      <code>v2x_regime</code> — Regimes of the World<br>
      <code>v2x_freexp_altinf</code>, <code>v2x_rule</code>, <code>v2xcs_ccsi</code></p>
    </div>
    <div>
      <h3>Built With</h3>
      <p>Python 3.14 · pandas · Plotly.js 2.35</p>
      <p>Single-file HTML · no server · no tracking</p>
      <p><a href="https://github.com/Kedirdan/POLI3148_2026Spring_GitHubPagesDemo">Source on GitHub</a></p>
    </div>
  </div>
  <div class="final-notice">
    <strong>🚫 READ THIS BEFORE YOU QUOTE ANYTHING.</strong><br><br>
    This page exists for <strong>one reason only</strong>: to demonstrate how a single HTML file can be published to GitHub Pages. That is the entire educational goal. Everything else is scaffolding.<br><br>
    The <strong>narrative text</strong>, the <strong>specific numbers quoted in the prose</strong>, the <strong>five-section historical framing</strong>, the <strong>country rankings</strong>, the <strong>interpretive "why it matters" callouts</strong> — all of it was generated by an AI assistant. None of it has been reviewed, fact-checked, or endorsed by a political scientist, a V-Dem researcher, or anyone with subject-matter authority.<br><br>
    <strong>Do not</strong> cite this dashboard in a paper. <strong>Do not</strong> quote any sentence as authoritative. <strong>Do not</strong> use any country ranking here as a fact. <strong>Do not</strong> treat the five-act framing as reflecting scholarly consensus — it doesn't.<br><br>
    For authoritative claims about European democracy, go directly to the <a href="https://v-dem.net/">V-Dem Institute</a>, their annual <em>Democracy Report</em>, the <em>V-Dem Codebook</em>, and peer-reviewed journal articles. The only reliable element on this page is the underlying numeric data — which you should fetch from V-Dem, not from this AI-mediated re-telling.<br><br>
    This is a GitHub Pages demo. That's all it is.
  </div>
</footer>

</div>

<button class="to-top" aria-label="Back to top" id="toTop">
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
</button>

<script>
(function() {{
  const btn = document.getElementById('toTop');
  window.addEventListener('scroll', function() {{
    btn.classList.toggle('visible', window.scrollY > 500);
  }}, {{ passive: true }});
  btn.addEventListener('click', function() {{
    window.scrollTo({{ top: 0, behavior: 'smooth' }});
  }});
}})();
</script>

</body>
</html>
"""


def main() -> None:
    print("Building 5 charts …")
    c1 = chart_rise_and_fall();       print("  ✓ 1. Rise and Fall")
    c2 = chart_divided_continent();   print("  ✓ 2. Divided Continent")
    c3 = chart_third_wave();          print("  ✓ 3. Third Wave")
    c4 = chart_backsliding();         print("  ✓ 4. Backsliding Wave")
    c5 = chart_typology();            print("  ✓ 5. Typology 2024")

    html = PAGE_TEMPLATE.format(chart1=c1, chart2=c2, chart3=c3, chart4=c4, chart5=c5)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"\nWrote {OUT} ({OUT.stat().st_size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
