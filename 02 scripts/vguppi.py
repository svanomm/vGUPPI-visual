import marimo

__generated_with = "0.19.10"
app = marimo.App()


@app.cell
def _(mo):
    mo.md(r"""
    This set of formulae calculate a variety of vertical gross upward pricing prices index (VGUPPI) values.

    Notation:

    U, D, and R are companies that make things.

    U: Upstream supplier that makes an input to D and R's product

    D: Downstream producer

    R: Downstream rival

    U and D form a single entity by vertical merger.
    """)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    # Interactive input parameters
    sliders = {
        "p_D": mo.ui.slider(1, 100, value=20, step=1, label="D's product price (p_D)"),
        "p_R": mo.ui.slider(1, 100, value=20, step=1, label="R's product price (p_R)"),
        "w_D": mo.ui.slider(1, 50, value=10, step=1, label="U's price selling to D (w_D)"),
        "w_R": mo.ui.slider(1, 50, value=10, step=1, label="U's price selling to R (w_R)"),
        "w_U": mo.ui.slider(1, 50, value=10, step=1, label="U's average price to rivals (w_U)"),
        "m_D": mo.ui.slider(0, 1, value=0.5, step=0.01, label="D's profit margin (m_D)"),
        "m_R": mo.ui.slider(0, 1, value=0.5, step=0.01, label="R's profit margin (m_R)"),
        "m_U": mo.ui.slider(0, 1, value=0.5, step=0.01, label="U's profit margin to rivals (m_U)"),
        "m_UD": mo.ui.slider(0, 1, value=0.5, step=0.01, label="U's profit margin to D (m_UD)"),
        "dr_RD": mo.ui.slider(0, 1, value=0.4, step=0.01, label="Diversion from R to D (dr_RD)"),
        "dr_DU": mo.ui.slider(0, 1, value=0.25, step=0.01, label="Sales gained by U from D increase (dr_DU)"),
        "dr_UD": mo.ui.slider(0, 1, value=0.4, step=0.01, label="Diversion from U to D (dr_UD)"),
        "ptr_U": mo.ui.slider(0, 1, value=0.5, step=0.01, label="U cost passthrough to R (ptr_U)"),
        "ptr_R": mo.ui.slider(0, 1, value=0.5, step=0.01, label="R cost passthrough (ptr_R)"),
        "e": mo.ui.slider(0, 5, value=1, step=0.1, label="Downstream demand elasticity (e)"),
    }

    mo.ui.dictionary(sliders)
    return (sliders,)


@app.cell
def _(sliders):
    # Extract values from sliders
    p_D = sliders["p_D"].value
    p_R = sliders["p_R"].value
    w_D = sliders["w_D"].value
    w_R = sliders["w_R"].value
    w_U = sliders["w_U"].value
    m_D = sliders["m_D"].value
    m_R = sliders["m_R"].value
    m_U = sliders["m_U"].value
    m_UD = sliders["m_UD"].value
    dr_RD = sliders["dr_RD"].value
    dr_DU = sliders["dr_DU"].value
    dr_UD = sliders["dr_UD"].value
    ptr_U = sliders["ptr_U"].value
    ptr_R = sliders["ptr_R"].value
    e = sliders["e"].value
    return (
        dr_DU,
        dr_RD,
        e,
        m_D,
        m_R,
        m_U,
        m_UD,
        p_D,
        p_R,
        ptr_R,
        ptr_U,
        w_D,
        w_R,
        w_U,
    )


@app.cell
def _(
    dr_DU,
    dr_RD,
    e,
    m_D,
    m_R,
    m_U,
    m_UD,
    p_D,
    p_R,
    ptr_R,
    ptr_U,
    w_D,
    w_R,
    w_U,
):
    # Calculate elasticity variables
    e_p = ptr_R * w_R / p_R
    e_sd = (1 / m_U) - (e * e_p)
    e_sr = (1 / m_U) - (e * e_p)

    # Calculate VGUPPI values
    vguppi_U = (dr_RD * m_D * p_D / w_R) / (1 + (m_R * e_sr / e_p))
    vguppi_R = vguppi_U * ptr_U * w_R / p_R * (1 - (vguppi_U * ptr_U * e_sr))

    vguppi_D1 = (
        dr_DU * m_U * w_U / p_D
    )  # Assumes no double margin elimination (EDM) or input substitution
    vguppi_D2 = vguppi_D1 - (m_UD * w_D / p_D)  # Assumes EDM but no input substitution
    vguppi_D3 = vguppi_D2 - (
        e_sd * (m_UD**2) * w_D / p_D
    )  # Assumes EDM and input substitution
    return e_p, e_sd, e_sr, vguppi_D1, vguppi_D2, vguppi_D3, vguppi_R, vguppi_U


@app.cell
def _(dr_RD, e_p, e_sr, m_D, m_R, p_D, w_R):
    print(dr_RD * m_D * p_D / w_R)
    print((1 + (m_R * e_sr / e_p)))
    return


@app.cell
def _(e_p, e_sd, e_sr, vguppi_D1, vguppi_D2, vguppi_D3, vguppi_R, vguppi_U):
    # Test: Print calculated values
    print("=== VGUPPI Calculations ===\n")
    print("Elasticity variables:")
    print(f"  e_p:  {e_p:.6f}")
    print(f"  e_sd: {e_sd:.6f}")
    print(f"  e_sr: {e_sr:.6f}\n")

    print("VGUPPI - Upstream (U):")
    print(f"  vguppi_U: {vguppi_U:.6f}\n")

    print("VGUPPI - Rival (R):")
    print(f"  vguppi_R: {vguppi_R:.6f}\n")

    print("VGUPPI - Downstream (D):")
    print(f"  vguppi_D1 (no EDM, no substitution): {vguppi_D1:.6f}")
    print(f"  vguppi_D2 (with EDM, no substitution): {vguppi_D2:.6f}")
    print(f"  vguppi_D3 (with EDM and substitution): {vguppi_D3:.6f}")
    return


if __name__ == "__main__":
    app.run()
