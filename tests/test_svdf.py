from svdf import analyze_paper, score_projects, load_paper_data

def test_paper_reproduction():
    r=analyze_paper(n_draws=200)
    assert len(r)==32
    assert int(r.frontier.sum())==3
    assert set(r.loc[r.frontier,'project_id'])=={'U04','U05','U06'}
    assert r['shared_value_gain'].between(0,1).all()
    assert r['implementation_complexity'].between(0,1).all()

def test_scoring_is_deterministic():
    d=load_paper_data()
    a=score_projects(d)
    b=score_projects(d)
    assert a[['shared_value_gain','implementation_complexity','frontier']].equals(b[['shared_value_gain','implementation_complexity','frontier']])
