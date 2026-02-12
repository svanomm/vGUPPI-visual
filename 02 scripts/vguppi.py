"""Vertical Gross Upward Pricing Pressure Index (vGUPPI) formulae.

This module provides pure functions to compute vGUPPI values — measures of
the incentive for anticompetitive pricing after a vertical merger.

Notation:
    U: Upstream supplier that makes an input used by D and R.
    D: Downstream producer (merges with U).
    R: Downstream rival.

The five vGUPPI measures are:
    vGUPPI_U  — Upstream pricing pressure on rival's input price.
    vGUPPI_R  — Rival's product-level pricing pressure.
    vGUPPI_D1 — Downstream pricing pressure (no EDM, no input substitution).
    vGUPPI_D2 — Downstream pricing pressure (with EDM, no input substitution).
    vGUPPI_D3 — Downstream pricing pressure (with EDM and input substitution).
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

import numpy as np
from numpy.typing import NDArray


# ---------------------------------------------------------------------------
# Input parameters
# ---------------------------------------------------------------------------
@dataclass
class VGUPPIInputs:
    """All input parameters for the vGUPPI calculations.

    Attributes:
        p_D: D's product price.
        p_R: R's product price.
        w_D: U's price selling to D.
        w_R: U's price selling to R.
        w_U: U's average price to rivals.
        m_D: D's profit margin (0–1).
        m_R: R's profit margin (0–1).
        m_U: U's average profit margin on sales to rivals (0–1).
        m_UD: U's profit margin on sales to D (0–1).
        dr_RD: Fraction of sales diverted to D from an R price increase (0–1).
        dr_DU: Fraction of sales gained by U from a D price increase (0–1).
        dr_UD: Fraction of sales diverted to D from a U price increase (0–1).
        ptr_U: Pass-through of U cost increase to prices for R (0–1).
        ptr_R: Pass-through of R cost increase to R's product (0–1).
        e: Elasticity of downstream demand w.r.t. downstream price.
    """

    p_D: float = 20.0
    p_R: float = 20.0
    w_D: float = 10.0
    w_R: float = 10.0
    w_U: float = 10.0
    m_D: float = 0.5
    m_R: float = 0.5
    m_U: float = 0.5
    m_UD: float = 0.5
    dr_RD: float = 0.4
    dr_DU: float = 0.25
    dr_UD: float = 0.4
    ptr_U: float = 0.5
    ptr_R: float = 0.5
    e: float = 1.0


# ---------------------------------------------------------------------------
# Metadata for slider / UI configuration
# ---------------------------------------------------------------------------

ParamMeta = dict[str, Any]

PARAM_META: dict[str, ParamMeta] = {
    # Prices
    "p_D": {
        "label": "D's product price (p_D)",
        "min": 10.0,
        "max": 50.0,
        "step": 1.0,
        "default": 20.0,
        "group": "Prices",
    },
    "p_R": {
        "label": "R's product price (p_R)",
        "min": 10.0,
        "max": 50.0,
        "step": 1.0,
        "default": 20.0,
        "group": "Prices",
    },
    "w_D": {
        "label": "U's price to D (w_D)",
        "min": 1.0,
        "max": 50.0,
        "step": 1.0,
        "default": 10.0,
        "group": "Prices",
    },
    "w_R": {
        "label": "U's price to R (w_R)",
        "min": 1.0,
        "max": 50.0,
        "step": 1.0,
        "default": 10.0,
        "group": "Prices",
    },
    "w_U": {
        "label": "U's avg price to rivals (w_U)",
        "min": 1.0,
        "max": 50.0,
        "step": 1.0,
        "default": 10.0,
        "group": "Prices",
    },
    # Margins
    "m_D": {
        "label": "D's profit margin (m_D)",
        "min": 0.0,
        "max": 1.0,
        "step": 0.05,
        "default": 0.5,
        "group": "Margins",
    },
    "m_R": {
        "label": "R's profit margin (m_R)",
        "min": 0.0,
        "max": 1.0,
        "step": 0.05,
        "default": 0.5,
        "group": "Margins",
    },
    "m_U": {
        "label": "U's avg margin to rivals (m_U)",
        "min": 0.0,
        "max": 1.0,
        "step": 0.05,
        "default": 0.5,
        "group": "Margins",
    },
    "m_UD": {
        "label": "U's margin on sales to D (m_UD)",
        "min": 0.0,
        "max": 1.0,
        "step": 0.05,
        "default": 0.5,
        "group": "Margins",
    },
    # Diversion ratios
    "dr_RD": {
        "label": "Diversion R→D (dr_RD)",
        "min": 0.0,
        "max": 1.0,
        "step": 0.05,
        "default": 0.4,
        "group": "Diversion Ratios",
    },
    "dr_DU": {
        "label": "Diversion D→U (dr_DU)",
        "min": 0.0,
        "max": 1.0,
        "step": 0.05,
        "default": 0.25,
        "group": "Diversion Ratios",
    },
    "dr_UD": {
        "label": "Diversion U→D (dr_UD)",
        "min": 0.0,
        "max": 1.0,
        "step": 0.05,
        "default": 0.4,
        "group": "Diversion Ratios",
    },
    # Pass-through rates
    "ptr_U": {
        "label": "Pass-through U→R (ptr_U)",
        "min": 0.0,
        "max": 1.0,
        "step": 0.05,
        "default": 0.5,
        "group": "Pass-through",
    },
    "ptr_R": {
        "label": "Pass-through R cost→price (ptr_R)",
        "min": 0.0,
        "max": 1.0,
        "step": 0.05,
        "default": 0.5,
        "group": "Pass-through",
    },
    # Elasticity
    "e": {
        "label": "Demand elasticity (ε)",
        "min": 0.1,
        "max": 5.0,
        "step": 0.05,
        "default": 1.0,
        "group": "Elasticity",
    },
}

PARAM_NAMES: list[str] = list(PARAM_META.keys())


def get_param_fields() -> list[str]:
    """Return the ordered list of parameter field names from VGUPPIInputs.

    Returns:
        List of field name strings.
    """
    return [f.name for f in fields(VGUPPIInputs)]


# ---------------------------------------------------------------------------
# Intermediate calculations
# ---------------------------------------------------------------------------


def compute_intermediates(inputs: VGUPPIInputs) -> dict[str, float]:
    """Compute intermediate elasticity values used by the vGUPPI formulae.

    Args:
        inputs: A VGUPPIInputs instance with all 15 parameters.

    Returns:
        Dictionary with keys ``e_p``, ``e_sd``, ``e_sr``.
    """
    e_p = inputs.ptr_R * inputs.w_R / inputs.p_R
    e_sd = (1.0 / inputs.m_U) - (inputs.e * e_p)
    e_sr = (1.0 / inputs.m_U) - (inputs.e * e_p)
    return {"e_p": e_p, "e_sd": e_sd, "e_sr": e_sr}


# ---------------------------------------------------------------------------
# vGUPPI formulae
# ---------------------------------------------------------------------------

VGUPPI_NAMES: list[str] = [
    "vGUPPI_U",
    "vGUPPI_R",
    "vGUPPI_D1",
    "vGUPPI_D2",
    "vGUPPI_D3",
]

VGUPPI_DESCRIPTIONS: dict[str, str] = {
    "vGUPPI_U": "Upstream pricing pressure",
    "vGUPPI_R": "Rival product-level pricing pressure",
    "vGUPPI_D1": "Downstream (no EDM, no input sub.)",
    "vGUPPI_D2": "Downstream (EDM, no input sub.)",
    "vGUPPI_D3": "Downstream (EDM + input sub.)",
}


def compute_vguppis(inputs: VGUPPIInputs) -> dict[str, float]:
    """Compute the five vGUPPI values.

    Args:
        inputs: A VGUPPIInputs instance with all 15 parameters.

    Returns:
        Dictionary mapping each vGUPPI name to its computed float value.
    """
    inter = compute_intermediates(inputs)
    e_p = inter["e_p"]
    e_sd = inter["e_sd"]
    e_sr = inter["e_sr"]

    # Upstream vGUPPI
    vguppi_u = (inputs.dr_RD * inputs.m_D * inputs.p_D / inputs.w_R) / (
        1.0 + (inputs.m_R * e_sr / e_p)
    )

    # Rival vGUPPI
    vguppi_r = (
        vguppi_u
        * inputs.ptr_U
        * inputs.w_R
        / inputs.p_R
        * (1.0 - (vguppi_u * inputs.ptr_U * e_sr))
    )

    # Downstream vGUPPIs
    vguppi_d1 = inputs.dr_DU * inputs.m_U * inputs.w_U / inputs.p_D
    vguppi_d2 = vguppi_d1 - (inputs.m_UD * inputs.w_D / inputs.p_D)
    vguppi_d3 = vguppi_d2 - (e_sd * (inputs.m_UD**2) * inputs.w_D / inputs.p_D)

    return {
        "vGUPPI_U": vguppi_u,
        "vGUPPI_R": vguppi_r,
        "vGUPPI_D1": vguppi_d1,
        "vGUPPI_D2": vguppi_d2,
        "vGUPPI_D3": vguppi_d3,
    }


# ---------------------------------------------------------------------------
# Heatmap grid computation
# ---------------------------------------------------------------------------


def compute_heatmap(
    inputs: VGUPPIInputs,
    x_param: str,
    y_param: str,
    vguppi_key: str,
    resolution: int = 50,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """Compute a 2-D grid of a single vGUPPI over two varying parameters.

    All other parameters are held at their current values in *inputs*.

    Args:
        inputs: Base parameter values.
        x_param: Name of the parameter to vary along the x-axis.
        y_param: Name of the parameter to vary along the y-axis.
        vguppi_key: Which vGUPPI to compute (e.g. ``"vGUPPI_U"``).
        resolution: Number of grid points per axis.

    Returns:
        Tuple of ``(x_vals, y_vals, z_grid)`` where *z_grid* has shape
        ``(resolution, resolution)`` with rows corresponding to *y_vals*
        and columns to *x_vals*.
    """
    x_meta = PARAM_META[x_param]
    y_meta = PARAM_META[y_param]

    x_vals = np.linspace(x_meta["min"], x_meta["max"], resolution)
    y_vals = np.linspace(y_meta["min"], y_meta["max"], resolution)

    z_grid = np.empty((resolution, resolution), dtype=np.float64)

    base_dict = {f.name: getattr(inputs, f.name) for f in fields(inputs)}

    for i, y_val in enumerate(y_vals):
        for j, x_val in enumerate(x_vals):
            params = base_dict.copy()
            params[x_param] = float(x_val)
            params[y_param] = float(y_val)
            result = compute_vguppis(VGUPPIInputs(**params))
            z_grid[i, j] = result[vguppi_key]

    return x_vals, y_vals, z_grid
