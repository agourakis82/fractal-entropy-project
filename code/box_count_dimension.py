import networkx as nx, numpy as np
def box_count_dimension(G, q=1):
    degrees = np.array([d for _, d in G.degree()])
    hist, bins = np.histogram(degrees, bins='auto', density=True)
    p = hist[hist > 0]
    if q == 1:
        return -np.sum(p * np.log(p)) / np.log(bins[-1]-bins[-2])
    else:
        return np.log(np.sum(p**q)/(bins[-1]-bins[-2]))/(1-q)

def box_count_dimension(G, q=1, epsilons=None):
    """
    Estimate multifractal dimension D_q for an ego graph G.
    Parameters
    ----------
    G : networkx.Graph
    q : float
    epsilons : iterable, box sizes (defaults to logspace)
    Returns
    -------
    D_q : float
    """
    # TODO: implement
    pass