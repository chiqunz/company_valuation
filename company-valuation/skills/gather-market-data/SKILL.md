---
name: gather-market-data
description: Use when gathering stock price, market cap, beta, and shares outstanding for a company valuation
---

# Gather Market Data

Search the web to collect current market data for a company.

## Before You Start

**Read the plugin README first** to understand the exact parameters needed:
- See `README.md` section: **"Required Data Parameters > Market Data (gather-market-data)"**
- This ensures you gather all required fields with correct types and units

## Required Data Points

| Data Point | Description | Example Source |
|------------|-------------|----------------|
| Stock Price | Current trading price | Yahoo Finance, Google Finance |
| Shares Outstanding | Diluted shares (millions) | Company filings, Yahoo Finance |
| Market Cap | Price × Shares | Calculated or from source |
| Beta | 5-year monthly vs S&P 500 | Yahoo Finance, Bloomberg |
| 52-Week Range | High and low prices | Yahoo Finance |

## Search Strategy

1. **Primary search**: `"{TICKER} stock price market cap shares outstanding"`
2. **Beta search**: `"{TICKER} beta coefficient"`
3. **Verify with**: `"{COMPANY_NAME} investor relations"`

## Output Format

After gathering data, store in this structure for the valuation:

```python
market_data = {
    "ticker": "AAPL",
    "company_name": "Apple Inc.",
    "price": 185.50,
    "shares_outstanding": 15500,  # millions
    "market_cap": 2875250,  # millions (price × shares)
    "beta": 1.25,
    "fifty_two_week_low": 165.00,
    "fifty_two_week_high": 199.62
}
```

## Validation

- Market cap should equal price × shares (within rounding)
- Beta typically between 0.5 and 2.5 for most stocks
- 52-week range should contain current price

## Notes

- Use multiple sources to cross-verify data
- Prefer most recent data (within last trading day)
- Note the date of data collection for the report
