#!/usr/bin/env python3
"""
Plot heatmaps from CSV and fix D1=inf/NaN issues with robust guards.

Example:
  python code/plot_empirical.py --input paper_data/run_20250723.csv       --x alpha --y beta --z D1 --out figures/heatmap_D1.png --impute median
"""
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from utils_fractal import sanitize_series

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="CSV with columns for x,y,z")
    ap.add_argument("--x", required=True, help="x column (e.g., alpha)")
    ap.add_argument("--y", required=True, help="y column (e.g., beta)")
    ap.add_argument("--z", required=True, help="z column (e.g., D1)")
    ap.add_argument("--out", required=True, help="output image path (png/pdf)")
    ap.add_argument("--impute", choices=["none","median","zero"], default="median")
    ap.add_argument("--title", default="D1 heatmap")
    args = ap.parse_args()

    df = pd.read_csv(args.input)
    for col in [args.x, args.y, args.z]:
        if col not in df.columns:
            raise SystemExit(f"Column '{col}' not found in {args.input} (have: {list(df.columns)})")
    # numeric casting
    for col in [args.x, args.y, args.z]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # sanitize z
    z_vals = sanitize_series(df[args.z].values, method=args.impute)
    df[args.z] = z_vals

    # pivot into grid (sorted unique coordinates)
    pivot = df.pivot_table(index=args.y, columns=args.x, values=args.z, aggfunc="mean")
    Z = pivot.values.astype(float)

    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=150)
    c = ax.pcolormesh(pivot.columns.values, pivot.index.values, Z, shading="auto")
    cb = fig.colorbar(c, ax=ax, shrink=0.9)
    ax.set_xlabel(args.x)
    ax.set_ylabel(args.y)
    ax.set_title(args.title)
    ax.grid(True, which="both", alpha=0.2)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(args.out)
    print(f"[ok] saved {args.out} ({Z.shape[1]}x{Z.shape[0]})")

if __name__ == "__main__":
    main()
