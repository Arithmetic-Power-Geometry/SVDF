# Shared Value Decision Frontier (SVDF)

**Strategic screening for sustainability portfolios when many projects look good but resources are limited.**

**Author:** Mohammad Amir Khusru Akhtar  
Usha Martin University, Ranchi–834001, Jharkhand, India  
Email: akakhtar.2024@gmail.com  
Try the SVDF Decision Support Software: https://arithmetic-power-geometry.github.io/SVDF-Decision-Studio/

## What problem does SVDF solve?

A university, company, city, hospital or public agency may have many worthwhile sustainability proposals. A simple ROI ranking can favour cheap projects. A sustainability score can favour high-impact projects even when implementation is difficult. A weighted total can also hide a serious weakness because a high score on one dimension compensates for a low score on another.

SVDF asks a narrower and more transparent question: **which alternatives are not clearly beaten by another alternative that is both easier to implement and stronger in shared value?**

The answer is the **Shared Value Decision Frontier**. It is a screening frontier, not an automatic funding list.

## Conceptual contribution

SVDF combines three ideas without treating them as interchangeable.

1. **Creating Shared Value (CSV)** supplies the management lens. Value should connect institutional/economic benefit with societal benefit.
2. **Discovery Plane Theory (DPT)** supplies the transferable decision geometry: competing coordinates, dominance, a non-dominated frontier, and sensitivity to declared conventions. SVDF adapts this logic from question screening to project screening.
3. **Experience Architecture (EA)** is deliberately light. After frontier screening, its six questions help managers ask whether evidence is actually organised so that it can change a reachable decision. EA is not used to manufacture an unsupported numerical consciousness or organisation score.

The novelty is therefore not another sustainability index. **SVDF reframes shared-value project selection from a compensatory ranking problem into a non-dominated frontier problem, then separates strategic attractiveness from organisational answerability.**

## What happens when you press Run?

SVDF follows six visible steps.

**Step 1 — Validate the portfolio.** The software recognizes either the paper-reproduction schema or a general portfolio schema. Missing fields produce an error instead of silent assumptions.

**Step 2 — Normalize the evidence.** Economic value, environmental value and stakeholder reach are converted to percentile scores inside the submitted portfolio. Complexity components are normalized in the same transparent way. The scores are therefore relative to the alternatives being compared.

**Step 3 — Calculate Shared Value Gain.** For project `j`,

`SVG_j = (E_j × V_j × S_j)^(1/3)`

where `E`, `V` and `S` are normalized economic, environmental and stakeholder-reach components. A geometric mean is used so that a zero dimension cannot be hidden by strong performance elsewhere.

**Step 4 — Calculate Implementation Complexity.**

`IC_j = 0.40 B_j + 0.35 L_j + 0.25 R_j`

where `B` is implementation burden, `L` is scale and `R` is volatility/uncertainty proxy. Lower IC is preferred. The weights are declared conventions, not natural constants.

**Step 5 — Apply dominance.** Alternative `a` dominates `b` when `IC_a ≤ IC_b` and `SVG_a ≥ SVG_b`, with at least one strict improvement. Alternatives not dominated by any observed alternative form the SVDF.

**Step 6 — Interpret rather than automate judgement.** The frontier identifies strategically efficient trade-offs. Managers still examine budget, feasibility, ethics, local policy, engineering constraints and stakeholder priorities.

For the Python paper reproduction, a 2,000-draw specification analysis also varies value and complexity weights. `frontier_frequency` reports how often each alternative remains on the frontier. It is a sensitivity measure, **not a confidence interval or p-value**.

## Three ways to use the software

### 1. Public browser app — no installation

Open the GitHub Pages site and choose **Reproduce the paper**, **Analyse your CSV**, or **Load API**. The browser performs the scoring locally. Uploaded CSV content is not sent to an SVDF server. A public API must allow browser CORS access.

### 2. Local Python application

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The Gradio interface supports the bundled paper data, user CSVs, and CSV/JSON APIs. For a private bearer-token API:

```bash
export SVDF_API_KEY="your-token"
python app.py
```

Never commit private API keys to GitHub.

### 3. GitHub Actions — reproducible run button

Open **Actions → Reproduce SVDF Analysis → Run workflow**. The workflow installs dependencies, runs tests, reproduces the analysis and uploads the result files as a GitHub artifact.

## Input data

### General portfolio schema

This is the recommended format for new users:

`project_id, project_name, economic_value, environmental_value, stakeholder_reach, implementation_burden, scale, volatility`

The values may be physical measures, verified estimates or declared scores. They need not use the same unit because SVDF converts them to within-portfolio percentile scores. However, each column must have a consistent meaning across all alternatives. Higher is better for the three value columns. Higher means more difficult for the three complexity columns.

Download `data/custom_portfolio_template.csv` or one of the four examples.

### Included teaching scenarios

- `data/examples/campus_energy_demo.csv`
- `data/examples/water_resilience_demo.csv`
- `data/examples/waste_circularity_demo.csv`
- `data/examples/mobility_demo.csv`

These four files are **synthetic demonstrations**, not empirical results. They are intentionally different so users can see that the frontier depends on the decision set.

### Paper reproduction schema

The paper reproduction uses:

`project_id, event_type, adjusted_change_pct, annualized_kwh_saved, capacity, gross_floor_area, pre_cv`

For this schema, the software transparently maps adjusted reduction to the economic proxy, annualized kWh reduction to the environmental proxy, capacity (or square-root floor area fallback) to stakeholder reach, intervention type to burden, floor area to scale, and baseline coefficient of variation to volatility. These are paper-specific proxies. They are not universal definitions of shared value or implementation cost.

## Outputs

The browser shows the frontier plot and frontier table and downloads a scored CSV. The Python app additionally generates a result bundle containing the full scored table, frontier figure, robustness figure and EA organisational diagnostic questions. Key fields include:

- `economic_score`, `environmental_score`, `stakeholder_score`
- `shared_value_gain` (SVG)
- `implementation_complexity` (IC)
- `frontier`
- `utility_0_50` and `strategic_rank` as transparent secondary summaries
- `frontier_frequency` in robustness runs

## How to interpret the graph

Move **up** for greater shared value. Move **left** for lower implementation complexity. Green alternatives are on the frontier. Grey alternatives are dominated. A frontier point is not automatically the best project. Different frontier points represent different value-complexity trade-offs.

## Limits

SVDF is decision support, not a causal estimator or investment guarantee. Results are conditional on the portfolio, input quality, normalization, proxies and declared weights. The paper event estimates are adjusted associations rather than randomized causal effects. IC is not CAPEX unless the user explicitly builds CAPEX into the general input. SVG is a screening construct, not a universal measurement scale for CSV.

## Data provenance

`data/paper_interventions.csv` is a processed event-level derivative used to reproduce the study from the UNICON university utilities dataset described by Moraliyage et al. (2022), DOI `10.1109/HSI55341.2022.9869498`. Raw UNICON files are not redistributed in this repository. See `DATA_NOTICE.md`.

## Citation

If you use the software in research, cite the associated SVDF paper when publicly available and cite the underlying UNICON dataset when using the bundled reproduction table.

## License and copyright

Software copyright © 2026 **Mohammad Amir Khusru Akhtar**.

Licensed under the **Apache License, Version 2.0**. See `LICENSE` and `NOTICE`. The Apache License is permissive and includes explicit patent terms. Third-party data remain subject to their own provenance and applicable terms.
