"""G1A fixed-count MCAR/MAR mask generator. No model fitting."""
import hashlib
import numpy as np


def stable_seed(seed, feature):
    b = f'{int(seed)}|{feature}'.encode()
    return int.from_bytes(hashlib.blake2b(b, digest_size=8).digest(), 'big')


def probabilities(anchors, rate, slope=1.0, pmin=0.01, pmax=0.99):
    """Clipped logistic inclusion weights; intercept calibrated to mean(rate)."""
    z = np.clip(np.asarray(anchors, dtype=float), -10, 10)
    if z.ndim != 1 or not np.isfinite(z).all() or not (0 < pmin < rate < pmax < 1):
        raise ValueError('invalid anchors or rate')
    lo, hi = -100.0, 100.0
    for _ in range(120):
        mid = (lo + hi)/2
        p = np.clip(1/(1+np.exp(-np.clip(mid+slope*z, -700, 700))),pmin,pmax)
        if p.mean() < rate: lo = mid
        else: hi = mid
    return np.clip(1/(1+np.exp(-np.clip((lo+hi)/2+slope*z,-700,700))),pmin,pmax)


def generate_mask(frame, features, mechanism, rate, seed, anchor_data=None, eligible=None):
    """Higher weighted MAR selection is by Gumbel-top-k; per-feature exact counts."""
    if mechanism not in ('MCAR','MAR') or not 0 < rate < 1:
        raise ValueError('invalid mechanism or rate')
    features = list(features)
    if not features or len(set(features)) != len(features) or not set(features).issubset(frame.columns):
        raise ValueError('invalid features')
    if mechanism == 'MAR':
        if anchor_data is None or set(anchor_data.columns) & set(features) or len(anchor_data) != len(frame):
            raise ValueError('MAR requires exclusively unmasked anchor columns')
        if anchor_data.shape[1] != 1:
            raise ValueError('G1A requires one pre-standardized anchor')
        z = anchor_data.iloc[:,0].to_numpy(dtype=float)
    n = len(frame)
    allow = np.ones((n,len(features)),dtype=bool) if eligible is None else np.asarray(eligible,dtype=bool)
    if allow.shape != (n,len(features)): raise ValueError('eligible shape mismatch')
    out = np.zeros_like(allow)
    for j,feature in enumerate(features):
        ids = np.flatnonzero(allow[:,j]); k = int(np.floor(rate*len(ids)+0.5))
        if not k: continue
        rng = np.random.default_rng(stable_seed(seed,feature))
        u = np.clip(rng.random(len(ids)),np.finfo(float).tiny,1-np.finfo(float).eps)
        g = -np.log(-np.log(u))
        if mechanism == 'MCAR': scores = g
        else:
            p = probabilities(z[ids],rate)
            scores = np.log(p) + g
        out[ids[np.argpartition(scores,-k)[-k:]],j] = True
    return out
