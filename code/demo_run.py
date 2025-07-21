from mc_sim import run_sim
from box_dimension import box_count_dimension
import pandas as pd

G = run_sim(1000, 500, alpha=0.3, beta=0.02)
D1 = box_count_dimension(G, q=1)
df = pd.DataFrame({'alpha':[0.3],'beta':[0.02],'D1':[D1]})
df.to_csv('../paper_data/demo_metrics.csv', index=False)
print("D1 =", D1)