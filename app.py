# app.py
import io
from datetime import date, timedelta

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF

# ---------- Page config ----------
st.set_page_config(page_title="Travel Budget Planner", page_icon="🧳", layout="wide")

# ---------- Helpers ----------
def normalize_weights(weights: dict) -> dict:
    total = sum(weights.values())
    if total == 0:
        # avoid div-by-zero: default to equal
        n = len(weights)
        return {k: 100 / n for k in weights}
    return {k: (v / total) * 100 for k, v in weights.items()}

def money(amount, currency):
    # lightweight formatter (no fx conversion here)
    return f"{currency} {amount:,.2f}"

def build_allocation_df(alloc_pct: dict, total_budget: float, currency: str):
    rows = []
    for k, pct in alloc_pct.items():
        amt = total_budget * (pct / 100)
        rows.append({"Category": k, "Share %": round(pct, 1), "Amount": money(amt, currency)})
    df = pd.DataFrame(rows).sort_values("Share %", ascending=False)
    return df

def per_day_breakdown(alloc_pct: dict, total_budget: float, days: int):
    # returns {cat: amount_per_day}
    return {k: (total_budget * (v / 100)) / max(1, days) for k, v in alloc_pct.items()}

def safe_int(x, minimum=1):
    try:
        v = int(x)
        return max(minimum, v)
    except Exception:
        return minimum

def generate_itinerary(days: int, destination: str, budget_per_day: float):
    # very simple offline generator; you can swap with Google Places later
    # picks ideas based on rough budget bands
    ideas_low = [
        "Self-guided city walk",
        "Local street food tour",
        "Public park & viewpoint",
        "Free museum/gallery day",
        "Beach sunset & night market",
    ]
    ideas_mid = [
        "Guided city tour",
        "Cultural show or cooking class",
        "Day-pass for metro/transport",
        "Boat ride / short cruise",
        "Museum + specialty café",
    ]
    ideas_high = [
        "Theme park or adventure activity",
        "Full-day guided excursion",
        "Scenic railway or hot air balloon (location permitting)",
        "Private food tasting tour",
        "Fine dining experience",
    ]

    plan = []
    for d in range(1, days + 1):
        if budget_per_day < 50:
            picks = np.random.choice(ideas_low, size=2, replace=False)
        elif budget_per_day < 120:
            picks = np.random.choice(ideas_mid, size=2, replace=False)
        else:
            picks = np.random.choice(ideas_high, size=2, replace=False)

        plan.append(
            {
                "Day": d,
                "Morning": picks[0],
                "Afternoon/Evening": picks[1],
                "Notes": f"Adjust based on {destination} opening times."
            }
        )
    return pd.DataFrame(plan)

def build_pdf(data: dict, alloc_df: pd.DataFrame, itin_df: pd.DataFrame) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Travel Budget Plan", ln=True)

    # Trip summary
    pdf.set_font("Arial", "", 12)
    for k, v in [
        ("Destination", data["destination"]),
        ("Dates", f'{data["start"].isoformat()} → {(data["start"] + timedelta(days=data["days"]-1)).isoformat()}'),
        ("Days", str(data["days"])),
        ("Travelers", str(data["travelers"])),
        ("Total Budget", f'{data["currency"]} {data["total_budget"]:,.2f}'),
        ("Budget / person / day", f'{data["currency"]} {data["per_person_per_day"]:,.2f}'),
    ]:
        pdf.cell(0, 8, f"{k}: {v}", ln=True)

    pdf.ln(4)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, "Budget Allocation", ln=True)
    pdf.set_font("Arial", "", 11)

    # Allocation table
    col_w = [60, 30, 50]
    pdf.cell(col_w[0], 8, "Category", border=1)
    pdf.cell(col_w[1], 8, "Share %", border=1)
    pdf.cell(col_w[2], 8, "Amount", border=1, ln=True)

    for _, row in alloc_df.iterrows():
        pdf.cell(col_w[0], 8, str(row["Category"]), border=1)
        pdf.cell(col_w[1], 8, str(row["Share %"]), border=1)
        pdf.cell(col_w[2], 8, str(row["Amount"]), border=1, ln=True)

    pdf.ln(4)
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 8, "Itinerary (Draft)", ln=True)
    pdf.set_font("Arial", "", 11)

    # Itinerary rows
    for _, r in itin_df.iterrows():
        pdf.multi_cell(0, 7, f'Day {int(r["Day"])}: {r["Morning"]} | {r["Afternoon/Evening"]} | {r["Notes"]}')

    # Output
    return bytes(pdf.output(dest="S").encode("latin-1"))

