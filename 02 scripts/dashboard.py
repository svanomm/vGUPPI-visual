"""Interactive vGUPPI dashboard built with Streamlit.

Launch with:
    uv run streamlit run "02 scripts/dashboard.py"
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Ensure the scripts folder is importable
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from vguppi import (  # noqa: E402
    PARAM_META,
    PARAM_NAMES,
    VGUPPI_DESCRIPTIONS,
    VGUPPI_NAMES,
    VGUPPIInputs,
    compute_heatmap,
    compute_intermediates,
    compute_vguppis,
)

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="vGUPPI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS for a cleaner look
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Metric cards — force readable text on both light and dark themes */
    div[data-testid="stMetric"] {
        background: #f8f9fb;
        border: 1px solid #e0e3e8;
        border-radius: 10px;
        padding: 12px 16px;
    }
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] label p {
        font-size: 0.85rem;
        color: #555 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1a1a2e !important;
    }
    /* Sidebar grouping */
    .sidebar-group-header {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #888;
        margin-top: 1rem;
        margin-bottom: 0.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================================
# Sidebar — input controls
# ============================================================================
st.sidebar.title("⚙️ Input Parameters")
st.sidebar.markdown("Adjust the values below. The dashboard updates automatically.")


def _reset_defaults() -> None:
    """Reset all input parameters to their default values."""
    for p_name in PARAM_NAMES:
        default = PARAM_META[p_name]["default"]
        st.session_state[f"{p_name}_slider"] = default
        st.session_state[f"{p_name}_number"] = default


st.sidebar.button(
    "🔄 Reset to defaults", on_click=_reset_defaults, use_container_width=True
)

# Group parameters by their 'group' key in PARAM_META
groups: dict[str, list[str]] = {}
for name in PARAM_NAMES:
    g = PARAM_META[name]["group"]
    groups.setdefault(g, []).append(name)

GROUP_ORDER = ["Prices", "Margins", "Diversion Ratios", "Pass-through", "Elasticity"]


def _sync_slider(param: str) -> None:
    """Copy the number-input value into the slider's session-state key."""
    st.session_state[f"{param}_slider"] = st.session_state[f"{param}_number"]


def _sync_number(param: str) -> None:
    """Copy the slider value into the number-input's session-state key."""
    st.session_state[f"{param}_number"] = st.session_state[f"{param}_slider"]


param_values: dict[str, float] = {}

for group_name in GROUP_ORDER:
    params_in_group = groups.get(group_name, [])
    if not params_in_group:
        continue
    st.sidebar.markdown(
        f'<p class="sidebar-group-header">{group_name}</p>',
        unsafe_allow_html=True,
    )
    for p in params_in_group:
        meta = PARAM_META[p]

        # Initialise session state on first run
        if f"{p}_slider" not in st.session_state:
            st.session_state[f"{p}_slider"] = meta["default"]
        if f"{p}_number" not in st.session_state:
            st.session_state[f"{p}_number"] = meta["default"]

        col_s, col_n = st.sidebar.columns([3, 1])
        with col_s:
            st.slider(
                meta["label"],
                min_value=meta["min"],
                max_value=meta["max"],
                step=meta["step"],
                key=f"{p}_slider",
                on_change=_sync_number,
                args=(p,),
                label_visibility="collapsed",
            )
        with col_n:
            st.number_input(
                meta["label"],
                min_value=meta["min"],
                max_value=meta["max"],
                step=meta["step"],
                key=f"{p}_number",
                on_change=_sync_slider,
                args=(p,),
                label_visibility="collapsed",
            )
        # Show the label above the controls
        st.sidebar.caption(meta["label"])

        param_values[p] = st.session_state[f"{p}_slider"]

# Build the inputs dataclass from current slider values
inputs = VGUPPIInputs(**param_values)

