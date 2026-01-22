---
name: run-valuation
description: Use when executing DCF, Comps, LBO, and Historical P/E valuation models using the company_valuation Python library
---

# Run Valuation Models

Generate and execute Python code to run institutional valuation models.

## Environment Setup

**IMPORTANT**: Always use `poetry run` to execute Python code. Never use `pip install` or `python` directly.

The valuation library is located in `scripts/` relative to this skill:
```
skills/run-valuation/
├── SKILL.md
└── scripts/
    ├── pyproject.toml
    ├── poetry.lock
    ├── company_valuation/   # Python package
    ├── tests/
    └── examples/
```

### First-time Setup

```bash
# Navigate to scripts directory and install dependencies
cd company-valuation/skills/run-valuation/scripts
poetry install
```

### Running Python Code

```bash
# Run Python scripts
cd company-valuation/skills/run-valuation/scripts
poetry run python <script.py>

# Run tests
poetry run pytest -v

# Run example
poetry run python examples/example_valuation.py
```

## Prerequisites

Ensure the `company_valuation` library is available in the project:
```python
from company_valuation import (
    WACC, CostOfEquity,
    DCFModel, UFCFProjection,
    ComparableAnalysis, PeerCompany,
    LBOModel,
    SensitivityAnalysis
)
```

## Step 1: Calculate WACC

```python
# Cost of Equity via CAPM
cost_of_equity = CostOfEquity(
    risk_free_rate=0.045,      # 10-year Treasury yield
    beta=market_data["beta"],
    equity_risk_premium=0.05   # Historical ERP ~5%
)

# WACC
wacc = WACC(
    equity_value=market_data["market_cap"],
    debt_value=financials["total_debt"],
    cost_of_equity=cost_of_equity.calculate(),
    cost_of_debt=0.06,  # Estimate based on credit rating
    tax_rate=financials["tax_rate"]
)
wacc_rate = wacc.calculate()
```

## Step 2: DCF Valuation

```python
# Create 5-year projections
growth_rate = financials["projected_growth_rate"]
projections = []

base_revenue = financials["revenue"]
base_ebit_margin = financials["ebit"] / financials["revenue"]

for year in range(1, 6):
    revenue = base_revenue * ((1 + growth_rate) ** year)
    ebit = revenue * base_ebit_margin
    da = revenue * (financials["depreciation_amortization"] / financials["revenue"])
    capex = revenue * (financials["capex"] / financials["revenue"])

    projections.append(UFCFProjection(
        year=year,
        revenue=revenue,
        ebit=ebit,
        tax_rate=financials["tax_rate"],
        depreciation_amortization=da,
        capex=capex,
        delta_nwc=revenue * 0.01  # ~1% of revenue
    ))

# Run DCF
dcf = DCFModel(
    projections=projections,
    wacc=wacc_rate,
    terminal_growth=0.025,  # Long-term GDP growth
    exit_multiple=financials["ebitda"] / financials["ebitda"] * 10,  # Sector average
    net_debt=financials["net_debt"],
    shares_outstanding=market_data["shares_outstanding"],
    mid_year_convention=True
)

dcf_perp = dcf.value_perpetuity_method()
dcf_exit = dcf.value_exit_multiple_method()
```

## Step 3: Comparable Company Analysis

```python
# Create PeerCompany objects from gathered peer data
peer_objects = [
    PeerCompany(
        ticker=p["ticker"],
        name=p["name"],
        price=p["price"],
        shares_outstanding=p["shares_outstanding"],
        net_debt=p["net_debt"],
        ltm_revenue=p["ltm_revenue"],
        ltm_ebitda=p["ltm_ebitda"],
        ltm_ebit=p.get("ltm_ebit"),
        ltm_net_income=p.get("ltm_net_income")
    )
    for p in peers
]

comps = ComparableAnalysis(peer_objects)

# Get multiples and implied values
ev_ebitda_data = comps.ev_ebitda_multiples()
implied_ev = comps.implied_value(
    target_metric=financials["ebitda"],
    multiple_type="ev_ebitda",
    use_median=True
)

# Convert to per-share
comps_ev = implied_ev["implied_value"]
comps_equity = comps_ev - financials["net_debt"]
comps_per_share = comps_equity / market_data["shares_outstanding"]
```

## Step 4: LBO Analysis

```python
# Simplified LBO - what can a sponsor pay for target IRR?
lbo = LBOModel.simple_lbo(
    entry_ebitda=financials["ebitda"],
    entry_multiple=10.0,  # Starting assumption
    leverage_turns=5.5,   # ~5.5x debt/EBITDA
    interest_rate=0.085,  # Current leveraged loan rates
    exit_multiple=10.0,   # Same as entry (conservative)
    hold_years=5,
    ebitda_growth=financials["projected_growth_rate"],
    capex_pct=financials["capex"] / financials["ebitda"],
    tax_rate=financials["tax_rate"]
)

lbo_result = lbo.run_model()

# Calculate max entry multiple for 20% IRR
max_multiple = lbo.solve_for_entry_multiple(target_irr=0.20)
```

