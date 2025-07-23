from mc_sim import run_sim
from box_count_dimension import box_count_dimension
import numpy as np, pandas as pd, pathlib

N, steps = 10000, 12000
def Lambda(t):          # Gaussian at t0=5000
    return 0.8*np.exp(-((t-5000)/500)**2)

G = run_sim(N, steps, alpha=0.3, beta=0.02, Lambda_func=Lambda, seed=42)
if not hasattr(G, "subgraph"):
    raise TypeError("run_sim did not return a graph object with a 'subgraph' method.")
window = 200           # sliding window size
D_ts = []
for t in range(0, steps, window):
    sub = G.subgraph(list(G.nodes)[t:t+window])
    D1,_,_ = box_count_dimension(sub, q=1, bootstrap=100)
    D_ts.append(D1)

pd.Series(D_ts).to_csv("../paper_data/H2_timeseries.csv", index=False)