# ============================================================================
# Main panel — title & description
# ============================================================================
st.title("📊 vGUPPI Dashboard")
st.markdown(
    "Vertical Gross Upward Pricing Pressure Index — an interactive tool "
    "for analysing the competitive effects of vertical mergers."
)
st.title("Introduction")
st.markdown("""
    vGUPPI stands for vertical Gross Upward Pricing Pressure Index. A positive value indicates that a merged entity is incentivized to raise prices post-merger, while a negative value suggests a potential price decrease. The vGUPPI models used here define 3 firms: an upstream supplier (U), a downstream partner (D) that purchases from U, and a downstream rival (R) that also purchases from U. U and D merge, and we want to understand how this affects the merged entity's incentives to raise prices.
            
    Moresi and Salop define 5 different vGUPPI metrics in their paper:

    - **vGUPPI_U**: The incentive for the upstream supplier to raise its price after the merger.
    - **vGUPPI_R**: The incentive for downstream rivals to raise their prices after the merger.
    - **vGUPPI_D1**: The incentive for the merged downstream partner to raise prices.
    - **vGUPPI_D2**: The incentive for the merged downstream partner to raise prices, allowing for elimination of double marginalization (EDM) effects.
    - **vGUPPI_D3**: The incentive for the merged downstream partner to raise prices, allowing for EDM effects and input substitution.
            
    In general, $vGUPPI_{D1} > vGUPPI_{D2} > vGUPPI_{D3}$, because successive adjustments introduce efficiencies (EDM) or competitive responses to price increases (input substitution) that reduce the merged entity's incentive to raise prices.
    """)

# ============================================================================
# Results — intermediate values + vGUPPI outputs
# ============================================================================
st.header("Results")

intermediates = compute_intermediates(inputs)
vguppis = compute_vguppis(inputs)

# Intermediates row
st.subheader("Intermediate Values")
int_cols = st.columns(3)
for i, (k, v) in enumerate(intermediates.items()):
    int_cols[i].metric(label=k, value=f"{v:.4f}")

# vGUPPI row
st.subheader("vGUPPI Values")
vg_cols = st.columns(5)
for i, name in enumerate(VGUPPI_NAMES):
    vg_cols[i].metric(
        label=name,
        value=f"{vguppis[name] * 100:.2f}%",
        help=VGUPPI_DESCRIPTIONS[name],
    )

# ============================================================================
# Heatmap section
# ============================================================================
st.header("Heatmap Explorer")
st.markdown(
    "Choose two input parameters for the axes. All other inputs are held at "
    "their current slider values. Each heatmap shows one vGUPPI measure. "
    "The **✕** marker shows the current parameter values."
)

hm_col1, hm_col2, hm_col3 = st.columns([2, 2, 1])
with hm_col1:
    x_param = st.selectbox(
        "X-axis parameter",
        options=PARAM_NAMES,
        format_func=lambda p: PARAM_META[p]["label"],
        index=PARAM_NAMES.index("dr_RD"),
    )
with hm_col2:
    # Default y to a different param than x
    default_y = "m_D" if x_param != "m_D" else "m_R"
    y_param = st.selectbox(
        "Y-axis parameter",
        options=PARAM_NAMES,
        format_func=lambda p: PARAM_META[p]["label"],
        index=PARAM_NAMES.index(default_y),
    )
with hm_col3:
    resolution = st.slider(
        "Grid resolution", min_value=20, max_value=100, value=50, step=10
    )

if x_param == y_param:
    st.warning("Please choose two **different** parameters for the axes.")
