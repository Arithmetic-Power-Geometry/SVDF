# Copyright 2026 Mohammad Amir Khusru Akhtar
# SPDX-License-Identifier: Apache-2.0
"""Shared Value Decision Frontier (SVDF) analysis engine."""
from __future__ import annotations
from pathlib import Path
import io, os
import numpy as np
import pandas as pd

PAPER_REQUIRED={"project_id","event_type","adjusted_change_pct","annualized_kwh_saved","capacity","gross_floor_area","pre_cv"}
GENERAL_REQUIRED={"project_id","economic_value","environmental_value","stakeholder_reach","implementation_burden","scale","volatility"}

def _positive_rank(values):
    s=pd.Series(values,dtype=float).fillna(0); out=np.zeros(len(s)); mask=s>0
    if mask.any(): out[mask]=s[mask].rank(method="average",pct=True).to_numpy(float)
    return out
def _rank(values):
    s=pd.Series(values,dtype=float); med=float(s.median()) if s.notna().any() else 0
    return s.fillna(med).rank(method="average",pct=True).to_numpy(float)
def _weighted_geomean(frame,weights):
    x=frame.to_numpy(float); w=np.asarray(weights,float); w=w/w.sum(); out=np.zeros(len(frame)); valid=(x>0).all(axis=1)
    out[valid]=np.exp((np.log(x[valid])*w).sum(axis=1)); return out
def _frontier(svg,ic):
    svg=np.asarray(svg,float); ic=np.asarray(ic,float); out=np.ones(len(svg),dtype=bool)
    for i in range(len(svg)):
        d=(ic<=ic[i])&(svg>=svg[i])&((ic<ic[i])|(svg>svg[i])); out[i]=not bool(d.any())
    return out
def detect_schema(df):
    c=set(df.columns)
    if PAPER_REQUIRED<=c:return 'paper'
    if GENERAL_REQUIRED<=c:return 'general'
    raise ValueError('CSV does not match the paper or general portfolio schema. See README.md.')
def score_projects(df,value_weights=(1,1,1),complexity_weights=(.40,.35,.25)):
    r=df.copy(); schema=detect_schema(r)
    if schema=='paper':
        rel=np.clip(-pd.to_numeric(r.adjusted_change_pct,errors='coerce').fillna(0)/100,0,None)
        annual=np.clip(pd.to_numeric(r.annualized_kwh_saved,errors='coerce').fillna(0),0,None)
        cap=pd.to_numeric(r.capacity,errors='coerce').fillna(0); area=pd.to_numeric(r.gross_floor_area,errors='coerce').fillna(0).clip(lower=0)
        reach=cap.where(cap>0,np.sqrt(area))
        r['economic_score']=_positive_rank(rel); r['environmental_score']=_positive_rank(annual); r['stakeholder_score']=_positive_rank(reach)
        r['type_complexity']=r.event_type.map({'LED_Installation':.30,'HVAC_Tuning':.55}).fillna(.50)
        r['scale_score']=_rank(np.log1p(area)); r['variability_score']=_rank(pd.to_numeric(r.pre_cv,errors='coerce'))
    else:
        r['economic_score']=_positive_rank(pd.to_numeric(r.economic_value,errors='coerce'))
        r['environmental_score']=_positive_rank(pd.to_numeric(r.environmental_value,errors='coerce'))
        r['stakeholder_score']=_positive_rank(pd.to_numeric(r.stakeholder_reach,errors='coerce'))
        r['type_complexity']=_rank(pd.to_numeric(r.implementation_burden,errors='coerce'))
        r['scale_score']=_rank(pd.to_numeric(r.scale,errors='coerce')); r['variability_score']=_rank(pd.to_numeric(r.volatility,errors='coerce'))
    r['shared_value_gain']=_weighted_geomean(r[['economic_score','environmental_score','stakeholder_score']],value_weights)
    cw=np.asarray(complexity_weights,float); cw=cw/cw.sum(); r['implementation_complexity']=r[['type_complexity','scale_score','variability_score']].to_numpy()@cw
    r['frontier']=_frontier(r.shared_value_gain,r.implementation_complexity)
    r['utility_0_50']=r.shared_value_gain-.50*r.implementation_complexity
    r['strategic_rank']=r.utility_0_50.rank(method='min',ascending=False).astype(int); r['schema_used']=schema
    return r
def specification_robustness(df,n_draws=2000,seed=2026):
    base=score_projects(df); X=base[['economic_score','environmental_score','stakeholder_score']]; C=base[['type_complexity','scale_score','variability_score']].to_numpy(float)
    rng=np.random.default_rng(seed); counts=np.zeros(len(base))
    for _ in range(int(n_draws)):
        counts+=_frontier(_weighted_geomean(X,rng.dirichlet([6,6,6])),C@rng.dirichlet([8,7,5]))
    base['frontier_frequency']=counts/float(n_draws); return base
def load_paper_data(path=None): return pd.read_csv(path or Path(__file__).resolve().parent/'data'/'paper_interventions.csv')
def analyze_paper(path=None,n_draws=2000): return specification_robustness(load_paper_data(path),n_draws=n_draws)
def load_remote_api(url,api_key=None,timeout=30):
    import requests
    key=api_key or os.getenv('SVDF_API_KEY'); headers={'Authorization':f'Bearer {key}'} if key else {}
    res=requests.get(url,headers=headers,timeout=timeout); res.raise_for_status(); ctype=res.headers.get('content-type','').lower()
    if 'csv' in ctype or url.lower().endswith('.csv'): return pd.read_csv(io.StringIO(res.text))
    obj=res.json(); obj=obj.get('data',obj) if isinstance(obj,dict) else obj
    if not isinstance(obj,list): raise ValueError('API JSON must be a list of records or {"data": [...]}')
    return pd.DataFrame(obj)
def ea_questions():
    return pd.DataFrame([('D','Difference','Can the institution distinguish a material sustainability problem from routine variation?'),('A','Availability','Does the evidence reach people who can authorise or redesign the intervention?'),('O','Orientation','Is the evidence linked to a clear strategic, financial, environmental or stakeholder goal?'),('I','Integration','Are technical, financial, operational and stakeholder consequences considered together?'),('T','Temporality','Is the effect tracked across time instead of being treated as a one-off observation?'),('R','Answerability','Can the evidence change the reachable decision set: fund, redesign, time, scale or reject?')],columns=['Code','Condition','Organisational diagnostic question'])
