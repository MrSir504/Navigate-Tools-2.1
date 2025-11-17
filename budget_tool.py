import streamlit as st
import pandas as pd
import io

def calculate_budget(monthly_income, expenses):
    """Calculate total expenses, remaining budget, and savings potential."""
    total_expenses = sum(expense for category, expense in expenses)
    remaining_budget = monthly_income - total_expenses
    savings_potential = max(0, remaining_budget)
    return total_expenses, remaining_budget, savings_potential

def show():
    snapshot = st.session_state.get("client_snapshot", {})
    default_income = float(snapshot.get("household_income", 39500))
    st.markdown(
        """
        <div class="nw-card">
            <h3>Cash Flow Map | Budget</h3>
            <p style="color: var(--muted);">
                Quickly split income, fixed and flexible spend to show affordability for new advice (RA, education, risk cover).
                Adjust categories live while talking through the client's month.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    monthly_income = st.number_input(
        "Monthly Income (R)", min_value=0.0, step=500.0, value=default_income, format="%.0f"
    )
    st.write("**Add Your Monthly Expenses**")
    with st.form(key="expense_form"):
        num_expenses = st.number_input("Number of Expense Categories", min_value=1, max_value=10, step=1, value=3)
        expenses = []
        for i in range(num_expenses):
            col1, col2 = st.columns(2)
            with col1:
                category = st.text_input(f"Expense Category {i+1}", value=f"Category {i+1}", key=f"category_{i}")
            with col2:
                amount = st.number_input(f"Amount (R)", min_value=0.0, step=100.0, format="%.0f", key=f"amount_{i}")
            expenses.append((category, amount))
        submit_button = st.form_submit_button("Calculate Budget", type="primary")

    if submit_button:
        if monthly_income < 0:
            st.error("Monthly income must be non-negative.")
        else:
            try:
                total_expenses, remaining_budget, savings_potential = calculate_budget(monthly_income, expenses)
                savings_rate = (savings_potential / monthly_income * 100) if monthly_income else 0

                k1, k2, k3 = st.columns(3)
                k1.metric("Total expenses", f"R {total_expenses:,.0f}")
                k2.metric("Remaining budget", f"R {remaining_budget:,.0f}")
                k3.metric("Savings rate", f"{savings_rate:.1f}%")

                st.write("**Expenses Breakdown**")
                expenses_data = []
                for category, amount in expenses:
                    expenses_data.append({"Category": category, "Amount (R)": amount})
                st.dataframe(pd.DataFrame(expenses_data), use_container_width=True)

                st.markdown(
                    f"""
                    <div class="nw-card">
                        <p><strong>Monthly income:</strong> R {monthly_income:,.0f}</p>
                        <p><strong>Total spend:</strong> R {total_expenses:,.0f}</p>
                        <p><strong>Remaining budget:</strong> R {remaining_budget:,.0f}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                summary_data = {
                    "Monthly Income (R)": [monthly_income],
                    "Total Monthly Expenses (R)": [total_expenses],
                    "Remaining Budget (R)": [remaining_budget]
                }
                if remaining_budget < 0:
                    st.warning("You're overspending! Consider reducing expenses to avoid debt.")
                else:
                    st.write(f"**Savings Potential**: R {savings_potential:,.2f}")
                    summary_data["Savings Potential (R)"] = [savings_potential]
                st.write("**Budget Breakdown Visualization**")
                chart_data = pd.DataFrame({
                    "Category": [category for category, amount in expenses] + ["Remaining Budget"],
                    "Amount (R)": [amount for category, amount in expenses] + [max(0, remaining_budget)]
                })
                st.bar_chart(chart_data.set_index("Category"))
                summary_df = pd.DataFrame(summary_data)
                expenses_df = pd.DataFrame(expenses_data)
                chart_df = pd.DataFrame(chart_data).reset_index()
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                    summary_df.to_excel(writer, index=False, sheet_name="Budget Summary")
                    expenses_df.to_excel(writer, startrow=len(summary_df) + 2, index=False, sheet_name="Budget Summary")
                    chart_df.to_excel(writer, index=False, sheet_name="Chart Data", startrow=0)
                    instructions = pd.DataFrame({
                        "Instructions": [
                            "This Excel file contains your Budget Summary and Chart Data.",
                            "To recreate the bar chart in Excel:",
                            "1. Go to the 'Chart Data' sheet.",
                            "2. Select the 'Category' and 'Amount (R)' columns.",
                            "3. Click Insert > Bar Chart in Excel to visualize the budget breakdown."
                        ]
                    })
                    instructions.to_excel(writer, index=False, sheet_name="Instructions")
                buffer.seek(0)
                st.download_button(
                    label="Download Summary as Excel",
                    data=buffer,
                    file_name="budget_summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Error: {e}")
