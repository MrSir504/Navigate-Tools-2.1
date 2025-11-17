import streamlit as st
import plotly.graph_objects as go

QUESTIONS = [
    ("Time horizon for this money?", ["<3 years", "3-5 years", "5-10 years", "10+ years"], [0, 2, 4, 6]),
    ("Primary goal?", ["Preserve capital", "Income & low volatility", "Balanced growth", "Max growth"], [0, 2, 4, 6]),
    ("Comfort with drawdowns?", ["<5%", "5-10%", "10-20%", "20%+"], [0, 2, 4, 6]),
    ("Reaction to a 15% drop?", ["Sell to stop loss", "Reduce exposure", "Hold", "Buy more"], [0, 1, 4, 6]),
    ("Experience with markets?", ["None", "Some funds", "Multi-asset / ETFs", "Direct equities / struct products"], [0, 2, 4, 6]),
    ("Liquidity need?", ["Need access monthly", "Quarterly", "Annually", "Can lock for 3+ yrs"], [0, 1, 3, 5]),
]

PROFILES = [
    ("Conservative", 0, 8, 20, "Protect capital, lower volatility, income focus."),
    ("Cautious", 9, 14, 35, "Some growth with downside buffers; diversify with income assets."),
    ("Balanced", 15, 20, 55, "Blend growth and stability; multi-asset high equity."),
    ("Growth", 21, 26, 70, "Long horizon, accepts volatility; equity-led."),
    ("Aggressive", 27, 36, 85, "Maximise growth; concentrated equity/alternatives appropriate."),
]


def get_profile(score: int):
    for name, low, high, equity, note in PROFILES:
        if low <= score <= high:
            return {"name": name, "equity": equity, "note": note}
    return {"name": "Aggressive", "equity": 85, "note": "Maximise growth; concentrated equity/alternatives appropriate."}


def show():
    snapshot = st.session_state.get("client_snapshot", {})
    st.markdown(
        """
        <div class="nw-card">
            <h3>Risk Profiler</h3>
            <p style="color: var(--muted);">
                Quick appetite scan to anchor your portfolio conversation. Scores map to suggested equity exposure and talking points.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1.2, 1])
    with c1:
        name = st.text_input("Client", value=snapshot.get("client_name", "Client"))
        default_age = snapshot.get("age", 40)
        try:
            default_age = int(default_age)
        except (TypeError, ValueError):
            default_age = 40
        age = st.number_input("Age", min_value=0, max_value=120, value=default_age, key="risk_profiler_age")
    with c2:
        context = st.text_area("Context / scenario", value="Retirement investing; RA/living annuity blend.", height=70)

    st.markdown("### Questionnaire")
    st.caption("Answer together with the client; bolder styling keeps it readable in bright rooms.")
    st.markdown('<div class="nw-card risk-qs">', unsafe_allow_html=True)
    score = 0
    for idx, (prompt, options, weights) in enumerate(QUESTIONS):
        choice = st.radio(prompt, options, key=f"risk_q{idx}", horizontal=True)
        score += weights[options.index(choice)]
    st.markdown("</div>", unsafe_allow_html=True)

    profile = get_profile(score)

    st.markdown("### Result")
    col_a, col_b = st.columns([1.1, 0.9])
    with col_a:
        st.metric("Profile", profile["name"], help=profile["note"])
        st.metric("Suggested equity allocation", f"{profile['equity']}%")
        st.write(f"**Talking point:** {profile['note']}")
        st.write(f"**Score:** {score} / 36")
        st.caption("Use this as a guide; adjust for regulation, objectives, and liquidity constraints.")
    with col_b:
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=profile["equity"],
                number={"suffix": "%", "font": {"size": 44, "color": "#0f172a"}},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "#2dd4bf", "thickness": 0.26},
                    "steps": [
                        {"range": [0, 20], "color": "rgba(45,212,191,0.24)"},
                        {"range": [20, 40], "color": "rgba(45,212,191,0.16)"},
                        {"range": [40, 60], "color": "rgba(59,130,246,0.16)"},
                        {"range": [60, 80], "color": "rgba(59,130,246,0.24)"},
                        {"range": [80, 100], "color": "rgba(59,130,246,0.3)"},
                    ],
                    "bgcolor": "rgba(255,255,255,0.85)",
                },
                title={"text": "Equity tilt guidance"},
            )
        )
        fig.update_layout(
            height=280,
            margin=dict(l=30, r=30, t=40, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#0f172a",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Next steps")
    st.write(
        "- Map to product: choose multi-asset/regulation-compliant funds that match this equity tilt.\n"
        "- Revisit with life events: marriage, new business, near-retirement.\n"
        "- Stress-test plan: 20% drawdown scenario and liquidity needs."
    )
