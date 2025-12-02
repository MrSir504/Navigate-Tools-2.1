import io
import datetime
import streamlit as st
import pandas as pd
from fpdf import FPDF
import re


def pdf_safe(text: str) -> str:
    """Ensure strings are Latin-1 safe for built-in FPDF fonts."""
    return str(text or "-").encode("latin-1", "replace").decode("latin-1")


def compute_snowball_schedule(debts, monthly_payment):
    """Simple avalanche payoff schedule (highest rate first)."""
    schedule = []
    order = sorted(debts, key=lambda d: d["rate"], reverse=True)
    month = 0
    remaining = [{"rate": d["rate"], "bal": d["bal"]} for d in order]
    while remaining and month < 600:  # cap to avoid infinite loops
        month += 1
        payment = monthly_payment
        for d in remaining:
            if d["bal"] <= 0:
                continue
            interest = d["bal"] * (d["rate"] / 100) / 12
            applied = min(payment, d["bal"] + interest)
            principal = max(0, applied - interest)
            d["bal"] = max(0, d["bal"] + interest - applied)
            payment = max(0, payment - applied)
        remaining = [d for d in remaining if d["bal"] > 1]
        if month % 1 == 0:
            schedule.append(
                {
                    "Month": month,
                    **{f"Debt{i+1} (R)": rem.get("bal", 0) for i, rem in enumerate(order[:3])},
                    "Total remaining (R)": sum(d["bal"] for d in remaining),
                }
            )
        if not remaining:
            break
    payoff_months = month
    return schedule, payoff_months


def build_pdf(data: dict, snowball_summary: str = "") -> bytes:
    def soften_line(text: str) -> str:
        """Break up very long tokens/URLs so FPDF can wrap safely."""
        tokens = re.split(r"(\s+)", pdf_safe(text))
        softened = []
        for tok in tokens:
            if tok.isspace():
                softened.append(tok)
                continue
            if len(tok) > 60:
                chunks = [tok[i : i + 25] for i in range(0, len(tok), 25)]
                softened.append(" ".join(chunks))
            else:
                softened.append(tok)
        return "".join(softened).replace("\n", " / ").replace("\r", " / ")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "Advisor Brief", ln=1)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, pdf_safe(f"Client: {data['Client']} | Age: {data['Age']} | Focus: {data['Focus']}"), ln=1)
    pdf.cell(0, 8, pdf_safe(f"Prepared: {data['Prepared']} | Next meeting: {data['Next meeting']}"), ln=1)
    pdf.ln(4)

    def line(label, value):
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(60, 8, f"{label}:")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, str(value), ln=1)

    line("Household income (R/mo)", f"{data['Household income (R/month)']:,.0f}")
    line("Fixed expenses (R/mo)", f"{data['Fixed expenses (R/month)']:,.0f}")
    line("Debt repayments (R/mo)", f"{data['Debt repayments (R/month)']:,.0f}")
    line("Free cash (R/mo)", f"{data['Free cash (R/month)']:,.0f}")
    line("Savings rate (%)", f"{data['Savings rate (%)']:.1f}%")
    line("Debt-to-income (%)", f"{data['Debt-to-income (%)']:.1f}%")
    line("Emergency fund (R)", f"{data['Emergency fund (R)']:,.0f}")
    line("Target cushion (R)", f"{data['Target cushion (R)']:,.0f}")
    line("Cushion gap (R)", f"{data['Cushion gap (R)']:,.0f}")
    if snowball_summary:
        line("Debt payoff", snowball_summary)
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Meeting notes / objections", ln=1)
    pdf.set_font("Helvetica", "", 11)
    line_width = getattr(pdf, "epw", pdf.w - 2 * pdf.l_margin)
    pdf.multi_cell(line_width, 7, soften_line(data["Notes"]))
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Action items", ln=1)
    pdf.set_font("Helvetica", "", 11)
    for idx, act in enumerate(data["Actions"], start=1):
        safe_act = soften_line(act)
        pdf.multi_cell(line_width, 6, soften_line(f"{idx}. {safe_act}"))
    raw_output = pdf.output(dest="S")
    # fpdf2 may return str or bytearray depending on version
    if isinstance(raw_output, str):
        pdf_output = raw_output.encode("latin-1")
    elif isinstance(raw_output, (bytes, bytearray)):
        pdf_output = bytes(raw_output)
    else:
        pdf_output = b""
    return pdf_output


