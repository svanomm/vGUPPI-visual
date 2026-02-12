## Python version
```python
""" 
This set of formulae calculate a variety of vertical gross upward pricing prices index (VGUPPI) values.

Notation:
U, D, and R are companies that make things.
U: Upstream supplier that makes an input to D and R's product
D: Downstream producer
R: Downstream rival
U and D form a single entity by vertical merger.
"""

p_D = 20     # D's product price
p_R = 20     # R's product price
w_D = 10     # U's price selling to D
w_R = 10     # U's price selling to R
w_U = 10     # U's average price to rivals
m_D = 0.5    # D's profit margin
m_R = 0.5    # R's profit margin
m_U = 0.5    # U's average profit margin on sales to rivals
m_UD = 0.5   # U's profit margin on sales to D
dr_RD = 0.4  # % of sales diverted to D from an R price increase
dr_DU = 0.25 # % of sales gained by U from a D price increase
dr_UD = 0.4  # % of sales diverted to D from a U price increase
ptr_U = 0.5  # Passthrough of U cost increase to prices for R
ptr_R = 0.5  # Passthrough of R cost increase to R's product 
e = 1        # Elasticity of downstream demand with respect to downstream price

e_p = ptr_R * w_R / p_R      # Elasticity of R price with respect to U price
e_sd = (1 / m_U) - (e * e_p) # Elasticity of U's share of D's input purchases with respect to U price
e_sr = (1 / m_U) - (e * e_p) # Elasticity of U's share of R's input purchases with respect to U price

vguppi_U = (dr_RD * m_D * p_D / w_R) / (1 + (m_R * e_sr / e_p))
vguppi_R = vguppi_U * ptr_U * w_R / p_R * (1 - (vguppi_U * ptr_U * e_sr))

vguppi_D1 = dr_DU * m_U * w_U / p_D # Assumes no double margin elimination (EDM) or input substitution
vguppi_D2 = vguppid1 - (m_UD * w_D / p_D) # Assumes EDM but no input substitution
vguppi_D3 = vguppid2 - (e_sd * (m_UD**2) * w_D / p_D) # Assumes EDM and input substitution
```
