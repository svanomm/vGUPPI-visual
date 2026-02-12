"""Unit tests for the vGUPPI formulae module."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure the scripts folder is importable
_SCRIPT_DIR = Path(__file__).resolve().parent.parent / "02 scripts"
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from vguppi import (  # noqa: E402
    PARAM_META,
    PARAM_NAMES,
    VGUPPI_NAMES,
    VGUPPIInputs,
    compute_heatmap,
    compute_intermediates,
    compute_vguppis,
    get_param_fields,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _default_inputs() -> VGUPPIInputs:
    """Return a VGUPPIInputs with all default values."""
    return VGUPPIInputs()


# ---------------------------------------------------------------------------
# Test intermediates
# ---------------------------------------------------------------------------


class TestIntermediates:
    """Tests for compute_intermediates."""

    def test_defaults(self) -> None:
        """Intermediates with default inputs match hand-calculated values."""
        inter = compute_intermediates(_default_inputs())
        # e_p = ptr_R * w_R / p_R = 0.5 * 10 / 20 = 0.25
        assert inter["e_p"] == pytest.approx(0.25)
        # e_sd = e_sr = (1/m_U) - (e * e_p) = 2.0 - 1*0.25 = 1.75
        assert inter["e_sd"] == pytest.approx(1.75)
        assert inter["e_sr"] == pytest.approx(1.75)


# ---------------------------------------------------------------------------
# Test vGUPPI values
# ---------------------------------------------------------------------------


class TestVGUPPIs:
    """Tests for compute_vguppis with default parameters."""

    def test_all_keys_present(self) -> None:
        """All five vGUPPI keys are returned."""
        result = compute_vguppis(_default_inputs())
        for name in VGUPPI_NAMES:
            assert name in result

    def test_vguppi_u(self) -> None:
        """vGUPPI_U = (0.4*0.5*20/10) / (1 + 0.5*1.75/0.25) = 0.4 / 4.5."""
        result = compute_vguppis(_default_inputs())
        expected = 0.4 / 4.5  # ≈ 0.08889
        assert result["vGUPPI_U"] == pytest.approx(expected, rel=1e-6)

    def test_vguppi_r(self) -> None:
        """vGUPPI_R derived from vGUPPI_U."""
        result = compute_vguppis(_default_inputs())
        vu = result["vGUPPI_U"]
        e_sr = 1.75
        expected = vu * 0.5 * 10 / 20 * (1 - vu * 0.5 * e_sr)
        assert result["vGUPPI_R"] == pytest.approx(expected, rel=1e-6)

    def test_vguppi_d1(self) -> None:
        """vGUPPI_D1 = dr_DU * m_U * w_U / p_D = 0.25*0.5*10/20 = 0.0625."""
        result = compute_vguppis(_default_inputs())
        assert result["vGUPPI_D1"] == pytest.approx(0.0625, rel=1e-6)

    def test_vguppi_d2(self) -> None:
        """vGUPPI_D2 = vGUPPI_D1 - m_UD*w_D/p_D = 0.0625 - 0.25 = -0.1875."""
        result = compute_vguppis(_default_inputs())
        assert result["vGUPPI_D2"] == pytest.approx(0.0625 - 0.25, rel=1e-6)

    def test_vguppi_d3(self) -> None:
        """vGUPPI_D3 = vGUPPI_D2 - e_sd * m_UD^2 * w_D / p_D."""
        result = compute_vguppis(_default_inputs())
        d2 = 0.0625 - 0.25
        e_sd = 1.75
        expected = d2 - e_sd * (0.5**2) * 10 / 20
        assert result["vGUPPI_D3"] == pytest.approx(expected, rel=1e-6)

    def test_values_are_finite(self) -> None:
        """All outputs should be finite real numbers with defaults."""
        result = compute_vguppis(_default_inputs())
        for v in result.values():
            assert isinstance(v, float)
            assert v == v  # not NaN


# ---------------------------------------------------------------------------
# Test heatmap grid
# ---------------------------------------------------------------------------


class TestHeatmap:
    """Tests for compute_heatmap."""

    def test_grid_shape(self) -> None:
        """Output arrays have the correct dimensions."""
        x, y, z = compute_heatmap(
            _default_inputs(), "dr_RD", "m_D", "vGUPPI_U", resolution=10
        )
        assert len(x) == 10
        assert len(y) == 10
        assert z.shape == (10, 10)

    def test_center_matches_direct(self) -> None:
        """The grid point closest to defaults should match direct computation."""
        inputs = _default_inputs()
        res = 51  # odd so there's a center point
        x, y, z = compute_heatmap(inputs, "dr_RD", "m_D", "vGUPPI_U", resolution=res)
        # Find indices closest to defaults
        ix = int(abs(x - 0.4).argmin())
        iy = int(abs(y - 0.5).argmin())
        expected = compute_vguppis(inputs)["vGUPPI_U"]
        assert z[iy, ix] == pytest.approx(expected, rel=1e-2)


# ---------------------------------------------------------------------------
# Test metadata consistency
# ---------------------------------------------------------------------------


class TestMetadata:
    """Tests that metadata and dataclass stay in sync."""

    def test_param_names_match_fields(self) -> None:
        """PARAM_NAMES should match the fields of VGUPPIInputs."""
        assert set(PARAM_NAMES) == set(get_param_fields())

    def test_all_groups_assigned(self) -> None:
        """Every parameter has a non-empty group."""
        for name in PARAM_NAMES:
            assert PARAM_META[name]["group"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
