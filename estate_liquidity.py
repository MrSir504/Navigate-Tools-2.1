import streamlit as st
import pandas as pd
import io

# Estate Duty Rates (2025)
ESTATE_DUTY_ABATEMENT = 3500000
ESTATE_DUTY_RATE_1 = 0.20
ESTATE_DUTY_RATE_2 = 0.25
ESTATE_DUTY_THRESHOLD = 30000000
EXECUTOR_FEE_RATE_DEFAULT = 0.035  # South African standard (3.5%)
CGT_INCLUSION_RATE = 0.40
CGT_EXCLUSION_DEATH = 300000

def calculate_estate_duty(net_value, has_surviving_spouse, spouse_bequest_value, pbo_bequest_value):
    """Calculate estate duty based on net estate value and deductions."""
    dutiable_value = max(0, net_value - spouse_bequest_value - pbo_bequest_value)
    dutiable_value = max(0, dutiable_value - ESTATE_DUTY_ABATEMENT)
    if dutiable_value <= 0:
        return 0
    if dutiable_value <= ESTATE_DUTY_THRESHOLD:
        estate_duty = dutiable_value * ESTATE_DUTY_RATE_1
    else:
        estate_duty = (ESTATE_DUTY_THRESHOLD * ESTATE_DUTY_RATE_1) + ((dutiable_value - ESTATE_DUTY_THRESHOLD) * ESTATE_DUTY_RATE_2)
    if has_surviving_spouse:
        return 0
    return estate_duty

def calculate_cgt(assets, marginal_tax_rate):
    """Calculate Capital Gains Tax on assets at death."""
    total_gain = 0
    for asset in assets:
        gain = max(0, asset["market_value"] - asset["base_cost"])
        total_gain += gain
    taxable_gain = max(0, total_gain - CGT_EXCLUSION_DEATH)
    taxable_amount = taxable_gain * CGT_INCLUSION_RATE
    cgt = taxable_amount * marginal_tax_rate
    return cgt

def calculate_executor_fees(gross_value, executor_fee_rate):
    """Calculate executor's fees based on gross estate value and user-defined rate."""
    base_fee = gross_value * executor_fee_rate
    return base_fee

