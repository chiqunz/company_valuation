"""
Example usage of the Company Valuation package.

This script demonstrates a complete valuation workflow including:
- DCF analysis
- Comparable company analysis
- LBO returns analysis
"""

from company_valuation import (
    WACC, CostOfEquity, BetaCalculator,
    DCFModel, UFCFProjection,
    ComparableAnalysis, PeerCompany,
    LBOModel,
    DDMModel,
    SensitivityAnalysis
)


def main():
    print("=" * 60)
    print("COMPANY VALUATION EXAMPLE")
    print("=" * 60)

    # ================================================================
    # STEP 1: WACC CALCULATION
    # ================================================================
    print("\n1. WACC CALCULATION")
    print("-" * 40)

    # Calculate cost of equity using CAPM
    cost_of_equity = CostOfEquity(
        risk_free_rate=0.045,      # 4.5% 10-year Treasury
        beta=1.15,                  # Company beta
        equity_risk_premium=0.05   # 5% ERP
    )
    print(f"Cost of Equity (CAPM): {cost_of_equity.calculate():.2%}")

    # Calculate WACC
    wacc = WACC(
        equity_value=10000,  # $10B market cap
        debt_value=3000,     # $3B debt
        cost_of_equity=cost_of_equity.calculate(),
        cost_of_debt=0.065,  # 6.5% cost of debt
        tax_rate=0.25
    )
    print(f"WACC: {wacc.calculate():.2%}")
    print(f"Equity Weight: {wacc.equity_weight:.1%}")
    print(f"Debt Weight: {wacc.debt_weight:.1%}")

    # ================================================================
    # STEP 2: DCF VALUATION
    # ================================================================
    print("\n2. DCF VALUATION")
    print("-" * 40)

    # Create 5-year projections
    projections = [
        UFCFProjection(year=1, revenue=5000, ebit=750, tax_rate=0.25,
                      depreciation_amortization=200, capex=250, delta_nwc=50),
        UFCFProjection(year=2, revenue=5500, ebit=850, tax_rate=0.25,
                      depreciation_amortization=220, capex=275, delta_nwc=50),
        UFCFProjection(year=3, revenue=6050, ebit=970, tax_rate=0.25,
                      depreciation_amortization=240, capex=300, delta_nwc=55),
        UFCFProjection(year=4, revenue=6655, ebit=1100, tax_rate=0.25,
                      depreciation_amortization=260, capex=330, delta_nwc=60),
        UFCFProjection(year=5, revenue=7320, ebit=1250, tax_rate=0.25,
                      depreciation_amortization=280, capex=365, delta_nwc=65),
    ]

    dcf = DCFModel(
        projections=projections,
        wacc=wacc.calculate(),
        terminal_growth=0.025,
        exit_multiple=10.0,
        net_debt=2500,
        shares_outstanding=500,
        mid_year_convention=True
    )

    # Value using perpetuity growth method
    result_perp = dcf.value_perpetuity_method()
    print("\nPerpetuity Growth Method:")
    print(f"  PV of Cash Flows: ${result_perp.pv_explicit_cashflows:,.0f}")
    print(f"  PV of Terminal Value: ${result_perp.pv_terminal_value:,.0f}")
    print(f"  Enterprise Value: ${result_perp.enterprise_value:,.0f}")
    print(f"  Equity Value: ${result_perp.equity_value:,.0f}")
    print(f"  Per Share: ${result_perp.equity_value_per_share:,.2f}")

    # Value using exit multiple method
    result_mult = dcf.value_exit_multiple_method()
    print("\nExit Multiple Method (10x EBITDA):")
    print(f"  Enterprise Value: ${result_mult.enterprise_value:,.0f}")
    print(f"  Per Share: ${result_mult.equity_value_per_share:,.2f}")
    print(f"  Implied Terminal Growth: {result_mult.implied_perpetual_growth:.2%}")

    # Terminal value percentage
    tv_pct = dcf.terminal_value_percentage("perpetuity")
    print(f"\nTerminal Value % of EV: {tv_pct:.1%}")

    # ================================================================
    # STEP 3: COMPARABLE COMPANY ANALYSIS
    # ================================================================
    print("\n3. COMPARABLE COMPANY ANALYSIS")
    print("-" * 40)

    peers = [
        PeerCompany(ticker="PEER1", name="Peer Company 1", price=85.0,
                   shares_outstanding=200, net_debt=800,
                   ltm_ebitda=900, ltm_revenue=4500),
        PeerCompany(ticker="PEER2", name="Peer Company 2", price=110.0,
                   shares_outstanding=150, net_debt=600,
                   ltm_ebitda=850, ltm_revenue=4200),
        PeerCompany(ticker="PEER3", name="Peer Company 3", price=95.0,
                   shares_outstanding=180, net_debt=700,
                   ltm_ebitda=880, ltm_revenue=4300),
        PeerCompany(ticker="PEER4", name="Peer Company 4", price=75.0,
                   shares_outstanding=250, net_debt=900,
                   ltm_ebitda=950, ltm_revenue=4800),
    ]

    comps = ComparableAnalysis(peers)
    ev_ebitda_data = comps.ev_ebitda_multiples()

    print("\nEV/EBITDA Multiples:")
    for ticker, mult in ev_ebitda_data["multiples"].items():
        if mult:
            print(f"  {ticker}: {mult:.1f}x")

    stats = ev_ebitda_data["statistics"]
    print(f"\nStatistics:")
    print(f"  Mean: {stats['mean']:.1f}x")
    print(f"  Median: {stats['median']:.1f}x")
    print(f"  Range: {stats['min']:.1f}x - {stats['max']:.1f}x")

    # Implied value for target company
    target_ebitda = 970  # Year 3 EBITDA
    implied = comps.implied_value(target_ebitda, "ev_ebitda", use_median=True)
    print(f"\nImplied EV for Target (EBITDA=${target_ebitda}):")
    print(f"  At Median Multiple: ${implied['implied_value']:,.0f}")
    print(f"  Range: ${implied['low']:,.0f} - ${implied['high']:,.0f}")

    # ================================================================
    # STEP 4: LBO ANALYSIS
    # ================================================================
    print("\n4. LBO ANALYSIS")
    print("-" * 40)

    lbo = LBOModel.simple_lbo(
        entry_ebitda=970,
        entry_multiple=10.0,
        leverage_turns=5.5,
        interest_rate=0.085,
        exit_multiple=10.0,
        hold_years=5,
        ebitda_growth=0.06,
        capex_pct=0.15,
        tax_rate=0.25
    )

    print(f"Entry:")
    print(f"  Purchase Price: ${lbo.purchase_price:,.0f}")
    print(f"  Initial Debt: ${lbo.total_initial_debt:,.0f}")
    print(f"  Sponsor Equity: ${lbo.initial_equity:,.0f}")

    lbo_result = lbo.run_model()
    print(f"\nReturns:")
    print(f"  MOIC: {lbo_result.moic:.2f}x")
    print(f"  IRR: {lbo_result.irr:.1%}")
    print(f"  Total Debt Paydown: ${lbo_result.total_debt_paydown:,.0f}")

    # ================================================================
    # STEP 5: SENSITIVITY ANALYSIS
    # ================================================================
    print("\n5. SENSITIVITY ANALYSIS")
    print("-" * 40)

    # DCF sensitivity: WACC vs Terminal Growth
    wacc_range = [0.08, 0.09, 0.10, 0.11, 0.12]
    growth_range = [0.02, 0.025, 0.03]

    print("\nDCF Sensitivity (Enterprise Value):")
    print("WACC \\ Growth    2.0%      2.5%      3.0%")
    print("-" * 45)

    for w in wacc_range:
        row = f"{w:.0%}          "
        for g in growth_range:
            dcf.wacc = w
            dcf.terminal_growth = g
            try:
                ev = dcf.value_perpetuity_method().enterprise_value
                row += f"${ev/1000:,.1f}B   "
            except ValueError:
                row += "   N/A    "
        print(row)

    # ================================================================
    # STEP 6: FOOTBALL FIELD SUMMARY
    # ================================================================
    print("\n6. VALUATION SUMMARY (Football Field)")
    print("-" * 40)

    # Reset DCF to base case
    dcf.wacc = wacc.calculate()
    dcf.terminal_growth = 0.025

    dcf_low = dcf.value_perpetuity_method().equity_value_per_share * 0.85
    dcf_mid = dcf.value_perpetuity_method().equity_value_per_share
    dcf_high = dcf.value_perpetuity_method().equity_value_per_share * 1.15

    comps_low = implied['low'] / 500 - 2500/500  # Approximate equity per share
    comps_mid = implied['implied_value'] / 500 - 2500/500
    comps_high = implied['high'] / 500 - 2500/500

    football = SensitivityAnalysis.create_football_field(
        dcf_range=(dcf_low, dcf_mid, dcf_high),
        comps_range=(comps_low, comps_mid, comps_high),
        fifty_two_week=(dcf_mid * 0.75, dcf_mid * 1.10),
        current_price=dcf_mid * 0.95
    )

    for bar in football.bars:
        print(f"\n{bar.method}:")
        print(f"  Range: ${bar.low:.2f} - ${bar.high:.2f}")
        print(f"  Midpoint: ${bar.mid:.2f}")

    overall = football.overall_range()
    print(f"\nOverall Valuation Range: ${overall[0]:.2f} - ${overall[1]:.2f}")

    print("\n" + "=" * 60)
    print("VALUATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
