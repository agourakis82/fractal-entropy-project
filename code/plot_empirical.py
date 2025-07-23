import pandas as pd, matplotlib.pyplot as plt, pathlib
data = pd.read_csv("../paper_data/run_20250723.csv")   # ajuste data
pivot = data.pivot(index="beta", columns="alpha", values="D1")
plt.imshow(pivot, origin="lower", aspect="auto",
           extent=[data.alpha.min(), data.alpha.max(),
                   data.beta.min(), data.beta.max()])
plt.xscale("log"); plt.yscale("log")
plt.xlabel(r"$\alpha$"); plt.ylabel(r"$\beta$")
plt.colorbar(label="D1 empirical")
out = pathlib.Path("../paper_model/figs/Fig4_heatmap_empirical.pdf")
plt.savefig(out, bbox_inches="tight")