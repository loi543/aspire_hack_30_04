# app.py
import streamlit as st
import matplotlib.pyplot as plt
from datetime import date
import numpy as np

# — 1. PAGE CONFIG (only once, first thing) —
st.set_page_config(
    page_title="Multi-Persona Savings App",
    page_icon="💰",
    layout="centered"
)

# — 2. INITIALIZE SESSION STATE —
if "personal_goal_count" not in st.session_state:
    st.session_state.personal_goal_count = 0
if "collective_goal_count" not in st.session_state:
    st.session_state.collective_goal_count = 0

# — 3. SIDEBAR: PERSONA SELECTOR —
persona = st.sidebar.selectbox("Who are you?", ["Grandparent", "Parent", "Child"])

# — 4. MAIN TITLE & INSTRUCTIONS —
st.title("🏦 Savings Goals Dashboard")
st.write(
    "Add your **Personal Goals** or join **Collective Goals** — click any goal to expand for details, "
    "insights, and projections."
)

# — 5. TABS FOR PERSONAL VS COLLECTIVE —
tab_personal, tab_collective = st.tabs(["💼 Personal Goals", "🤝 Collective Goals"])

# ----- PERSONAL GOALS TAB -----
with tab_personal:
    st.header("Your Personal Goals")
    if st.button("➕ Add a personal goal"):
        st.session_state.personal_goal_count += 1
        i = st.session_state.personal_goal_count
        # initialize defaults
        st.session_state[f"pg_name_{i}"] = f"Goal {i}"
        st.session_state[f"pg_target_{i}"] = 1000.0
        st.session_state[f"pg_current_{i}"] = 0.0
        st.session_state[f"pg_monthly_{i}"] = 50.0
        st.session_state[f"pg_product_{i}"] = "Regular (2%)"

    rate_map = {
        "Regular (2%)": 0.02,
        "Cash ISA (1.5%)": 0.015,
        "Stocks & Shares ISA (5%)": 0.05
    }

    for i in range(1, st.session_state.personal_goal_count + 1):
        goal_label = st.session_state[f"pg_name_{i}"]
        with st.expander(f"📌 {goal_label}", expanded=False):
            name = st.text_input("Goal name", key=f"pg_name_{i}")
            product = st.selectbox(
                "Savings product",
                list(rate_map.keys()),
                key=f"pg_product_{i}"
            )
            rate = rate_map[product]

            target = st.number_input(
                "Target amount (£)",
                min_value=0.0,
                step=100.0,
                key=f"pg_target_{i}"
            )
            current = st.number_input(
                "Current saved (£)",
                min_value=0.0,
                step=10.0,
                key=f"pg_current_{i}"
            )
            monthly = st.number_input(
                "Monthly contribution (£)",
                min_value=0.0,
                step=10.0,
                key=f"pg_monthly_{i}"
            )

            # Progress bar & % reached
            progress = (current / target) if target > 0 else 0
            st.progress(min(progress, 1.0))
            st.write(f"**{progress*100:,.1f}%** of your target reached.")

            # Estimate months to goal
            if monthly > 0 and rate >= 0:
                r = rate / 12
                A = current
                P = monthly
                # Define FV difference
                def fv_diff(n):
                    return A*(1+r)**n + P*(((1+r)**n - 1)/r) - target
                # Bisection between 0 and 600 months
                low, high = 0, 600
                for _ in range(50):
                    mid = (low + high) / 2
                    if fv_diff(mid) < 0:
                        low = mid
                    else:
                        high = mid
                st.write(
                    f"At **£{monthly}/mo** and **{rate*100:.1f}%** p.a., "
                    f"you’ll hit this goal in **{high:,.0f} months**."
                )
            else:
                st.info("Enter a monthly contribution to see time-to-goal.")

# ----- COLLECTIVE GOALS TAB -----
with tab_collective:
    st.header("Shared Collective Goals")
    if st.button("➕ Add a collective goal"):
        st.session_state.collective_goal_count += 1
        j = st.session_state.collective_goal_count
        st.session_state[f"cg_name_{j}"] = f"Group Goal {j}"
        st.session_state[f"cg_target_{j}"] = 2000.0
        st.session_state[f"cg_deadline_{j}"] = date.today()
        for r in ["Grandparent", "Parent", "Child"]:
            st.session_state[f"cg_cont_{j}_{r}"] = 0.0

    for j in range(1, st.session_state.collective_goal_count + 1):
        goal_label = st.session_state[f"cg_name_{j}"]
        with st.expander(f"🌐 {goal_label}", expanded=False):
            name = st.text_input("Goal name", key=f"cg_name_{j}")
            target = st.number_input(
                "Target amount (£)",
                min_value=0.0,
                step=100.0,
                key=f"cg_target_{j}"
            )
            deadline = st.date_input(
                "Deadline",
                key=f"cg_deadline_{j}"
            )

            # Gather each persona's contribution
            contribs = {}
            for r in ["Grandparent", "Parent", "Child"]:
                contribs[r] = st.number_input(
                    f"{r}'s contribution (£)",
                    min_value=0.0,
                    step=10.0,
                    key=f"cg_cont_{j}_{r}"
                )

            total = sum(contribs.values())
            days_left = (deadline - date.today()).days

            # Metrics row
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Your share", f"£{contribs[persona]:,.2f}")
            c2.metric("Total saved", f"£{total:,.2f}")
            c3.metric("Target", f"£{target:,.2f}")
            c4.metric("Days left", days_left)

            # Pie chart breakdown
            if total > 0:
                fig, ax = plt.subplots()
                ax.pie(
                    list(contribs.values()),
                    labels=list(contribs.keys()),
                    autopct="%1.1f%%"
                )
                ax.set_title("Contribution Breakdown")
                st.pyplot(fig)
            else:
                st.info("No contributions yet – update above to see the pie chart.")

            # Completion status
            if total < target:
                st.warning(f"£{target - total:,.2f} still needed to hit this collective goal.")
            else:
                st.success("🎉 This collective goal is fully funded!")

# — END OF APP —

