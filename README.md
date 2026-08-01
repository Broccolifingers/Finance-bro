# Finance Bro 💸

A Gen Z-focused financial decision app. Not just an expense tracker it tells you whether a
purchase is actually worth making, **before** you spend the money.

## Features

- **Purchase Analyzer**
-  Worth-It Score, pros/cons, time-to-recover, goal delay
- **Future You Simulator**
-  projected balance with vs. without a purchase (1/3/6 months)
- **Goal Delay Simulator**
- Buy It vs. Skip It balance projection chart
- **Worth-It Score Engine**
-  weighted scoring across affordability, frequency, motivation, goal impact
- **Financial Personality Test**
-  Impulse Buyer / Trend Chaser / Saver / Investor / Balanced Planner
- **Streaks & Gamification**
-  no-impulse / budget / saving streaks with Bronze → Legend badges
- **AI Money Bro**
-  fully offline, rule-based chatbot (no API key required)
- **FOMO Detector**
- flags trend/social-pressure purchases and reality-checks you
- **Smart Dashboard**
-  balance, goal progress, personality, streak, spending, recent decisions
- **Spending Insights**
-  category breakdown, worth-it score trend, bought vs. skipped
- **Exports**
- download purchase history as CSV or Excel

## Tech Stack

- **Frontend:** Streamlit + custom CSS (dark mode, glassmorphism)
- **Charts:** Plotly
- **Data:** Pandas
- **Database:** SQLite (local file `finance_bro.db`, created automatically)

## Project Structure

```
finance_bro/
├── app.py           # Main Streamlit app — navigation & page rendering
├── db.py             # SQLite schema + all database functions
├── logic.py          # Scoring engine, projections, quiz, chatbot logic
├── styles.py          # Custom CSS (glassmorphism / dark mode)
├── requirements.txt
└── README.md
```

## Installation & Setup

1. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   streamlit run app.py
   ```

4. Open the URL Streamlit prints (usually `http://localhost:8501`).

On first launch you'll be asked to set up a profile (name, income, balance, savings goal).
Check "seed sample data" to see the dashboard populated with example purchases immediately.

## Notes

- All data is stored locally in `finance_bro.db` (SQLite) — nothing leaves your machine.
- The AI Money Bro chatbot is **rule-based** and works completely offline. If you want to wire
  it up to a real LLM later, swap the body of `money_bro_reply()` in `logic.py` for an API call.
- Use **⚙️ Profile & Export** to edit your income/balance/goal, download your purchase history,
  or wipe local data and start fresh.