else:
    # Current crosshair position
    x_current = param_values[x_param]
    y_current = param_values[y_param]

    # Determine a nice colour scale diverging around 0
    color_scale = "RdBu_r"

    # Compute all heatmaps first to determine global min/max for consistent scaling
    heatmap_data = {}
    z_global_min = float("inf")
    z_global_max = float("-inf")

    for vg_name in VGUPPI_NAMES:
        x_vals, y_vals, z_grid = compute_heatmap(
            inputs, x_param, y_param, vg_name, resolution=resolution
        )
        heatmap_data[vg_name] = (x_vals, y_vals, z_grid)
        z_global_min = min(z_global_min, z_grid.min())
        z_global_max = max(z_global_max, z_grid.max())

    # Use symmetric range around 0 for consistent red (negative) / blue (positive) coloring
    z_abs_max = max(abs(z_global_min), abs(z_global_max))
    zmin = -z_abs_max
    zmax = z_abs_max

    # Render heatmaps in a 2-then-3 grid (or 3+2)
    row1_cols = st.columns(3)
    row2_cols = st.columns(3)
    all_slots = row1_cols + row2_cols  # 6 slots, use first 5

    for idx, vg_name in enumerate(VGUPPI_NAMES):
        x_vals, y_vals, z_grid = heatmap_data[vg_name]

        fig = go.Figure()

        # Heatmap trace with fixed color scale
        fig.add_trace(
            go.Heatmap(
                x=np.round(x_vals, 4),
                y=np.round(y_vals, 4),
                z=z_grid * 100,
                colorscale=color_scale,
                zmin=zmin * 100,
                zmax=zmax * 100,
                zmid=0,
                colorbar=dict(title=dict(text=vg_name, side="right")),
                hovertemplate=(
                    f"{PARAM_META[x_param]['label']}: %{{x:.3f}}<br>"
                    f"{PARAM_META[y_param]['label']}: %{{y:.3f}}<br>"
                    f"{vg_name}: %{{z:.2f}}%<extra></extra>"
                ),
            )
        )

        # Crosshair marker at current slider values
        fig.add_trace(
            go.Scatter(
                x=[x_current],
                y=[y_current],
                mode="markers",
                marker=dict(
                    symbol="x",
                    size=14,
                    color="black",
                    line=dict(width=2),
                ),
                name="Current",
                showlegend=False,
                hovertemplate=(
                    f"Current: ({x_current:.3f}, {y_current:.3f})<br>"
                    f"{vg_name}: {vguppis[vg_name] * 100:.2f}%<extra></extra>"
                ),
            )
        )

        fig.update_layout(
            title=dict(text=f"{vg_name}", font=dict(size=14)),
            xaxis_title=PARAM_META[x_param]["label"],
            yaxis_title=PARAM_META[y_param]["label"],
            height=400,
            margin=dict(l=60, r=20, t=40, b=60),
        )

        with all_slots[idx]:
            st.plotly_chart(fig, use_container_width=True, key=f"heatmap_{vg_name}")


# Intuition
st.header("Intuition")
st.markdown(
    """
    We present intuition for some of the more complex intermediate values.

    **Diversion ratios:**

    $dr_{RD}$: Sales gained by the downstream supplier divided by revenue lost by rival increasing prices. When R raises prices, customers purchase less from R and more from D.
    
    $dr_{DU}$: Sales gained by the upstream supplier divided by revenue lost by downstream partner increasing prices. When D raises prices, customers purchase less from D and more from R, but R has to purchase more input from U.
    
    $dr_{UD}$: Sales gained by the downstream partner divided by revenue lost by upstream supplier increasing prices. U raises the price it charges to R. Customers purchase less from R and more from D.

    **Elasticities:**

    $e_p$: % change in price of downstream rival divided by % change in price of upstream supplier. When input prices increase, how much do rivals pass through in their product?

    $e_{sd}=e_{sr}$: When input prices increase, how much do downstream companies shift their purchases to other upstream suppliers?
    """
)

# ============================================================================
# Formulas
# ============================================================================
st.header("Formulas")

st.latex(
    r"vGUPPI_U = \frac{dr_{RD}\cdot m_D \cdot p_D / w_R}{1 + (m_R \cdot e_{sr} / e_p)}"
)
st.latex(
    r"vGUPPI_R = vGUPPI_U \cdot ptr_U \cdot \frac{w_R}{p_R} \cdot (1 - (vGUPPI_U \cdot ptr_U \cdot e_{sr}))"
)
st.latex(r"vGUPPI_{D1} = \frac{dr_{DU}\cdot m_U\cdot w_U}{p_D}")
st.latex(r"vGUPPI_{D2} = vGUPPI_1 - \frac{m_{UD}\cdot w_D}{p_D}")
st.latex(r"E_P = \frac{ptr_R\cdot w_R}{p_R}")
st.latex(r"E_{SD} = \frac{1}{m_U} - (e\cdot e_p)")
st.latex(r"vGUPPI_{D3} = vGUPPI_2 - \frac{e_{sd} \cdot m_{UD}^2 \cdot w_D}{p_D}")

# ============================================================================
# Footer
# ============================================================================
st.markdown("---")
st.caption(
    "vGUPPI formulae based on Moresi & Salop (2013). Built with Streamlit and Plotly."
)
