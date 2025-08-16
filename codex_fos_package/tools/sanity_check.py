#!/usr/bin/env python3
import re, sys, argparse, pathlib

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True, help="path to main.log")
    args = ap.parse_args()
    p = pathlib.Path(args.log)
    if not p.exists():
        print(f"!! [sanity] Log not found: {p}")
        return 1
    txt = p.read_text(errors="ignore")
    errs = []
    warns = []

    if "Undefined control sequence" in txt or "Emergency stop" in txt:
        errs.append("LaTeX: Undefined control sequence / emergency stop detected.")
    if "There were undefined references" in txt or "LaTeX Warning: There were undefined references." in txt:
        errs.append("LaTeX: Undefined references present.")
    if "LaTeX Warning: Citation" in txt and "undefined" in txt:
        errs.append("LaTeX: Undefined citations present.")
    if "File `Orcidlogo.eps' not found" in txt:
        warns.append("Missing Orcidlogo.eps (either add the EPS or comment \\orcid{...}).")
    # Overfull hbox count
    overfull = len(re.findall(r"Overfull \\\\hbox", txt))
    if overfull > 0:
        warns.append(f"{overfull} overfull hbox occurrences. Consider adding \\emergencystretch=3em and breaking long URLs.")
    # Hyperref bookmark level warnings
    if "Package hyperref Warning: Difference" in txt:
        warns.append("Hyperref bookmark level differences detected. Avoid skipping heading levels or add TOC entries for starred sections.")

    if errs:
        print("!! [sanity] ERRORS:")
        for e in errs:
            print("   - " + e)
        return 2
    print(">> [sanity] No fatal errors detected.")
    if warns:
        print(">> [sanity] WARNINGS:")
        for w in warns:
            print("   - " + w)
    return 0

if __name__ == "__main__":
    sys.exit(main())
