---
name: gather-risk-potential-analysis
description: Use when researching downside risks and upside potential catalysts for a stock, industry, and broader market
---

# Gather Risk & Potential Analysis

Search the web for comprehensive analysis of risks (downside factors) and potential catalysts (upside factors) at three levels: stock-specific, industry, and market.

## Before You Start

**Read the plugin README first** to understand the context of valuation analysis.

## Required Data Points

### Stock-Specific Risks (Downside)

| Category | Examples |
|----------|----------|
| Financial Risks | Debt levels, liquidity issues, declining margins, earnings misses |
| Operational Risks | Supply chain issues, key person dependency, execution challenges |
| Competitive Risks | Market share loss, pricing pressure, disruption threats |
| Regulatory Risks | Pending litigation, regulatory scrutiny, compliance issues |
| Valuation Risks | Overvaluation concerns, multiple compression risk |

### Stock-Specific Potential (Upside)

| Category | Examples |
|----------|----------|
| Growth Catalysts | New product launches, market expansion, M&A opportunities |
| Margin Expansion | Cost cutting initiatives, operating leverage, pricing power |
| Capital Returns | Buyback programs, dividend increases |
| Undervaluation | Trading below intrinsic value, hidden assets |
| Management | New leadership, strategic pivots, insider buying |

### Industry-Level Factors

| Factor Type | Risks | Potential |
|-------------|-------|-----------|
| Demand | Demand decline, commoditization | Secular growth, new use cases |
| Competition | New entrants, consolidation pressure | High barriers, oligopoly benefits |
| Regulation | Adverse regulation, ESG mandates | Favorable policy, subsidies |
| Technology | Disruption, obsolescence | Innovation leadership, IP moats |
| Cycle | Cyclical downturn, overcapacity | Cycle upturn, supply constraints |

### Market-Level Factors

| Factor Type | Risks | Potential |
|-------------|-------|-----------|
| Macro | Recession, inflation, rate hikes | Economic expansion, rate cuts |
| Geopolitical | Trade wars, sanctions, conflicts | Trade deals, stability |
| Sentiment | Risk-off, multiple compression | Risk-on, multiple expansion |
| Liquidity | Tightening, credit stress | QE, accommodative policy |
| Currency | FX headwinds | FX tailwinds |

## Search Strategy

### Stock-Specific Searches

1. **Risks**: `"{TICKER} risks concerns bearish case"`
2. **Bull case**: `"{TICKER} bull case upside potential catalysts"`
3. **Recent news**: `"{TICKER} stock news analysis {CURRENT_MONTH} {CURRENT_YEAR}"`
4. **Analyst concerns**: `"{TICKER} analyst downgrade concerns"`
5. **Analyst bullish**: `"{TICKER} analyst upgrade bullish"`

### Industry Searches

1. **Industry outlook**: `"{INDUSTRY} industry outlook 2026 risks opportunities"`
2. **Industry trends**: `"{INDUSTRY} sector trends headwinds tailwinds"`
3. **Competitive dynamics**: `"{INDUSTRY} competition market share"`

### Market Searches

1. **Market outlook**: `"stock market outlook 2026 risks opportunities"`
2. **Macro factors**: `"macroeconomic outlook recession inflation rates"`
3. **Sector rotation**: `"{SECTOR} sector outlook rotation"`

## Output Format

```python
risk_potential_analysis = {
    # Stock-Specific
    "stock_risks": [
        {
            "category": "Financial",
            "risk": "High debt-to-equity ratio of 2.5x",
            "severity": "Medium",  # Low, Medium, High
            "probability": "Medium"
        },
        # ... more risks
    ],
    "stock_catalysts": [
        {
            "category": "Growth",
            "catalyst": "New AI product launch expected Q2 2026",
            "impact": "High",  # Low, Medium, High
            "timeline": "Near-term"  # Near-term (<6mo), Medium-term (6-18mo), Long-term (>18mo)
        },
        # ... more catalysts
    ],

    # Industry-Level
    "industry_risks": [
        {
            "factor": "Regulatory",
            "risk": "Proposed antitrust legislation",
            "impact_on_stock": "Medium"
        }
    ],
    "industry_tailwinds": [
        {
            "factor": "Demand",
            "tailwind": "AI adoption driving 20% industry growth",
            "impact_on_stock": "High"
        }
    ],

    # Market-Level
    "market_risks": [
        {
            "factor": "Macro",
            "risk": "Fed rate uncertainty",
            "impact_on_stock": "Low"
        }
    ],
    "market_tailwinds": [
        {
            "factor": "Liquidity",
            "tailwind": "Potential rate cuts in H2 2026",
            "impact_on_stock": "Medium"
        }
    ],

    # Summary Assessment
    "risk_reward_summary": {
        "overall_risk_level": "Medium",  # Low, Medium, High
        "overall_opportunity_level": "High",
        "key_risk": "Competition from new entrants",
        "key_catalyst": "AI product launch",
        "analyst_sentiment": "Cautiously optimistic"
    }
}
```

## Analysis Guidelines

### Depth of Research

- **Minimum 3-5 risks** at stock level
- **Minimum 3-5 catalysts** at stock level
- **At least 2 factors** at industry level (each side)
- **At least 2 factors** at market level (each side)

### Severity/Impact Assessment

| Level | Definition |
|-------|------------|
| Low | Minor impact on valuation (<5%) |
| Medium | Moderate impact (5-15%) |
| High | Significant impact (>15%) |

### Probability Assessment

| Level | Definition |
|-------|------------|
| Low | <25% likelihood |
| Medium | 25-60% likelihood |
| High | >60% likelihood |

### Timeline Categories

| Category | Definition |
|----------|------------|
| Near-term | Within 6 months |
| Medium-term | 6-18 months |
| Long-term | Beyond 18 months |

## Data Sources

- Seeking Alpha (bull/bear cases)
- The Motley Fool
- Bloomberg/Reuters analysis
- Company earnings call transcripts
- Industry research reports
- Analyst notes (via financial news)
- SEC filings (risk factors section)

## Validation

- Cross-reference risks mentioned in 10-K risk factors
- Check if catalysts are already priced in
- Compare bear/bull cases from multiple sources
- Note recency of analysis (prefer last 90 days)
- Distinguish between company-specific vs systemic risks

## Usage in Valuation

Risk/potential analysis informs:
1. **DCF sensitivity** - Adjust scenarios based on key risks
2. **Multiple selection** - Premium/discount to peers based on risk profile
3. **Investment thesis** - Support or challenge the valuation conclusion
4. **Report narrative** - Provide context beyond numbers