def show():
    snapshot = st.session_state.get("client_snapshot", {})
    client_name = snapshot.get("client_name", "")

    st.markdown(
        """
        <div class="nav-card">
            <h3>Estate Liquidity | South Africa</h3>
            <p style="color: var(--muted);">
                Stress-test the estate for executor fees, CGT at death and estate duty.
                Surface the liquidity gap so you can position life cover or restructuring options.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not client_name:
        st.warning("Please set up the Client Profile in the sidebar first.")
        return

    st.markdown(f"**Client:** {client_name}")

    info_col, status_col = st.columns(2)
    with info_col:
        marital_status = st.selectbox("Marital Status", ["Single", "Married in Community of Property", "Married Out of Community (No Accrual)", "Married Out of Community (With Accrual)"])
    with status_col:
        has_surviving_spouse = st.checkbox("Surviving spouse?", value=False)
        st.caption("2025 SA estate duty rules: R3.5M abatement, 20% up to R30M, 25% thereafter.")

    st.write("**Liquid Assets**")
    cash = st.number_input("Cash in Bank/Savings (R)", min_value=0.0, step=1000.0, format="%.0f")
    life_insurance_to_estate = st.number_input("Life Insurance Payable to Estate (R)", min_value=0.0, step=1000.0, format="%.0f")

    with st.expander("Non-Liquid Assets", expanded=True):
        num_properties = st.number_input("Number of Properties", min_value=0, max_value=10, step=1, value=0)
        properties = []
        for i in range(num_properties):
            st.write(f"**Property {i+1}**")
            market_value = st.number_input(f"Market Value of Property {i+1} (R)", min_value=0.0, step=1000.0, format="%.0f", key=f"prop_value_{i}")
            properties.append(market_value)
        num_investments = st.number_input("Number of Investments (e.g., Shares, Bonds)", min_value=0, max_value=10, step=1, value=0)
        investments = []
        for i in range(num_investments):
            st.write(f"**Investment {i+1}**")
            market_value = st.number_input(f"Market Value of Investment {i+1} (R)", min_value=0.0, step=1000.0, format="%.0f", key=f"inv_value_{i}")
            base_cost = st.number_input(f"Base Cost of Investment {i+1} (R)", min_value=0.0, step=1000.0, format="%.0f", key=f"inv_base_{i}")
            investments.append({"market_value": market_value, "base_cost": base_cost})
        other_assets = st.number_input("Other Non-Liquid Assets (e.g., Vehicles, Jewelry) (R)", min_value=0.0, step=1000.0, format="%.0f")

    with st.expander("Liabilities & Costs", expanded=True):
        debts = st.number_input("Outstanding Debts (e.g., Loans, Bonds) (R)", min_value=0.0, step=1000.0, format="%.0f")
        medical_bills = st.number_input("Medical Bills or Pre-Death Expenses (R)", min_value=0.0, step=1000.0, format="%.0f")
        cash_bequests = st.number_input("Cash Bequests to Beneficiaries (R)", min_value=0.0, step=1000.0, format="%.0f")
        spouse_bequest_value = st.number_input("Bequests to Surviving Spouse (R)", min_value=0.0, step=1000.0, format="%.0f", disabled=not has_surviving_spouse)
        pbo_bequest_value = st.number_input("Bequests to Public Benefit Organizations (R)", min_value=0.0, step=1000.0, format="%.0f")

    st.write("**Assumptions**")
    marginal_tax_rate = st.number_input("Marginal Tax Rate for CGT (e.g., 0.45 for 45%)", min_value=0.0, max_value=0.45, value=0.45, step=0.01)
    executor_fee_rate = st.number_input("Executor Fee Rate (%)", min_value=0.0, max_value=10.0, value=EXECUTOR_FEE_RATE_DEFAULT * 100, step=0.1) / 100
    if st.button("Calculate Estate Liquidity", type="primary"):
        if cash < 0 or life_insurance_to_estate < 0 or any(p < 0 for p in properties) or any(i["market_value"] < 0 or i["base_cost"] < 0 for i in investments) or other_assets < 0 or debts < 0 or medical_bills < 0 or cash_bequests < 0 or spouse_bequest_value < 0 or pbo_bequest_value < 0 or marginal_tax_rate < 0 or marginal_tax_rate > 0.45 or executor_fee_rate < 0:
            st.error("All financial inputs must be non-negative, marginal tax rate must be between 0 and 45%, and executor fee rate must be non-negative.")
        else:
            try:
                gross_estate = cash + life_insurance_to_estate + sum(properties) + sum(i["market_value"] for i in investments) + other_assets
                net_estate = gross_estate - debts - medical_bills - cash_bequests
                cgt = calculate_cgt(investments, marginal_tax_rate)
                estate_duty = calculate_estate_duty(net_estate, has_surviving_spouse, spouse_bequest_value, pbo_bequest_value)
                executor_fees = calculate_executor_fees(gross_estate, executor_fee_rate)
                total_costs = cgt + estate_duty + executor_fees
                liquid_assets = cash + life_insurance_to_estate
                liquidity_shortfall = max(0, total_costs - liquid_assets)

                k1, k2, k3 = st.columns(3)
                k1.metric("Total estate costs", f"R {total_costs:,.0f}")
                k2.metric("Liquid assets on death", f"R {liquid_assets:,.0f}")
                k3.metric("Liquidity gap", f"R {liquidity_shortfall:,.0f}" if liquidity_shortfall > 0 else "None")

                st.success("--- Estate Liquidity Summary ---")
                st.write(f"**Client**: {client_name}")
                st.write(f"**Gross Estate Value**: R {gross_estate:,.2f}")
                st.write(f"**Net Estate Value (after debts, medical bills, and cash bequests)**: R {net_estate:,.2f}")
                st.write(f"**Capital Gains Tax**: R {cgt:,.2f}")
                st.write(f"**Estate Duty**: R {estate_duty:,.2f}")
                st.write(f"**Executor Fees**: R {executor_fees:,.2f}")
                st.write(f"**Total Costs**: R {total_costs:,.2f}")
                st.write(f"**Liquid Assets Available**: R {liquid_assets:,.2f}")
                if liquidity_shortfall > 0:
                    st.warning(f"**Liquidity Shortfall**: R {liquidity_shortfall:,.2f}")
                    st.write("**Recommendation**: Consider increasing life insurance payable to the estate or liquidating non-liquid assets to cover the shortfall.")
                else:
                    st.write("**Liquidity Status**: Sufficient liquid assets to cover costs.")
                summary_data = {
                    "Client": [client_name],
                    "Gross Estate Value (R)": [gross_estate],
                    "Net Estate Value (R)": [net_estate],
                    "Capital Gains Tax (R)": [cgt],
                    "Estate Duty (R)": [estate_duty],
                    "Executor Fees (R)": [executor_fees],
                    "Total Costs (R)": [total_costs],
                    "Liquid Assets Available (R)": [liquid_assets],
                    "Liquidity Shortfall (R)": [liquidity_shortfall if liquidity_shortfall > 0 else 0]
                }
                summary_df = pd.DataFrame(summary_data)
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                    summary_df.to_excel(writer, index=False, sheet_name="Estate Liquidity Summary")
                    instructions = pd.DataFrame({
                        "Instructions": [
                            "This Excel file contains your Estate Liquidity Summary.",
                            "There are no charts in this tool, but you can create your own in Excel.",
                            "For example, select your data and use Insert > Chart to visualize your results."
                        ]
                    })
                    instructions.to_excel(writer, index=False, sheet_name="Instructions")
                buffer.seek(0)
                st.download_button(
                    label="Download Summary as Excel",
                    data=buffer,
                    file_name="estate_liquidity_summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Error: {e}")
