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
UIF_RATE = 0.01
UIF_MONTHLY_CAP = 17712
UIF_ANNUAL_CAP = UIF_MONTHLY_CAP * 12
MTC_PER_PERSON = 364
MTC_ADDITIONAL_DEPENDANT = 246

def get_tax_rate(income):
    """Return the marginal tax rate based on annual taxable income (2024/2025 rates)."""
    for lower, upper, rate, base_tax in TAX_BRACKETS:
        if lower <= income <= upper:
            return rate
    return 0.45

def calculate_medical_tax_credits(num_dependants):
    """Calculate the Medical Scheme Fees Tax Credit (MTC) based on the number of dependants."""
    if num_dependants <= 0:
        return 0, 0
    if num_dependants <= 2:
        annual_mtc = num_dependants * MTC_PER_PERSON * 12
    else:
        annual_mtc = (2 * MTC_PER_PERSON * 12) + ((num_dependants - 2) * MTC_ADDITIONAL_DEPENDANT * 12)
    monthly_mtc = annual_mtc / 12
    return annual_mtc, monthly_mtc

def calculate_salary_tax(gross_salary, pension_contribution, age, medical_contributions, num_dependants):
    """Calculate PAYE, UIF, MTC, taxable income, and tax rates."""
    max_deductible = min(gross_salary * 0.275, 350000)
    deductible_contribution = min(pension_contribution, max_deductible)
    taxable_income = max(0, gross_salary - deductible_contribution)
    tax_before_rebates = 0
    marginal_rate = 0
    for lower, upper, rate, base_tax in TAX_BRACKETS:
        if taxable_income > lower:
            if taxable_income <= upper:
                tax_before_rebates = base_tax + (taxable_income - lower) * rate
                marginal_rate = rate
                break
            marginal_rate = rate
        else:
            break
    total_rebate = REBATES["primary"]
    if age >= 75:
        total_rebate += REBATES["secondary"] + REBATES["tertiary"]
    elif age >= 65:
        total_rebate += REBATES["secondary"]
    paye_before_mtc = max(0, tax_before_rebates - total_rebate)
    paye_before_mtc_monthly = paye_before_mtc / 12
    mtc_annual, mtc_monthly = calculate_medical_tax_credits(num_dependants)
    paye = max(0, paye_before_mtc - mtc_annual)
    paye_monthly = paye / 12
    annual_salary_for_uif = min(gross_salary, UIF_ANNUAL_CAP)
    uif = annual_salary_for_uif * UIF_RATE
    uif_monthly = uif / 12
    net_income = gross_salary - paye - uif
    net_income_monthly = net_income / 12
    return taxable_income, paye_before_mtc, paye_before_mtc_monthly, mtc_annual, mtc_monthly, paye, paye_monthly, uif, uif_monthly, net_income, net_income_monthly, marginal_rate

