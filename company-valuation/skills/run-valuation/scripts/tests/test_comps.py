"""Tests for Comparable Company Analysis."""

import pytest
from company_valuation.comps import PeerCompany, ComparableAnalysis


class TestPeerCompany:
    """Tests for PeerCompany calculations."""

    def test_market_cap(self):
        """Test market cap calculation."""
        peer = PeerCompany(
            ticker="AAPL",
            name="Apple Inc",
            price=150.0,
            shares_outstanding=16000,  # millions
            net_debt=-50000  # net cash
        )
        # Market Cap = 150 × 16000 = 2,400,000
        assert peer.market_cap == pytest.approx(2400000, rel=1e-6)

    def test_enterprise_value(self):
        """Test enterprise value calculation."""
        peer = PeerCompany(
            ticker="MSFT",
            name="Microsoft",
            price=300.0,
            shares_outstanding=7500,
            net_debt=20000
        )
        # EV = Market Cap + Net Debt = 2,250,000 + 20,000 = 2,270,000
        assert peer.enterprise_value == pytest.approx(2270000, rel=1e-6)

    def test_ltm_calculation(self):
        """Test LTM metric calculation: FY + Current YTD - Prior YTD."""
        peer = PeerCompany(
            ticker="TEST",
            name="Test Co",
            price=100.0,
            shares_outstanding=100,
            net_debt=500,
            fy_revenue=1000,
            ytd_revenue=300,
            prior_ytd_revenue=250,
            fy_ebitda=200,
            ytd_ebitda=60,
            prior_ytd_ebitda=50
        )
        # LTM Revenue = 1000 + 300 - 250 = 1050
        assert peer.get_ltm_revenue() == pytest.approx(1050, rel=1e-6)
        # LTM EBITDA = 200 + 60 - 50 = 210
        assert peer.get_ltm_ebitda() == pytest.approx(210, rel=1e-6)

    def test_pre_calculated_ltm(self):
        """Test pre-calculated LTM values take precedence."""
        peer = PeerCompany(
            ticker="TEST",
            name="Test Co",
            price=100.0,
            shares_outstanding=100,
            net_debt=500,
            fy_revenue=1000,
            ytd_revenue=300,
            prior_ytd_revenue=250,
            ltm_revenue=1100  # Pre-calculated
        )
        # Should use pre-calculated value
        assert peer.get_ltm_revenue() == 1100

    def test_ev_ebitda_multiple(self):
        """Test EV/EBITDA multiple calculation."""
        peer = PeerCompany(
            ticker="TEST",
            name="Test Co",
            price=100.0,
            shares_outstanding=100,
            net_debt=1000,
            ltm_ebitda=1000
        )
        # EV = 100 × 100 + 1000 = 11,000
        # EV/EBITDA = 11,000 / 1,000 = 11.0x
        assert peer.ev_ebitda() == pytest.approx(11.0, rel=1e-6)

    def test_ev_revenue_multiple(self):
        """Test EV/Revenue multiple calculation."""
        peer = PeerCompany(
            ticker="TEST",
            name="Test Co",
            price=50.0,
            shares_outstanding=200,
            net_debt=2000,
            ltm_revenue=6000
        )
        # EV = 50 × 200 + 2000 = 12,000
        # EV/Revenue = 12,000 / 6,000 = 2.0x
        assert peer.ev_revenue() == pytest.approx(2.0, rel=1e-6)

    def test_pe_ratio(self):
        """Test P/E ratio calculation."""
        peer = PeerCompany(
            ticker="TEST",
            name="Test Co",
            price=100.0,
            shares_outstanding=100,
            net_debt=500,
            ltm_net_income=500
        )
        # EPS = 500 / 100 = 5.0
        # P/E = 100 / 5.0 = 20.0x
        assert peer.pe_ratio() == pytest.approx(20.0, rel=1e-6)

    def test_price_to_book(self):
        """Test P/BV ratio calculation."""
        peer = PeerCompany(
            ticker="TEST",
            name="Test Co",
            price=80.0,
            shares_outstanding=100,
            net_debt=500,
            book_value=4000
        )
        # Market Cap = 80 × 100 = 8,000
        # P/BV = 8,000 / 4,000 = 2.0x
        assert peer.price_to_book() == pytest.approx(2.0, rel=1e-6)

    def test_ntm_multiples(self):
        """Test forward (NTM) multiple calculations."""
        peer = PeerCompany(
            ticker="TEST",
            name="Test Co",
            price=100.0,
            shares_outstanding=100,
            net_debt=1000,
            ltm_ebitda=800,
            ntm_ebitda=1000
        )
        # LTM EV/EBITDA = 11,000 / 800 = 13.75x
        # NTM EV/EBITDA = 11,000 / 1,000 = 11.0x
        assert peer.ev_ebitda(use_ntm=False) == pytest.approx(13.75, rel=1e-6)
        assert peer.ev_ebitda(use_ntm=True) == pytest.approx(11.0, rel=1e-6)


