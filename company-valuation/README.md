# Company Valuation Plugin for Claude Code

A Claude Code plugin that performs institutional-grade company valuation analysis using DCF, Comparable Company, LBO, and Historical P/E models.

## Features

- **Web-based data gathering**: Searches for current market data, financials, and analyst estimates
- **DCF Valuation**: Perpetuity growth and exit multiple methods with sensitivity analysis
- **Comparable Company Analysis**: Peer group identification and trading multiples
- **LBO Analysis**: Sponsor ability-to-pay analysis
- **Historical P/E Valuation**: Uses 2-year P/E percentiles with TTM and forward EPS
- **Comprehensive Reports**: Generates detailed markdown valuation reports

## Installation

Install the plugin in Claude Code:

```bash
claude --plugin-dir ./company-valuation
```

Or add to your Claude Code settings:

```json
{
  "plugins": ["./company-valuation"]
}
```

### Python Library Setup

```bash
cd company-valuation/skills/run-valuation/scripts
poetry install
```

## Usage

Run a valuation analysis:

```
/company-valuation:value-company AAPL
```

## Plugin Structure

```
company-valuation/
├── .claude-plugin/
│   └── plugin.json           # Plugin manifest
├── commands/
│   └── value-company.md      # Main orchestrator command
├── skills/
│   ├── gather-market-data/   # Stock price, market cap, beta
│   ├── gather-financials/    # Financial statement data
│   ├── gather-peers/         # Comparable company data
│   ├── gather-analyst-estimates/  # Price targets, ratings
│   ├── gather-historical-pe/ # Historical P/E data
│   ├── run-valuation/        # Execute Python models
│   │   ├── SKILL.md
│   │   └── scripts/          # Python valuation library
│   └── generate-report/      # Create markdown report
└── README.md
```

## Skills Overview

| Skill | Purpose |
|-------|---------|
| `gather-market-data` | Collect stock price, shares outstanding, beta, 52-week range |
| `gather-financials` | Collect revenue, EBITDA, debt, CapEx, growth rates |
| `gather-peers` | Identify 4-6 comparable companies and gather their data |
| `gather-analyst-estimates` | Find analyst price targets and consensus ratings |
| `gather-historical-pe` | Collect 2-year historical P/E data and percentiles |
| `run-valuation` | Execute DCF, Comps, LBO, Historical P/E models |
| `generate-report` | Create comprehensive markdown valuation report |

---

## Required Data Parameters

This section documents all required parameters for the valuation models. **All gather skills should reference this section** to ensure they collect the correct data.

### Market Data (gather-market-data)

| Parameter | Type | Unit | Description | Used By |
|-----------|------|------|-------------|---------|
| `ticker` | string | - | Stock ticker symbol (e.g., "AAPL") | All models |
| `company_name` | string | - | Full company name | Report |
| `price` | float | $ | Current stock price | Comps, P/E |
| `shares_outstanding` | float | millions | Diluted shares outstanding | DCF, Comps |
| `market_cap` | float | millions $ | Market capitalization (price × shares) | WACC, Comps |
| `beta` | float | - | 5-year monthly beta vs S&P 500 (typically 0.5-2.5) | WACC/CAPM |
| `fifty_two_week_low` | float | $ | 52-week low price | Report |
| `fifty_two_week_high` | float | $ | 52-week high price | Report |

### Financial Data (gather-financials)

#### Income Statement (LTM values in millions $)

| Parameter | Type | Description | Used By |
|-----------|------|-------------|---------|
| `revenue` | float | Total revenue / sales | DCF projections, Comps |
| `ebitda` | float | EBITDA (EBIT + D&A) | Comps, LBO |
| `ebit` | float | Operating income | DCF (UFCF calculation) |
| `net_income` | float | Net income | P/E calculation |
| `depreciation_amortization` | float | D&A expense | DCF (UFCF = NOPAT + D&A - CapEx - ΔNWC) |

#### Balance Sheet (in millions $)

