"""
Company Valuation - Institutional-grade valuation models.

This package provides implementations of:
- DCF (Discounted Cash Flow)
- Comparable Company Analysis (Trading Comps)
- Precedent Transaction Analysis
- LBO (Leveraged Buyout)
- DDM (Dividend Discount Model)
- SOTP (Sum-of-the-Parts)
"""

from company_valuation.wacc import WACC, CostOfEquity, BetaCalculator
from company_valuation.dcf import DCFModel, UFCFProjection
from company_valuation.comps import ComparableAnalysis, PeerCompany
from company_valuation.precedent import PrecedentAnalysis, Transaction
from company_valuation.lbo import LBOModel, DebtTranche
from company_valuation.ddm import DDMModel
from company_valuation.sotp import SOTPModel, Segment
from company_valuation.sensitivity import SensitivityAnalysis
from company_valuation.utils import treasury_stock_method, diluted_shares

__version__ = "0.1.0"

__all__ = [
    "WACC",
    "CostOfEquity",
    "BetaCalculator",
    "DCFModel",
    "UFCFProjection",
    "ComparableAnalysis",
    "PeerCompany",
    "PrecedentAnalysis",
    "Transaction",
    "LBOModel",
    "DebtTranche",
    "DDMModel",
    "SOTPModel",
    "Segment",
    "SensitivityAnalysis",
    "treasury_stock_method",
    "diluted_shares",
]
