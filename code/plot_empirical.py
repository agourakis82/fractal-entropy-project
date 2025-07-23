import pandas as pd
import matplotlib.pyplot as plt
import pathlib

# Carrega o CSV (ajuste o nome se necessário)
data = pd.read_csv("../paper_data/run_20250723.csv")

# Gera matriz de calor (pivot)
pivot = data.pivot(index="beta", columns="alpha", values="D1")

# Plota heatmap
plt.figure(figsize=(6, 4))
plt.imshow(pivot, origin="lower", aspect="auto",
           extent=[pivot.columns.min(), pivot.columns.max(),
                   pivot.index.min(), pivot.index.max()])
plt.xlabel(r"$\alpha$")
plt.ylabel(r"$\beta$")
plt.xscale("log")
plt.yscale("log")
plt.colorbar(label="D₁ empirical")

# Cria pasta se necessário e salva figura
out = pathlib.Path("../paper_model/figs/Fig4_heatmap_empirical.pdf")
out.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(out, bbox_inches="tight")
plt.close()