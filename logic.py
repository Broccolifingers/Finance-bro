"""
Finance Bro — Core Logic
--------------------------
Pure-python calculation & decision engine. No Streamlit imports here so this
module can be unit-tested independently.
"""

import math
import re

# --------------------------------------------------------------------------
# WORTH-IT SCORE ENGINE
# --------------------------------------------------------------------------

FREQUENCY_WEIGHTS = {
    "Daily": 1.0,
    "Weekly": 0.8,
    "Monthly": 0.55,
    "Rarely": 0.3,
    "One-time": 0.15,
}

MOTIVATION_WEIGHTS = {
    "Need": 1.0,
    "Reward": 0.7,
    "Investment": 0.9,
    "Trend": 0.35,
    "Social Pressure": 0.25,
    "Impulse": 0.15,
}


def calculate_worth_it_score(price, monthly_income, current_balance, goal_amount,
                              goal_saved, frequency="Monthly", motivation="Need"):
    """
    Returns (score 0-10, breakdown dict).

    Weighted blend of:
      - affordability (% of balance / income consumed)
      - frequency of use (recurring value)
      - motivation quality (need vs impulse)
      - goal impact (how much it sets back the savings goal)
    """
    monthly_income = max(monthly_income, 1)
    current_balance = max(current_balance, 0)

    # 1. Affordability: lower % of balance used -> higher sub-score
    pct_of_balance = price / max(current_balance, 1)
    affordability_score = max(0, 1 - pct_of_balance) * 10
    affordability_score = min(affordability_score, 10)

    # 2. Budget percentage: lower % of monthly income -> higher sub-score
    pct_of_income = price / monthly_income
    budget_score = max(0, 1 - pct_of_income) * 10
    budget_score = min(budget_score, 10)

    # 3. Frequency of use
    freq_score = FREQUENCY_WEIGHTS.get(frequency, 0.5) * 10

    # 4. Motivation quality
    motivation_score = MOTIVATION_WEIGHTS.get(motivation, 0.5) * 10

    # 5. Goal impact: how many days of goal-saving does this cost?
    remaining_goal = max(goal_amount - goal_saved, 0)
    if remaining_goal > 0 and monthly_income > 0:
        goal_delay_days_est = (price / monthly_income) * 30
        goal_impact_score = max(0, 10 - (goal_delay_days_est / 3))  # 3 days delay ~ -1 point
        goal_impact_score = max(0, min(goal_impact_score, 10))
    else:
        goal_impact_score = 10  # no active goal or already funded -> no penalty

    weights = {
        "affordability": 0.30,
        "budget": 0.20,
        "frequency": 0.20,
        "motivation": 0.15,
        "goal_impact": 0.15,
    }
    final_score = (
        affordability_score * weights["affordability"]
        + budget_score * weights["budget"]
        + freq_score * weights["frequency"]
        + motivation_score * weights["motivation"]
        + goal_impact_score * weights["goal_impact"]
    )
    final_score = round(max(0, min(final_score, 10)), 1)

    breakdown = {
        "affordability_score": round(affordability_score, 1),
        "budget_score": round(budget_score, 1),
        "frequency_score": round(freq_score, 1),
        "motivation_score": round(motivation_score, 1),
        "goal_impact_score": round(goal_impact_score, 1),
        "pct_of_balance": round(pct_of_balance * 100, 1),
        "pct_of_income": round(pct_of_income * 100, 1),
    }
    return final_score, breakdown


def verdict_from_score(score):
    if score >= 8:
        return "Worth It", "🟢"
    elif score >= 5:
        return "Think Carefully", "🟡"
    else:
        return "Bad Financial Decision", "🔴"


def generate_pros_cons(price, monthly_income, current_balance, goal_amount, goal_saved, breakdown):
    pros, cons = [], []

    if breakdown["pct_of_income"] <= 15:
        pros.append("Fits comfortably within your monthly budget")
    else:
        cons.append(f"Eats up {breakdown['pct_of_income']:.0f}% of your monthly allowance")

    if breakdown["pct_of_balance"] <= 25:
        pros.append("Leaves your balance mostly intact")
    else:
        cons.append(f"Uses {breakdown['pct_of_balance']:.0f}% of your current balance")

    if breakdown["motivation_score"] >= 7:
        pros.append("Driven by genuine need or investment value")
    elif breakdown["motivation_score"] <= 3.5:
        cons.append("Mostly driven by trend or social pressure, not need")

    if breakdown["frequency_score"] >= 7:
        pros.append("High long-term value from frequent use")
    elif breakdown["frequency_score"] <= 3:
        cons.append("Low usage frequency — value may not justify cost")

    remaining_goal = max(goal_amount - goal_saved, 0)
    if remaining_goal > 0 and monthly_income > 0:
        delay_days = round((price / monthly_income) * 30)
        if delay_days >= 3:
            cons.append(f"Delays your savings goal by ~{delay_days} days")
        else:
            pros.append("Minimal impact on your savings goal")

    if not pros:
        pros.append("None significant — proceed with caution")
    if not cons:
        cons.append("None significant — looks like a solid choice")

    return pros, cons


