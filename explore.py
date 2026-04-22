"""Exploratory analysis on the Europe V-Dem slice.

Pulls the specific numbers that anchor each dashboard section's analytical text:
peaks, troughs, biggest decliners/improvers, clustering snapshots.
Output is printed so the numbers can be pasted into the HTML copy verbatim.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent
CSV = ROOT / "data" / "processed" / "vdem_europe.csv"

df = pd.read_csv(CSV)
df["year"] = df["year"].astype(int)

print("=" * 70)
print("SECTION 1 — 1900-1945: Rise and Fall")
print("=" * 70)

interwar = df[(df["year"] >= 1918) & (df["year"] <= 1939)]
yearly_median_polyarchy = interwar.groupby("year")["v2x_polyarchy"].median()
print("\nMedian electoral-democracy index across Europe, 1918-1939:")
print(yearly_median_polyarchy.round(3))
print(f"\nEurope-wide polyarchy peak 1900-1945: "
      f"{df[(df.year<=1945)].groupby('year').v2x_polyarchy.median().idxmax()} "
      f"at {df[(df.year<=1945)].groupby('year').v2x_polyarchy.median().max():.3f}")
print(f"Interwar trough: "
      f"{df[(df.year>=1918)&(df.year<=1945)].groupby('year').v2x_polyarchy.median().idxmin()} "
      f"at {df[(df.year>=1918)&(df.year<=1945)].groupby('year').v2x_polyarchy.median().min():.3f}")

print("\nSpecific interwar collapses (polyarchy drop from peak to 1939):")
for country in ["Germany", "Italy", "Austria", "Spain", "Estonia", "Latvia", "Lithuania", "Poland"]:
    sub = df[df["country_name"] == country]
    pre = sub[(sub["year"] >= 1918) & (sub["year"] <= 1935)]
    if len(pre) == 0:
        continue
    peak_row = pre.loc[pre["v2x_polyarchy"].idxmax()]
    v1939 = sub[sub["year"] == 1939]["v2x_polyarchy"].values
    v1939 = v1939[0] if len(v1939) else None
    if v1939 is not None:
        print(f"  {country:12} peak {peak_row['v2x_polyarchy']:.3f} ({int(peak_row['year'])}) "
              f"→ 1939: {v1939:.3f}  (Δ {v1939 - peak_row['v2x_polyarchy']:+.3f})")

print("\n" + "=" * 70)
print("SECTION 2 — 1945-1989: A Divided Continent")
print("=" * 70)

west = ["United Kingdom", "France", "Germany", "Italy", "Netherlands", "Belgium",
        "Luxembourg", "Denmark", "Sweden", "Norway", "Finland", "Iceland",
        "Ireland", "Austria", "Switzerland", "Spain", "Portugal", "Greece"]
east = ["Poland", "Czechia", "Slovakia", "Hungary", "Romania", "Bulgaria",
        "Albania", "German Democratic Republic", "Russia"]

cw = df[(df["year"] >= 1950) & (df["year"] <= 1988)]
west_avg = cw[cw["country_name"].isin(west)].groupby("year")["v2x_polyarchy"].mean()
east_avg = cw[cw["country_name"].isin(east)].groupby("year")["v2x_polyarchy"].mean()
print(f"\nMean polyarchy 1950-1988:")
print(f"  Western Europe: {west_avg.mean():.3f}  (range {west_avg.min():.3f} – {west_avg.max():.3f})")
print(f"  Eastern bloc:   {east_avg.mean():.3f}  (range {east_avg.min():.3f} – {east_avg.max():.3f})")

print("\nIberian peninsula authoritarian period:")
for country in ["Spain", "Portugal", "Greece"]:
    sub = df[(df["country_name"] == country) & (df["year"].between(1950, 1990))]
    print(f"  {country}: lowest {sub['v2x_polyarchy'].min():.3f} "
          f"({int(sub.loc[sub['v2x_polyarchy'].idxmin(), 'year'])}), "
          f"1990: {sub[sub['year']==1990]['v2x_polyarchy'].values[0]:.3f}")

print("\n" + "=" * 70)
print("SECTION 3 — 1989-2010: The Third Wave")
print("=" * 70)

post = df[(df["year"] >= 1989) & (df["year"] <= 2010)]
east_eu = ["Poland", "Czechia", "Slovakia", "Hungary", "Slovenia",
           "Estonia", "Latvia", "Lithuania", "Romania", "Bulgaria", "Croatia"]
for country in east_eu:
    sub = df[df["country_name"] == country]
    v1989 = sub[sub["year"] == 1989]["v2x_polyarchy"].values
    v2010 = sub[sub["year"] == 2010]["v2x_polyarchy"].values
    if len(v1989) and len(v2010):
        print(f"  {country:12} 1989: {v1989[0]:.3f}  →  2010: {v2010[0]:.3f}  "
              f"(Δ {v2010[0] - v1989[0]:+.3f})")

print("\nPost-Soviet trajectories (1992 vs 2010):")
for country in ["Russia", "Ukraine", "Belarus", "Moldova"]:
    sub = df[df["country_name"] == country]
    v92 = sub[sub["year"] == 1992]["v2x_polyarchy"].values
    v2010 = sub[sub["year"] == 2010]["v2x_polyarchy"].values
    if len(v92) and len(v2010):
        print(f"  {country:12} 1992: {v92[0]:.3f}  →  2010: {v2010[0]:.3f}  "
              f"(Δ {v2010[0] - v92[0]:+.3f})")

print("\n" + "=" * 70)
print("SECTION 4 — 2010-2024: The Backsliding Wave")
print("=" * 70)

d2010 = df[df["year"] == 2010][["country_name", "v2x_polyarchy", "v2x_libdem"]].set_index("country_name")
d2024 = df[df["year"] == 2024][["country_name", "v2x_polyarchy", "v2x_libdem"]].set_index("country_name")
delta = (d2024 - d2010).dropna()

print("\nBiggest declines in liberal democracy 2010 → 2024:")
worst = delta.sort_values("v2x_libdem").head(10)
for name, row in worst.iterrows():
    before = d2010.loc[name, "v2x_libdem"]
    after = d2024.loc[name, "v2x_libdem"]
    print(f"  {name:25}  {before:.3f} → {after:.3f}   (Δ {row['v2x_libdem']:+.3f})")

print("\nImprovers 2010 → 2024:")
best = delta.sort_values("v2x_libdem", ascending=False).head(5)
for name, row in best.iterrows():
    before = d2010.loc[name, "v2x_libdem"]
    after = d2024.loc[name, "v2x_libdem"]
    print(f"  {name:25}  {before:.3f} → {after:.3f}   (Δ {row['v2x_libdem']:+.3f})")

print("\n" + "=" * 70)
print("SECTION 5 — 2024 Typology")
print("=" * 70)

latest = df[df["year"] == 2024].copy()
print(f"\n2024 snapshot ({len(latest)} countries):")
print(f"  median polyarchy: {latest['v2x_polyarchy'].median():.3f}")
print(f"  median libdem:    {latest['v2x_libdem'].median():.3f}")
print(f"  min polyarchy:    {latest['v2x_polyarchy'].min():.3f} ({latest.loc[latest['v2x_polyarchy'].idxmin(),'country_name']})")
print(f"  max polyarchy:    {latest['v2x_polyarchy'].max():.3f} ({latest.loc[latest['v2x_polyarchy'].idxmax(),'country_name']})")

v2x_regime_labels = {0: "Closed autocracy", 1: "Electoral autocracy",
                     2: "Electoral democracy", 3: "Liberal democracy"}
if "v2x_regime" in latest.columns:
    latest["regime_label"] = latest["v2x_regime"].map(v2x_regime_labels)
    print("\nRegime distribution 2024:")
    print(latest["regime_label"].value_counts().to_string())
    print("\nBy regime:")
    for r in range(4):
        countries = sorted(latest[latest["v2x_regime"] == r]["country_name"].tolist())
        print(f"  {v2x_regime_labels[r]}: {', '.join(countries)}")
