import streamlit as st
import pandas as pd


def calculate_gap(
    annual_income,
    debts,
    education,
    final_expenses,
    existing_life,
    existing_di,
    existing_ci,
    income_replacement_ratio,
    survivors_years,
):
    future_income_need = annual_income * income_replacement_ratio * survivors_years
    life_need = future_income_need + debts + education + final_expenses

    # Disability: assume similar to income replacement with shorter horizon
    di_years = min(survivors_years, 15)
    di_need = annual_income * income_replacement_ratio * di_years + debts + education * 0.5

    # CI: lump-sum lighter than DI
    ci_need = (annual_income * 0.5) + education * 0.3 + final_expenses

    life_gap = life_need - existing_life
    di_gap = di_need - existing_di
    ci_gap = ci_need - existing_ci

    return {
        "life_need": life_need,
        "di_need": di_need,
        "ci_need": ci_need,
        "life_gap": life_gap,
        "di_gap": di_gap,
        "ci_gap": ci_gap,
        "future_income_need": future_income_need,
        "di_years": di_years,
    }


def show():
    snapshot = st.session_state.get("client_snapshot", {})
    client_name = snapshot.get("client_name", "")
    default_annual_income = float(snapshot.get("household_income", 45000)) * 12

    st.markdown(
        """
        <div class="nav-card">
            <h3>Life / Disability / Critical Illness Gap</h3>
            <p style="color: var(--muted);">
                Quantify needs for income replacement, debt clearance, education, and final expenses.
                Compare to existing cover and surface the gap.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not client_name:
        st.warning("Please set up the Client Profile in the sidebar first.")
        return

    st.markdown(f"**Client:** {client_name}")

    c1, c2, c3 = st.columns(3)
    with c1:
        annual_income = st.number_input(
            "Annual income (R)",
            min_value=0.0,
            step=10000.0,
            value=default_annual_income,
        )
        replacement_years = st.slider("Years of income to replace", 1, 25, 10)
    with c2:
        debts = st.number_input(
            "Debt payoff (R)", min_value=0.0, step=10000.0, value=400000.0
        )
        education = st.number_input(
            "Education fund (R)", min_value=0.0, step=10000.0, value=300000.0
        )
        final_expenses = st.number_input(
            "Final expenses (R)", min_value=0.0, step=10000.0, value=80000.0
        )
    with c3:
        existing_life = st.number_input(
            "Existing LIFE cover (R)", min_value=0.0, step=100000.0, value=800000.0
        )
        existing_di = st.number_input(
            "Existing DISABILITY cover (R)",
            min_value=0.0,
            step=100000.0,
            value=500000.0,
        )
        existing_ci = st.number_input(
            "Existing CRITICAL ILLNESS cover (R)",
            min_value=0.0,
            step=50000.0,
            value=250000.0,
        )

    st.markdown("### Assumptions")
    col_a, col_b = st.columns(2)
    with col_a:
        inflation = (
            st.number_input(
                "Inflation (%)", min_value=0.0, max_value=15.0, value=6.0, step=0.5
            )
            / 100
        )
        growth = (
            st.number_input(
                "Investment return (%)",
                min_value=0.0,
                max_value=15.0,
                value=8.0,
                step=0.5,
            )
            / 100
        )
    with col_b:
        income_replacement_ratio = st.slider("Income replacement %", 50, 100, 75) / 100
        survivors_years = st.slider("Years support for survivors", 1, 25, 15)
        st.caption("Adjust for family size and desired lifestyle stability.")

    if st.button("Calculate Cover", type="primary"):
        results = calculate_gap(
            annual_income,
            debts,
            education,
            final_expenses,
            existing_life,
            existing_di,
            existing_ci,
            income_replacement_ratio,
            survivors_years,
        )

        life_need = results["life_need"]
        di_need = results["di_need"]
        ci_need = results["ci_need"]
        life_gap = results["life_gap"]
        di_gap = results["di_gap"]
        ci_gap = results["ci_gap"]
        future_income_need = results["future_income_need"]

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Life need", f"R {life_need:,.0f}", delta=f"Gap R {life_gap:,.0f}")
        k2.metric("Disability need", f"R {di_need:,.0f}", delta=f"Gap R {di_gap:,.0f}")
        k3.metric(
            "Critical illness need", f"R {ci_need:,.0f}", delta=f"Gap R {ci_gap:,.0f}"
        )
        k4.metric("Income replacement %", f"{income_replacement_ratio*100:.0f}%")

        st.markdown("#### Breakdown (Life)")
        st.write(
            f"- Income replacement ({survivors_years} yrs @ {income_replacement_ratio*100:.0f}%): R {future_income_need:,.0f}\n"
            f"- Debt payoff: R {debts:,.0f}\n"
            f"- Education: R {education:,.0f}\n"
            f"- Final expenses: R {final_expenses:,.0f}"
        )

        df = pd.DataFrame(
            [
                ["Life", life_need, existing_life, life_gap],
                ["Disability", di_need, existing_di, di_gap],
                ["Critical Illness", ci_need, existing_ci, ci_gap],
            ],
            columns=["Cover type", "Need (R)", "Existing cover (R)", "Gap (R)"],
        )
        st.dataframe(df, use_container_width=True)

        st.info(
            "Guidance: match Life gap with term or whole-life cover as appropriate; "
            "DI gap with lump sum and income benefits; CI gap with layered benefits."
        )
