"""Extract V-Dem v16 RData into a compact parquet file for Europe 1900-2024.

Reads the R package dataset, filters to European countries and relevant indicators,
writes `data/processed/vdem_europe.parquet` and a plaintext `variables.txt` for
quick reference.
"""

from pathlib import Path
import pyreadr
import pandas as pd

ROOT = Path(__file__).parent
RAW = ROOT / "data" / "raw" / "vdem-v16.RData"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

EUROPE_COUNTRIES = [
    "United Kingdom", "Ireland", "France", "Germany", "German Democratic Republic",
    "Netherlands", "Belgium", "Luxembourg", "Austria", "Switzerland", "Italy",
    "Spain", "Portugal", "Greece", "Cyprus", "Malta",
    "Denmark", "Sweden", "Norway", "Finland", "Iceland",
    "Poland", "Czechia", "Slovakia", "Hungary", "Slovenia",
    "Estonia", "Latvia", "Lithuania",
    "Romania", "Bulgaria", "Croatia", "Serbia", "Bosnia and Herzegovina",
    "Albania", "North Macedonia", "Kosovo", "Montenegro",
    "Russia", "Ukraine", "Belarus", "Moldova",
    "Türkiye",
]

INDICATORS = [
    "country_name", "country_id", "country_text_id", "year", "historical_date",
    "v2x_polyarchy",
    "v2x_libdem",
    "v2x_partipdem",
    "v2x_delibdem",
    "v2x_egaldem",
    "v2x_freexp_altinf",
    "v2x_rule",
    "v2xcs_ccsi",
    "v2x_regime",
]


def main() -> None:
    print(f"Reading {RAW} …")
    result = pyreadr.read_r(str(RAW))
    df = result["vdem"]
    print(f"Full V-Dem shape: {df.shape}")
    print(f"Year range: {df['year'].min()} – {df['year'].max()}")

    present = [c for c in INDICATORS if c in df.columns]
    missing = set(INDICATORS) - set(present)
    if missing:
        print(f"NOTE — missing columns in v16: {missing}")
    df = df[present].copy()

    europe_present = sorted(set(EUROPE_COUNTRIES) & set(df["country_name"].unique()))
    europe_missing = sorted(set(EUROPE_COUNTRIES) - set(df["country_name"].unique()))
    print(f"\nEurope countries found ({len(europe_present)}):")
    for c in europe_present:
        print(f"  • {c}")
    if europe_missing:
        print(f"\nEurope countries NOT found (check V-Dem naming):")
        for c in europe_missing:
            print(f"  • {c}")

    europe = df[df["country_name"].isin(europe_present)].copy()
    europe = europe[(europe["year"] >= 1900) & (europe["year"] <= 2024)].copy()
    print(f"\nEurope 1900-2024 shape: {europe.shape}")

    out_path = OUT / "vdem_europe.csv"
    europe.to_csv(out_path, index=False)
    print(f"\nWrote {out_path} ({out_path.stat().st_size / 1024:.1f} KB)")

    with open(OUT / "variables.txt", "w") as f:
        f.write("V-Dem v16 — variables kept for the Europe dashboard\n")
        f.write("=" * 60 + "\n\n")
        for col in present:
            f.write(f"{col}\n")

    print("\nSample rows:")
    print(europe.sample(min(5, len(europe)), random_state=1).to_string())


if __name__ == "__main__":
    main()