def show():
    """Advisor-ready one-pager: snapshot, quick ratios, notes, actions, and exports."""
    snap = st.session_state.get("client_snapshot", {})
    client_name = snap.get("client_name", "")
    today = datetime.date.today().strftime("%Y-%m-%d")

    st.markdown(
        """
        <div class="nav-card">
            <h3>Advisor Brief</h3>
            <p style="color: var(--muted);">
                Use this as a pre-meeting cockpit: verify snapshot data, check affordability, capture notes/actions,
                and export a branded one-pager (Excel or PDF).
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
        age_default = snap.get("age", 38)
        try:
            age_default = int(age_default)
        except (TypeError, ValueError):
            age_default = 38
        age = st.number_input("Age", min_value=0, max_value=120, value=age_default, step=1, key="brief_age")
        meeting_focus = st.selectbox(
            "Focus",
            ["Cash flow", "Tax & RA", "Retirement gap", "Estate", "Proposal / Quote"],
            index=["Cash flow", "Tax & RA", "Retirement gap", "Estate", "Proposal / Quote"].index(snap.get("meeting_focus", "Cash flow"))
            if snap.get("meeting_focus") in ["Cash flow", "Tax & RA", "Retirement gap", "Estate", "Proposal / Quote"] else 0,
        )
    with c2:
        monthly_income = st.number_input(
            "Household income (R / month)", min_value=0, step=500, value=int(snap.get("household_income", 45000))
        )
        fixed_expenses = st.number_input("Fixed expenses (R / month)", min_value=0, step=500, value=22000)
        debt_repayments = st.number_input("Debt repayments (R / month)", min_value=0, step=500, value=6000)
    with c3:
        cash_on_hand = st.number_input("Emergency fund on hand (R)", min_value=0, step=1000, value=30000)
        goal_months_cushion = st.slider("Target months of cushion", 1, 12, 6)
        notes = st.text_area("Meeting notes / objections", value=snap.get("notes", ""), height=110)

    # Quick ratios
    free_cash = max(0, monthly_income - fixed_expenses - debt_repayments)
    savings_rate = (free_cash / monthly_income * 100) if monthly_income else 0
    dti_ratio = (debt_repayments / monthly_income * 100) if monthly_income else 0
    target_cushion = goal_months_cushion * (fixed_expenses + debt_repayments)
    cushion_gap = target_cushion - cash_on_hand

    st.markdown("### Health check")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Savings rate", f"{savings_rate:.1f}%")
    k2.metric("Debt-to-income", f"{dti_ratio:.1f}%")
    k3.metric("Cushion target", f"R {target_cushion:,.0f}", delta=f"Gap R {cushion_gap:,.0f}" if cushion_gap > 0 else "Met")
    k4.metric("Free cash / mo", f"R {free_cash:,.0f}")

    st.markdown("### Emergency fund & debt snowball")
    ef_col, debt_col = st.columns(2)
    with ef_col:
        monthly_top_up = st.number_input("Amount you can save monthly (R)", min_value=0, step=500, value=int(free_cash))
        months_to_target = (cushion_gap / monthly_top_up) if monthly_top_up > 0 and cushion_gap > 0 else 0
        st.info(f"~{months_to_target:.1f} months to hit cushion target at this savings rate." if cushion_gap > 0 else "Target met.")
    with debt_col:
        st.caption("Enter up to 3 debts to prioritize snowball/avalanche.")
        debts = []
        for i in range(3):
            c_apr, c_bal = st.columns(2)
            with c_apr:
                rate = st.number_input(f"Debt {i+1} rate (%)", min_value=0.0, max_value=40.0, value=14.0, step=0.5, key=f"debt_rate_{i}")
            with c_bal:
                bal = st.number_input(f"Debt {i+1} balance (R)", min_value=0.0, step=1000.0, value=0.0, key=f"debt_bal_{i}")
            if bal > 0:
                debts.append({"rate": rate, "bal": bal})
        snowball_schedule = []
        payoff_months = None
        if debts and monthly_top_up > 0:
            snowball_schedule, payoff_months = compute_snowball_schedule(debts, monthly_top_up + debt_repayments)
            st.write(f"Estimated payoff if you direct R {monthly_top_up + debt_repayments:,.0f}/mo (incl. current repayments): ~{payoff_months} months.")
            if snowball_schedule:
                st.dataframe(pd.DataFrame(snowball_schedule).head(24), use_container_width=True)
        elif debts:
            st.write("Enter a monthly amount to compute payoff timeline.")

    st.markdown("### Actions")
    with st.form("advisor_actions"):
        col_a, col_b = st.columns(2)
        with col_a:
            action1 = st.text_input("Action 1", value="Confirm payslip + medical aid details")
            action2 = st.text_input("Action 2", value="Model RA top-up for tax efficiency")
            action3 = st.text_input("Action 3", value="Stress-test retirement income drawdown")
        with col_b:
            action4 = st.text_input("Action 4", value="Check estate liquidity & fees")
            action5 = st.text_input("Action 5", value="Compare Everest options vs fee layers")
            next_meeting = st.date_input("Next meeting", value=datetime.date.today() + datetime.timedelta(days=14))
        submitted = st.form_submit_button("Save / refresh summary", type="primary")

    if submitted:
        st.success("Brief updated.")

    st.markdown("### Export one-pager")
    export_data = {
        "Client": client_name,
        "Age": age,
        "Focus": meeting_focus,
        "Household income (R/month)": monthly_income,
        "Fixed expenses (R/month)": fixed_expenses,
        "Debt repayments (R/month)": debt_repayments,
        "Free cash (R/month)": free_cash,
        "Savings rate (%)": savings_rate,
        "Debt-to-income (%)": dti_ratio,
        "Emergency fund (R)": cash_on_hand,
        "Target cushion (R)": target_cushion,
        "Cushion gap (R)": cushion_gap,
        "Notes": notes,
        "Actions": [
            action1, action2, action3, action4, action5
        ],
        "Next meeting": next_meeting.strftime("%Y-%m-%d"),
        "Prepared": today,
    }

    buffer = io.BytesIO()
    df_main = pd.DataFrame([{
        key: val for key, val in export_data.items() if key != "Actions"
    }])
    df_actions = pd.DataFrame({"Action items": export_data["Actions"]})
    df_debts = pd.DataFrame(debts) if debts else pd.DataFrame()
    df_schedule = pd.DataFrame(snowball_schedule) if snowball_schedule else pd.DataFrame()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_main.to_excel(writer, index=False, sheet_name="Advisor Brief")
        df_actions.to_excel(writer, index=False, sheet_name="Action Items")
        if not df_debts.empty:
            df_debts.to_excel(writer, index=False, sheet_name="Debts")
        if not df_schedule.empty:
            df_schedule.to_excel(writer, index=False, sheet_name="Debt Snowball")
    buffer.seek(0)
    st.download_button(
        "Download brief (Excel)",
        data=buffer,
        file_name="advisor_brief.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    snowball_summary = f"~{payoff_months} months to clear debts @ R {monthly_top_up + debt_repayments:,.0f}/mo" if payoff_months else ""
    pdf_bytes = build_pdf(export_data, snowball_summary=snowball_summary)
    st.download_button(
        "Download PDF",
        data=pdf_bytes,
        file_name="advisor_brief.pdf",
        mime="application/pdf",
    )
