import streamlit as st
import advisor_brief
import budget_tool
import estate_liquidity
import everest_wealth
import life_cover_gap
import ra_calculator
import retirement_calculator
import risk_profiler
import salary_calculator
import datetime

# --- Configuration ---
st.set_page_config(
    page_title="Navigate Wealth",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Load Custom CSS ---
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("dashboard_style.css")

# --- Session State Management ---
if "client_snapshot" not in st.session_state:
    st.session_state.client_snapshot = {
        "client_name": "",
        "age": 0,
        "retirement_age": 65,
        "household_income": 0.0,
        "savings_balance": 0.0,
        "dependants": 0
    }

# --- Sidebar Navigation ---
st.sidebar.markdown("## NAVIGATE WEALTH")
st.sidebar.markdown("---")

# Menu Structure
menu_categories = {
    "Client Profile": ["Client Details"],
    "Cashflow & Tax": ["Salary Calculator", "Budget Tool"],
    "Wealth Planning": ["Retirement Calculator", "Everest Wealth", "RA Calculator"],
    "Risk & Estate": ["Risk Profiler", "Life Cover Gap", "Estate Liquidity"],
    "Reports": ["Advisor Brief"]
}

selected_category = st.sidebar.radio("MODULES", list(menu_categories.keys()))
selected_tool = st.sidebar.radio("TOOLS", menu_categories[selected_category])

st.sidebar.markdown("---")
st.sidebar.caption(f"v2.1.0 | {datetime.date.today().strftime('%b %d, %Y')}")

# --- Client Context Banner ---
def render_client_banner():
    snapshot = st.session_state.client_snapshot
    if not snapshot["client_name"]:
        name_display = "No Client Selected"
    else:
        name_display = snapshot["client_name"]
    
    st.markdown(
        f"""
        <div class="client-context-banner">
            <div>
                <div class="client-name">{name_display}</div>
            </div>
            <div style="text-align: right; color: var(--text-secondary);">
                <span style="margin-right: 15px;">Age: <strong>{snapshot.get('age', '--')}</strong></span>
                <span>Monthly Income: <strong>R {snapshot.get('household_income', 0):,.0f}</strong></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

render_client_banner()

# --- Main Content Router ---

if selected_tool == "Client Details":
    st.markdown("## Client Profile")
    st.markdown(
        """
        <div class="nav-card">
            <h3>Global Client Settings</h3>
            <p style="color: var(--text-secondary);">
                Enter client information here once. These details will automatically populate all calculators and tools.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("client_global_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Personal Details")
            new_name = st.text_input("Full Name", value=st.session_state.client_snapshot["client_name"])
            new_age = st.number_input("Current Age", min_value=0, max_value=120, value=int(st.session_state.client_snapshot["age"]))
            new_ret_age = st.number_input("Target Retirement Age", min_value=0, max_value=120, value=int(st.session_state.client_snapshot.get("retirement_age", 65)))
            
        with col2:
            st.subheader("Financial Overview")
            new_income = st.number_input("Gross Monthly Household Income (R)", min_value=0.0, step=1000.0, value=float(st.session_state.client_snapshot["household_income"]))
            new_savings = st.number_input("Current Total Savings/Investments (R)", min_value=0.0, step=1000.0, value=float(st.session_state.client_snapshot.get("savings_balance", 0.0)))
            new_dependants = st.number_input("Number of Dependants", min_value=0, step=1, value=int(st.session_state.client_snapshot.get("dependants", 0)))

        if st.form_submit_button("Save Client Profile", type="primary"):
            st.session_state.client_snapshot.update({
                "client_name": new_name,
                "age": new_age,
                "retirement_age": new_ret_age,
                "household_income": new_income,
                "savings_balance": new_savings,
                "dependants": new_dependants
            })
            st.success("Client profile updated successfully!")
            st.rerun()

elif selected_tool == "Advisor Brief":
    advisor_brief.show()
elif selected_tool == "Salary Calculator":
    salary_calculator.show()
elif selected_tool == "Budget Tool":
    budget_tool.show()
elif selected_tool == "Retirement Calculator":
    retirement_calculator.show()
elif selected_tool == "Everest Wealth":
    everest_wealth.show()
elif selected_tool == "RA Calculator":
    ra_calculator.show()
elif selected_tool == "Risk Profiler":
    risk_profiler.show()
elif selected_tool == "Life Cover Gap":
    life_cover_gap.show()
elif selected_tool == "Estate Liquidity":
    estate_liquidity.show()
