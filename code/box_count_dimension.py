import numpy as np
def box_count_dimension(G, q=1, bootstrap=200):
    degrees = np.array([d for _, d in G.degree()])
    hist, bins = np.histogram(degrees, bins="auto", density=True)
    p = hist[hist > 0]
    delta = bins[1] - bins[0]
    if q == 1:
        D1 = -np.sum(p * np.log(p)) / np.log(delta)
    else:
        D1 = np.log(np.sum(p**q) / delta) / (1 - q)

    # bootstrap CI
    boots = []
    rng = np.random.default_rng(42)
    for _ in range(bootstrap):
        sample = rng.choice(degrees, size=len(degrees), replace=True)
        h, b = np.histogram(sample, bins=bins, density=True)
        pp = h[h > 0]
        if q == 1:
            d1 = -np.sum(pp * np.log(pp)) / np.log(delta)
        else:
            d1 = np.log(np.sum(pp**q) / delta) / (1 - q)
        boots.append(d1)
    ci = np.percentile(boots, [2.5, 97.5])
    return D1, ci[0], ci[1]