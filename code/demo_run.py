import os
import pandas as pd
from mc_sim import run_sim
from box_count_dimension import box_count_dimension  # Certifique-se do nome correto

# Simulação
G = run_sim(1000, 500, alpha=0.3, beta=0.02)

# Calcular dimensão fractal
D1 = box_count_dimension(G)  # Se sua função aceitar 'q', adicione: q=1

# Garantir que a pasta existe
os.makedirs("../paper_data", exist_ok=True)

# Salvar os dados
df = pd.DataFrame({'alpha': [0.3], 'beta': [0.02], 'D1': [D1]})
df.to_csv("../paper_data/demo_metrics.csv", index=False)

print("✅ Dimensão D1 calculada:", D1)