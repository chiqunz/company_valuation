"""Tests for Precedent Transaction Analysis."""

import pytest
from datetime import date
from company_valuation.precedent import Transaction, PrecedentAnalysis


class TestTransaction:
    """Tests for Transaction calculations."""

    def test_control_premium(self):
        """Test control premium calculation."""
        txn = Transaction(
            target_name="Target Co",
            acquirer_name="Acquirer Inc",
            announce_date=date(2024, 6, 15),
            deal_value=1500,
            equity_value=1200,
            pre_announcement_price=80.0,
            deal_price_per_share=100.0
        )
        # Control Premium = (100 - 80) / 80 = 25%
        assert txn.control_premium == pytest.approx(0.25, rel=1e-6)

    def test_ev_ebitda_multiple(self):
        """Test EV/EBITDA transaction multiple."""
        txn = Transaction(
            target_name="Target Co",
            acquirer_name="Acquirer Inc",
            announce_date=date(2024, 6, 15),
            deal_value=1000,
            equity_value=800,
            target_ltm_ebitda=100
        )
        # EV/EBITDA = 1000 / 100 = 10.0x
        assert txn.ev_ebitda == pytest.approx(10.0, rel=1e-6)

    def test_ev_revenue_multiple(self):
        """Test EV/Revenue transaction multiple."""
        txn = Transaction(
            target_name="Target Co",
            acquirer_name="Acquirer Inc",
            announce_date=date(2024, 6, 15),
            deal_value=500,
            equity_value=400,
            target_ltm_revenue=250
        )
        # EV/Revenue = 500 / 250 = 2.0x
        assert txn.ev_revenue == pytest.approx(2.0, rel=1e-6)

    def test_years_since(self):
        """Test years since announcement calculation."""
        txn = Transaction(
            target_name="Target Co",
            acquirer_name="Acquirer Inc",
            announce_date=date(2022, 1, 1),
            deal_value=500,
            equity_value=400
        )
        # ~3 years from Jan 2022 to Jan 2025
        years = txn.years_since(date(2025, 1, 1))
        assert 2.9 < years < 3.1

    def test_missing_metrics_return_none(self):
        """Test that missing metrics return None."""
        txn = Transaction(
            target_name="Target Co",
            acquirer_name="Acquirer Inc",
            announce_date=date(2024, 6, 15),
            deal_value=500,
            equity_value=400
            # No financial metrics
        )
        assert txn.ev_ebitda is None
        assert txn.ev_revenue is None
        assert txn.control_premium is None


class TestPrecedentAnalysis:
    """Tests for PrecedentAnalysis."""

    @pytest.fixture
    def sample_transactions(self):
        """Create sample transaction set."""
        return [
            Transaction(
                target_name="Target A", acquirer_name="Buyer X",
                announce_date=date(2024, 3, 1), deal_value=1000, equity_value=800,
                target_ltm_ebitda=100, target_ltm_revenue=500,
                pre_announcement_price=40, deal_price_per_share=50,
                deal_type="strategic", sector="Tech"
            ),
            Transaction(
                target_name="Target B", acquirer_name="PE Fund Y",
                announce_date=date(2023, 9, 15), deal_value=800, equity_value=600,
                target_ltm_ebitda=80, target_ltm_revenue=400,
                pre_announcement_price=30, deal_price_per_share=36,
                deal_type="financial", sector="Tech"
            ),
            Transaction(
                target_name="Target C", acquirer_name="Buyer Z",
                announce_date=date(2024, 1, 10), deal_value=1200, equity_value=950,
                target_ltm_ebitda=110, target_ltm_revenue=550,
                pre_announcement_price=45, deal_price_per_share=58,
                deal_type="strategic", sector="Tech"
            ),
            Transaction(
                target_name="Old Deal", acquirer_name="Old Buyer",
                announce_date=date(2020, 6, 1), deal_value=600, equity_value=500,
                target_ltm_ebitda=50, target_ltm_revenue=300,
                deal_type="strategic", sector="Tech"
            ),
        ]

    def test_ev_ebitda_statistics(self, sample_transactions):
        """Test EV/EBITDA multiple statistics."""
        analysis = PrecedentAnalysis(sample_transactions)
        result = analysis.ev_ebitda_multiples()

        # Should have multiples for all transactions
        assert len(result["multiples"]) == 4

        stats = result["statistics"]
        assert stats["count"] == 4
        assert stats["mean"] is not None
        assert stats["median"] is not None

    def test_control_premium_statistics(self, sample_transactions):
        """Test control premium statistics."""
        analysis = PrecedentAnalysis(sample_transactions)
        result = analysis.control_premium_statistics()

        # Only 3 transactions have control premium data
        assert result["count"] == 3

        # Target A: 25%, Target B: 20%, Target C: ~29%
        assert 0.20 < result["mean"] < 0.30
        assert 0.20 < result["median"] < 0.30

    def test_filter_by_recency(self, sample_transactions):
        """Test filtering by transaction recency."""
        analysis = PrecedentAnalysis(sample_transactions)

        # Filter to last 2 years from 2025
        recent = analysis.filter_by_recency(max_years=2.0, reference_date=date(2025, 1, 1))

        # Should exclude 2020 deal
        assert len(recent.transactions) == 3
        assert all(t.target_name != "Old Deal" for t in recent.transactions)

    def test_filter_by_deal_type(self, sample_transactions):
        """Test filtering by deal type (strategic vs financial)."""
        analysis = PrecedentAnalysis(sample_transactions)

        strategic = analysis.filter_by_deal_type("strategic")
        assert len(strategic.transactions) == 3

        financial = analysis.filter_by_deal_type("financial")
        assert len(financial.transactions) == 1

    def test_filter_by_size(self, sample_transactions):
        """Test filtering by deal size."""
        analysis = PrecedentAnalysis(sample_transactions)

        # Deals between 700 and 1100
        filtered = analysis.filter_by_size(min_value=700, max_value=1100)
        assert len(filtered.transactions) == 2

    def test_implied_value(self, sample_transactions):
        """Test implied value calculation."""
        analysis = PrecedentAnalysis(sample_transactions)

        result = analysis.implied_value(
            target_metric=120,  # EBITDA of 120
            multiple_type="ev_ebitda",
            use_median=True
        )

        assert result["implied_value"] is not None
        assert result["transaction_count"] == 4
        assert result["implied_value"] > 0

    def test_summary(self, sample_transactions):
        """Test summary includes all metrics."""
        analysis = PrecedentAnalysis(sample_transactions)
        summary = analysis.summary()

        assert "ev_ebitda" in summary
        assert "ev_ebit" in summary
        assert "ev_revenue" in summary
        assert "control_premium" in summary
        assert summary["transaction_count"] == 4

    def test_empty_after_filter(self, sample_transactions):
        """Test handling when filter results in no transactions."""
        analysis = PrecedentAnalysis(sample_transactions)

        # Filter to non-existent sector
        filtered = analysis.filter_by_sector("Healthcare")
        result = filtered.ev_ebitda_multiples()

        assert result["statistics"]["count"] == 0
        assert result["statistics"]["mean"] is None

    def test_chained_filters(self, sample_transactions):
        """Test chaining multiple filters."""
        analysis = PrecedentAnalysis(sample_transactions)

        result = (analysis
                 .filter_by_recency(max_years=3.0, reference_date=date(2025, 1, 1))
                 .filter_by_deal_type("strategic")
                 .filter_by_size(min_value=500))

        # Should get strategic deals from last 3 years above 500
        assert len(result.transactions) == 2
