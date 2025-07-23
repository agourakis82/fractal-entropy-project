#!/usr/bin/env python
import argparse, networkx as nx, numpy as np, csv, time, pathlib

def bernoulli_step(G, alpha, beta, rng):
    for u in G.nodes:
        k = G.degree[u]
        if rng.random() < np.exp(-alpha * k):
            # add tie
            v = rng.choice(G.nodes)
            G.add_edge(u, v)
        if G.degree[u] > 0 and rng.random() < beta:
            # remove random tie (social trimming)
            v = rng.choice(list(G.neighbors(u)))
            G.remove_edge(u, v)
    return G

def run_sim(N, steps, alpha, beta, seed=0):
    rng = np.random.default_rng(seed)
    G = nx.gnm_random_graph(N, N*3, seed=seed)
    for _ in range(steps):
        bernoulli_step(G, alpha, beta, rng)
    return G

def main():
    p = argparse.ArgumentParser(description="Bernoulli–fractal social simulation")
    p.add_argument("--N", type=int, default=10000)
    p.add_argument("--steps", type=int, default=10000)
    p.add_argument("--alpha", type=float, default=0.3)
    p.add_argument("--beta", type=float, default=0.02)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--outcsv", default=None, help="If given, append summary to CSV")
    args = p.parse_args()

    t0 = time.time()
    G = run_sim(args.N, args.steps, args.alpha, args.beta, args.seed)
    runtime = time.time() - t0

    from box_count_dimension import box_count_dimension
    D1, ci_low, ci_high = box_count_dimension(G, q=1, bootstrap=200)

    print(f"D1={D1:.3f}  95%CI=[{ci_low:.3f},{ci_high:.3f}]  runtime={runtime:.1f}s")

    if args.outcsv:
        header = not pathlib.Path(args.outcsv).exists()
        with open(args.outcsv, "a", newline="") as f:
            w = csv.writer(f)
            if header:
                w.writerow(["N","steps","alpha","beta","seed","D1","ci_low","ci_high","runtime"])
            w.writerow([args.N,args.steps,args.alpha,args.beta,args.seed,f"{D1:.3f}",f"{ci_low:.3f}",f"{ci_high:.3f}",f"{runtime:.1f}"])

if __name__ == "__main__":
    main()