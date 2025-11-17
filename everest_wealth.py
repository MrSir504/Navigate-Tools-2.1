import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# Constants for Everest Wealth Products
ONYX_INCOME_PLUS_RATE = 0.142  # 14.2% annual return
STRATEGIC_INCOME_RATE = 0.128  # 12.8% annual return
DIVIDEND_TAX_RATE = 0.20  # 20% dividend tax
TERM_YEARS = 5
STRATEGIC_INCOME_BONUS = 0.10  # 10% special dividend bonus at the end of term
ONYX_BROKER_COMMISSION = 0.04  # 4% commission for Onyx Income Plus
STRATEGIC_BROKER_COMMISSION = 0.05  # 5% commission for Strategic Income
MINIMUM_INVESTMENT = 100000  # R100,000 minimum
INVESTMENT_INCREMENT = 5000  # Must be divisible by R5,000

def calculate_investment_results(investment_amount, product):
    """Calculate gross and net returns for the selected Everest Wealth product."""
    # Determine the annual rate and broker commission based on the product
    if product == "Onyx Income Plus":
        annual_rate = ONYX_INCOME_PLUS_RATE
        broker_commission_rate = ONYX_BROKER_COMMISSION
        special_bonus = 0  # No bonus for Onyx Income Plus
    else:  # Strategic Income
        annual_rate = STRATEGIC_INCOME_RATE
        broker_commission_rate = STRATEGIC_BROKER_COMMISSION
        special_bonus = investment_amount * STRATEGIC_INCOME_BONUS  # 10% bonus

    # Calculate broker fee
    broker_fee = investment_amount * broker_commission_rate

    # Gross returns
    gross_annual_return = investment_amount * annual_rate
    gross_monthly_income = gross_annual_return / 12
    gross_total_return = (gross_annual_return * TERM_YEARS) + special_bonus  # Include bonus for Strategic Income

    # Net returns after dividend tax
    net_monthly_income = gross_monthly_income * (1 - DIVIDEND_TAX_RATE)
    net_annual_return = net_monthly_income * 12
    net_bonus = special_bonus * (1 - DIVIDEND_TAX_RATE) if special_bonus > 0 else 0
    net_total_return = (net_annual_return * TERM_YEARS) + net_bonus  # Include net bonus

    return {
        "gross_monthly_income": gross_monthly_income,
        "gross_annual_return": gross_annual_return,
        "gross_total_return": gross_total_return,
        "net_monthly_income": net_monthly_income,
        "net_annual_return": net_annual_return,
        "net_total_return": net_total_return,
        "broker_fee": broker_fee,
        "special_bonus": special_bonus,
        "net_bonus": net_bonus,
    }

