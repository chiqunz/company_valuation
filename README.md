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

## Technical Background

### Discounted Cash Flow (DCF)

The DCF model calculates intrinsic value as the present value of future cash flows:

```
V = SUM(UFCF_t / (1 + WACC)^t) + TV / (1 + WACC)^n
```

**Key Components:**

- **UFCF (Unlevered Free Cash Flow)**: `EBIT × (1 - Tax) + D&A - CapEx - Delta NWC`
- **Terminal Value**: Perpetuity method `UFCF × (1+g) / (WACC - g)` or Exit Multiple method
- **Mid-Year Convention**: Adjusts discount periods by -0.5 to reflect continuous cash generation

### WACC and Cost of Equity

**WACC Formula:**
```
WACC = (E/V × Re) + (D/V × Rd × (1-T))
```

**Cost of Equity (CAPM):**
```
Re = Rf + Beta × (Rm - Rf)
```

**Beta Calculations:**
- Unlever: `Beta_U = Beta_L / (1 + (1-T) × D/E)`
- Relever: `Beta_L = Beta_U × (1 + (1-T) × D/E)`

### Comparable Company Analysis

Calculates valuation multiples from peer companies:

- **LTM Calculation**: `FY Metric + Current YTD - Prior YTD`
- **Key Multiples**: EV/EBITDA, EV/EBIT, P/E, EV/Revenue, P/BV

| Multiple | Best Use Case |
|----------|---------------|
| EV/EBITDA | Core standard (Tech, Industrial, Media) |
| EV/EBIT | Capital-intensive (Auto, Airlines) |
| P/E | Financials (Banks, Insurance) |
| EV/Revenue | High-growth / unprofitable companies |
| P/BV | Banks, Real Estate |

### Precedent Transaction Analysis

Analyzes historical M&A transactions with control premiums (typically 20-40% over trading price).

### Leveraged Buyout (LBO)

Models PE-style acquisitions with debt financing:

- **IRR Target**: Typically 20-25% over 5-year hold
- **MOIC Target**: 2.0x - 3.0x
- **Key Mechanics**: Debt scheduling, cash sweep, mandatory amortization

```
MOIC = Exit Equity / Initial Equity
IRR = MOIC^(1/Years) - 1
```

### Dividend Discount Model (DDM)

For valuing financial institutions where standard DCF fails:

```
V = SUM(DPS_t / (1 + Ke)^t) + Terminal Value
```

### Sum-of-the-Parts (SOTP)

For conglomerates with diverse business units:
1. Value each segment using appropriate methodology
2. Sum segment values
3. Subtract capitalized corporate overhead
4. Apply conglomerate discount (typically 10-20%)

### Sensitivity Analysis

The "Football Field" visualization presents valuation ranges from multiple methodologies:
- DCF range (WACC vs Terminal Growth sensitivity)
- Comps range (25th-75th percentile multiples)
- LBO floor (PE sponsor capability to pay)
- 52-week trading range

### Treasury Stock Method

Calculates fully diluted share count:
```
New Shares = Options × (1 - Strike/Price)
```

## Project Structure

```
company_valuation/
├── pyproject.toml           # Poetry configuration
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose for easy usage
├── company_valuation/       # Main package
│   ├── __init__.py
│   ├── wacc.py             # WACC and CAPM calculations
│   ├── dcf.py              # Discounted Cash Flow model
│   ├── comps.py            # Comparable Company Analysis
│   ├── precedent.py        # Precedent Transaction Analysis
│   ├── lbo.py              # Leveraged Buyout model
│   ├── ddm.py              # Dividend Discount Model
│   ├── sotp.py             # Sum-of-the-Parts Analysis
│   ├── sensitivity.py      # Sensitivity analysis utilities
│   └── utils.py            # Treasury Stock Method, helpers
├── tests/                   # Test suite
└── examples/                # Example usage scripts
```

## Design Philosophy

1. **Dataclass-based inputs**: Structured, type-safe input parameters
2. **Immutable calculations**: Models return results without side effects
3. **Clear separation**: Each valuation methodology in its own module
4. **Full type hints**: Complete type annotations for clarity
5. **No over-engineering**: Simple, direct implementations

## Dependencies

- Python 3.11+
- numpy: Numerical calculations
- pandas: Data manipulation (optional, for DataFrame-based workflows)
- pytest: Testing
