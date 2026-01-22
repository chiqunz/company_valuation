---
name: gather-analyst-estimates
description: Use when searching for analyst price targets, ratings, and forward estimates for a company
---

# Gather Analyst Estimates

Search the web for sell-side analyst coverage and consensus estimates.

## Before You Start

**Read the plugin README first** to understand the exact parameters needed:
- See `README.md` section: **"Required Data Parameters > Analyst Estimates (gather-analyst-estimates)"**
- This ensures you gather all required fields with correct types

## Required Data Points

| Data Point | Description |
|------------|-------------|
| Price Target Low | Lowest analyst price target |
| Price Target Mean | Average/consensus price target |
| Price Target High | Highest analyst price target |
| Consensus Rating | Buy/Hold/Sell rating |
| Number of Analysts | Coverage count |
| Forward Revenue | NTM revenue estimate |
| Forward EPS | NTM EPS estimate |

## Search Strategy

1. **Price targets**: `"{TICKER} analyst price target consensus"`
2. **Ratings**: `"{TICKER} analyst rating buy sell hold"`
3. **Estimates**: `"{TICKER} revenue EPS estimates forward"`
4. **Specific**: `"{TICKER} analyst coverage Wall Street"`

## Output Format

```python
analyst_estimates = {
    "price_target_low": 165.00,
    "price_target_mean": 195.00,
    "price_target_high": 235.00,
    "consensus_rating": "Buy",  # Strong Buy, Buy, Hold, Sell, Strong Sell
    "analyst_count": 42,

    # Forward estimates
    "forward_revenue": 410000,  # NTM revenue in millions
    "forward_eps": 7.25,  # NTM EPS

    # Optional: growth estimates
    "revenue_growth_estimate": 0.07,  # 7% expected growth
    "eps_growth_estimate": 0.10  # 10% expected growth
}
```

## Rating Interpretation

| Rating | Meaning |
|--------|---------|
| Strong Buy | >80% buy recommendations |
| Buy | >60% buy recommendations |
| Hold | Mixed recommendations |
| Sell | >40% sell recommendations |
| Strong Sell | >60% sell recommendations |

## Data Sources

- Yahoo Finance (Analyst Recommendations)
- TipRanks
- MarketWatch
- Seeking Alpha
- Bloomberg (if available)

## Validation

- Price target range should be reasonable (typically within +/- 30% of current price)
- More analysts = higher confidence
- Compare estimates to historical growth rates
- Note the recency of estimates (prefer last 90 days)

## Usage in Valuation

Analyst estimates provide:
1. **Sanity check** - Compare your DCF result to analyst targets
2. **Forward multiples** - Use forward estimates for NTM valuation
3. **Growth assumptions** - Validate projection assumptions
