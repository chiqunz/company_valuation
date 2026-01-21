---
name: generate-report
description: Use when generating the final markdown valuation report from collected data and model results
---

# Generate Valuation Report

Create a comprehensive markdown report from all gathered data and valuation results.

## Report Location

Save reports to: `./valuation_reports/{TICKER}_{DATE}.md`

Create the directory if it doesn't exist:
```bash
mkdir -p ./valuation_reports
```

## Report Template

```markdown
# Company Valuation Report: {COMPANY_NAME} ({TICKER})

**Date:** {DATE}
**Analyst:** Claude Code
**Current Price:** ${CURRENT_PRICE}

---

## Executive Summary

{COMPANY_NAME} is valued at **${FAIR_VALUE_LOW} - ${FAIR_VALUE_HIGH}** per share based on
a blend of DCF, comparable company, and LBO analyses. The current stock price of
${CURRENT_PRICE} represents a {PREMIUM_DISCOUNT}% {premium/discount} to our midpoint
fair value estimate of ${FAIR_VALUE_MID}.

| Methodology | Low | Mid | High |
|-------------|-----|-----|------|
| DCF (Perpetuity Growth) | ${DCF_PERP_LOW} | ${DCF_PERP_MID} | ${DCF_PERP_HIGH} |
| DCF (Exit Multiple) | ${DCF_EXIT_LOW} | ${DCF_EXIT_MID} | ${DCF_EXIT_HIGH} |
| Trading Comps | ${COMPS_LOW} | ${COMPS_MID} | ${COMPS_HIGH} |
| Historical P/E (TTM) | ${HIST_PE_TTM_LOW} | ${HIST_PE_TTM_MID} | ${HIST_PE_TTM_HIGH} |
| Historical P/E (Forward) | ${HIST_PE_FWD_LOW} | ${HIST_PE_FWD_MID} | ${HIST_PE_FWD_HIGH} |
| LBO Ability-to-Pay | ${LBO_LOW} | ${LBO_MID} | ${LBO_HIGH} |
| **Blended Range** | **${BLEND_LOW}** | **${BLEND_MID}** | **${BLEND_HIGH}** |

---

## Company Overview

- **Sector:** {SECTOR}
- **Market Cap:** ${MARKET_CAP}B
- **Enterprise Value:** ${EV}B
- **52-Week Range:** ${52W_LOW} - ${52W_HIGH}

---

## DCF Analysis

### WACC Calculation

| Component | Value |
|-----------|-------|
| Risk-Free Rate | {RF_RATE}% |
| Beta | {BETA} |
| Equity Risk Premium | {ERP}% |
| Cost of Equity | {COE}% |
| Cost of Debt (pre-tax) | {COD}% |
| Tax Rate | {TAX_RATE}% |
| Equity Weight | {E_WEIGHT}% |
| Debt Weight | {D_WEIGHT}% |
| **WACC** | **{WACC}%** |

### Cash Flow Projections

| Year | Revenue | EBITDA | EBIT | UFCF |
|------|---------|--------|------|------|
| 1 | ${REV_1} | ${EBITDA_1} | ${EBIT_1} | ${UFCF_1} |
| 2 | ${REV_2} | ${EBITDA_2} | ${EBIT_2} | ${UFCF_2} |
| 3 | ${REV_3} | ${EBITDA_3} | ${EBIT_3} | ${UFCF_3} |
| 4 | ${REV_4} | ${EBITDA_4} | ${EBIT_4} | ${UFCF_4} |
| 5 | ${REV_5} | ${EBITDA_5} | ${EBIT_5} | ${UFCF_5} |

### Valuation Output

**Perpetuity Growth Method (g = {TERM_GROWTH}%)**
- PV of Cash Flows: ${PV_CF}
- PV of Terminal Value: ${PV_TV}
- Enterprise Value: ${DCF_EV}
- Equity Value: ${DCF_EQUITY}
- **Per Share: ${DCF_PER_SHARE}**

**Exit Multiple Method ({EXIT_MULT}x EBITDA)**
- Enterprise Value: ${DCF_EXIT_EV}
- Implied Terminal Growth: {IMPLIED_GROWTH}%
- **Per Share: ${DCF_EXIT_PER_SHARE}**

### Sensitivity Analysis (WACC vs Terminal Growth)

|  | {G1}% | {G2}% | {G3}% | {G4}% | {G5}% |
|--|-------|-------|-------|-------|-------|
| {W1}% | ${V11} | ${V12} | ${V13} | ${V14} | ${V15} |
| {W2}% | ${V21} | ${V22} | ${V23} | ${V24} | ${V25} |
| **{W3}%** | ${V31} | ${V32} | **${V33}** | ${V34} | ${V35} |
| {W4}% | ${V41} | ${V42} | ${V43} | ${V44} | ${V45} |
| {W5}% | ${V51} | ${V52} | ${V53} | ${V54} | ${V55} |

*Base case highlighted*

---

## Comparable Company Analysis

### Peer Group

| Company | Ticker | EV/EBITDA | EV/Revenue | P/E |
|---------|--------|-----------|------------|-----|
| {PEER1_NAME} | {PEER1} | {P1_EV_EBITDA}x | {P1_EV_REV}x | {P1_PE}x |
| {PEER2_NAME} | {PEER2} | {P2_EV_EBITDA}x | {P2_EV_REV}x | {P2_PE}x |
| {PEER3_NAME} | {PEER3} | {P3_EV_EBITDA}x | {P3_EV_REV}x | {P3_PE}x |
| {PEER4_NAME} | {PEER4} | {P4_EV_EBITDA}x | {P4_EV_REV}x | {P4_PE}x |
| **Median** | | **{MED_EV_EBITDA}x** | **{MED_EV_REV}x** | **{MED_PE}x** |

### Implied Valuation

| Multiple | Median | Implied EV | Implied Equity | Per Share |
|----------|--------|------------|----------------|-----------|
| EV/EBITDA | {MED_EV_EBITDA}x | ${IMPL_EV_EBITDA} | ${IMPL_EQ_EBITDA} | ${IMPL_PS_EBITDA} |
| EV/Revenue | {MED_EV_REV}x | ${IMPL_EV_REV} | ${IMPL_EQ_REV} | ${IMPL_PS_REV} |

---

## LBO Analysis

### Transaction Assumptions

| Item | Value |
|------|-------|
| Entry EBITDA | ${ENTRY_EBITDA} |
| Entry Multiple | {ENTRY_MULT}x |
| Purchase Price | ${PURCHASE_PRICE} |
| Leverage | {LEVERAGE}x EBITDA |
| Interest Rate | {INT_RATE}% |
| Hold Period | {HOLD_YEARS} years |

### Returns Analysis

| Metric | Value |
|--------|-------|
| Entry Equity | ${ENTRY_EQUITY} |
| Exit Equity | ${EXIT_EQUITY} |
| MOIC | {MOIC}x |
| IRR | {IRR}% |

### Ability-to-Pay

For a target IRR of **20%**, a financial sponsor could pay up to **{MAX_MULT}x EBITDA**,
implying a maximum equity value of **${MAX_EQUITY_VALUE}** or **${MAX_PER_SHARE}/share**.

---

## Historical P/E Valuation

This methodology values the stock based on where it has traded historically over the past ~500 trading days (~2 years).

### Historical P/E Statistics

| Statistic | P/E Multiple |
|-----------|--------------|
| Minimum | {PE_MIN}x |
| 10th Percentile | {PE_P10}x |
| 25th Percentile | {PE_P25}x |
| Median (50th) | {PE_MEDIAN}x |
| Mean | {PE_MEAN}x |
| 75th Percentile | {PE_P75}x |
| 90th Percentile | {PE_P90}x |
| Maximum | {PE_MAX}x |
| **Current P/E** | **{PE_CURRENT}x** |
| Current Percentile Rank | {PE_PERCENTILE_RANK}th percentile |

### Implied Valuation

**Using TTM EPS (${EPS_TTM})**

| Scenario | P/E Multiple | Implied Price |
|----------|--------------|---------------|
| Conservative (25th %ile) | {PE_P25}x | ${HIST_PE_TTM_LOW} |
| Base Case (Median) | {PE_MEDIAN}x | ${HIST_PE_TTM_MID} |
| Optimistic (75th %ile) | {PE_P75}x | ${HIST_PE_TTM_HIGH} |

**Using Forward EPS (${EPS_FORWARD})**

| Scenario | P/E Multiple | Implied Price |
|----------|--------------|---------------|
| Conservative (25th %ile) | {PE_P25}x | ${HIST_PE_FWD_LOW} |
| Base Case (Median) | {PE_MEDIAN}x | ${HIST_PE_FWD_MID} |
| Optimistic (75th %ile) | {PE_P75}x | ${HIST_PE_FWD_HIGH} |

### Assessment

{PE_ASSESSMENT}

The current P/E of **{PE_CURRENT}x** sits at the **{PE_PERCENTILE_RANK}th percentile** of its 2-year historical range.
At the current price of **${CURRENT_PRICE}**, the stock is trading at {PREMIUM_DISCOUNT_VS_MEDIAN}%
{premium/discount} to the median historical P/E implied value.

---

## Analyst Estimates

| Metric | Low | Mean | High |
|--------|-----|------|------|
| Price Target | ${PT_LOW} | ${PT_MEAN} | ${PT_HIGH} |
| Forward Revenue | - | ${FWD_REV} | - |
| Forward EPS | - | ${FWD_EPS} | - |

**Consensus Rating:** {RATING} ({ANALYST_COUNT} analysts)

---

## Key Assumptions & Risks

### Assumptions
- Revenue growth: {GROWTH_RATE}% annually
- Terminal growth rate: {TERM_GROWTH}%
- EBITDA margin: {EBITDA_MARGIN}%
- Tax rate: {TAX_RATE}%

### Key Risks
- Market/macroeconomic conditions
- Competitive dynamics
- Execution risk on growth initiatives
- Interest rate sensitivity

---

## Data Sources

- Market data: Yahoo Finance, as of {DATE}
- Financial statements: Company 10-K/10-Q filings
- Analyst estimates: Consensus from multiple sources
- Peer data: Public filings and financial data providers

---

*This valuation report was generated using the company_valuation library.*
*Report generated: {TIMESTAMP}*
```

## Instructions

1. Replace all `{PLACEHOLDER}` values with actual data
2. Format numbers appropriately:
   - Currency: `$X,XXX` or `$X.XXB` for billions
   - Percentages: `X.X%`
   - Multiples: `X.Xx`
3. Highlight the base case in sensitivity tables
4. Include data attribution for transparency
5. Calculate premium/discount vs current price

## File Naming

Format: `{TICKER}_{YYYY-MM-DD}.md`

Example: `AAPL_2026-01-20.md`