def show():
    snapshot = st.session_state.get("client_snapshot", {})
    client_name = snapshot.get("client_name", "")
    default_monthly_income = float(snapshot.get("household_income", 0))
    default_annual_income = default_monthly_income * 12 if default_monthly_income else 0

    st.markdown(
        """
        <div class="nav-card">
            <h3>Payslip Story | TAX • UIF • Medical Credits</h3>
            <p style="color: var(--muted);">
                Perfect for payroll conversations. We adjust pension/RA deductions, apply medical credits and UIF caps,
                and split results annual vs monthly for clarity.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not client_name:
        st.warning("Please set up the Client Profile in the sidebar first.")
        return

    left, right = st.columns(2)
    with left:
        st.markdown(f"**Client:** {client_name}")
        gross_salary = st.number_input(
            "Gross Annual Salary (R)", min_value=0.0, step=1000.0, value=default_annual_income, format="%.0f"
        )
        pension_contribution = st.number_input("Annual Pension/RA Contribution (R)", min_value=0.0, step=1000.0, format="%.0f")
    with right:
        medical_contributions = st.number_input("Annual Medical Scheme Contributions (R)", min_value=0.0, step=1000.0, format="%.0f")
        num_dependants = st.number_input("Number of Dependants on Medical Scheme (including you)", min_value=0, max_value=10, step=1, value=int(snapshot.get("dependants", 0)))
        age = st.number_input("Client's Age", min_value=0, max_value=120, step=1, value=int(snapshot.get("age", 35)))
        st.caption("SA 2024/25 tax tables and UIF cap assumed. Update values if SARS releases new thresholds.")

    if st.button("Calculate Tax", type="primary"):
        if gross_salary < 0 or pension_contribution < 0 or medical_contributions < 0 or num_dependants < 0 or age < 0:
            st.error("All inputs must be non-negative.")
        else:
            try:
                # ... (rest of the logic remains the same, just changing 'name' variable usage if needed)
                taxable_income, paye_before_mtc, paye_before_mtc_monthly, mtc_annual, mtc_monthly, paye, paye_monthly, uif, uif_monthly, net_income, net_income_monthly, marginal_rate = calculate_salary_tax(gross_salary, pension_contribution, age, medical_contributions, num_dependants)
                k1, k2, k3 = st.columns(3)
                k1.metric("Net monthly income", f"R {net_income_monthly:,.0f}")
                k2.metric("PAYE monthly", f"R {paye_monthly:,.0f}")
                k3.metric("Marginal rate", f"{marginal_rate * 100:.1f}%")

                st.markdown(
                    f"""
                    <div class="nav-card">
                        <p><strong>Client:</strong> {client_name} • Taxable income: R {taxable_income:,.0f}</p>
                        <p style="color: var(--muted); margin-bottom: 0.3rem;">
                            Pension/RA deduction applied: R {min(pension_contribution, gross_salary * 0.275):,.0f}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                summary_data = {
                    "Client": [client_name],
                    "Gross Annual Salary (R)": [gross_salary],
                    "Taxable Income (R)": [taxable_income],
                    "PAYE Before Medical Tax Credits (Annual) (R)": [paye_before_mtc],
                    "PAYE Before Medical Tax Credits (Monthly) (R)": [paye_before_mtc_monthly]
                }
                if num_dependants > 0:
                    st.write(f"**Medical Tax Credits (Annual)**: R {mtc_annual:,.2f}")
                    st.write(f"**Medical Tax Credits (Monthly)**: R {mtc_monthly:,.2f}")
                    tax_savings_percentage = min((mtc_annual / paye_before_mtc) * 100 if paye_before_mtc > 0 else 0, 100)
                    st.write(f"**Tax Savings from Medical Credits**: {tax_savings_percentage:.1f}% of your PAYE")
                    st.progress(tax_savings_percentage / 100)
                    st.markdown(
                        "<p style='font-size: 14px; font-style: italic; color: var(--muted);'>Dependent Credits: R364/month for you and your first dependant, R246/month for each additional dependant (e.g., spouse, children, or other family members on your medical scheme).</p>",
                        unsafe_allow_html=True
                    )
                    summary_data["Medical Tax Credits (Annual) (R)"] = [mtc_annual]
                    summary_data["Medical Tax Credits (Monthly) (R)"] = [mtc_monthly]
                    summary_data["Tax Savings from Medical Credits (%)"] = [tax_savings_percentage]
                st.write(f"**PAYE (After Medical Tax Credits, Annual)**: R {paye:,.2f}")
                st.write(f"**PAYE (After Medical Tax Credits, Monthly)**: R {paye_monthly:,.2f}")
                st.write(f"**UIF Contribution (Employee, Annual)**: R {uif:,.2f}")
                st.write(f"**UIF Contribution (Employee, Monthly)**: R {uif_monthly:,.2f}")
                st.write(f"**Net Annual Income**: R {net_income:,.2f}")
                st.write(f"**Net Monthly Income**: R {net_income_monthly:,.2f}")
                st.write(f"**Marginal Tax Rate**: {marginal_rate * 100:.1f}%")
                summary_data["PAYE After Medical Tax Credits (Annual) (R)"] = [paye]
                summary_data["PAYE After Medical Tax Credits (Monthly) (R)"] = [paye_monthly]
                summary_data["UIF Contribution (Employee, Annual) (R)"] = [uif]
                summary_data["UIF Contribution (Employee, Monthly) (R)"] = [uif_monthly]
                summary_data["Net Annual Income (R)"] = [net_income]
                summary_data["Net Monthly Income (R)"] = [net_income_monthly]
                summary_data["Marginal Tax Rate (%)"] = [marginal_rate * 100]
                st.write("**Tax Breakdown Visualization**")
                chart_data = pd.DataFrame({
                    "Category": ["Gross Income", "PAYE", "UIF", "Medical Tax Credits", "Net Income"],
                    "Amount (R)": [gross_salary, -paye, -uif, -mtc_annual if num_dependants > 0 else 0, net_income]
                })
                st.bar_chart(chart_data.set_index("Category"))
                st.markdown(
                    "<p style='font-size: 14px; color: var(--muted);'>Note: Tax rates, UIF limits, and medical tax credits are based on 2024/2025 SARS tables. Verify with 2025/2026 rates when available.</p>",
                    unsafe_allow_html=True
                )
                summary_df = pd.DataFrame(summary_data)
                chart_df = pd.DataFrame(chart_data).reset_index()
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                    summary_df.to_excel(writer, index=False, sheet_name="Salary Tax Summary")
                    chart_df.to_excel(writer, index=False, sheet_name="Chart Data", startrow=0)
                    instructions = pd.DataFrame({
                        "Instructions": [
                            "This Excel file contains your Salary Tax Summary and Chart Data.",
                            "To recreate the bar chart in Excel:",
                            "1. Go to the 'Chart Data' sheet.",
                            "2. Select the 'Category' and 'Amount (R)' columns.",
                            "3. Click Insert > Bar Chart in Excel to visualize the tax breakdown.",
                            "Note: The progress bar (Tax Savings %) cannot be exported as it is a dynamic widget."
                        ]
                    })
                    instructions.to_excel(writer, index=False, sheet_name="Instructions")
                buffer.seek(0)
                st.download_button(
                    label="Download Summary as Excel",
                    data=buffer,
                    file_name="salary_tax_summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Error: {e}")
