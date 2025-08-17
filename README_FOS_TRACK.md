# FoS track (manuscrito + código) — pronto para integrar ao repositório

## Estrutura
```
fos_track_package/
  fos/
    main.tex
    references_fos.bib
  code/
    utils_fractal.py
    plot_empirical.py
    demo_run.py
  paper_data/
  figures/
```

## Roteiro em **3 comandos** (gera dado demo + heatmap)
```bash
python code/demo_run.py
python code/plot_empirical.py --input paper_data/demo_metrics.csv   --x alpha --y beta --z D1 --out figures/heatmap_D1.png --impute median
# (opcional) compilar LaTeX
pdflatex fos/main.tex && bibtex main && pdflatex fos/main.tex && pdflatex fos/main.tex
```
- `plot_empirical.py` corrige automaticamente `inf/NaN` em D1 (imputação `--impute median` por padrão) e
  **clipa extremos** por quantis (1–99%) para estabilizar a paleta.

## Como usar com seu CSV real
```bash
python code/plot_empirical.py --input paper_data/run_YYYYMMDD.csv   --x alpha --y beta --z D1 --out figures/heatmap_D1.png --impute median
```
- Se sua coluna de intensidade tiver outro nome (ex.: `D1_est`), troque `--z D1` por `--z D1_est`.
- O script faz `pivot` por média quando houver múltiplas medições por célula.

## Integração ao Git
1) Crie a pasta `fos/` na raiz do seu repo (ou mova estes arquivos para lá).
2) Coloque `code/*.py` junto do seu pipeline de simulação para reutilizar `plot_empirical.py`.
3) Adicione ao `.gitignore` os artefatos LaTeX: `*.aux,*.bbl,*.blg,*.out,*.toc,*.synctex*`.

## Requisitos mínimos
```
python >= 3.9
numpy, pandas, matplotlib
TeX Live com sn-jnl e pgfplots (compat=1.18)
```
