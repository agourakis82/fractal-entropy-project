"""
Supplementary Methods — Figure Generation (FoS, isolated)
Saves figures only under fos/manuscript/core/figures to avoid conflicts.
"""
import os, numpy as np, matplotlib.pyplot as plt, pandas as pd
OUT = "fos/manuscript/core/figures"; os.makedirs(OUT, exist_ok=True)

# Grid and fields
x = np.linspace(-3, 3, 120); y = np.linspace(-3, 3, 120)
X, Y = np.meshgrid(x, y)
V = (X**4 + Y**4)/18 - (X**2 + Y**2)/3
psi2 = 0.6*np.exp(-((X-1.2)**2 + (Y+0.6)**2)/0.7) + 0.4*np.exp(-((X+1.0)**2 + (Y-0.8)**2)/0.5)

# Fig1 — 3D surface (no explicit styles)
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
fig1 = plt.figure(figsize=(6,4))
ax1 = fig1.add_subplot(111, projection='3d')
ax1.plot_surface(X, Y, psi2)
ax1.set_xlabel("Symbolic dimension 1"); ax1.set_ylabel("Symbolic dimension 2"); ax1.set_zlabel("|ψ_s|^2")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "Fig1.png"), dpi=300); plt.close(fig1)

# Fig2 — 2D density + V contours
fig2, ax2 = plt.subplots(figsize=(5,4))
ax2.imshow(psi2, extent=[x.min(), x.max(), y.min(), y.max()], origin='lower', aspect='auto')
CS = ax2.contour(X, Y, V)
ax2.clabel(CS, inline=True, fontsize=6)
ax2.set_xlabel("Symbolic dimension 1"); ax2.set_ylabel("Symbolic dimension 2")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "Fig2.png"), dpi=300); plt.close(fig2)

# Fig3 — rank–frequency (SWOW-style subset)
data = [
    ("order","law",48),("order","structure",22),("order","chaos",5),
    ("freedom","choice",35),("freedom","rights",28),("freedom","order",9),
    ("law","order",40),("law","justice",33),("law","punishment",14),
    ("chaos","disorder",42),("chaos","freedom",6),("chaos","creation",8),
    ("norm","conformity",31),("norm","sanction",19),("norm","deviance",12),
    ("identity","group",27),("identity","self",21),("identity","belonging",24),
]
df = pd.DataFrame(data, columns=["cue","response","strength"])
rf = df.groupby("response")["strength"].sum().sort_values(ascending=False).reset_index()
rf["rank"] = np.arange(1, len(rf)+1); rf["log_rank"] = np.log10(rf["rank"]); rf["log_freq"] = np.log10(rf["strength"])

fig3, ax3 = plt.subplots(figsize=(4.5,3.8))
ax3.plot(rf["log_rank"], rf["log_freq"], marker='o')
ax3.set_xlabel("log10(rank)"); ax3.set_ylabel("log10(total strength)"); ax3.set_title("Rank–frequency (aggregated responses)")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "Fig3.png"), dpi=300); plt.close(fig3)
