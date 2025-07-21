import networkx as nx
import numpy as np

def bernoulli_step(G, alpha, beta):
    """Single Euler step of Bernoulli social flow."""
    for u in G.nodes:
        k = G.degree[u]
        prob_add = min(1, np.exp(-alpha * k) + beta)
        if np.random.rand() < prob_add:
            v = np.random.choice(G.nodes)
            G.add_edge(u, v)
    return G

def run_sim(N=10000, steps=10000, alpha=0.3, beta=0.02):
    G = nx.gnm_random_graph(N, N*3)  # avg deg ~6
    for _ in range(steps):
        G = bernoulli_step(G, alpha, beta)
    return G