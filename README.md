# Shared Value Decision Frontier (SVDF)

SVDF is a reproducible strategy-screening tool for sustainability portfolios. 

## Fastest use

The repository includes the processed 32-intervention paper dataset.

```bash
pip install -r requirements.txt
python app.py
```

Open the shown local address and press **Reproduce Paper Analysis**.

## GitHub Actions button

Upload the **contents of this `software` folder** to the root of a GitHub repository. Open **Actions -> Reproduce SVDF Analysis -> Run workflow**. GitHub runs the tests, reproduces the 2,000-specification analysis, and provides `svdf-results` as a downloadable workflow artifact.

## Browser-hosted GitHub app

The repository also contains a pure HTML/JavaScript version (`index.html`). The included **Deploy SVDF Web App to GitHub Pages** workflow publishes it from an ordinary GitHub repository. After the Pages deployment is enabled for GitHub Actions, each push to `main` or `master` updates the public app. The browser app reproduces the paper frontier, accepts a user CSV, and can read a public CORS-enabled CSV/JSON API.

## API input

The local Python app accepts CSV or JSON APIs. The JSON response may be a list of project records or `{"data": [...]}`. For a private bearer-token API, set:

```bash
export SVDF_API_KEY="your-token"
python app.py
```

The static GitHub Pages app should only be used with public CORS-enabled APIs. Do not place private API keys in browser code or the repository.

## Model

For project `j`, the paper defines

`SVG_j = (E_j V_j S_j)^(1/3)`

where `E`, `V`, and `S` are normalized economic, environmental, and stakeholder-reach components. The geometric mean is deliberately non-compensatory: a zero component produces zero shared-value gain.

Implementation Complexity is

`IC_j = 0.40 Type_j + 0.35 Scale_j + 0.25 Volatility_j`.

Project `a` dominates `b` when `IC_a <= IC_b` and `SVG_a >= SVG_b`, with at least one strict improvement. Projects not dominated by any alternative form the Shared Value Decision Frontier.

## Custom portfolio columns

Required columns are:

`project_id, event_type, adjusted_change_pct, annualized_kwh_saved, capacity, gross_floor_area, pre_cv`

`LED_Installation` and `HVAC_Tuning` use the paper's intervention-burden values. Other event types receive a neutral default. If actual CAPEX, implementation time, community reach, or other verified measures are available, adapt `score_projects()` so the institution-specific variables replace the published proxies.

## Data provenance and boundary

`data/paper_interventions.csv` is a processed event-level derivative of the UNICON university utilities dataset (Moraliyage et al., 2022, DOI: 10.1109/HSI55341.2022.9869498). The raw high-frequency files are not needed for reproduction.

The event estimates are adjusted associations, not randomized causal effects. SVG is a transparent screening proxy for shared value, not a universal CSV measure. IC is an implementation proxy, not CAPEX. EA is used only as a qualitative post-frontier organisational diagnostic.
