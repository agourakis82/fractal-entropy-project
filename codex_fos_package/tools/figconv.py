#!/usr/bin/env python3
import os, sys, shutil, subprocess, argparse, glob, pathlib

def exists(cmd):
    return shutil.which(cmd) is not None

def convert_one(src_path, out_pdf):
    src = str(src_path)
    dst = str(out_pdf)
    ext = src_path.suffix.lower()
    # Prefer ImageMagick if available
    if exists("magick"):
        cmd = ["magick", src, dst]
        return subprocess.run(cmd).returncode == 0
    # macOS sips to PDF
    if exists("sips"):
        cmd = ["sips", "-s", "format", "pdf", src, "--out", dst]
        return subprocess.run(cmd).returncode == 0
    # Inkscape for SVG
    if ext == ".svg" and exists("inkscape"):
        cmd = ["inkscape", src, "--export-filename", dst]
        return subprocess.run(cmd).returncode == 0
    # Ghostscript for EPS/PDF conversions (rarely needed here)
    # Fallback fail
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--figdir", required=True, help="Directory with figures")
    args = ap.parse_args()
    figdir = pathlib.Path(args.figdir)
    if not figdir.exists():
        print(f">> [figconv] No figure dir: {figdir}")
        return 0

    patterns = ["*.png","*.jpg","*.jpeg","*.tif","*.tiff","*.svg"]
    files = []
    for pat in patterns:
        files.extend(figdir.glob(pat))

    if not files:
        print(">> [figconv] No raster/SVG figures to convert.")
        return 0

    ok, fail = 0, 0
    for p in files:
        out_pdf = p.with_suffix(".pdf")
        if out_pdf.exists():
            continue
        print(f">> [figconv] Converting {p.name} -> {out_pdf.name}")
        if convert_one(p, out_pdf):
            ok += 1
        else:
            print(f"!! [figconv] Could not convert {p.name}. Install ImageMagick (magick) or use vector export from source.")
            fail += 1
    print(f">> [figconv] Done. Converted ok={ok}, failed={fail}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