## Step 5: Historical P/E Valuation

Use historical P/E data to estimate fair value based on where the stock has traded historically.

```python
# Historical P/E valuation - no library needed, pure calculation

# P/E percentiles from gathered data
pe_p25 = historical_pe["pe_p25"]
pe_median = historical_pe["pe_median"]
pe_p75 = historical_pe["pe_p75"]
pe_current = historical_pe["pe_current"]

# EPS values
eps_ttm = historical_pe["eps_ttm"]
eps_forward = historical_pe["eps_forward"]

# Calculate implied prices using TTM EPS
hist_pe_ttm_low = eps_ttm * pe_p25      # 25th percentile P/E
hist_pe_ttm_mid = eps_ttm * pe_median   # Median P/E
hist_pe_ttm_high = eps_ttm * pe_p75     # 75th percentile P/E

# Calculate implied prices using Forward EPS
hist_pe_fwd_low = eps_forward * pe_p25
hist_pe_fwd_mid = eps_forward * pe_median
hist_pe_fwd_high = eps_forward * pe_p75

# Current valuation context
current_price = market_data["price"]
pe_percentile_rank = historical_pe["pe_percentile_rank"]

# Determine if over/under valued vs history
if pe_current < pe_p25:
    pe_assessment = "Below historical 25th percentile - potentially undervalued"
elif pe_current > pe_p75:
    pe_assessment = "Above historical 75th percentile - potentially overvalued"
else:
    pe_assessment = "Within historical normal range (25th-75th percentile)"
```

## Step 6: Sensitivity Analysis

```python
# DCF sensitivity: WACC vs Terminal Growth
wacc_range = [wacc_rate - 0.02, wacc_rate - 0.01, wacc_rate,
              wacc_rate + 0.01, wacc_rate + 0.02]
growth_range = [0.015, 0.020, 0.025, 0.030, 0.035]

sensitivity = SensitivityAnalysis.dcf_sensitivity(
    base_dcf=dcf,
    wacc_range=wacc_range,
    growth_range=growth_range
)

# Football field
football = SensitivityAnalysis.create_football_field(
    dcf_range=(dcf_low, dcf_mid, dcf_high),  # Calculate from sensitivity
    comps_range=(comps_low, comps_mid, comps_high),
    lbo_range=(lbo_low, lbo_mid, lbo_high),
    fifty_two_week=(market_data["fifty_two_week_low"],
                    market_data["fifty_two_week_high"]),
    current_price=market_data["price"]
)
```

## Output Structure

Store all results for the report generator:

```python
valuation_results = {
    "wacc": {
        "rate": wacc_rate,
        "cost_of_equity": cost_of_equity.calculate(),
        "cost_of_debt": 0.06,
        "equity_weight": wacc.equity_weight,
        "debt_weight": wacc.debt_weight
    },
    "dcf_perpetuity": {
        "enterprise_value": dcf_perp.enterprise_value,
        "equity_value": dcf_perp.equity_value,
        "per_share": dcf_perp.equity_value_per_share,
        "pv_cash_flows": dcf_perp.pv_explicit_cashflows,
        "pv_terminal": dcf_perp.pv_terminal_value
    },
    "dcf_exit_multiple": {
        "enterprise_value": dcf_exit.enterprise_value,
        "equity_value": dcf_exit.equity_value,
        "per_share": dcf_exit.equity_value_per_share,
        "implied_growth": dcf_exit.implied_perpetual_growth
    },
    "comps": {
        "ev_ebitda_median": ev_ebitda_data["statistics"]["median"],
        "implied_ev": comps_ev,
        "implied_per_share": comps_per_share,
        "peer_multiples": ev_ebitda_data["multiples"]
    },
    "lbo": {
        "base_irr": lbo_result.irr,
        "base_moic": lbo_result.moic,
        "max_multiple_20_irr": max_multiple
    },
    "historical_pe": {
        "pe_statistics": {
            "min": historical_pe["pe_min"],
            "max": historical_pe["pe_max"],
            "mean": historical_pe["pe_mean"],
            "median": historical_pe["pe_median"],
            "p25": historical_pe["pe_p25"],
            "p75": historical_pe["pe_p75"],
            "p10": historical_pe["pe_p10"],
            "p90": historical_pe["pe_p90"]
        },
        "current_pe": historical_pe["pe_current"],
        "percentile_rank": historical_pe["pe_percentile_rank"],
        "eps_ttm": historical_pe["eps_ttm"],
        "eps_forward": historical_pe["eps_forward"],
        "implied_ttm": {
            "low": hist_pe_ttm_low,
            "mid": hist_pe_ttm_mid,
            "high": hist_pe_ttm_high
        },
        "implied_forward": {
            "low": hist_pe_fwd_low,
            "mid": hist_pe_fwd_mid,
            "high": hist_pe_fwd_high
        },
        "assessment": pe_assessment
    },
    "sensitivity": sensitivity.to_dict(),
    "football_field": football.to_dict()
}
```
