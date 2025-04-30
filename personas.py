# personas.py
# Keeping personas.py for potential dynamic defaults; currently static roles.

def get_persona_roles() -> list:
    """
    Returns a list of family roles (personas) available in the app.
    """
    return ["Grandparent", "Parent", "Child"]


# app.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import date
from personas import get_persona_roles

# Page config
st.set_page_config(
    page_title="Family Savings App",
    layout="centered",
    page_icon="💰"
)

# Static roles and products
roles = get_persona_roles()

savings_products = {
    "Regular Savings (2% p.a.)": 0.02,
    "Cash ISA (1% p.a.)": 0.01,
    "Stocks & Shares ISA (5% p.a.)": 0.05
}

# Projection function (used for personal & collective goals)
def project_balance(current_balance, contribution, freq_per_year, annual_rate, years):
    dates = np.arange(0, years + 1)
    cont_bal, no_cont_bal = [], []
    for t in dates:
        if annual_rate > 0:
            fv_series = contribution * (
                ((1 + annual_rate/freq_per_year)**(freq_per_year * t) - 1)
                / (annual_rate/freq_per_year)
            )
        else:
            fv_series = contribution * freq_per_year * t
        cont_bal.append(current_balance * (1 + annual_rate)**t + fv_series)
        no_cont_bal.append(current_balance * (1 + annual_rate)**t)
    return dates, cont_bal, no_cont_bal

# Sidebar: select role
with st.sidebar:
    st.title("Family Savings App")
    role = st.selectbox("Who are you?", roles)

# Main area: tabs for personal vs collective goals
tab_personal, tab_collective = st.tabs(["Personal Goals", "Collective Goals"])

# PERSONAL GOALS
with tab_personal:
    st.header(f"{role}'s Personal Goals")
    num_goals = st.number_input(
        "How many personal goals?", min_value=1, max_value=10, value=1, key="num_personal"
    )
    for i in range(num_goals):
        with st.expander(f"Personal Goal #{i+1}", expanded=(i==0)):
            name = st.text_input("Goal name", value=f"Goal {i+1}", key=f"p_name_{i}")
            target = st.number_input("Target amount (£)", min_value=0.0, value=1000.0,
                                     step=100.0, key=f"p_target_{i}")
            current = st.number_input("Current saved (£)", min_value=0.0,
                                      value=0.0, step=50.0, key=f"p_current_{i}")
            monthly_contrib = st.number_input(
                "Monthly contribution (£)", min_value=0.0,
                value=0.0, step=10.0, key=f"p_contrib_{i}"
            )
            product = st.selectbox(
                "Savings product", list(savings_products.keys()), key=f"p_prod_{i}"
            )
            years = st.slider(
                "Projection horizon (years)", 1, 30, 10, key=f"p_horizon_{i}"
            )

            # Progress tracker
            progress = min(current / target if target > 0 else 0, 1)
            st.progress(progress)
            st.write(f"**{progress*100:.1f}%** of goal reached")

            # Projections
            freq_per_year = 12  # assume monthly for personal
            rate = savings_products[product]
            dates, with_c, without_c = project_balance(
                current, monthly_contrib, freq_per_year, rate, years
            )
            final_with = with_c[-1]
            final_without = without_c[-1]
            col1, col2 = st.columns(2)
            col1.metric("Projected with contributions", f"£{final_with:,.0f}")
            col2.metric("Projected without contributions", f"£{final_without:,.0f}")
            if final_with >= target:
                st.success(f"On track to hit " + name)
            else:
                gap = target - final_with
                st.warning(f"Shortfall of £{gap:,.0f} in {years} years")

            # Plot
            fig, ax = plt.subplots()
            ax.plot(dates, with_c, label="With contributions")
            ax.plot(dates, without_c, linestyle="--", label="No contributions")
            ax.axhline(target, linestyle=":", color="gray")
            ax.set_title(name)
            ax.set_xlabel("Years")
            ax.set_ylabel("Balance (£)")
            ax.legend()
            st.pyplot(fig)

# COLLECTIVE GOALS
with tab_collective:
    st.header("Collective Goals")
    num_cgoals = st.number_input(
        "How many collective goals?", min_value=1, max_value=10, value=1, key="num_collective"
    )
    for j in range(num_cgoals):
        with st.expander(f"Collective Goal #{j+1}", expanded=(j==0)):
            cname = st.text_input("Goal name", value=f"Collective {j+1}", key=f"c_name_{j}")
            ctarget = st.number_input(
                "Target amount (£)", min_value=0.0, value=5000.0,
                step=100.0, key=f"c_target_{j}"
            )
            cdate = st.date_input(
                "Goal deadline", value=date.today(), key=f"c_date_{j}"
            )

            # Contributions by each role
            st.markdown("**Current contributions by role**")
            contribs = {r: st.number_input(
                        f"{r} saved so far (£)", min_value=0.0, value=0.0,
                        key=f"c_current_{j}_{r}") for r in roles}
            total_saved = sum(contribs.values())

            # Pie chart of shares (only if contributions exist)
            nonzero = [(r, v) for r, v in contribs.items() if v > 0]
            if nonzero:
                labels, vals = zip(*nonzero)
                fig1, ax1 = plt.subplots()
                ax1.pie(vals, labels=labels, autopct="%1.1f%%")
                ax1.set_title("Contribution Share")
                st.pyplot(fig1)
            else:
                st.info("No contributions to show yet.")

            # Countdown & remaining
            days_left = (cdate - date.today()).days
            st.write(f"**Days until deadline:** {days_left} days")
            st.write(f"**Remaining amount:** £{ctarget - total_saved:,.2f}")

            # Projection for collective goal
            st.markdown("---")
            st.markdown("**Projection for combined savings**")
            cprod = st.selectbox(
                "Savings product for projection", list(savings_products.keys()),
                key=f"c_prod_{j}"
            )
            c_monthly = sum(
                st.number_input(
                    f"{r}'s monthly contribution (£)", min_value=0.0, value=0.0,
                    key=f"c_mcontrib_{j}_{r}") for r in roles
            )
            c_years = st.slider(
                "Projection horizon (years)", 1, 30, 10, key=f"c_horizon_{j}"
            )
            freq_c = 12  # monthly contributions
            rate_c = savings_products[cprod]
            dates_c, with_cc, without_cc = project_balance(
                total_saved, c_monthly, freq_c, rate_c, c_years
            )
            final_with_c = with_cc[-1]
            col3, col4 = st.columns(2)
            col3.metric("Projected with contributions", f"£{final_with_c:,.0f}")
            col4.metric("Projected without contributions", f"£{without_cc[-1]:,.0f}")
            if final_with_c >= ctarget:
                st.success("On track for collective goal")
            else:
                gap_c = ctarget - final_with_c
                st.warning(f"Collective shortfall: £{gap_c:,.0f} in {c_years} years")

            fig2, ax2 = plt.subplots()
            ax2.plot(dates_c, with_cc, label="With contributions")
            ax2.plot(dates_c, without_cc, linestyle="--", label="No contributions")
            ax2.axhline(ctarget, linestyle=":", color="gray")
            ax2.set_title(cname)
            ax2.set_xlabel("Years")
            ax2.set_ylabel("Balance (£)")
            ax2.legend()
            st.pyplot(fig2)