# --------------------------------------------------------------------------
# TIME TO RECOVER
# --------------------------------------------------------------------------

def time_to_recover(price, monthly_income):
    """Convert a purchase price into days / weeks / months of income needed."""
    monthly_income = max(monthly_income, 1)
    daily_income = monthly_income / 30
    days = price / daily_income if daily_income else 0
    weeks = days / 7
    months = days / 30
    return {
        "days": round(days, 1),
        "weeks": round(weeks, 1),
        "months": round(months, 2),
    }


def goal_delay_days(price, monthly_income, goal_amount, goal_saved):
    """Estimate how many extra days a purchase delays reaching the savings goal,
    assuming the user saves 100% of leftover monthly income toward the goal."""
    monthly_income = max(monthly_income, 1)
    remaining = max(goal_amount - goal_saved, 0)
    if remaining == 0:
        return 0
    daily_income = monthly_income / 30
    return round(price / daily_income) if daily_income else 0


# --------------------------------------------------------------------------
# FUTURE YOU SIMULATOR / GOAL DELAY SIMULATOR
# --------------------------------------------------------------------------

def simulate_future_balance(current_balance, monthly_income, monthly_spend_avg,
                             months_list=(1, 3, 6), purchase_price=0):
    """
    Projects balance forward assuming a constant net monthly savings rate.
    purchase_price is deducted once at t=0 if scenario == 'buy'.
    """
    net_monthly = monthly_income - monthly_spend_avg
    results = {}
    for m in months_list:
        balance = current_balance - purchase_price + net_monthly * m
        results[m] = round(balance, 2)
    return results


def buy_vs_skip_projection(current_balance, monthly_income, monthly_spend_avg, price, months=3):
    """Returns two lists (buy_path, skip_path) of balances for months 0..months for charting."""
    net_monthly = monthly_income - monthly_spend_avg
    buy_path, skip_path = [], []
    for m in range(0, months + 1):
        buy_path.append(round(current_balance - price + net_monthly * m, 2))
        skip_path.append(round(current_balance + net_monthly * m, 2))
    return buy_path, skip_path


# --------------------------------------------------------------------------
# FINANCIAL PERSONALITY QUIZ
# --------------------------------------------------------------------------

QUIZ_QUESTIONS = [
    {
        "question": "💸 Payday just hit. What's your first move?",
        "options": {
            "Buy something I've been eyeing immediately": "Impulse Buyer",
            "Check what's trending and grab it before it's sold out": "Trend Chaser",
            "Move a chunk straight into savings": "Saver",
            "Look for a stock/fund to put money into": "Investor",
            "Split it: bills, savings, fun money": "Balanced Planner",
        },
    },
    {
        "question": "🛍️ You see a 'limited edition' drop online. You:",
        "options": {
            "Buy instantly, limited = must-have": "Impulse Buyer",
            "Buy it because everyone's posting about it": "Trend Chaser",
            "Skip it, wasn't in the budget": "Saver",
            "Check if it'll hold resale value first": "Investor",
            "Think about it for a day before deciding": "Balanced Planner",
        },
    },
    {
        "question": "📉 The market/crypto dips 15% in a day. Your reaction:",
        "options": {
            "Don't really follow markets": "Impulse Buyer",
            "Panic and check social media for what to do": "Trend Chaser",
            "Stay calm, I barely invest anyway": "Saver",
            "See it as a buying opportunity": "Investor",
            "Check my plan, stick to it": "Balanced Planner",
        },
    },
    {
        "question": "🎯 How do you feel about savings goals?",
        "options": {
            "Goals are hard, I spend as I go": "Impulse Buyer",
            "I save for whatever's hyped at the moment": "Trend Chaser",
            "I track every rupee toward my goal": "Saver",
            "I'd rather grow money than just store it": "Investor",
            "I balance saving with enjoying life now": "Balanced Planner",
        },
    },
    {
        "question": "👥 A friend says 'you HAVE to buy this'. You:",
        "options": {
            "Already added to cart before they finished the sentence": "Impulse Buyer",
            "Trust them, they always know what's cool": "Trend Chaser",
            "Say no, not in my budget right now": "Saver",
            "Ask if it's actually worth the money long-term": "Investor",
            "Consider it against my other priorities first": "Balanced Planner",
        },
    },
]

PERSONALITY_DESCRIPTIONS = {
    "Impulse Buyer": {
        "emoji": "⚡",
        "desc": "You buy first, think later. Fun in the moment, rough on the wallet.",
        "tip": "Try a 24-hour rule before non-essential purchases.",
    },
    "Trend Chaser": {
        "emoji": "🔥",
        "desc": "If it's viral, you're on it. Your spending follows the algorithm.",
        "tip": "Ask 'would I still want this in a month?' before buying.",
    },
    "Saver": {
        "emoji": "🐢",
        "desc": "Careful and consistent — your balance rarely surprises you.",
        "tip": "You're safe — just make sure you're also letting money grow.",
    },
    "Investor": {
        "emoji": "📈",
        "desc": "You think in returns, not just receipts.",
        "tip": "Keep an emergency buffer even while you chase growth.",
    },
    "Balanced Planner": {
        "emoji": "⚖️",
        "desc": "You spend, save, and invest with intention. Certified Finance Bro.",
        "tip": "Stay consistent — you're the benchmark.",
    },
}


