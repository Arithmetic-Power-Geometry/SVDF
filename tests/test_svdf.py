# Copyright 2026 Mohammad Amir Khusru Akhtar
# SPDX-License-Identifier: Apache-2.0
import pandas as pd
from svdf import analyze_paper, score_projects, load_paper_data, detect_schema

def test_paper_reproduction():
    r=analyze_paper(n_draws=50)
    assert len(r)==32
    assert int(r.frontier.sum())==3
    assert set(r.loc[r.frontier,'project_id'])=={'U04','U05','U06'}
    assert r.shared_value_gain.between(0,1).all()
    assert r.implementation_complexity.between(0,1).all()

def test_general_schema():
    df=pd.DataFrame([
      {'project_id':'A','project_name':'A','economic_value':90,'environmental_value':90,'stakeholder_reach':90,'implementation_burden':10,'scale':10,'volatility':10},
      {'project_id':'B','project_name':'B','economic_value':20,'environmental_value':20,'stakeholder_reach':20,'implementation_burden':90,'scale':90,'volatility':90}])
    assert detect_schema(df)=='general'
    r=score_projects(df)
    assert bool(r.loc[r.project_id=='A','frontier'].iloc[0])
    assert not bool(r.loc[r.project_id=='B','frontier'].iloc[0])
