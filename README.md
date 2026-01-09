# Company Valuation

Institutional-grade company valuation models implemented in Python.

## Features

- **DCF (Discounted Cash Flow)**: Intrinsic valuation with mid-year convention, stub periods, and multiple terminal value methods
- **Comparable Company Analysis**: Trading multiples with LTM/NTM calculations
- **Precedent Transaction Analysis**: M&A transaction multiples with control premium analysis
- **LBO (Leveraged Buyout)**: PE-style returns analysis with debt scheduling
- **DDM (Dividend Discount Model)**: Valuation for financial institutions
- **SOTP (Sum-of-the-Parts)**: Conglomerate valuation
- **Sensitivity Analysis**: Two-variable tables and football field visualization

## Installation

### Using Poetry

```bash
poetry install
```

### Using Docker

```bash
docker-compose build
docker-compose run valuation  # Run tests
docker-compose run example    # Run example
docker-compose run shell      # Interactive Python shell
```

## Quick Start

```python
from company_valuation import (
    WACC, CostOfEquity,
    DCFModel, UFCFProjection,
    ComparableAnalysis, PeerCompany,
    LBOModel
)

# Calculate WACC
wacc = WACC(
    equity_value=10000,
    debt_value=3000,
    cost_of_equity=0.10,
    cost_of_debt=0.06,
    tax_rate=0.25
)
print(f"WACC: {wacc.calculate():.2%}")

# DCF Valuation
projections = [
    UFCFProjection(year=1, revenue=1000, ebit=200, tax_rate=0.25,
                   depreciation_amortization=50, capex=60, delta_nwc=10)
    # ... add more years
]

dcf = DCFModel(
    projections=projections,
    wacc=0.10,
    terminal_growth=0.025,
    net_debt=500
)
result = dcf.value_perpetuity_method()
print(f"Enterprise Value: ${result.enterprise_value:,.0f}")

# LBO Analysis
lbo = LBOModel.simple_lbo(
    entry_ebitda=100,
    entry_multiple=10.0,
    leverage_turns=6.0,
    interest_rate=0.08,
    exit_multiple=10.0
)
lbo_result = lbo.run_model()
print(f"IRR: {lbo_result.irr:.1%}, MOIC: {lbo_result.moic:.2f}x")
```

## Running Tests

```bash
poetry run pytest -v
```

## Modules

| Module | Description |
|--------|-------------|
| `wacc` | WACC and CAPM calculations, beta unlevering/relevering |
| `dcf` | Discounted Cash Flow model |
| `comps` | Comparable Company Analysis |
| `precedent` | Precedent Transaction Analysis |
| `lbo` | Leveraged Buyout model |
| `ddm` | Dividend Discount Model |
| `sotp` | Sum-of-the-Parts Analysis |
| `sensitivity` | Sensitivity analysis and football field |
| `utils` | Treasury Stock Method, EV/Equity bridge |