def show():
    st.markdown(
        """
        <div class="nw-card">
            <h3>Everest Wealth | Quick Quote</h3>
            <p style="color: var(--muted);">
                Present Onyx Income Plus or Strategic Income with clear gross/net income, broker fee and the Strategic bonus.
                Rates set to current marketing: 14.2% (Onyx), 12.8% (Strategic) over 5 years with 20% dividend tax.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)
    with left:
        name = st.text_input("Client's Name", key="everest_wealth_name")
        product = st.selectbox("Select Everest Wealth Product", ["Onyx Income Plus", "Strategic Income"])
    with right:
        investment_amount = st.number_input(
            "Investment Amount (R)",
            min_value=MINIMUM_INVESTMENT,
            step=INVESTMENT_INCREMENT,
            value=MINIMUM_INVESTMENT,
            help="Minimum investment is R100,000, and the amount must be divisible by R5,000.",
            format="%.0f",
        )
        st.caption("All returns shown net of 20% dividend tax. Strategic Income includes the 10% bonus at term.")

    # Validate that the investment amount is divisible by 5,000
    if investment_amount % INVESTMENT_INCREMENT != 0:
        st.error(f"Investment amount must be divisible by R{INVESTMENT_INCREMENT:,}. For example, R{investment_amount - (investment_amount % INVESTMENT_INCREMENT):,} or R{(investment_amount + INVESTMENT_INCREMENT - (investment_amount % INVESTMENT_INCREMENT)):,}.")
        return

    if st.button("Calculate Investment Returns"):
        if not name.strip():
            st.error("Please enter a name.")
        elif investment_amount < MINIMUM_INVESTMENT:
            st.error(f"Investment amount must be at least R{MINIMUM_INVESTMENT:,}.")
        else:
            try:
                # Calculate results
                results = calculate_investment_results(investment_amount, product)

                # Display summary
                st.success("--- Everest Wealth Investment Summary ---")
                st.write(f"**Client**: {name}")
                st.write(f"**Product**: {product}")
                st.write(f"**Investment Amount**: R {investment_amount:,.2f}")

                k1, k2, k3 = st.columns(3)
                k1.metric("Gross monthly income", f"R {results['gross_monthly_income']:,.0f}")
                k2.metric("Net monthly income (after tax)", f"R {results['net_monthly_income']:,.0f}")
                k3.metric("Broker fee", f"R {results['broker_fee']:,.0f}")

                # Summary table with improved styling
                summary_data = {
                    "Metric": [
                        "Gross Monthly Income (R)",
                        "Gross Annual Return (R)",
                        "Gross Total Return Over Term (R)",
                        "Net Monthly Income (R)",
                        "Net Annual Return (R)",
                        "Net Total Return Over Term (R)",
                        "Special Dividend Bonus (Gross, if any)",
                        "Special Dividend Bonus (Net, if any)",
                        "Broker Fee Earned (R)"
                    ],
                    "Value": [
                        results["gross_monthly_income"],
                        results["gross_annual_return"],
                        results["gross_total_return"],
                        results["net_monthly_income"],
                        results["net_annual_return"],
                        results["net_total_return"],
                        results["special_bonus"],
                        results["net_bonus"],
                        results["broker_fee"]
                    ]
                }
                summary_df = pd.DataFrame(summary_data)
                summary_df["Value"] = summary_df["Value"].apply(lambda x: f"R {x:,.2f}")

                # Add custom CSS for the dataframe to improve visibility
                st.markdown(
                    """
                    <style>
                    .dataframe {
                        background-color: #0f1b30;
                        color: #e6edf7;
                        border: 1px solid rgba(255, 255, 255, 0.12);
                    }
                    .dataframe th {
                        background-color: #11213b;
                        color: #e6edf7;
                        border: 1px solid rgba(255, 255, 255, 0.18);
                    }
                    .dataframe td {
                        background-color: #0f1b30;
                        color: #e6edf7;
                        border: 1px solid rgba(255, 255, 255, 0.08);
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                st.write("**Investment Returns**")
                st.dataframe(summary_df, use_container_width=True)

                tax_drag = results["gross_total_return"] - results["net_total_return"]
                client_color = "#3a60d1"
                tax_color = "#f59e0b"
                broker_color = "#10b981"

                # Bar chart for gross vs net monthly income
                fig = go.Figure(data=[
                    go.Bar(name="Gross Monthly Income", x=["Gross"], y=[results["gross_monthly_income"]], marker_color=client_color),
                    go.Bar(name="Net Monthly Income", x=["Net"], y=[results["net_monthly_income"]], marker_color=broker_color)
                ])
                fig.update_layout(
                    title="Gross vs Net Monthly Income",
                    xaxis_title="Income Type",
                    yaxis_title="Amount (R)",
                    barmode="group",
                    showlegend=True,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="#f8fafc",
                    font={'color': "#0f172a"},
                    height=340,
                    margin=dict(l=30, r=20, t=60, b=40),
                )
                st.plotly_chart(fig, use_container_width=True)

                # Cumulative returns over the five-year term
                years = list(range(1, TERM_YEARS + 1))
                gross_cumulative = []
                net_cumulative = []
                for year in years:
                    gross_total = results["gross_annual_return"] * year
                    net_total = results["net_annual_return"] * year
                    if product == "Strategic Income" and year == TERM_YEARS:
                        gross_total += results["special_bonus"]
                        net_total += results["net_bonus"]
                    gross_cumulative.append(gross_total)
                    net_cumulative.append(net_total)

                line_fig = go.Figure()
                line_fig.add_trace(go.Scatter(
                    x=years, y=gross_cumulative, mode="lines+markers", name="Gross cumulative",
                    line=dict(color=client_color, width=3), marker=dict(size=9)
                ))
                line_fig.add_trace(go.Scatter(
                    x=years, y=net_cumulative, mode="lines+markers", name="Net cumulative",
                    line=dict(color=broker_color, width=3), marker=dict(size=9)
                ))
                line_fig.update_layout(
                    title="Cumulative returns over term",
                    xaxis_title="Year",
                    yaxis_title="Total returns (R)",
                    hovermode="x unified",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="#f8fafc",
                    font={'color': "#0f172a"},
                    height=380,
                    margin=dict(l=40, r=20, t=60, b=50),
                )
                st.plotly_chart(line_fig, use_container_width=True)

                # Flow of returns at term-end
                mix_fig = go.Figure(go.Pie(
                    labels=["Net income to client", "Tax drag", "Broker fee"],
                    values=[results["net_total_return"], tax_drag, results["broker_fee"]],
                    hole=0.55,
                    marker=dict(colors=[client_color, tax_color, broker_color]),
                    textinfo="label+percent",
                    hovertemplate="%{label}: R %{value:,.0f}<extra></extra>",
                    sort=False,
                ))
                mix_fig.update_layout(
                    title="Where the income flows",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font={'color': "#0f172a"},
                    height=360,
                    legend_orientation="h",
                    legend_y=-0.08,
                    margin=dict(l=20, r=20, t=60, b=20),
                )
                st.plotly_chart(mix_fig, use_container_width=True)

                # Additional note for Strategic Income
                if product == "Strategic Income":
                    st.write(f"**Note**: Strategic Income includes a special dividend bonus of R {results['special_bonus']:,.2f} (Net: R {results['net_bonus']:,.2f} after 20% dividend tax) at the end of the term.")

                # Downloadable summary
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                    summary_df.to_excel(writer, index=False, sheet_name="Everest Wealth Summary")
                    instructions = pd.DataFrame({
                        "Instructions": [
                            "This Excel file contains your Everest Wealth Investment Summary.",
                            "The bar chart compares Gross vs Net Monthly Income.",
                            "You can recreate the chart in Excel by selecting the Gross and Net Monthly Income rows and using Insert > Bar Chart."
                        ]
                    })
                    instructions.to_excel(writer, index=False, sheet_name="Instructions")
                buffer.seek(0)
                st.download_button(
                    label="Download Summary as Excel",
                    data=buffer,
                    file_name="everest_wealth_summary.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            except Exception as e:
                st.error(f"Error: {e}")

if __name__ == "__main__":
    show()
