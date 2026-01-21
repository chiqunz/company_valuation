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

1. Ensure the `company_valuation` Python library is available in your project
2. Install the plugin in Claude Code:

```bash
claude --plugin-dir ./company-valuation
```

Or add to your Claude Code settings:

```json
{
  "plugins": ["./company-valuation"]
}
```

## Usage

Run a valuation analysis:

```
/company-valuation:value-company AAPL
```

This will:
1. Search for Apple's current market data (price, shares, beta)
2. Gather financial metrics (revenue, EBITDA, debt, etc.)
3. Identify comparable companies and gather their data
4. Search for analyst price targets and estimates
5. Gather historical P/E data (500 trading days / ~2 years)
6. Execute DCF, Comps, LBO, and Historical P/E valuation models
7. Generate a comprehensive report at `./valuation_reports/AAPL_YYYY-MM-DD.md`

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

## Valuation Models

### DCF (Discounted Cash Flow)
- 5-year explicit forecast period
- WACC calculated via CAPM
- Terminal value via perpetuity growth and exit multiple
- Mid-year convention
- Sensitivity analysis (WACC vs terminal growth)

### Comparable Company Analysis
- 4-6 peer companies
- Trading multiples: EV/EBITDA, EV/Revenue, P/E
- Implied valuation based on peer medians

### LBO (Leveraged Buyout)
- Simplified single-tranche debt structure
- Ability-to-pay analysis (max price for target IRR)
- MOIC and IRR calculation

### Historical P/E Valuation
- Uses ~500 trading days (~2 years) of P/E history
- Calculates P/E percentiles (10th, 25th, 50th, 75th, 90th)
- Applies P/E percentiles to TTM EPS for valuation range
- Applies P/E percentiles to Forward EPS for growth-adjusted range
- Shows current P/E percentile rank vs history

## Report Output

Reports are saved to `./valuation_reports/` with the format:
```
{TICKER}_{YYYY-MM-DD}.md
```

Example: `AAPL_2026-01-20.md`

## Requirements

- Claude Code with plugin support
- Python 3.10+
- `company_valuation` library installed
- Web search capability for data gathering

## Example Output

```
> /company-valuation:value-company MSFT

Gathering market data for MSFT...
  - Price: $378.50
  - Market Cap: $2.81T
  - Beta: 0.89

Gathering financial data...
  - LTM Revenue: $227.6B
  - LTM EBITDA: $108.5B

Identifying comparable companies...
  - AAPL, GOOGL, META, AMZN

Gathering historical P/E data...
  - 2-year P/E range: 24.5x - 38.2x
  - Current P/E: 32.1x (68th percentile)

Running valuation models...
  - WACC: 9.2%
  - DCF (Perpetuity): $385 per share
  - DCF (Exit Multiple): $392 per share
  - Trading Comps: $365 per share
  - Historical P/E (TTM): $355 - $410 per share
  - Historical P/E (Forward): $375 - $435 per share

Generating report...
Report saved to: ./valuation_reports/MSFT_2026-01-20.md

Valuation Summary:
- Fair Value Range: $350 - $420 per share
- Current Price: $378.50
- Implied: -2% discount to midpoint
```

## Disclaimer

This tool is for educational and informational purposes only. The valuations produced are estimates based on publicly available data and should not be considered investment advice. Always conduct your own due diligence and consult with qualified financial professionals before making investment decisions.
