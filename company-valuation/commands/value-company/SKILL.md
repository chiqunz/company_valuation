---
name: value-company
description: Run comprehensive company valuation analysis with DCF, Comps, LBO, and Historical P/E models
disable-model-invocation: true
---

# Company Valuation Command

Run a comprehensive institutional-grade valuation analysis for a publicly traded company.

## Usage

```
/value-company <TICKER>
```

## Workflow

Execute these steps in order, using the plugin's specialized skills:

### Step 1: Gather Market Data
Use the `gather-market-data` skill to search for:
- Current stock price
- Shares outstanding (diluted)
- Market capitalization
- Beta coefficient
- 52-week high/low

### Step 2: Gather Financial Data
Use the `gather-financials` skill to search for:
- LTM Revenue, EBITDA, EBIT, Net Income
- Total debt and cash
- CapEx, D&A
- Historical growth rates
- Operating margins
- Tax rate

### Step 3: Identify and Gather Peer Data
Use the `gather-peers` skill to:
- Identify 4-6 comparable companies in the same sector
- Gather market data and financials for each peer
- Calculate trading multiples (EV/EBITDA, EV/Revenue, P/E)

### Step 4: Gather Analyst Estimates
Use the `gather-analyst-estimates` skill to search for:
- Analyst price targets (low/mean/high)
- Consensus rating
- Forward revenue/EPS estimates

### Step 5: Gather Historical P/E Data
Use the `gather-historical-pe` skill to search for:
- Historical P/E ratio over past 500 trading days (~2 years)
- P/E percentiles (10th, 25th, 50th, 75th, 90th)
- Current P/E and percentile rank
- TTM EPS and Forward EPS estimates

### Step 6: Run Valuation Models
Use the `run-valuation` skill to execute Python code using the `company_valuation` library:
- Calculate WACC using CAPM
- Run DCF with perpetuity growth and exit multiple methods
- Run Comparable Company Analysis
- Run simplified LBO analysis
- Run Historical P/E valuation (using P/E percentiles × EPS)
- Generate sensitivity tables

### Step 7: Generate Report
Use the `generate-report` skill to create a comprehensive markdown report at:
```
./valuation_reports/{TICKER}_{DATE}.md
```

## Output

The command produces:
1. A detailed valuation report in markdown format
2. Console summary of key valuation metrics

## Example

```
> /company-valuation:value-company AAPL

Gathering market data for AAPL...
Gathering financial data...
Identifying comparable companies...
Gathering analyst estimates...
Gathering historical P/E data...
Running valuation models...
Generating report...

Report saved to: ./valuation_reports/AAPL_2026-01-20.md

Valuation Summary:
- DCF (Perpetuity): $185 - $225 per share
- DCF (Exit Multiple): $190 - $230 per share
- Trading Comps: $175 - $210 per share
- Historical P/E (TTM): $170 - $215 per share
- Historical P/E (Forward): $180 - $228 per share
- Analyst Consensus: $195 (range: $165 - $235)

Current P/E of 28.5x is at 62nd percentile of 2-year history.
```
