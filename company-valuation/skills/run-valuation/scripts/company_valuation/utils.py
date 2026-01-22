"""
Utility functions for valuation.

This module implements:
- Treasury Stock Method (TSM) for diluted shares
- Common financial calculations
- Shared statistical utilities
"""

from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class OptionGrant:
    """
    Option or warrant grant for TSM calculation.

    Attributes:
        quantity: Number of options/warrants
        strike_price: Exercise price
        is_in_the_money: Whether options are ITM at current price
    """
    quantity: float
    strike_price: float
    is_in_the_money: bool = True


def treasury_stock_method(
    options: list[OptionGrant],
    current_price: float
) -> float:
    """
    Calculate additional dilutive shares using Treasury Stock Method.

    TSM assumes option exercise proceeds are used to buy back shares
    at current market price, reducing dilution.

    Formula: New Shares = Options × (1 - Strike/Price)

    Only in-the-money options (Strike < Price) are dilutive.

    Args:
        options: List of option grants
        current_price: Current stock price

    Returns:
        Number of additional dilutive shares
    """
    if current_price <= 0:
        return 0.0

    total_dilution = 0.0

    for opt in options:
        # Only ITM options are dilutive
        if opt.strike_price < current_price:
            # Shares from exercise
            gross_shares = opt.quantity
            # Shares bought back with proceeds
            proceeds = opt.quantity * opt.strike_price
            shares_repurchased = proceeds / current_price
            # Net dilution
            net_shares = gross_shares - shares_repurchased
            total_dilution += max(0, net_shares)

    return total_dilution


def diluted_shares(
    basic_shares: float,
    options: list[OptionGrant],
    current_price: float,
    rsus: float = 0.0
) -> float:
    """
    Calculate fully diluted share count.

    Diluted Shares = Basic Shares + TSM Dilution + RSUs

    Args:
        basic_shares: Basic shares outstanding
        options: List of option grants
        current_price: Current stock price
        rsus: Restricted stock units outstanding

    Returns:
        Fully diluted share count
    """
    tsm_dilution = treasury_stock_method(options, current_price)
    return basic_shares + tsm_dilution + rsus


def enterprise_value(
    equity_value: float,
    total_debt: float,
    cash: float,
    minority_interest: float = 0.0,
    preferred_stock: float = 0.0
) -> float:
    """
    Calculate Enterprise Value from Equity Value.

    EV = Equity Value + Debt - Cash + Minority Interest + Preferred

    Args:
        equity_value: Market cap or equity value
        total_debt: Total debt (short + long term)
        cash: Cash and cash equivalents
        minority_interest: Minority/non-controlling interest
        preferred_stock: Preferred stock (if not in equity)

    Returns:
        Enterprise Value
    """
    return equity_value + total_debt - cash + minority_interest + preferred_stock


def equity_value_from_ev(
    enterprise_value: float,
    total_debt: float,
    cash: float,
    minority_interest: float = 0.0,
    preferred_stock: float = 0.0
) -> float:
    """
    Calculate Equity Value from Enterprise Value.

    Equity = EV - Debt + Cash - Minority Interest - Preferred

    Args:
        enterprise_value: Enterprise Value
        total_debt: Total debt
        cash: Cash and equivalents
        minority_interest: Minority interest
        preferred_stock: Preferred stock

    Returns:
        Equity Value
    """
    return enterprise_value - total_debt + cash - minority_interest - preferred_stock


def net_debt(
    total_debt: float,
    cash: float
) -> float:
    """
    Calculate Net Debt.

    Net Debt = Total Debt - Cash

    Negative net debt means company has more cash than debt.

    Args:
        total_debt: Total debt
        cash: Cash and equivalents

    Returns:
        Net Debt
    """
    return total_debt - cash


def ltm_calculation(
    fiscal_year: float,
    ytd_current: float,
    ytd_prior: float
) -> float:
    """
    Calculate LTM (Last Twelve Months) metric.

    LTM = Fiscal Year + Current YTD - Prior Year YTD

    This calendarizes metrics to the most recent 12-month period.

    Args:
        fiscal_year: Full fiscal year amount
        ytd_current: Current year-to-date amount
        ytd_prior: Prior year YTD (same period as current YTD)

    Returns:
        LTM metric value
    """
    return fiscal_year + ytd_current - ytd_prior


def implied_perpetual_growth(
    terminal_value: float,
    final_fcf: float,
    discount_rate: float
) -> float:
    """
    Calculate implied perpetual growth rate from terminal value.

    Given TV = FCF(1+g)/(r-g), solve for g:
    g = (TV × r - FCF) / (TV + FCF)

    Used to sanity-check exit multiple terminal values.

    Args:
        terminal_value: Terminal value
        final_fcf: Final year free cash flow
        discount_rate: WACC or cost of equity

    Returns:
        Implied perpetual growth rate
    """
    if terminal_value + final_fcf == 0:
        return 0.0

    numerator = terminal_value * discount_rate - final_fcf
    denominator = terminal_value + final_fcf
    return numerator / denominator


def rule_of_40(
    revenue_growth: float,
    profit_margin: float
) -> float:
    """
    Calculate Rule of 40 score for SaaS companies.

    Rule of 40 = Revenue Growth % + Profit Margin %

    Score >= 40% generally indicates healthy SaaS business.

    Args:
        revenue_growth: YoY revenue growth rate (e.g., 0.25 for 25%)
        profit_margin: EBITDA or FCF margin (e.g., 0.20 for 20%)

    Returns:
        Rule of 40 score (as decimal, e.g., 0.45 for 45%)
    """
    return revenue_growth + profit_margin


def ev_to_equity_bridge(
    enterprise_value: float,
    net_debt: float,
    diluted_shares: float
) -> dict:
    """
    Bridge from Enterprise Value to Equity Value per Share.

    Common final step in DCF and Comps analysis.

    Args:
        enterprise_value: Enterprise Value
        net_debt: Net Debt (debt - cash)
        diluted_shares: Fully diluted share count

    Returns:
        Dictionary with equity value and per-share value
    """
    equity_value = enterprise_value - net_debt
    per_share = equity_value / diluted_shares if diluted_shares > 0 else 0

    return {
        "enterprise_value": enterprise_value,
        "net_debt": net_debt,
        "equity_value": equity_value,
        "diluted_shares": diluted_shares,
        "equity_value_per_share": per_share
    }


def filter_valid_values(values: list[Optional[float]]) -> list[float]:
    """
    Filter out None values and return valid floats.

    Args:
        values: List of optional float values

    Returns:
        List containing only non-None values
    """
    return [v for v in values if v is not None]


def calculate_statistics(values: list[float]) -> dict:
    """
    Calculate descriptive statistics for a list of values.

    Args:
        values: List of numeric values

    Returns:
        Dictionary with mean, median, min, max, p25, p75, and count
    """
    if not values:
        return {
            "mean": None,
            "median": None,
            "min": None,
            "max": None,
            "p25": None,
            "p75": None,
            "count": 0
        }

    arr = np.array(values)
    return {
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "p25": float(np.percentile(arr, 25)),
        "p75": float(np.percentile(arr, 75)),
        "count": len(values)
    }
