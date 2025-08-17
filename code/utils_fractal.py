import numpy as np

def safe_clip_probs(p, eps=1e-12):
    """Clip probabilities to (eps,1) and renormalize to avoid log(0) and inf/NaN."""
    p = np.asarray(p, dtype=float)
    if p.ndim == 0:
        p = p[None]
    p = np.clip(p, eps, np.inf)
    s = p.sum()
    if not np.isfinite(s) or s <= 0:
        # fallback to uniform if degenerate
        p = np.full_like(p, 1.0 / p.size)
    else:
        p = p / s
    return p

def shannon_entropy(p, eps=1e-12):
    """Shannon entropy with guards: finite even if zeros present."""
    p = safe_clip_probs(p, eps=eps)
    return float(-(p * np.log(p)).sum())

def generalized_q_entropy(p, q, eps=1e-12):
    """Rényi/Tsallis base components with guards for q != 1."""
    p = safe_clip_probs(p, eps=eps)
    if np.isclose(q, 1.0):
        return shannon_entropy(p, eps=eps)
    s = (p ** q).sum()
    if not np.isfinite(s) or s <= 0:
        return np.nan
    return float(np.log(s) / (1.0 - q))

def sanitize_series(x, method="median", clip_quantiles=(1.0, 99.0)):
    """Replace inf with NaN, then optionally impute NaN with median or zero, and clip extremes."""
    x = np.asarray(x, dtype=float)
    x[~np.isfinite(x)] = np.nan
    if method == "median":
        med = np.nanmedian(x)
        x = np.where(np.isnan(x), med, x)
    elif method == "zero":
        x = np.where(np.isnan(x), 0.0, x)
    # clip extreme tails if requested
    lo, hi = np.nanpercentile(x, [clip_quantiles[0], clip_quantiles[1]])
    x = np.clip(x, lo, hi)
    return x
