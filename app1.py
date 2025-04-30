# app.py

import streamlit as st
import matplotlib.pyplot as plt
from datetime import date
from dateutil.relativedelta import relativedelta

# 1) PAGE CONFIG
st.set_page_config(
    page_title="All Savings Goals",
    page_icon="💰",
    layout="centered"
)

# 2) SESSION-STATE INIT
if "pg_count" not in st.session_state:
    st.session_state["pg_count"] = 0
if "cg_count" not in st.session_state:
    st.session_state["cg_count"] = 0

# 3) CONSTANTS
STATIC_ROLES = ["Grandparent", "Parent", "Child"]
RATE_MAP = {
    "Regular (2%)": 0.02,
    "Cash ISA (1.5%)": 0.015,
    "Stocks & Shares ISA (5%)": 0.05
}

# 4) INITIALIZE ANY EXISTING GOALS TO AVOID KeyError
for i in range(1, st.session_state["pg_count"] + 1):
    st.session_state.setdefault(f"pg_owner_{i}", "")
    st.session_state.setdefault(f"pg_name_{i}", f"Personal Goal {i}")
    st.session_state.setdefault(f"pg_target_{i}", 1000.0)
    st.session_state.setdefault(f"pg_current_{i}", 0.0)
    st.session_state.setdefault(f"pg_monthly_{i}", 50.0)
    st.session_state.setdefault(f"pg_product_{i}", list(RATE_MAP.keys())[0])

for j in range(1, st.session_state["cg_count"] + 1):
    st.session_state.setdefault(f"cg_name_{j}", f"Group Goal {j}")
    st.session_state.setdefault(f"cg_target_{j}", 2000.0)
    st.session_state.setdefault(f"cg_deadline_{j}", date.today())
    st.session_state.setdefault(f"cg_participants_{j}", [])

# 5) “Your role” DROPDOWN DYNAMICALLY INCLUDES ANY CUSTOM NAMES
dynamic_names = []
for j in range(1, st.session_state["cg_count"] + 1):
    dynamic_names += st.session_state[f"cg_participants_{j}"]
persona_options = STATIC_ROLES + [
    n for n in dict.fromkeys(dynamic_names) if n not in STATIC_ROLES
]
persona = st.sidebar.selectbox("Your role", persona_options)

# 6) HEADER + ADD-BUTTONS
st.title("🏦 All Savings Goals")
st.write(
    "➕ Use the buttons below to add a Personal or Collective goal.  \n"
    "You’ll only see goals that belong to (or include) your selected role/name."
)
col1, col2 = st.columns(2)
with col1:
    if st.button("➕ Add Personal Goal"):
        i = st.session_state["pg_count"] + 1
        st.session_state["pg_count"] = i
        st.session_state[f"pg_owner_{i}"]   = persona
        st.session_state[f"pg_name_{i}"]    = f"Personal Goal {i}"
        st.session_state[f"pg_target_{i}"]  = 1000.0
        st.session_state[f"pg_current_{i}"] = 0.0
        st.session_state[f"pg_monthly_{i}"] = 50.0
        st.session_state[f"pg_product_{i}"] = list(RATE_MAP.keys())[0]
with col2:
    if st.button("➕ Add Collective Goal"):
        j = st.session_state["cg_count"] + 1
        st.session_state["cg_count"] = j
        st.session_state[f"cg_name_{j}"]         = f"Group Goal {j}"
        st.session_state[f"cg_target_{j}"]       = 2000.0
        st.session_state[f"cg_deadline_{j}"]     = date.today()
        # Auto-include the creator
        st.session_state[f"cg_participants_{j}"] = [persona]

