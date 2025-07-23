import numpy as np

def _shannon_entropy(p):
    p = p[p > 0]
    return -np.sum(p * np.log(p))

def box_count_dimension(G, q=1, bootstrap=200):
    deg = np.array([d for _, d in G.degree()])
    # 6 escalas log‑espalhadas entre 1 e max degree
    eps = np.unique(
        np.geomspace(1, max(deg), num=6, dtype=int)
    )
    if eps[0] != 1:
        eps = np.insert(eps, 0, 1)

    S = []  # entropias por escala
    for e in eps:
        hist, _ = np.histogram(deg, bins=range(0, max(deg)+e, e), density=True)
        if q == 1:
            S.append(_shannon_entropy(hist))
        else:
            p = hist[hist > 0]
            S.append(np.log(np.sum(p**q))/(1-q))

    # Regressão linear S = -D_q * log ε  → slope = -D_q
    slope, _ = np.polyfit(np.log(eps), S, deg=1)
    Dq = -slope

    # Bootstrap
    boots = []
    rng = np.random.default_rng(42)
    for _ in range(bootstrap):
        sample = rng.choice(deg, size=len(deg), replace=True)
        S_b = []
        for e in eps:
            h, _ = np.histogram(sample, bins=range(0, max(sample)+e, e), density=True)
            if q == 1:
                S_b.append(_shannon_entropy(h))
            else:
                p = h[h > 0]
                S_b.append(np.log(np.sum(p**q))/(1-q))
        slope_b, _ = np.polyfit(np.log(eps), S_b, deg=1)
        boots.append(-slope_b)

    ci_low, ci_high = np.percentile(boots, [2.5, 97.5])
    return Dq, ci_low, ci_high