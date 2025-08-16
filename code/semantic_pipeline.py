#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pipeline mínimo:
1) Carrega arestas SWOW (cue,target,weight) -> grafo ponderado.
2) Embedding simples (SVD do adjacente) -> UMAP 2D + k-means com silhueta.
3) Curvatura de Ollivier (maior componente) + entropia por nó.
4) Rewire progressivo -> curva média de entropia×curvatura (colapso/recuperação).
Salva figuras e CSVs em --outdir.
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from GraphRicciCurvature.OllivierRicci import OllivierRicci
from sklearn.cluster import KMeans
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import silhouette_score
from umap import UMAP


def read_edges(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    cols = {c.lower(): c for c in df.columns}
    # tenta mapear nomes comuns
    cue = cols.get("cue") or cols.get("source") or list(df.columns)[0]
    tgt = cols.get("target") or cols.get("response") or list(df.columns)[1]
    # peso: weight, strength, R1.Strength...
    weight = (cols.get("weight") or cols.get("strength") or
              cols.get("r1.strength") or cols.get("w") or
              (list(df.columns)[2] if df.shape[1] >= 3 else None))
    if weight is None:
        df["weight"] = 1.0
        weight = "weight"
    # normaliza tipos
    out = df[[cue, tgt, weight]].copy()
    out.columns = ["cue", "target", "weight"]
    out["weight"] = pd.to_numeric(out["weight"], errors="coerce").fillna(1.0)
    return out


def build_graph(edges: pd.DataFrame, undirected: bool = True) -> nx.Graph:
    if undirected:
        # agrega pesos simétricos
        s = (edges.groupby(["cue", "target"])["weight"]
                  .sum()
                  .reset_index())
        # soma espelhos
        s_rev = s.rename(columns={"cue": "target", "target": "cue"})
        all_e = pd.concat([s, s_rev], ignore_index=True)
        agg = (all_e.groupby(["cue", "target"])["weight"]
                    .sum()
                    .reset_index())
        G = nx.Graph()
    else:
        agg = edges.copy()
        G = nx.DiGraph()
    for r in agg.itertuples(index=False):
        if r.cue == r.target:
            continue
        G.add_edge(str(r.cue), str(r.target), weight=float(r.weight))
    return G


def largest_component(G: nx.Graph) -> nx.Graph:
    if G.is_directed():
        comps = nx.weakly_connected_components(G)
    else:
        comps = nx.connected_components(G)
    nodes = max(comps, key=len)
    return G.subgraph(nodes).copy()


def adjacency_embedding(G: nx.Graph, dim: int = 128) -> Tuple[np.ndarray, list[str]]:
    nodes = list(G.nodes())
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    data = np.zeros((n, n), dtype=float)
    for u, v, w in G.edges(data="weight"):
        i, j = idx[u], idx[v]
        data[i, j] = w
        data[j, i] = w
    # normalização simples
    row_sum = data.sum(axis=1, keepdims=True) + 1e-9
    P = data / row_sum
    svd = TruncatedSVD(n_components=min(dim, max(2, n - 1)), random_state=42)
    X = svd.fit_transform(P)
    return X, nodes


def umap_kmeans(X: np.ndarray, nodes: list[str], outdir: Path) -> pd.DataFrame:
    um = UMAP(n_neighbors=25, min_dist=0.05, metric="cosine", random_state=42)
    U = um.fit_transform(X)
    ks = range(2, 9)
    sils = []
    labels_best = None
    k_best = None
    best = -1.0
    for k in ks:
        km = KMeans(n_clusters=k, n_init=20, random_state=42)
        y = km.fit_predict(U)
        s = silhouette_score(U, y, metric="euclidean")
        sils.append(s)
        if s > best:
            best, k_best, labels_best = s, k, y
    # figuras
    outdir.mkdir(parents=True, exist_ok=True)
    plt.figure()
    plt.plot(list(ks), sils, marker="o")
    plt.xlabel("k")
    plt.ylabel("Silhueta média")
    plt.title("Silhueta vs k (UMAP)")
    plt.grid(True, alpha=0.3)
    plt.savefig(outdir / "Fig_silhouette_vs_k.png", dpi=200, bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(6, 5))
    plt.scatter(U[:, 0], U[:, 1], s=6, c=labels_best, alpha=0.8)
    plt.xlabel("UMAP-1")
    plt.ylabel("UMAP-2")
    plt.title(f"UMAP + k-means (k={k_best}, sil={best:.2f})")
    plt.tight_layout()
    plt.savefig(outdir / "Fig_umap_clusters.png", dpi=220)
    plt.close()

    df = pd.DataFrame(
        {"node": nodes, "umap_x": U[:, 0], "umap_y": U[:, 1], "cluster": labels_best}
    )
    df.to_csv(outdir / "umap_clusters.csv", index=False)
    return df


def node_entropy(G: nx.Graph) -> pd.Series:
    ent = {}
    for n in G.nodes():
        nbrs = G[n]
        if not nbrs:
            ent[n] = 0.0
            continue
        w = np.array([nbrs[v].get("weight", 1.0) for v in nbrs], dtype=float)
        p = w / (w.sum() + 1e-12)
        h = -(p * np.log2(p + 1e-12)).sum()
        ent[n] = float(h)
    return pd.Series(ent)


def ricci_curvature(G: nx.Graph) -> pd.DataFrame:
    orc = OllivierRicci(G, alpha=0.5, verbose="ERROR", method="OTD")
    orc.compute_ricci_curvature()
    rows = []
    for u, v, d in orc.G.edges(data=True):
        rows.append({"u": u, "v": v, "orc": d.get("ricciCurvature", np.nan)})
    return pd.DataFrame(rows)


def plot_curv_entropy(Gc: nx.Graph, curv_df: pd.DataFrame, outdir: Path) -> None:
    deg = dict(Gc.degree())
    ent = node_entropy(Gc)
    curv_edge = curv_df["orc"].values
    # ORC hist
    plt.figure()
    plt.hist(curv_edge, bins=50, alpha=0.9)
    plt.xlabel("Curvatura de Ollivier (arestas)")
    plt.ylabel("freq")
    plt.title("Distribuição de curvatura")
    plt.tight_layout()
    plt.savefig(outdir / "Fig_orc_hist.png", dpi=200)
    plt.close()
    # entropia hist
    plt.figure()
    plt.hist(ent.values, bins=40, alpha=0.9)
    plt.xlabel("Entropia de vizinhança (bits) — nós")
    plt.ylabel("freq")
    plt.title("Entropia local")
    plt.tight_layout()
    plt.savefig(outdir / "Fig_entropy_hist.png", dpi=200)
    plt.close()
    # curva vs grau (média por nó via média das arestas incidentes)
    edge_map = {}
    for r in curv_df.itertuples(index=False):
        edge_map[(r.u, r.v)] = r.orc
        edge_map[(r.v, r.u)] = r.orc
    curv_node = {}
    for n in Gc.nodes():
        cs = [edge_map[(n, v)] for v in Gc[n]]
        curv_node[n] = float(np.mean(cs)) if cs else np.nan
    # scatter
    d = np.array([deg[n] for n in Gc.nodes()], dtype=float)
    c = np.array([curv_node[n] for n in Gc.nodes()], dtype=float)
    plt.figure()
    plt.scatter(d, c, s=6, alpha=0.6)
    plt.xlabel("Grau")
    plt.ylabel("Curvatura média (nó)")
    plt.title("Curvatura × Grau")
    plt.tight_layout()
    plt.savefig(outdir / "Fig_curvature_vs_degree.png", dpi=220)
    plt.close()
    # salva CSV
    pd.DataFrame({"node": list(Gc.nodes()), "degree": d, "curv_node": c,
                  "entropy": [ent[n] for n in Gc.nodes()]}
                 ).to_csv(outdir / "node_metrics.csv", index=False)


def rewire_curve(Gc: nx.Graph, steps: int, outdir: Path) -> None:
    """rewire preservando grau (double_edge_swap) e mede <H_node> e <ORC_edge>"""
    rng = np.random.default_rng(42)
    n_swaps = max(1, Gc.number_of_edges() // 50)
    ps, mean_H, mean_ORC = [], [], []
    base = Gc.copy()
    for i, p in enumerate(np.linspace(0.0, 1.0, steps)):
        Gp = base.copy()
        # número de swaps proporcional a p
        nx.double_edge_swap(Gp, nswap=int(p * n_swaps), max_tries=10 * n_swaps, seed=42)
        ent = node_entropy(Gp).mean()
        curv = ricci_curvature(largest_component(Gp))["orc"].mean()
        ps.append(p)
        mean_H.append(ent)
        mean_ORC.append(curv)
    df = pd.DataFrame({"p_rewire": ps, "mean_entropy": mean_H, "mean_orc": mean_ORC})
    df.to_csv(outdir / "rewire_entropy_curvature.csv", index=False)
    plt.figure()
    plt.plot(ps, mean_H, marker="o", label="⟨Entropia (nós)⟩")
    plt.plot(ps, mean_ORC, marker="s", label="⟨ORC (arestas)⟩")
    plt.xlabel("fração de rewire (preserva grau)")
    plt.legend()
    plt.title("Colapso/recuperação: entropia × curvatura")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(outdir / "Fig_rewire_entropy_curvature.png", dpi=220)
    plt.close()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--swow", type=Path, required=True,
                   help="CSV de arestas (cue,target,weight)")
    p.add_argument("--outdir", type=Path, default=Path("results_semantic"))
    p.add_argument("--max_nodes", type=int, default=5000,
                   help="limita por maior grau (para velocidade)")
    args = p.parse_args()

    out = args.outdir
    out.mkdir(parents=True, exist_ok=True)

    edges = read_edges(args.swow)
    G = build_graph(edges, undirected=True)

    # recorta top-N por grau para acelerar
    deg = dict(G.degree())
    keep = set(sorted(G.nodes(), key=lambda n: deg[n], reverse=True)[:args.max_nodes])
    G = G.subgraph(keep).copy()
    Gc = largest_component(G)

    # 1) UMAP + clusters
    X, nodes = adjacency_embedding(Gc, dim=128)
    df_umap = umap_kmeans(X, nodes, out)

    # 2) Curvatura + entropia
    curv_df = ricci_curvature(Gc)
    plot_curv_entropy(Gc, curv_df, out)

    # 3) Rewire curve
    rewire_curve(Gc, steps=9, outdir=out)

    print("[ok] figuras e CSVs em:", out.resolve())


if __name__ == "__main__":
    main()