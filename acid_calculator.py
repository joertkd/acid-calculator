import streamlit as st
import math

st.set_page_config(page_title="Glyphosate pH Adjustment Tool")
st.title("Glyphosate pH Adjustment Tool")

st.markdown("""
This tool calculates how much acid to add to a glyphosate mixture to reach a desired pH.

---  
""")

# Volume of glyphosate mixture
V_solution = st.number_input("Volume of glyphosate solution (L)", min_value=0.01, format="%.2f", value=40.0)

# Initial and target pH
initial_pH = st.number_input("Initial pH of solution", min_value=0.0, max_value=14.0, value=6.5)
target_pH = st.number_input("Target pH", min_value=0.0, max_value=14.0, value=2.90)

# Optional details
with st.expander("🔧 Advanced Options"):
    glyphosate_conc = st.number_input("Glyphosate concentration (g/L) (optional)", min_value=0.0, value=0.0)
    temperature = st.number_input("Temperature (°C) (optional)", min_value=0.0, value=25.0)
    buffer_toggle = st.checkbox("Account for buffering effect (resists pH change)?", value=False)
    acid_type = st.selectbox("Acid type", ["Monoprotic (1 H⁺)", "Diprotic (2 H⁺)", "Triprotic (3 H⁺)"])
    use_custom_pKa = st.checkbox("Manually enter pKa?", value=False)

# Preset acids
acids = {
    "Citric acid": {"pKa": 3.13, "MW": 192.12},
    "Formic acid": {"pKa": 3.75, "MW": 46.03},
    "Acetic acid": {"pKa": 4.76, "MW": 60.05},
    "Hydrochloric acid": {"pKa": -6.3, "MW": 36.46},
    "Sulfuric acid (1st proton)": {"pKa": -3.0, "MW": 98.08},
    "Nitric acid": {"pKa": -1.4, "MW": 63.01},
    "Phosphoric acid (1st proton)": {"pKa": 2.15, "MW": 98.00}
}

acid_choice = st.selectbox("Select an acid", list(acids.keys()))
acid_data = acids[acid_choice]
MW = acid_data["MW"]
pKa = acid_data["pKa"]

# Override pKa manually if desired
if use_custom_pKa:
    pKa = st.number_input("Manual pKa value", value=pKa)

# Concentration input toggle
conc_unit = st.selectbox("How will you enter acid concentration?", ["g/L", "mol/L"])

if conc_unit == "g/L":
    acid_conc_g_per_L = st.number_input(f"{acid_choice} concentration (g/L)", min_value=0.01, value=100.0, format="%.2f")
    acid_molarity = acid_conc_g_per_L / MW
else:
    acid_molarity = st.number_input(f"{acid_choice} molarity (mol/L)", min_value=0.001, value=1.0, format="%.3f")

# Adjust for buffering if selected
buffer_factor = 1.0
if buffer_toggle:
    buffer_factor = 1.5  # crude multiplier for resistance to pH change

# Adjust for acid type
proton_count = {"Monoprotic (1 H⁺)": 1, "Diprotic (2 H⁺)": 2, "Triprotic (3 H⁺)": 3}[acid_type]

# Core calculations
H_target = 10 ** (-target_pH)
initial_pH = st.number_input("Initial pH of glyphosate mixture", value=5.5)
H_initial = 10 ** (-initial_pH)
delta_H = (H_target - H_initial) * V_solution * buffer_factor  # mol of H+ needed

alpha = 1 / (1 + 10 ** (target_pH - pKa))  # fraction of acid dissociated
effective_molarity = acid_molarity * alpha * proton_count

# Output
st.markdown("---")

if delta_H < 0:
    st.warning("Target pH is higher than the initial pH — no acid is needed.")
elif effective_molarity <= 0:
    st.error("Effective molarity too low — acid won’t dissociate enough at that pH.")
else:
    volume_acid_L = delta_H / effective_molarity
    volume_acid_L = max(volume_acid_L, 0)

    st.subheader("Result:")
    st.write(f"To reduce the pH from **{initial_pH:.2f}** to **{target_pH:.2f}** in **{V_solution:.2f} L** of glyphosate mixture:")
    st.success(f"Add approximately **{volume_acid_L:.3f} L** of **{acid_choice}** at **{acid_molarity:.3f} mol/L**.")

    st.caption("This tool assumes ideal dilution and no interfering buffers.")