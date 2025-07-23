import pandas as pd, matplotlib.pyplot as plt, numpy as np, pathlib
ts = pd.read_csv("../paper_data/H2_timeseries.csv", squeeze=True)
t = np.arange(len(ts))*200
plt.plot(t, ts)
plt.axvline(5000, linestyle="--", label=r"peak $\Lambda$")
plt.xlabel("t")
plt.ylabel(r"$D_1$")
plt.title("Recovery of $D_1$ after symbolic rupture")
plt.legend()
out = pathlib.Path(__file__).resolve().parent.parent / "paper_model/figs/Fig5_H2_decay.pdf"
out.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(out, bbox_inches="tight")
print("Figura salva em", out)