def score_quiz(answers):
    """answers: list of personality-type strings chosen. Returns (winner, tally dict)."""
    tally = {}
    for a in answers:
        tally[a] = tally.get(a, 0) + 1
    winner = max(tally, key=tally.get)
    return winner, tally


# --------------------------------------------------------------------------
# FOMO DETECTOR
# --------------------------------------------------------------------------

FOMO_ROASTS = [
    "Bro, that's just the algorithm talking, not your bank account. 🤖",
    "Ngl this is giving 'bought it for the Instagram story' energy. 📸",
    "Your FYP does not pay your rent. Just saying. 🏠",
    "The hype cycle for this drops in 2 weeks. Your bank balance won't reset that fast. ⏳",
    "Nobody's thinking about your purchase as much as you think they are. 👀",
]

FOMO_GENUINE = [
    "Okay this actually sounds like a need, not a vibe. Proceed. ✅",
    "Solid reasoning — this isn't FOMO, this is a plan. 📋",
]


def fomo_feedback(motivation):
    import random
    if motivation in ("Trend", "Social Pressure"):
        return random.choice(FOMO_ROASTS), True
    return random.choice(FOMO_GENUINE), False


# --------------------------------------------------------------------------
# AI MONEY BRO — rule-based offline chatbot
# --------------------------------------------------------------------------

# Rough price guesses for common Gen Z purchases so the bot can respond
# meaningfully even with zero info from the user.
KNOWN_ITEM_PRICES = {
    "airpods": 24900, "airpods pro": 24900, "ps5": 54990, "playstation": 54990,
    "iphone": 79900, "laptop": 55000, "sneakers": 6000, "shoes": 4000,
    "concert ticket": 3500, "netflix": 649, "spotify": 119, "gym membership": 1500,
    "phone": 20000, "headphones": 3000, "smartwatch": 5000, "bike": 60000,
}


def _guess_price(message):
    msg = message.lower()
    for item, price in KNOWN_ITEM_PRICES.items():
        if item in msg:
            return item, price
    return None, None


def money_bro_reply(message, user):
    """
    Rule-based chatbot. Works fully offline.
    `user` is a dict from db.get_user().
    """
    msg = message.lower().strip()
    income = user.get("monthly_income", 0) or 1
    balance = user.get("current_balance", 0) or 0
    goal_amount = user.get("goal_amount", 0) or 0
    goal_saved = user.get("goal_saved", 0) or 0
    name = user.get("name", "bro")

    # Detect "can I afford X" style questions
    if re.search(r"afford|should i buy|worth (it|buying)", msg):
        item, price = _guess_price(msg)
        if price:
            pct_balance = price / max(balance, 1) * 100
            pct_income = price / income * 100
            if pct_balance <= 30 and pct_income <= 25:
                verdict = f"Yeah {name}, you can afford the {item.title()} (₹{price:,}). It's about {pct_balance:.0f}% of your balance. Just don't make it a habit. ✅"
            elif pct_balance <= 60:
                verdict = f"You *can* afford the {item.title()} (₹{price:,}), but it'll eat {pct_balance:.0f}% of your balance. Sleep on it for a day. 🟡"
            else:
                verdict = f"Hard pass for now — {item.title()} is ₹{price:,}, that's {pct_balance:.0f}% of your balance. Your future self says no. 🔴"
            return verdict
        else:
            return (f"Tell me the price and I'll run the numbers, {name}. "
                    f"Right now you've got ₹{balance:,.0f} in balance and ₹{income:,.0f}/month coming in.")

    if "how much should i save" in msg or "how much to save" in msg:
        suggested = round(income * 0.2)
        return (f"General rule: aim to save at least 20% of your income — that's about ₹{suggested:,} a month for you. "
                f"You're currently at ₹{goal_saved:,.0f} of your ₹{goal_amount:,.0f} goal.")

    if "goal" in msg and ("progress" in msg or "how" in msg):
        if goal_amount > 0:
            pct = min(goal_saved / goal_amount * 100, 100)
            return f"You're {pct:.0f}% of the way to your goal. Keep stacking — you got this. 💪"
        return "You haven't set a savings goal yet — head to your profile and set one!"

    if "budget" in msg:
        return f"Your monthly income is ₹{income:,.0f}. A simple split: 50% needs, 30% wants, 20% savings — that's roughly ₹{income*0.5:,.0f} / ₹{income*0.3:,.0f} / ₹{income*0.2:,.0f}."

    if any(g in msg for g in ("hi", "hello", "hey", "yo", "sup")):
        return f"Yo {name}! I'm Money Bro 🤝 Ask me if something's worth buying, or how much you should be saving."

    # Fallback
    item, price = _guess_price(msg)
    if price:
        return f"That's roughly a ₹{price:,} purchase. Run it through the Purchase Analyzer for a full Worth-It Score. 📊"

    return "Not totally sure on that one — try asking me things like 'Can I afford AirPods?' or 'How much should I save this month?'"
