import streamlit as st

import budget_tool
import estate_liquidity
import everest_wealth
import ra_calculator
import retirement_calculator
import salary_calculator
import advisor_brief
import risk_profiler
import life_cover_gap


st.set_page_config(
    page_title="Navigate Wealth | Advisor Toolkit",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_global_styles():
    """Injects global styles from the style.css file."""
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


inject_global_styles()

TOOL_DETAILS = {
    "Budget Tool": "Cash flow & savings rate",
    "Advisor Brief": "Snapshot, notes, export",
    "Salary Tax Calculator": "PAYE, UIF, medical credits",
    "Retirement Calculator": "Income goal vs drawdown",
    "RA Tax Rebate Calculator": "Deductible cap & uplift",
    "Estate Liquidity Tool": "Liquidity & executor fees",
    "Everest Wealth": "Onyx/Strategic quote",
    "Risk Profiler": "Risk appetite & equity tilt",
    "Life Cover Gap": "Life/DI/CI need vs cover",
}


if "active_tool" not in st.session_state:
    st.session_state.active_tool = "Showcase"


def launchpad():
    """Creates a launchpad for the application."""
    st.markdown(
        '<div class="nw-section-title"><span class="nw-dot"></span>Choose a workspace</div>',
        unsafe_allow_html=True,
    )

    icons = {
        "Budget Tool": "📊",
        "Advisor Brief": "📝",
        "Salary Tax Calculator": "💵",
        "Retirement Calculator": "📈",
        "RA Tax Rebate Calculator": "💰",
        "Estate Liquidity Tool": "🏡",
        "Everest Wealth": "🏔️",
        "Risk Profiler": "🎯",
        "Life Cover Gap": "❤️",
    }

    cols = st.columns(3)
    for i, (tool, desc) in enumerate(TOOL_DETAILS.items()):
        with cols[i % 3]:
            if st.button(f"{icons.get(tool, '💼')} {tool}\n\n{desc}", key=f"tool_{tool}", use_container_width=True):
                st.session_state.active_tool = tool
                st.rerun()


def init_snapshot_state() -> None:
    """Initializes the client snapshot in the session state."""
    if "client_snapshot" not in st.session_state:
        st.session_state.client_snapshot = {
            "client_name": "Client",
            "advisor_name": "Advisor",
            "age": 38,
            "household_income": 45000,
            "meeting_focus": "Cash flow & salary",
            "notes": "",
        }
    if "active_preset" not in st.session_state:
        st.session_state.active_preset = "Custom"


def apply_preset(preset: str) -> None:
    """Applies a preset to the client snapshot."""
    presets = {
        "Young Professional": {
            "client_name": "Young Pro",
            "age": 30,
            "household_income": 42000,
            "meeting_focus": "Cash flow & salary",
            "notes": "Early career; maximize tax benefits.",
        },
        "Family Builder": {
            "client_name": "Family",
            "age": 40,
            "household_income": 65000,
            "meeting_focus": "Retirement gap",
            "notes": "School fees; protect income; grow RA.",
        },
        "Pre-Retiree": {
            "client_name": "Pre-Retiree",
            "age": 58,
            "household_income": 90000,
            "meeting_focus": "Retirement gap",
            "notes": "Sequence risk; drawdown strategy.",
        },
        "Business Owner": {
            "client_name": "Business Owner",
            "age": 45,
            "household_income": 120000,
            "meeting_focus": "Estate & protection",
            "notes": "Liquidity for estate + key person cover.",
        },
    }
    if preset in presets:
        for key, val in presets[preset].items():
            st.session_state.client_snapshot[key] = val
        st.session_state.active_preset = preset
    else:
        st.session_state.active_preset = "Custom"


def header():
    """Creates a header for the application."""
    st.image("logo.png", width=220)
    st.markdown(
        """
        <div class="hero-panel">
            <div class="hero-pill">Broker dashboard</div>
            <h1 style="margin: 0.35rem 0 0;">Navigate Wealth Advisor Toolkit</h1>
            <p style="margin: 0.35rem 0 0; color: #4b5563; font-size: 1.02rem;">
                A modern toolkit for financial advisors in South Africa — snapshot once, run every tool with context.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Suggested Meeting Flow"):
        st.markdown(
            """
            1.  **Payslip & cash flow:** Salary Tax → Budget to surface free cash.
            2.  **Goal gap:** Retirement for drawdown lens; add RA uplift if needed.
            3.  **Protection:** Estate Liquidity to show executor fees/duty & shortfalls.
            4.  **Product:** Everest for Onyx/Strategic quote with broker fee compare.
            """
        )


def client_snapshot_panel():
    """Creates a client snapshot panel for the application."""
    with st.expander("Client Snapshot", expanded=True):
        snap = st.session_state.client_snapshot
        preset_col, c1, c2, c3, c4 = st.columns([0.7, 1.2, 0.7, 1, 1], gap="medium")
        with preset_col:
            preset_choice = st.selectbox(
                "Persona",
                ["Custom", "Young Professional", "Family Builder", "Pre-Retiree", "Business Owner"],
                index=["Custom", "Young Professional", "Family Builder", "Pre-Retiree", "Business Owner"].index(
                    st.session_state.active_preset
                )
                if st.session_state.active_preset in ["Custom", "Young Professional", "Family Builder", "Pre-Retiree", "Business Owner"]
                else 0,
            )
            if preset_choice != st.session_state.active_preset:
                apply_preset(preset_choice)
                snap = st.session_state.client_snapshot
        with c1:
            snap["client_name"] = st.text_input("Client name", value=snap["client_name"])
            snap["advisor_name"] = st.text_input("Advisor (for exports)", value=snap["advisor_name"])
        with c2:
            snap["age"] = st.number_input("Age", min_value=0, max_value=120, value=snap["age"])
            snap["meeting_focus"] = st.selectbox(
                "Meeting focus",
                ["Cash flow & salary", "Retirement gap", "Estate & protection", "Investment proposal", "Everest quote"],
                index=["Cash flow & salary", "Retirement gap", "Estate & protection", "Investment proposal", "Everest quote"].index(snap["meeting_focus"])
                if snap.get("meeting_focus") in [
                    "Cash flow & salary",
                    "Retirement gap",
                    "Estate & protection",
                    "Investment proposal",
                    "Everest quote",
                ] else 0,
            )
        with c3:
            snap["household_income"] = st.number_input(
                "Household monthly income (R)", min_value=0, step=1000, value=int(snap["household_income"])
            )
            st.caption("Used as a default for cash flow, retirement and tax tools.")
        with c4:
            snap["notes"] = st.text_area("Prep notes / objections", value=snap["notes"], height=96)
        st.session_state.client_snapshot = snap





def main():
    """Main function to run the Streamlit application."""
    init_snapshot_state()

    header()
    client_snapshot_panel()

    st.markdown("---")

    with st.sidebar:
        st.markdown("#### Navigation")
        sidebar_options = ["Showcase"] + list(TOOL_DETAILS.keys())
        
        # Get the index of the active tool, or default to 0 if not found
        try:
            active_index = sidebar_options.index(st.session_state.get("active_tool", "Showcase"))
        except ValueError:
            active_index = 0

        # Use a callback to update the active tool
        def on_change():
            st.session_state.active_tool = st.session_state.sidebar_radio
        
        st.radio(
            "Workspace", 
            sidebar_options, 
            index=active_index, 
            key="sidebar_radio",
            on_change=on_change
        )
        st.divider()
        st.caption("Client snapshot feeds defaults into tools.")

    active_tool = st.session_state.get("active_tool", "Showcase")

    if active_tool == "Showcase":
        launchpad()
    else:
        st.header(active_tool)
        if active_tool == "Budget Tool":
            budget_tool.show()
        elif active_tool == "Advisor Brief":
            advisor_brief.show()
        elif active_tool == "Risk Profiler":
            risk_profiler.show()
        elif active_tool == "Estate Liquidity Tool":
            estate_liquidity.show()
        elif active_tool == "Everest Wealth":
            everest_wealth.show()
        elif active_tool == "RA Tax Rebate Calculator":
            ra_calculator.show()
        elif active_tool == "Retirement Calculator":
            retirement_calculator.show()
        elif active_tool == "Salary Tax Calculator":
            salary_calculator.show()
        elif active_tool == "Life Cover Gap":
            life_cover_gap.show()

if __name__ == "__main__":
    main()
