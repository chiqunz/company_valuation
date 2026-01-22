---
name: gather-peers
description: Use when identifying comparable companies and gathering their financial data for trading comps analysis
---

# Gather Peer Company Data

Identify and collect data for comparable companies to use in trading comps analysis.

## Before You Start

**Read the plugin README first** to understand the exact parameters needed:
- See `README.md` section: **"Required Data Parameters > Peer Company Data (gather-peers)"**
- This ensures you gather all required fields for each peer with correct types and units

## Peer Selection Criteria

Select 4-6 peers based on:
1. **Same industry/sector** - Similar business model
2. **Similar size** - Market cap within 0.5x to 2x of target
3. **Geographic exposure** - Similar markets
4. **Growth profile** - Similar growth stage

## Search Strategy

1. **Identify peers**: `"{TICKER} comparable companies competitors"`
2. **Industry peers**: `"{SECTOR} largest companies by market cap"`
3. **Per peer**: `"{PEER_TICKER} market cap revenue EBITDA"`

## Required Data Per Peer

For each peer company, gather:

| Data Point | Description |
|------------|-------------|
| Ticker | Stock symbol |
| Company Name | Full name |
| Price | Current stock price |
| Shares Outstanding | Diluted shares (millions) |
| Net Debt | Total debt - cash |
| LTM Revenue | Last twelve months revenue |
| LTM EBITDA | Last twelve months EBITDA |
| LTM EBIT | Last twelve months EBIT (optional) |
| LTM Net Income | For P/E calculation (optional) |

## Output Format

```python
peers = [
    {
        "ticker": "MSFT",
        "name": "Microsoft Corporation",
        "price": 378.50,
        "shares_outstanding": 7430,  # millions
        "net_debt": -35000,  # negative = net cash
        "ltm_revenue": 227580,
        "ltm_ebitda": 108550,
        "ltm_ebit": 88520,
        "ltm_net_income": 72361
    },
    {
        "ticker": "GOOGL",
        "name": "Alphabet Inc.",
        "price": 142.80,
        "shares_outstanding": 12600,
        "net_debt": -95000,
        "ltm_revenue": 307390,
        "ltm_ebitda": 97230,
        "ltm_ebit": 84290,
        "ltm_net_income": 73795
    },
    # ... 2-4 more peers
]
```

## Calculated Multiples

The `run-valuation` skill will calculate these from the peer data:

| Multiple | Formula |
|----------|---------|
| EV/EBITDA | (Market Cap + Net Debt) / LTM EBITDA |
| EV/Revenue | (Market Cap + Net Debt) / LTM Revenue |
| P/E | Price / (LTM Net Income / Shares) |

## Common Peer Groups by Sector

| Sector | Example Peers |
|--------|---------------|
| Big Tech | AAPL, MSFT, GOOGL, META, AMZN |
| Semiconductors | NVDA, AMD, INTC, QCOM, AVGO |
| Banks | JPM, BAC, WFC, C, GS |
| Consumer | PG, KO, PEP, JNJ, UNH |
| Energy | XOM, CVX, COP, EOG, SLB |

## Validation

- All peers should have positive revenue and EBITDA
- Multiples should be within reasonable range for sector
- Exclude outliers (negative EBITDA, extreme multiples)
