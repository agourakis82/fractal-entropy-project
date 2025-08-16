# CODEX – Submission Package (Foundations of Science / Springer)

## What this does
- Converts figures to PDF (if needed).
- Builds LaTeX (pdflatex + bibtex) with Springer `sn-jnl.cls`.
- Runs sanity checks.
- Creates two ZIPs:
  - `submission_source.zip` — sources only (no PDF) for Editorial Manager.
  - `for_review_with_pdf.zip` — includes compiled `main.pdf` (for internal review).

## Quick Start
1) Drop this `codex_fos_package/` folder into your repo root.
2) Ensure your manuscript is under `fos/manuscript/core/` with:
   - `main.tex`, `references.bib`, `sn-jnl.cls`, `sn-chicago.bst` (or `sn-basic.bst`), and `figures/`.
3) (Optional) Copy templates:  
   - `templates/main.tex` → `fos/manuscript/core/main.tex`  
   - `templates/references.bib` → `fos/manuscript/core/references.bib`
4) Run:
```bash
make          # figures + pdf + sanity
make package  # submission_source.zip
make package-pdf
make docx     # optional, if pandoc is installed
```

## Notes
- If `sn-chicago.bst` is missing, the build falls back to `sn-basic.bst` and patches `\\bibliographystyle{...}` in `main.tex`.
- If `Orcidlogo.eps` is missing, either comment `\\orcid{...}` or add an EPS icon in the manuscript dir.
- ZIPs are written under `dist/`. Unzip in a clean folder and test compile to simulate the publisher’s environment.

## CI (optional)
You can call `make` in GitHub Actions to validate that the paper compiles in a clean environment before submission.
