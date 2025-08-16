#!/usr/bin/env python3
import os, sys, argparse, pathlib, shutil, zipfile

AUX_EXTS = {".aux",".log",".out",".toc",".lof",".lot",".fls",".fdb_latexmk",".synctex.gz",".bbl",".blg"}

def add_file(z, base_dir, relpath):
    p = (base_dir / relpath).resolve()
    if not p.exists():
        return False
    z.write(p, arcname=relpath.as_posix())
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="Manuscript directory (e.g., fos/manuscript/core)")
    ap.add_argument("--dist", required=True, help="Dist output dir")
    ap.add_argument("--zip", required=True, help="Zip filename")
    ap.add_argument("--with-pdf", required=True, choices=["true","false"], help="Include main.pdf in zip")
    args = ap.parse_args()

    src = pathlib.Path(args.src).resolve()
    dist = pathlib.Path(args.dist).resolve()
    dist.mkdir(parents=True, exist_ok=True)
    zip_path = dist / args.zip

    if zip_path.exists():
        zip_path.unlink()

    files = []
    # Collect required sources
    needed = ["main.tex", "references.bib", "sn-jnl.cls"]
    # Try both styles; include whichever exists
    styles = ["sn-chicago.bst", "sn-basic.bst"]
    figures = []
    for f in src.glob("*"):
        if f.suffix.lower() in AUX_EXTS:
            continue
        # include figures in same dir (flat) or under ./figures
    figdir = src/"figures"
    if figdir.exists():
        for g in figdir.iterdir():
            if g.is_file():
                figures.append(("figures/"+g.name, g))

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        # add required files if present
        for n in needed:
            p = src / n
            if p.exists():
                z.write(p, arcname=n)
        # add available styles
        have_style = False
        for s in styles:
            p = src / s
            if p.exists():
                z.write(p, arcname=s)
                have_style = True
        # add figures (preserve figures/)
        for relname, p in figures:
            z.write(p, arcname=relname)
        # optionally add PDF
        if args.with_pdf == "true":
            pdf = src / "main.pdf"
            if pdf.exists():
                z.write(pdf, arcname="main.pdf")

    print(f">> [pkg] Wrote zip: {zip_path}")
    # Simple hints
    hints = []
    if not (src/"sn-jnl.cls").exists():
        hints.append("sn-jnl.cls missing in sources (copy from Springer template).")
    if not any((src/s).exists() for s in styles):
        hints.append("No .bst found (sn-chicago.bst or sn-basic.bst); add one into manuscript dir.")
    if hints:
        print(">> [pkg] HINTS:")
        for h in hints:
            print("   - " + h)
    return 0

if __name__ == "__main__":
    sys.exit(main())
