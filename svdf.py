"""Shared Value Decision Frontier (SVDF) analysis engine.

CSV provides the strategy lens. The non-dominated frontier logic is adapted from
Discovery Plane Theory (DPT). Experience Architecture (EA) is used only after
frontier screening as a qualitative organisational diagnostic.
"""
from __future__ import annotations
from pathlib import Path
import io, os
import numpy as np
import pandas as pd

REQUIRED = {
    "project_id", "event_type", "adjusted_change_pct", "annualized_kwh_saved",
    "capacity", "gross_floor_area", "pre_cv"
}

def _positive_rank(values):
    s = pd.Series(values, dtype=float).fillna(0.0)
    out = np.zeros(len(s), dtype=float)
    mask = s > 0
    if mask.any():
        out[mask] = s[mask].rank(method="average", pct=True).to_numpy(dtype=float)
    return out

def _rank(values):
    s = pd.Series(values, dtype=float)
    med = float(s.median()) if s.notna().any() else 0.0
    return s.fillna(med).rank(method="average", pct=True).to_numpy(dtype=float)

def _weighted_geomean(frame, weights):
    x = frame.to_numpy(dtype=float)
    w = np.asarray(weights, dtype=float); w = w / w.sum()
    out = np.zeros(len(frame), dtype=float)
    valid = (x > 0).all(axis=1)
    out[valid] = np.exp((np.log(x[valid]) * w).sum(axis=1))
    return out

def _frontier(svg, ic):
    svg=np.asarray(svg,float); ic=np.asarray(ic,float)
    out=np.ones(len(svg),dtype=bool)
    for i in range(len(svg)):
        dominated=(ic<=ic[i]) & (svg>=svg[i]) & ((ic<ic[i]) | (svg>svg[i]))
        out[i]=not bool(dominated.any())
    return out

def score_projects(df, value_weights=(1,1,1), complexity_weights=(0.40,0.35,0.25)):
    """Return SVG, IC and the non-dominated frontier for a project portfolio."""
    missing=REQUIRED-set(df.columns)
    if missing:
        raise ValueError("Missing required columns: "+", ".join(sorted(missing)))
    r=df.copy()
    rel=np.clip(-pd.to_numeric(r.adjusted_change_pct,errors='coerce').fillna(0)/100.0,0,None)
    annual=np.clip(pd.to_numeric(r.annualized_kwh_saved,errors='coerce').fillna(0),0,None)
    cap=pd.to_numeric(r.capacity,errors='coerce').fillna(0)
    area=pd.to_numeric(r.gross_floor_area,errors='coerce').fillna(0).clip(lower=0)
    reach=cap.where(cap>0,np.sqrt(area))
    r['economic_score']=_positive_rank(rel)
    r['environmental_score']=_positive_rank(annual)
    r['stakeholder_score']=_positive_rank(reach)
    r['shared_value_gain']=_weighted_geomean(
        r[['economic_score','environmental_score','stakeholder_score']],value_weights)
    r['type_complexity']=r.event_type.map({'LED_Installation':0.30,'HVAC_Tuning':0.55}).fillna(0.50)
    r['scale_score']=_rank(np.log1p(area))
    r['variability_score']=_rank(pd.to_numeric(r.pre_cv,errors='coerce'))
    cw=np.asarray(complexity_weights,float); cw=cw/cw.sum()
    r['implementation_complexity']=r[['type_complexity','scale_score','variability_score']].to_numpy()@cw
    r['frontier']=_frontier(r.shared_value_gain,r.implementation_complexity)
    r['utility_0_50']=r.shared_value_gain-0.50*r.implementation_complexity
    r['strategic_rank']=r.utility_0_50.rank(method='min',ascending=False).astype(int)
    return r

def specification_robustness(df, n_draws=2000, seed=2026):
    """Frontier frequency under alternative plausible component weights.

    The frequency is a specification-sensitivity measure, not a confidence interval.
    """
    base=score_projects(df)
    X=base[['economic_score','environmental_score','stakeholder_score']]
    C=base[['type_complexity','scale_score','variability_score']].to_numpy(dtype=float)
    rng=np.random.default_rng(seed); counts=np.zeros(len(base),dtype=float)
    for _ in range(int(n_draws)):
        wv=rng.dirichlet([6,6,6])
        wc=rng.dirichlet([8,7,5])
        counts += _frontier(_weighted_geomean(X,wv),C@wc)
    base['frontier_frequency']=counts/float(n_draws)
    return base

def load_paper_data(path=None):
    if path is None:
        path=Path(__file__).resolve().parent/'data'/'paper_interventions.csv'
    return pd.read_csv(path)

def analyze_paper(path=None,n_draws=2000):
    return specification_robustness(load_paper_data(path),n_draws=n_draws)

def load_remote_api(url, api_key=None, timeout=30):
    """Load a project portfolio from a CSV/JSON HTTP API.

    The endpoint may return CSV, a JSON list, or {"data": [...]}.
    A bearer key can be supplied directly or through SVDF_API_KEY.
    """
    import requests
    headers={}
    key=api_key or os.getenv('SVDF_API_KEY')
    if key: headers['Authorization']=f'Bearer {key}'
    res=requests.get(url,headers=headers,timeout=timeout)
    res.raise_for_status()
    ctype=res.headers.get('content-type','').lower()
    if 'csv' in ctype or url.lower().endswith('.csv'):
        return pd.read_csv(io.StringIO(res.text))
    obj=res.json()
    if isinstance(obj,dict) and 'data' in obj: obj=obj['data']
    if not isinstance(obj,list):
        raise ValueError('API JSON must be a list of records or an object containing a data list.')
    return pd.DataFrame(obj)

def ea_questions():
    return pd.DataFrame([
        ('D','Difference','Can the institution distinguish a material sustainability problem from routine variation?'),
        ('A','Availability','Does the evidence reach people who can authorise or redesign the intervention?'),
        ('O','Orientation','Is the evidence linked to a clear strategic, financial, environmental or stakeholder goal?'),
        ('I','Integration','Are technical, financial, operational and stakeholder consequences considered together?'),
        ('T','Temporality','Is the effect tracked across time instead of being treated as a one-off observation?'),
        ('R','Answerability','Can the evidence change the reachable decision set: fund, redesign, time, scale or reject?'),
    ],columns=['Code','Condition','Organisational diagnostic question'])