class TestComparableAnalysis:
    """Tests for ComparableAnalysis peer group analysis."""

    @pytest.fixture
    def sample_peers(self):
        """Create sample peer group."""
        return [
            PeerCompany(ticker="A", name="Company A", price=100, shares_outstanding=100,
                       net_debt=500, ltm_ebitda=500, ltm_revenue=2000, ltm_net_income=200),
            PeerCompany(ticker="B", name="Company B", price=80, shares_outstanding=150,
                       net_debt=800, ltm_ebitda=600, ltm_revenue=2500, ltm_net_income=250),
            PeerCompany(ticker="C", name="Company C", price=120, shares_outstanding=80,
                       net_debt=300, ltm_ebitda=450, ltm_revenue=1800, ltm_net_income=180),
            PeerCompany(ticker="D", name="Company D", price=90, shares_outstanding=120,
                       net_debt=600, ltm_ebitda=550, ltm_revenue=2200, ltm_net_income=220),
        ]

    def test_ev_ebitda_statistics(self, sample_peers):
        """Test EV/EBITDA statistics calculation."""
        analysis = ComparableAnalysis(sample_peers)
        result = analysis.ev_ebitda_multiples()

        # Should have multiples for each peer
        assert len(result["multiples"]) == 4

        # Statistics should be calculated
        stats = result["statistics"]
        assert stats["mean"] is not None
        assert stats["median"] is not None
        assert stats["min"] < stats["max"]
        assert stats["p25"] <= stats["median"] <= stats["p75"]

    def test_peer_multiples_calculated_correctly(self, sample_peers):
        """Test individual peer multiples are correct."""
        analysis = ComparableAnalysis(sample_peers)
        result = analysis.ev_ebitda_multiples()

        # Company A: EV = 10,000 + 500 = 10,500; EV/EBITDA = 21.0x
        assert result["multiples"]["A"] == pytest.approx(21.0, rel=1e-6)

        # Company B: EV = 12,000 + 800 = 12,800; EV/EBITDA = 21.33x
        assert result["multiples"]["B"] == pytest.approx(12800/600, rel=1e-6)

    def test_implied_value(self, sample_peers):
        """Test implied value calculation from peer multiples."""
        analysis = ComparableAnalysis(sample_peers)

        # Implied value for company with EBITDA = 700
        result = analysis.implied_value(
            target_metric=700,
            multiple_type="ev_ebitda",
            use_median=True
        )

        assert result["implied_value"] is not None
        assert result["low"] is not None
        assert result["high"] is not None
        assert result["low"] < result["implied_value"] < result["high"]

    def test_summary(self, sample_peers):
        """Test summary includes all multiple types."""
        analysis = ComparableAnalysis(sample_peers)
        summary = analysis.summary()

        assert "ev_ebitda" in summary
        assert "ev_ebit" in summary
        assert "ev_revenue" in summary
        assert "pe" in summary
        assert "price_to_book" in summary

    def test_empty_peer_group(self):
        """Test handling of empty peer group."""
        analysis = ComparableAnalysis([])
        result = analysis.ev_ebitda_multiples()

        assert len(result["multiples"]) == 0
        assert result["statistics"]["mean"] is None

    def test_pe_ratios(self, sample_peers):
        """Test P/E ratio calculation across peers."""
        analysis = ComparableAnalysis(sample_peers)
        result = analysis.pe_ratios()

        # All peers should have P/E calculated
        assert all(v is not None for v in result["multiples"].values())

        # Company A: EPS = 200/100 = 2.0; P/E = 100/2.0 = 50x
        assert result["multiples"]["A"] == pytest.approx(50.0, rel=1e-6)