# ---------- Sidebar (Inputs) ----------
with st.sidebar:
    st.header("Trip Details")
    destination = st.text_input("Destination", value="Kandy")
    start_date = st.date_input("Start Date", value=date.today())
    days = st.number_input("No. of days", min_value=1, max_value=60, value=5, step=1)
    travelers = st.number_input("Travelers", min_value=1, max_value=20, value=2, step=1)

    st.divider()
    st.subheader("Budget")
    currency = st.selectbox("Currency", ["LKR", "USD", "EUR", "INR"], index=0)
    budget_mode = st.radio("Budget is entered as", ["Total (group)", "Per person"], horizontal=True)
    budget_value = st.number_input("Budget amount", min_value=0.0, value=150000.0, step=1000.0)

    if budget_mode == "Per person":
        total_budget = budget_value * travelers
    else:
        total_budget = budget_value

    st.caption(f"Calculated total budget: {money(total_budget, currency)}")

    st.divider()
    st.subheader("Preferences (weights)")
    st.caption("Adjust sliders—weights are auto-normalized to 100%.")
    w_accom = st.slider("Accommodation", 0, 100, 40)
    w_food = st.slider("Food", 0, 100, 25)
    w_transport = st.slider("Transport", 0, 100, 15)
    w_activities = st.slider("Activities", 0, 100, 15)
    w_shopping = st.slider("Shopping", 0, 100, 5)
    raw_weights = {
        "Accommodation": w_accom,
        "Food": w_food,
        "Transport": w_transport,
        "Activities": w_activities,
        "Shopping": w_shopping,
    }
    weights = normalize_weights(raw_weights)

# ---------- Main ----------
st.title("🧳 Travel Budget Planner")
st.caption("Quickly split your budget, visualize spending, and auto-generate a draft itinerary. (Streamlit)")

# Budget summary
colA, colB, colC = st.columns([1.2, 1, 1])
with colA:
    st.subheader("Budget Allocation")
    alloc_df = build_allocation_df(weights, total_budget, currency)
    st.dataframe(alloc_df, use_container_width=True)

with colB:
    st.subheader("Pie Chart")
    # matplotlib pie
    fig, ax = plt.subplots()
    labels = list(weights.keys())
    sizes = [weights[k] for k in labels]
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig, clear_figure=True)

with colC:
    st.subheader("Key Numbers")
    per_person_per_day = (total_budget / travelers) / max(1, days)
    st.metric("Total Budget", money(total_budget, currency))
    st.metric("Per Person / Day", money(per_person_per_day, currency))
    daily = per_day_breakdown(weights, total_budget, days)
    daily_df = pd.DataFrame(
        {"Category": list(daily.keys()),
         "Per day": [money(v, currency) for v in daily.values()]}
    )
    st.table(daily_df)

st.divider()

# Itinerary generator
st.subheader("Draft Itinerary")
itin_df = generate_itinerary(int(days), destination, per_person_per_day)
st.dataframe(itin_df, use_container_width=True)

# Tips (static examples; tune per destination later)
st.markdown("### Cost-Saving Tips")
tips = [
    "Book intercity transport in advance to lock lower fares.",
    "Use day passes for public transport instead of taxis.",
    "Bundle attractions (city pass) if you plan 3+ paid entries.",
    "Eat one local street-food meal per day to cut costs ~20–30%.",
]
st.markdown("\n".join([f"- {t}" for t in tips]))

# Downloads
st.divider()
st.subheader("Export")
col1, col2 = st.columns(2)
with col1:
    json_bytes = io.BytesIO()
    export = {
        "destination": destination,
        "start": str(start_date),
        "days": int(days),
        "travelers": int(travelers),
        "currency": currency,
        "total_budget": float(total_budget),
        "per_person_per_day": float(per_person_per_day),
        "allocation_percent": weights,
        "itinerary": itin_df.to_dict(orient="records"),
    }
    json_bytes.write(pd.Series(export).to_json(indent=2).encode("utf-8"))
    st.download_button("Download Plan (JSON)", data=json_bytes.getvalue(),
                       file_name="travel_plan.json", mime="application/json")

with col2:
    try:
        pdf_bytes = build_pdf(
            {
                "destination": destination,
                "start": start_date,
                "days": int(days),
                "travelers": int(travelers),
                "currency": currency,
                "total_budget": float(total_budget),
                "per_person_per_day": float(per_person_per_day),
            },
            alloc_df,
            itin_df,
        )
        st.download_button("Download PDF", data=pdf_bytes,
                           file_name="travel_budget_plan.pdf", mime="application/pdf")
    except Exception as e:
        st.info("PDF export needs the 'fpdf2' package. If you see errors, run: `pip install fpdf2`.")