| Parameter | Type | Description | Used By |
|-----------|------|-------------|---------|
| `total_debt` | float | Short-term + long-term debt | WACC, EV bridge |
| `cash` | float | Cash and cash equivalents | Net debt calculation |
| `net_debt` | float | Total debt - cash (negative = net cash) | DCF equity bridge, Comps EV |

#### Cash Flow Statement (in millions $)

| Parameter | Type | Description | Used By |
|-----------|------|-------------|---------|
| `capex` | float | Capital expenditures (positive number) | DCF (UFCF), LBO |
| `delta_nwc` | float | Change in net working capital (increase = positive) | DCF (UFCF) |

#### Rates and Margins

| Parameter | Type | Description | Used By |
|-----------|------|-------------|---------|
| `tax_rate` | float | Effective tax rate (e.g., 0.25 for 25%) | WACC, DCF, LBO |
| `ebitda_margin` | float | EBITDA / Revenue | Projections validation |
| `revenue_growth_3yr` | float | 3-year revenue CAGR | DCF projections |
| `projected_growth_rate` | float | Forward growth rate for projections | DCF 5-year forecast |

### Peer Company Data (gather-peers)

For each of 4-6 comparable companies:

| Parameter | Type | Unit | Description | Used By |
|-----------|------|------|-------------|---------|
| `ticker` | string | - | Peer stock ticker | Comps |
| `name` | string | - | Peer company name | Comps |
| `price` | float | $ | Current stock price | Comps (market cap) |
| `shares_outstanding` | float | millions | Diluted shares | Comps (market cap) |
| `net_debt` | float | millions $ | Total debt - cash | Comps (EV calculation) |
| `ltm_revenue` | float | millions $ | Last twelve months revenue | EV/Revenue multiple |
| `ltm_ebitda` | float | millions $ | Last twelve months EBITDA | EV/EBITDA multiple |
| `ltm_ebit` | float | millions $ | Last twelve months EBIT (optional) | EV/EBIT multiple |
| `ltm_net_income` | float | millions $ | Last twelve months net income (optional) | P/E ratio |

### Analyst Estimates (gather-analyst-estimates)

| Parameter | Type | Description | Used By |
|-----------|------|-------------|---------|
| `price_target_low` | float | Lowest analyst price target | Report comparison |
| `price_target_mean` | float | Consensus price target | Report comparison |
| `price_target_high` | float | Highest analyst price target | Report comparison |
| `consensus_rating` | string | "Strong Buy", "Buy", "Hold", "Sell", "Strong Sell" | Report |
| `analyst_count` | int | Number of analysts covering | Report confidence |
| `forward_revenue` | float | NTM revenue estimate (millions $) | NTM multiples |
| `forward_eps` | float | NTM EPS estimate | P/E valuation |
| `revenue_growth_estimate` | float | Expected revenue growth rate | Projection validation |

### Historical P/E Data (gather-historical-pe)

| Parameter | Type | Description | Used By |
|-----------|------|-------------|---------|
| `pe_min` | float | Minimum P/E over 2-year period | P/E valuation range |
| `pe_max` | float | Maximum P/E over 2-year period | P/E valuation range |
| `pe_mean` | float | Average P/E over period | P/E valuation |
| `pe_median` | float | Median P/E (50th percentile) | P/E valuation base case |
| `pe_p10` | float | 10th percentile P/E | P/E valuation range |
| `pe_p25` | float | 25th percentile P/E | P/E valuation conservative |
| `pe_p75` | float | 75th percentile P/E | P/E valuation optimistic |
| `pe_p90` | float | 90th percentile P/E | P/E valuation range |
| `pe_current` | float | Current trailing P/E | Valuation context |
| `pe_percentile_rank` | int | Current P/E percentile vs history (0-100) | Over/undervalued assessment |
| `eps_ttm` | float | Trailing twelve months EPS | P/E valuation (TTM basis) |
| `eps_forward` | float | Forward (NTM) EPS estimate | P/E valuation (forward basis) |

