import streamlit as st
import pandas as pd
import io

# Tax Rates and Rebates (2024/2025)
TAX_BRACKETS = [
    (0, 237100, 0.18, 0),
    (237101, 370500, 0.26, 42678),
    (370501, 512800, 0.31, 77362),
    (512801, 673000, 0.36, 121475),
    (673001, 857900, 0.39, 179147),
    (857901, 1817000, 0.41, 251258),
    (1817001, float('inf'), 0.45, 644489)
]
REBATES = {
    "primary": 17235,
    "secondary": 9444,
    "tertiary": 3145
}

def get_tax_rate(income):
    """Return the marginal tax rate based on annual taxable income (2024/2025 rates)."""
    for lower, upper, rate, base_tax in TAX_BRACKETS:
        if lower <= income <= upper:
            return rate
    return 0.45

def calculate_ra_rebate(income, contribution):
    """Calculate the tax rebate for RA contributions and excess carryover."""
    max_deductible = min(income * 0.275, 350000)
    deductible = min(contribution, max_deductible)
    excess = max(0, contribution - max_deductible)
    tax_rate = get_tax_rate(income)
    rebate = deductible * tax_rate
    return deductible, tax_rate, rebate, excess

def show():
    st.markdown(
        """
        <div class="nw-card">
            <h3>Retirement Annuity | Tax Rebate</h3>
            <p style="color: var(--muted);">
                Map the deductible limit (27.5% of income, capped at R350,000), flag excess contributions that roll forward,
                and show the marginal rate used for the benefit.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_left, col_right = st.columns(2)
    with col_left:
        name = st.text_input("Client's Name")
        income = st.number_input("Annual Pensionable Income (R)", min_value=0.0, step=1000.0, format="%.0f")
    with col_right:
        contribution = st.number_input("Annual RA Contribution (R)", min_value=0.0, step=1000.0, format="%.0f")
        st.caption("Assumptions: 2024/2025 marginal rates. Confirm caps if new SARS tables apply.")

    if st.button("Calculate Rebate", type="primary"):
        if not name.strip():
            st.error("Please enter a name.")
        elif income < 0 or contribution < 0:
            st.error("Income and contribution must be non-negative.")
        else:
            try:
                deductible, tax_rate, rebate, excess = calculate_ra_rebate(
                    income, contribution
                )
                max_deductible = min(income * 0.275, 350000)
                remaining_space = max(0, max_deductible - contribution)

                k1, k2, k3 = st.columns(3)
                k1.metric("Deductible this year", f"R {deductible:,.0f}")
                k2.metric("Marginal tax rate", f"{tax_rate * 100:.1f}%")
                k3.metric("Tax rebate", f"R {rebate:,.0f}")

                st.markdown(
                    f"""
                    <div class="nw-card" style="margin-top: 0.5rem;">
                        <p><strong>Client:</strong> {name}</p>
                        <p style="color: var(--muted); margin-bottom: 0.3rem;">
                            Income: R {income:,.0f} • Contribution: R {contribution:,.0f}
                        </p>
                        <ul>
                            <li>Deductible cap (27.5%, max R350,000): R {max_deductible:,.0f}</li>
                            <li>Room before cap: R {remaining_space:,.0f}</li>
                            <li>Excess carried to next year: R {excess:,.0f}</li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown(
                    "<p style='font-size: 14px; color: var(--muted);'>If you have payroll access, schedule this amount as a pre-tax deduction to capture the rebate monthly.</p>",
                    unsafe_allow_html=True,
                )
                summary_data = {
                    "Client": [name],
                    "Annual Pensionable Income (R)": [income],
                    "RA Contribution (R)": [contribution],
                    "Deductible Contribution (R)": [deductible],
                    "Excess Contribution (Carried Over) (R)": [excess if excess > 0 else 0],
                    "Marginal Tax Rate (%)": [tax_rate * 100],
                    "Tax Rebate (R)": [rebate]
                }
                df = pd.DataFrame(summary_data)
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                    df.to_excel(writer, index=False, sheet_name="RA Tax Rebate Summary")
                    instructions = pd.DataFrame({
                        "Instructions": [
                            "This Excel file contains your RA Tax Rebate Summary.",
                            "There are no charts in this tool, but you can create your own in Excel.",
                            "For example, select your data and use Insert > Chart to visualize your results."
                        ]
                    })
                    instructions.to_excel(writer, index=False, sheet_name="Instructions")
                buffer.seek(0)
                st.download_button(
                    label="Download Summary as Excel",
                    data=buffer,
                    file_name="ra_tax_rebate_summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Error: {e}")
