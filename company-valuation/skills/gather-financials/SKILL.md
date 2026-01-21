---
name: gather-financials
description: Use when gathering revenue, EBITDA, debt, and other financial metrics for company valuation
---

# Gather Financial Data

Search the web to collect financial statement data for DCF and comparable analysis.

## Required Data Points

### Income Statement (LTM - Last Twelve Months)
| Metric | Description |
|--------|-------------|
| Revenue | Total sales/revenue |
| EBITDA | Earnings before interest, taxes, depreciation, amortization |
| EBIT | Operating income |
| Net Income | Bottom line earnings |
| D&A | Depreciation and amortization |

### Balance Sheet
| Metric | Description |
|--------|-------------|
| Total Debt | Short-term + long-term debt |
| Cash | Cash and cash equivalents |
| Net Debt | Total debt - cash |

### Cash Flow Statement
| Metric | Description |
|--------|-------------|
| CapEx | Capital expenditures |
| Working Capital Change | Change in NWC |

### Derived Metrics
| Metric | Calculation |
|--------|-------------|
| Revenue Growth | YoY growth rate |
| EBITDA Margin | EBITDA / Revenue |
| Tax Rate | Effective or marginal |

## Search Strategy

1. **Financial statements**: `"{TICKER} income statement balance sheet 10-K"`
2. **Key metrics**: `"{TICKER} revenue EBITDA net income LTM"`
3. **Debt info**: `"{TICKER} total debt cash position"`
4. **Growth rates**: `"{TICKER} revenue growth rate historical"`

## Output Format

```python
financials = {
    # Income Statement (LTM, in millions)
    "revenue": 383285,
    "ebitda": 125820,
    "ebit": 114300,
    "net_income": 96995,
    "depreciation_amortization": 11520,

    # Balance Sheet (in millions)
    "total_debt": 111088,
    "cash": 61555,
    "net_debt": 49533,

    # Cash Flow (in millions)
    "capex": 10959,
    "delta_nwc": 2500,  # Change in working capital

    # Rates and Margins
    "revenue_growth_3yr": 0.08,  # 8% CAGR
    "ebitda_margin": 0.328,  # 32.8%
    "tax_rate": 0.25,

    # For projections
    "projected_growth_rate": 0.05  # Analyst consensus or estimate
}
```

## Data Sources Priority

1. Company 10-K/10-Q filings (most accurate)
2. Financial data providers (Yahoo Finance, Morningstar)
3. Financial news sites (cross-verify)

## Validation Checks

- EBITDA = EBIT + D&A (approximately)
- Net Debt = Total Debt - Cash
- Margins should be consistent with industry
- Growth rates should be reasonable (verify with historical data)