# 7) PERSONAL GOALS
st.subheader("📌 Personal Goals")
for i in range(1, st.session_state["pg_count"] + 1):
    owner = st.session_state[f"pg_owner_{i}"]
    if owner != persona:
        continue  # Only show your own

    # Collapsed header: current/target
    curr = st.session_state[f"pg_current_{i}"]
    targ = st.session_state[f"pg_target_{i}"]
    header = f"📌 {st.session_state[f'pg_name_{i}']} [{int(curr)}/{int(targ)}]"

    with st.expander(header):
        # Editable fields
        name    = st.text_input("Goal name", key=f"pg_name_{i}")
        product = st.selectbox("Product", list(RATE_MAP.keys()), key=f"pg_product_{i}")
        rate    = RATE_MAP[product]
        target  = st.number_input("Target (£)",  min_value=0.0, step=100.0, key=f"pg_target_{i}")
        current = st.number_input("Current (£)", min_value=0.0, step=10.0,  key=f"pg_current_{i}")
        monthly = st.number_input("Monthly (£)", min_value=0.0, step=10.0,  key=f"pg_monthly_{i}")

        # Progress bar & percent
        prog = current / target if target > 0 else 0
        st.progress(min(prog, 1.0))
        st.write(f"**{prog*100:.1f}%** of target reached")

        # Time-to-goal estimate (months)
        if monthly > 0:
            r = rate / 12
            A, P = current, monthly
            def fv_diff(n): return A*(1+r)**n + P*(((1+r)**n - 1)/r) - target

            low, high = 0, 600
            for _ in range(50):
                mid = (low + high) / 2
                if fv_diff(mid) < 0:
                    low = mid
                else:
                    high = mid

            st.write(
                f"At **£{monthly}/mo** & **{rate*100:.1f}%** p.a., "
                f"you’ll hit this in **{high:.0f} months**."
            )
        else:
            st.info("Enter a monthly contribution to see time-to-goal.")

# 8) COLLECTIVE GOALS
st.subheader("🌐 Collective Goals")
for j in range(1, st.session_state["cg_count"] + 1):
    name_key  = f"cg_name_{j}"
    parts_key = f"cg_participants_{j}"
    participants = st.session_state[parts_key]

    if persona not in participants:
        continue  # Only show if you’re included

    # Compute actual saved vs target for header
    target       = st.session_state[f"cg_target_{j}"]
    # Sum up each participant’s “contributed so far” values
    total_current = sum(
        st.session_state.get(f"cg_current_{j}_{idx}", 0.0)
        for idx in range(len(participants))
    )
    header = f"🌐 {st.session_state[name_key]} [{int(total_current)}/{int(target)}]"

    with st.expander(header):
        # Basic fields
        name     = st.text_input("Goal name", key=name_key)
        deadline = st.date_input("Deadline", key=f"cg_deadline_{j}")
        target   = st.number_input("Target (£)",
                                   min_value=0.0,
                                   step=100.0,
                                   key=f"cg_target_{j}")

        # Add participants
        if st.button("➕ Add participant", key=f"cg_add_part_{j}"):
            st.session_state[parts_key].append("")
        for idx, old in enumerate(st.session_state[parts_key]):
            new = st.text_input(f"Participant #{idx+1}",
                                value=old,
                                key=f"cg_part_{j}_{idx}")
            st.session_state[parts_key][idx] = new

        # Enter each person’s % share
        shares = []
        for idx, p in enumerate(st.session_state[parts_key]):
            shares.append(
                st.number_input(f"{p} share (%)",
                                min_value=0.0,
                                max_value=100.0,
                                step=1.0,
                                key=f"cg_share_{j}_{idx}")
            )
        total_pct = sum(shares)
        if participants and total_pct != 100:
            st.warning(f"Shares sum to {total_pct}%. Please adjust to 100%.")

        # Enter each person’s **actual** contributed-so-far
        currents = []
        for idx, p in enumerate(st.session_state[parts_key]):
            curr = st.number_input(f"{p} contributed so far (£)",
                                   min_value=0.0,
                                   step=10.0,
                                   key=f"cg_current_{j}_{idx}")
            currents.append(curr)
        total_current = sum(currents)

        # Months until deadline
        rd = relativedelta(st.session_state[f"cg_deadline_{j}"], date.today())
        months_left = rd.years * 12 + rd.months

        # Metrics
        c1, c2, c3, c4 = st.columns(4)
        your_idx = participants.index(persona)
        c1.metric("Your contributed",  f"£{currents[your_idx]:,.2f}")
        c2.metric("Total contributed", f"£{total_current:,.2f}")
        c3.metric("Goal target",       f"£{target:,.2f}")
        c4.metric("Months remaining",   months_left)

        # Pie chart of actual contributions
        if total_current > 0:
            fig, ax = plt.subplots()
            ax.pie(currents,
                   labels=participants,
                   autopct="%1.1f%%")
            ax.set_title("Contribution Breakdown")
            st.pyplot(fig)
        else:
            st.info("No contributions yet—enter amounts above to see the chart.")

        # Completion status
        if total_current < target:
            st.warning(f"£{target - total_current:,.2f} still needed.")
        else:
            st.success("🎉 Fully funded!")
