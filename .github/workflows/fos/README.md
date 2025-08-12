# Foundations of Science — Submission Package (FoS)
This directory is **self-contained**. It does not modify legacy pipelines.
- Generate figures: `python3 fos/code/methods_figure_generation.py`
- Compile PDF (LaTeX sn-jnl): `latexmk -pdf -cd fos/manuscript/core/main.tex`
- Figures are saved only under `fos/manuscript/core/figures/`
