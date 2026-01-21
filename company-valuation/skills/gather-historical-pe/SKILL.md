---
name: gather-historical-pe
description: Use when gathering historical P/E ratio data for historical valuation analysis
---

# Gather Historical P/E Data

Search the web to collect historical P/E ratio data for a company over the past 500 trading days (~2 years).

## Required Data Points

| Data Point | Description |
|------------|-------------|
| Historical P/E Range | Min and max P/E over period |
| P/E Percentiles | 10th, 25th, 50th, 75th, 90th |
| Current P/E | Today's trailing P/E |
| Average P/E | Mean over the period |
| TTM EPS | Trailing twelve months EPS |
| Forward EPS | NTM EPS estimate |

## Search Strategy

1. **Historical P/E**: `"{TICKER} historical PE ratio 2 year chart"`
2. **PE statistics**: `"{TICKER} PE ratio range high low average"`
3. **EPS data**: `"{TICKER} EPS TTM forward estimate"`
4. **Valuation history**: `"{TICKER} valuation history PE multiple"`

## Data Sources

| Source | Data Available |
|--------|----------------|
| Macrotrends | Historical P/E charts with downloadable data |
| YCharts | P/E percentile rankings |
| Morningstar | Valuation statistics |
| Yahoo Finance | Current P/E and EPS |
| GuruFocus | P/E percentile vs history |

## Output Format

```python
historical_pe = {
    # P/E Statistics (500 trading days / ~2 years)
    "pe_min": 18.5,
    "pe_max": 35.2,
    "pe_mean": 25.8,
    "pe_median": 24.5,

    # Percentiles
    "pe_p10": 20.1,
    "pe_p25": 22.3,
    "pe_p50": 24.5,  # Same as median
    "pe_p75": 28.7,
    "pe_p90": 32.4,

    # Current values
    "pe_current": 26.8,
    "pe_percentile_rank": 58,  # Current P/E is at 58th percentile historically

    # EPS for valuation
    "eps_ttm": 6.42,
    "eps_forward": 7.15,  # NTM estimate

    # Metadata
    "period_start": "2024-01-20",
    "period_end": "2026-01-20",
    "data_points": 500
}
```

## Calculating Implied Valuations

From the historical P/E data, calculate implied stock prices:

```python
# Using TTM EPS
implied_low_ttm = eps_ttm * pe_p25      # Conservative (25th percentile P/E)
implied_mid_ttm = eps_ttm * pe_median   # Base case (median P/E)
implied_high_ttm = eps_ttm * pe_p75     # Optimistic (75th percentile P/E)

# Using Forward EPS
implied_low_fwd = eps_forward * pe_p25
implied_mid_fwd = eps_forward * pe_median
implied_high_fwd = eps_forward * pe_p75
```

## Interpretation Guide

| Current P/E vs History | Interpretation |
|------------------------|----------------|
| Below 25th percentile | Potentially undervalued |
| 25th - 75th percentile | Fair value range |
| Above 75th percentile | Potentially overvalued |

## Validation

- P/E should be positive (exclude loss periods)
- Forward EPS should be reasonable vs TTM
- Verify data covers requested time period
- Cross-check current P/E with multiple sources
- Note if company had unusual periods (losses, one-time items)

## Common Issues

| Issue | Handling |
|-------|----------|
| Negative EPS periods | Exclude from P/E calculation, note in report |
| Stock splits | Ensure EPS is split-adjusted |
| One-time items | Note if GAAP vs adjusted EPS differs significantly |
| Recent IPO | Use available history, note limited data |