---

## Valuation Model Details

### WACC Calculation

**Formula**: `WACC = (E/V × Re) + (D/V × Rd × (1-T))`

| Input | Source | Notes |
|-------|--------|-------|
| `equity_value` | gather-market-data | Market cap |
| `debt_value` | gather-financials | Total debt (market value proxy) |
| `risk_free_rate` | External | 10-year Treasury yield (~4.5%) |
| `beta` | gather-market-data | 5-year monthly beta |
| `equity_risk_premium` | External | Historical ERP (~5%) |
| `cost_of_debt` | Estimate | Based on credit rating (~6-8%) |
| `tax_rate` | gather-financials | Effective or marginal tax rate |

### DCF Model (UFCFProjection)

**UFCF Formula**: `EBIT × (1 - Tax Rate) + D&A - CapEx - ΔNWC`

| Input | Source | Notes |
|-------|--------|-------|
| `revenue` | Projected | Base from gather-financials, grown at projected_growth_rate |
| `ebit` | Projected | Apply historical EBIT margin to projected revenue |
| `tax_rate` | gather-financials | Marginal tax rate |
| `depreciation_amortization` | Projected | % of revenue based on historical |
| `capex` | Projected | % of revenue based on historical |
| `delta_nwc` | Projected | ~1% of revenue change |
| `wacc` | Calculated | From WACC model |
| `terminal_growth` | Assumption | Long-term GDP growth (~2.5%) |
| `exit_multiple` | Comps | Sector average EV/EBITDA |
| `net_debt` | gather-financials | For equity bridge |
| `shares_outstanding` | gather-market-data | For per-share value |

### Comparable Company Analysis (PeerCompany)

| Input | Source | Notes |
|-------|--------|-------|
| `ticker` | gather-peers | Peer identifier |
| `name` | gather-peers | Display name |
| `price` | gather-peers | Current stock price |
| `shares_outstanding` | gather-peers | Diluted shares |
| `net_debt` | gather-peers | For EV calculation |
| `ltm_revenue` | gather-peers | For EV/Revenue |
| `ltm_ebitda` | gather-peers | For EV/EBITDA |
| `ltm_ebit` | gather-peers | For EV/EBIT (optional) |
| `ltm_net_income` | gather-peers | For P/E (optional) |

### LBO Model (simple_lbo)

| Input | Source | Notes |
|-------|--------|-------|
| `entry_ebitda` | gather-financials | Current EBITDA |
| `entry_multiple` | Assumption | Starting EV/EBITDA (e.g., 10x) |
| `leverage_turns` | Assumption | Debt/EBITDA (e.g., 5-6x) |
| `interest_rate` | Market | Leveraged loan rate (~8-9%) |
| `exit_multiple` | Assumption | Often same as entry (conservative) |
| `hold_years` | Assumption | Typically 5 years |
| `ebitda_growth` | gather-financials | projected_growth_rate |
| `capex_pct` | gather-financials | capex / ebitda |
| `tax_rate` | gather-financials | Cash tax rate |

### Historical P/E Valuation

| Input | Source | Notes |
|-------|--------|-------|
| `pe_p25`, `pe_median`, `pe_p75` | gather-historical-pe | P/E percentiles |
| `eps_ttm` | gather-historical-pe | For TTM-based valuation |
| `eps_forward` | gather-historical-pe | For forward-based valuation |

**Implied Price Calculation**:
- Conservative: `EPS × P/E_25th`
- Base Case: `EPS × P/E_median`
- Optimistic: `EPS × P/E_75th`

---

## Running Tests

```bash
cd company-valuation/skills/run-valuation/scripts
poetry run pytest -v
```

## Disclaimer

This tool is for educational and informational purposes only. The valuations produced are estimates based on publicly available data and should not be considered investment advice. Always conduct your own due diligence and consult with qualified financial professionals before making investment decisions.
