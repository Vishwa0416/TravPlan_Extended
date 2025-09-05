# 🧳 Travel Budget Planner (Streamlit)

A **Streamlit-based travel budget planner** that helps travelers quickly plan trips, split budgets across categories, generate draft itineraries, and export plans to **PDF or JSON**.  
This project extends my [TravPlan](https://github.com/Vishwa0416/TravPlan) mobile app by providing a lightweight **web companion tool**.

---

## ✨ Features
- 📋 **Trip Input Form** – destination, days, travelers, budget mode (total / per person).  
- 💰 **Budget Allocation** – auto-normalized sliders for accommodation, food, transport, activities, shopping.  
- 📊 **Visualization** – interactive pie chart, table, and per-day budget breakdown.  
- 🗓 **Itinerary Generator** – draft day-by-day plan with suggested activities (budget-aware).  
- 💡 **Cost-Saving Tips** – quick travel hacks to optimize expenses.  
- 📂 **Export Options** – download as **PDF** or **JSON** for easy sharing.  

---

## 🚀 Demo
Run locally with Streamlit:

```bash
git clone https://github.com/Vishwa0416/TravPlan_Extended.git
cd TravPlan_Extended

# (optional) create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# install dependencies
pip install -r requirements.txt
```
## 🛠 Tech Stack

- Streamlit
 – UI framework

- Pandas
 – data handling

- Matplotlib
 – charts

- FPDF2
 – PDF export

## 🔮 Future Improvements

- 🌍 Integrate Google Places API for real attraction suggestions.

- 💱 Add currency conversion via live exchange rate APIs.

- 📤 Shareable links to plans (Supabase/Gist integration).

- 🔗 Direct integration with TravPlan mobile app.

