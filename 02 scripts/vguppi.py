import marimo

__generated_with = "0.10.9"
app = marimo.App()


@app.cell
def __():
    """
    This set of formulae calculate a variety of vertical gross upward pricing prices index (VGUPPI) values.

    Notation:
    U, D, and R are companies that make things.
    U: Upstream supplier that makes an input to D and R's product
    D: Downstream producer
    R: Downstream rival
    U and D form a single entity by vertical merger.
    """
    return None


@app.cell
def __():
    # Input parameters
    p_D = 20  # D's product price
    p_R = 20  # R's product price
    w_D = 10  # U's price selling to D
    w_R = 10  # U's price selling to R
    w_U = 10  # U's average price to rivals
    m_D = 0.5  # D's profit margin
    m_R = 0.5  # R's profit margin
    m_U = 0.5  # U's average profit margin on sales to rivals
    m_UD = 0.5  # U's profit margin on sales to D
    dr_RD = 0.4  # % of sales diverted to D from an R price increase
    dr_DU = 0.25  # % of sales gained by U from a D price increase
    dr_UD = 0.4  # % of sales diverted to D from a U price increase
    ptr_U = 0.5  # Passthrough of U cost increase to prices for R
    ptr_R = 0.5  # Passthrough of R cost increase to R's product
    e = 1  # Elasticity of downstream demand with respect to downstream price

    return (
        p_D,
        p_R,
        w_D,
        w_R,
        w_U,
        m_D,
        m_R,
        m_U,
        m_UD,
        dr_RD,
        dr_DU,
        dr_UD,
        ptr_U,
        ptr_R,
        e,
    )


@app.cell
def __(
    p_D, p_R, w_D, w_R, w_U, m_D, m_R, m_U, m_UD, dr_RD, dr_DU, dr_UD, ptr_U, ptr_R, e
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

    return e_p, e_sd, e_sr, vguppi_U, vguppi_R, vguppi_D1, vguppi_D2, vguppi_D3


@app.cell
def __(vguppi_U, vguppi_R, vguppi_D1, vguppi_D2, vguppi_D3, e_p, e_sd, e_sr):
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

    return None


if __name__ == "__main__":
    app.run()
