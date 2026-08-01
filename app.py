"""
Finance Bro 💸 — Gen Z Financial Decision App
================================================
Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import io
from datetime import datetime

import db
import logic
from styles import inject_css, metric_card_html, pill_html

# --------------------------------------------------------------------------
# PAGE CONFIG + INIT
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Finance Bro ",
    page_icon="\n",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css(st)
db.init_db()

if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "quiz_step" not in st.session_state:
    st.session_state.quiz_step = 0
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = []
if "last_score_result" not in st.session_state:
    st.session_state.last_score_result = None


BADGE_THRESHOLDS = [
    (3, "Bronze Bro", "🥉"),
    (7, "Silver Bro", "🥈"),
    (14, "Gold Bro", "🥇"),
    (30, "Finance Legend", "👑"),
]


def check_and_award_badges(user_id, streak_count):
    newly = []
    for threshold, name, emoji in BADGE_THRESHOLDS:
        if streak_count >= threshold:
            if db.award_badge(user_id, name):
                newly.append((name, emoji))
    return newly


# --------------------------------------------------------------------------
# ONBOARDING
# --------------------------------------------------------------------------
def render_onboarding():
    st.markdown(
        """
        <div class="bro-hero">
            <h1><span class="bro-gradient-text">Finance Bro</span> </h1>
            <p style="color:#c7c7d1; font-size:1.05rem; margin-top:-8px;">
            Before you spend, know if it's actually worth it. Let's set you up.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("onboarding_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Your name", placeholder="e.g. Navnee")
            age = st.number_input("Age", min_value=13, max_value=100, value=20)
            monthly_income = st.number_input("Monthly allowance / income (₹)", min_value=0, value=10000, step=500)
        with col2:
            current_balance = st.number_input("Current balance (₹)", min_value=0, value=8000, step=500)
            goal_name = st.text_input("Savings goal", placeholder="e.g. New Laptop")
            goal_amount = st.number_input("Goal amount (₹)", min_value=0, value=80000, step=1000)

        seed = st.checkbox("Seed some sample data so I can see the app in action", value=True)
        submitted = st.form_submit_button("🚀 Enter Finance Bro")

    if submitted:
        if not name.strip():
            st.error("Enter a name to continue, bro.")
            return
        user_id = db.create_user(name.strip(), age, monthly_income, current_balance, goal_name.strip() or "General Savings", goal_amount)
        if seed:
            db.seed_dummy_data(user_id)
        st.session_state.user_id = user_id
        st.rerun()


# --------------------------------------------------------------------------
# SIDEBAR NAV
# --------------------------------------------------------------------------
def render_sidebar(user):
    with st.sidebar:
        st.markdown(f"###  Yo, {user['name']}")
        st.markdown(pill_html(user.get("personality") or "Personality: TBD", "purple"), unsafe_allow_html=True)
        st.markdown("---")
        page = st.radio(
            "Navigate",
            [
                " Dashboard",
                " Purchase Analyzer",
                " Future You Simulator",
                " Personality Quiz",
                " Streaks & Badges",
                " AI Money Bro",
                " Insights",
                " Profile & Export",
            ],
            label_visibility="collapsed",
        )
        st.markdown("---")
        st.caption("Finance Bro v1.0 · Fully offline · SQLite local storage")
        return page


# --------------------------------------------------------------------------
# DASHBOARD
# --------------------------------------------------------------------------
def render_dashboard(user):
    st.markdown(
        f"""
        <div class="bro-hero">
            <h2 style="margin-bottom:0;">Welcome back, <span class="bro-gradient-text">{user['name']}</span> 👋</h2>
            <p style="color:#c7c7d1; margin-top:4px;">Here's your money snapshot for today.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    purchases = db.get_purchases(user["id"])
    avg_score = round(sum(p["worth_it_score"] for p in purchases) / len(purchases), 1) if purchases else 0.0
    streak = db.get_streak(user["id"], "no_impulse")
    streak_count = streak["current_count"] if streak else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card_html("Current Balance", f"₹{user['current_balance']:,.0f}", "Available now"), unsafe_allow_html=True)
    with c2:
        goal_pct = min(user["goal_saved"] / user["goal_amount"] * 100, 100) if user["goal_amount"] else 0
        st.markdown(metric_card_html(f"Goal: {user['goal_name']}", f"{goal_pct:.0f}%", f"₹{user['goal_saved']:,.0f} / ₹{user['goal_amount']:,.0f}"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card_html("No-Impulse Streak", f"{streak_count} 🔥", "Days without impulse buys"), unsafe_allow_html=True)
    with c4:
        st.markdown(metric_card_html("Avg Worth-It Score", f"{avg_score}/10", f"Across {len(purchases)} decisions"), unsafe_allow_html=True)

    st.write("")
    col_left, col_right = st.columns([1.3, 1])

    with col_left:
        st.markdown("#### 📈 Monthly Spending")
        if purchases:
            df = pd.DataFrame(purchases)
            df["created_at"] = pd.to_datetime(df["created_at"])
            df["month"] = df["created_at"].dt.strftime("%b %Y")
            bought = df[df["decision"] == "bought"]
            if not bought.empty:
                monthly = bought.groupby("month")["price"].sum().reset_index()
                fig = px.bar(monthly, x="month", y="price", color_discrete_sequence=["#8b5cf6"])
                fig.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    font_color="#f5f5f7", margin=dict(l=10, r=10, t=10, b=10), height=280,
                    xaxis_title=None, yaxis_title="₹ spent",
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No purchases logged yet — try the Purchase Analyzer!")
        else:
            st.info("No purchases logged yet — try the Purchase Analyzer!")

    with col_right:
        st.markdown("####  Financial Personality")
        pers = user.get("personality")
        if pers:
            info = logic.PERSONALITY_DESCRIPTIONS.get(pers, {})
            st.markdown(
                f"""
                <div class="glass-card">
                    <div style="font-size:2.2rem;">{info.get('emoji','')}</div>
                    <div style="font-weight:700; font-size:1.15rem;">{pers}</div>
                    <div style="color:#c7c7d1; font-size:0.88rem; margin-top:6px;">{info.get('desc','')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("Take the Personality Quiz to find out your money type!")

    st.markdown("#### 🕒 Recent Decisions")
    if purchases:
        for p in purchases[:5]:
            score = p["worth_it_score"]
            kind = "pill-green" if score >= 8 else "pill-yellow" if score >= 5 else "pill-red"
            decision_emoji = "✅ Bought" if p["decision"] == "bought" else "🚫 Skipped"
            st.markdown(
                f"""
                <div class="glass-card" style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <strong>{p['product_name']}</strong> — ₹{p['price']:,.0f}
                        <div style="color:#8b8b96; font-size:0.8rem;">{decision_emoji} · {p['category'] or 'Uncategorized'}</div>
                    </div>
                    <div>{pill_html(f"{score}/10", kind)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.caption("Nothing here yet. Analyze your first purchase to get started!")


# --------------------------------------------------------------------------
# PURCHASE ANALYZER  (Features 1, 2, 3, 5, 9)
# --------------------------------------------------------------------------
def render_purchase_analyzer(user):
    st.markdown("## 🧮 Purchase Analyzer")
    st.caption("Find out if it's actually worth your money — before you spend it.")

    with st.form("purchase_form"):
        col1, col2 = st.columns(2)
        with col1:
            product_name = st.text_input("Product name", placeholder="e.g. AirPods Pro")
            price = st.number_input("Price (₹)", min_value=0, value=1000, step=100)
            category = st.selectbox("Category", ["Tech", "Fashion", "Food", "Entertainment", "Education", "Fitness", "Travel", "Other"])
        with col2:
            frequency = st.selectbox("How often will you use it?", list(logic.FREQUENCY_WEIGHTS.keys()), index=2)
            motivation = st.selectbox("Why are you buying this?", list(logic.MOTIVATION_WEIGHTS.keys()))
        analyze = st.form_submit_button("🔍 Analyze Purchase")

    if analyze:
        if not product_name.strip():
            st.error("Give it a product name, bro.")
            return

        score, breakdown = logic.calculate_worth_it_score(
            price, user["monthly_income"], user["current_balance"],
            user["goal_amount"], user["goal_saved"], frequency, motivation,
        )
        verdict, emoji = logic.verdict_from_score(score)
        pros, cons = logic.generate_pros_cons(price, user["monthly_income"], user["current_balance"], user["goal_amount"], user["goal_saved"], breakdown)
        recovery = logic.time_to_recover(price, user["monthly_income"])
        delay_days = logic.goal_delay_days(price, user["monthly_income"], user["goal_amount"], user["goal_saved"])

        st.session_state.last_score_result = {
            "product_name": product_name, "price": price, "category": category,
            "motivation": motivation, "score": score, "verdict": verdict,
            "breakdown": breakdown, "pros": pros, "cons": cons,
            "recovery": recovery, "delay_days": delay_days,
        }

        # FOMO detector nudge
        fomo_msg, is_fomo = logic.fomo_feedback(motivation)
        if is_fomo:
            st.warning(f"🚨 FOMO Check: {fomo_msg}")

    result = st.session_state.last_score_result
    if result:
        color = "var(--bro-green)" if result["score"] >= 8 else "var(--bro-yellow)" if result["score"] >= 5 else "var(--bro-red)"
        st.markdown(
            f"""
            <div class="verdict-box" style="border-color:{color};">
                <div style="font-size:0.85rem; color:#c7c7d1; letter-spacing:0.08em; text-transform:uppercase;">Finance Bro Verdict</div>
                <div class="verdict-score" style="color:{color};">{result['score']}/10</div>
                <div class="verdict-label" style="color:{color};">{result['verdict']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # gauge chart
        gcol, tcol = st.columns([1, 1.3])
        with gcol:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=result["score"],
                number={"suffix": "/10", "font": {"color": "#f5f5f7"}},
                gauge={
                    "axis": {"range": [0, 10], "tickcolor": "#f5f5f7"},
                    "bar": {"color": color},
                    "bgcolor": "rgba(0,0,0,0)",
                    "steps": [
                        {"range": [0, 5], "color": "rgba(248,113,113,0.25)"},
                        {"range": [5, 8], "color": "rgba(251,191,36,0.25)"},
                        {"range": [8, 10], "color": "rgba(34,211,165,0.25)"},
                    ],
                },
            ))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#f5f5f7", height=250, margin=dict(l=20, r=20, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)

        with tcol:
            st.markdown("**Pros**")
            for p in result["pros"]:
                st.markdown(f"✓ {p}")
            st.markdown("**Cons**")
            for c in result["cons"]:
                st.markdown(f"✗ {c}")

        st.markdown("#### ⏱️ Time to Recover")
        r1, r2, r3 = st.columns(3)
        with r1:
            st.markdown(metric_card_html("Days of income", f"{result['recovery']['days']}", ""), unsafe_allow_html=True)
        with r2:
            st.markdown(metric_card_html("Weeks of income", f"{result['recovery']['weeks']}", ""), unsafe_allow_html=True)
        with r3:
            st.markdown(metric_card_html("Goal delay", f"{result['delay_days']} days", f"toward {user['goal_name']}"), unsafe_allow_html=True)

        st.markdown("#### ⚖️ Buy It vs Skip It")
        buy_path, skip_path = logic.buy_vs_skip_projection(
            user["current_balance"], user["monthly_income"], user["monthly_income"] * 0.6, result["price"], months=3
        )
        months_axis = list(range(0, 4))
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=months_axis, y=buy_path, mode="lines+markers", name="Buy It", line=dict(color="#f87171", width=3)))
        fig2.add_trace(go.Scatter(x=months_axis, y=skip_path, mode="lines+markers", name="Skip It", line=dict(color="#22d3a5", width=3)))
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#f5f5f7",
            height=300, margin=dict(l=10, r=10, t=30, b=10),
            xaxis_title="Months from now", yaxis_title="Balance (₹)", legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown(f"**After 3 months:** Buy → ₹{buy_path[-1]:,.0f}  |  Skip → ₹{skip_path[-1]:,.0f}  "
                    f"(difference of ₹{skip_path[-1]-buy_path[-1]:,.0f})")

        b1, b2, _ = st.columns([1, 1, 2])
        with b1:
            if st.button("✅ I Bought It", type="primary"):
                db.add_purchase(user["id"], result["product_name"], result["price"], result["category"],
                                 result["motivation"], result["score"], result["verdict"], "bought")
                db.adjust_balance(user["id"], -result["price"])
                db.bump_streak(user["id"], "no_impulse", reset=True)
                st.session_state.last_score_result = None
                st.success("Logged. Balance updated. No judgment. 💸")
                st.rerun()
        with b2:
            if st.button("🚫 I'll Skip It"):
                db.add_purchase(user["id"], result["product_name"], result["price"], result["category"],
                                 result["motivation"], result["score"], result["verdict"], "skipped")
                new_streak = db.bump_streak(user["id"], "no_impulse")
                newly = check_and_award_badges(user["id"], new_streak)
                st.session_state.last_score_result = None
                st.success(f"Respect. Streak up to {new_streak} 🔥")
                for name, emoji in newly:
                    st.balloons()
                    st.success(f"New badge unlocked: {emoji} {name}!")
                st.rerun()


# --------------------------------------------------------------------------
# FUTURE YOU SIMULATOR (Feature 4)
# --------------------------------------------------------------------------
def render_future_you(user):
    st.markdown("##  Future You Simulator")
    st.caption("See where your money lands in 1, 3, and 6 months — with vs without this purchase.")

    col1, col2 = st.columns(2)
    with col1:
        price = st.number_input("Hypothetical purchase price (₹)", min_value=0, value=5000, step=500)
    with col2:
        monthly_spend = st.number_input("Typical monthly spending, excluding this (₹)", min_value=0,
                                         value=int(user["monthly_income"] * 0.55), step=500)

    months_list = [1, 3, 6]
    scenario_buy = logic.simulate_future_balance(user["current_balance"], user["monthly_income"], monthly_spend, months_list, purchase_price=price)
    scenario_skip = logic.simulate_future_balance(user["current_balance"], user["monthly_income"], monthly_spend, months_list, purchase_price=0)

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Purchase Made", x=[f"{m} mo" for m in months_list], y=[scenario_buy[m] for m in months_list], marker_color="#f87171"))
    fig.add_trace(go.Bar(name="Purchase Avoided", x=[f"{m} mo" for m in months_list], y=[scenario_skip[m] for m in months_list], marker_color="#22d3a5"))
    fig.update_layout(
        barmode="group", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font_color="#f5f5f7", height=380, margin=dict(l=10, r=10, t=30, b=10),
        yaxis_title="Projected balance (₹)", legend=dict(orientation="h", y=1.12),
    )
    st.plotly_chart(fig, use_container_width=True)

    cols = st.columns(3)
    for i, m in enumerate(months_list):
        with cols[i]:
            diff = scenario_skip[m] - scenario_buy[m]
            st.markdown(metric_card_html(f"{m}-Month Gap", f"₹{diff:,.0f}", "extra saved by skipping"), unsafe_allow_html=True)


# --------------------------------------------------------------------------
# PERSONALITY QUIZ (Feature 6)
# --------------------------------------------------------------------------
def render_quiz(user):
    st.markdown("##  Financial Personality Test")
    st.caption("5 quick questions. Zero judgment (okay, maybe a little).")

    questions = logic.QUIZ_QUESTIONS
    step = st.session_state.quiz_step

    if step < len(questions):
        q = questions[step]
        st.progress(step / len(questions))
        st.markdown(f"#### {q['question']}")
        choice = st.radio("Pick one:", list(q["options"].keys()), key=f"quiz_q_{step}", label_visibility="collapsed")
        if st.button("Next ➡️" if step < len(questions) - 1 else "See My Result 🎉"):
            st.session_state.quiz_answers.append(q["options"][choice])
            st.session_state.quiz_step += 1
            st.rerun()
    else:
        winner, tally = logic.score_quiz(st.session_state.quiz_answers)
        info = logic.PERSONALITY_DESCRIPTIONS[winner]
        db.save_personality_result(user["id"], winner, str(tally))

        st.balloons()
        st.markdown(
            f"""
            <div class="verdict-box">
                <div style="font-size:3rem;">{info['emoji']}</div>
                <div class="verdict-label bro-gradient-text" style="font-size:1.6rem;">{winner}</div>
                <div style="color:#c7c7d1; margin-top:10px;">{info['desc']}</div>
                <div style="color:#a1a1aa; margin-top:10px; font-size:0.88rem;">💡 {info['tip']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        df = pd.DataFrame({"type": list(tally.keys()), "count": list(tally.values())})
        fig = px.pie(df, names="type", values="count", hole=0.5,
                     color_discrete_sequence=["#8b5cf6", "#ec4899", "#22d3a5", "#fbbf24", "#60a5fa"])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#f5f5f7", height=320, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

        if st.button("🔁 Retake Quiz"):
            st.session_state.quiz_step = 0
            st.session_state.quiz_answers = []
            st.rerun()


# --------------------------------------------------------------------------
# STREAKS & BADGES (Feature 7)
# --------------------------------------------------------------------------
def render_streaks(user):
    st.markdown("##  Streaks & Badges")
    st.caption("Consistency is the real flex.")

    streak_types = [("no_impulse", "No-Impulse Streak", "🔥"), ("budget", "Budget Streak", "📊"), ("saving", "Saving Streak", "💰")]
    cols = st.columns(3)
    for i, (stype, label, emoji) in enumerate(streak_types):
        s = db.get_streak(user["id"], stype)
        count = s["current_count"] if s else 0
        best = s["best_count"] if s else 0
        with cols[i]:
            st.markdown(
                f"""
                <div class="glass-card" style="text-align:center;">
                    <div style="font-size:2rem;">{emoji}</div>
                    <div class="streak-count bro-gradient-text">{count}</div>
                    <div class="metric-sub">{label} · best {best}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("#### 🏅 Badge Collection")
    earned = {b["badge_name"] for b in db.get_badges(user["id"])}
    bcols = st.columns(4)
    for i, (threshold, name, emoji) in enumerate(BADGE_THRESHOLDS):
        locked = name not in earned
        with bcols[i]:
            st.markdown(
                f"""
                <div class="badge-tile {'locked' if locked else ''}">
                    <div class="emoji">{emoji}</div>
                    <div style="font-weight:600; margin-top:4px;">{name}</div>
                    <div class="metric-sub">{'Locked' if locked else 'Unlocked'} · {threshold}-streak</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    if st.button("➕ Log a No-Impulse Day (manual check-in)"):
        new_count = db.bump_streak(user["id"], "no_impulse")
        newly = check_and_award_badges(user["id"], new_count)
        st.success(f"Streak now at {new_count} 🔥")
        for name, emoji in newly:
            st.balloons()
            st.success(f"New badge: {emoji} {name}!")
        st.rerun()


# --------------------------------------------------------------------------
# AI MONEY BRO CHATBOT (Feature 8)
# --------------------------------------------------------------------------
def render_chatbot(user):
    st.markdown("##  AI Money Bro")
    st.caption("Ask me anything about your money. Fully offline, rule-based — no API key needed.")

    suggestions = ["Can I afford AirPods?", "Should I buy a PS5?", "How much should I save?", "What's my goal progress?"]
    scols = st.columns(len(suggestions))
    picked = None
    for i, s in enumerate(suggestions):
        if scols[i].button(s, key=f"sugg_{i}"):
            picked = s

    history = db.get_chat_history(user["id"])
    for h in history:
        cls = "chat-bubble-user" if h["role"] == "user" else "chat-bubble-bro"
        st.markdown(f'<div class="{cls}">{h["message"]}</div>', unsafe_allow_html=True)

    user_msg = st.chat_input("Ask Money Bro...")
    final_msg = picked or user_msg
    if final_msg:
        db.log_chat(user["id"], "user", final_msg)
        reply = logic.money_bro_reply(final_msg, user)
        db.log_chat(user["id"], "bro", reply)
        st.rerun()


# --------------------------------------------------------------------------
# SPENDING INSIGHTS (Feature 11)
# --------------------------------------------------------------------------
def render_insights(user):
    st.markdown("##  Spending Insights")
    purchases = db.get_purchases(user["id"])
    if not purchases:
        st.info("No purchase data yet. Analyze a few purchases first!")
        return

    df = pd.DataFrame(purchases)
    df["created_at"] = pd.to_datetime(df["created_at"])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🗂️ Spend by Category")
        cat_df = df[df["decision"] == "bought"].groupby("category")["price"].sum().reset_index()
        if not cat_df.empty:
            fig = px.pie(cat_df, names="category", values="price", hole=0.45,
                         color_discrete_sequence=px.colors.sequential.Purples_r)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#f5f5f7", height=320, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No purchases logged as 'bought' yet.")

    with col2:
        st.markdown("#### 🎯 Worth-It Score Trend")
        fig2 = px.line(df.sort_values("created_at"), x="created_at", y="worth_it_score", markers=True,
                        color_discrete_sequence=["#22d3a5"])
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f5f5f7",
                            height=320, margin=dict(l=10, r=10, t=10, b=10), yaxis_range=[0, 10])
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### 📅 Bought vs Skipped")
    decision_counts = df["decision"].value_counts().reset_index()
    decision_counts.columns = ["decision", "count"]
    fig3 = px.bar(decision_counts, x="decision", y="count", color="decision",
                  color_discrete_map={"bought": "#f87171", "skipped": "#22d3a5"})
    fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#f5f5f7",
                        height=280, margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("#### 🧾 Goal Progress")
    goal_pct = min(user["goal_saved"] / user["goal_amount"] * 100, 100) if user["goal_amount"] else 0
    st.progress(goal_pct / 100)
    st.caption(f"₹{user['goal_saved']:,.0f} of ₹{user['goal_amount']:,.0f} toward {user['goal_name']} ({goal_pct:.0f}%)")


# --------------------------------------------------------------------------
# PROFILE & EXPORT (Feature 12)
# --------------------------------------------------------------------------
def render_profile(user):
    st.markdown("##  Profile & Export")

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            monthly_income = st.number_input("Monthly income (₹)", value=float(user["monthly_income"]), step=500.0)
            current_balance = st.number_input("Current balance (₹)", value=float(user["current_balance"]), step=500.0)
        with col2:
            goal_name = st.text_input("Goal name", value=user["goal_name"])
            goal_amount = st.number_input("Goal amount (₹)", value=float(user["goal_amount"]), step=1000.0)
        goal_saved = st.number_input("Amount already saved toward goal (₹)", value=float(user["goal_saved"]), step=500.0)
        save = st.form_submit_button("💾 Save Changes")

    if save:
        db.update_user_field(user["id"], "monthly_income", monthly_income)
        db.update_user_field(user["id"], "current_balance", current_balance)
        db.update_user_field(user["id"], "goal_name", goal_name)
        db.update_user_field(user["id"], "goal_amount", goal_amount)
        db.update_user_field(user["id"], "goal_saved", goal_saved)
        st.success("Profile updated!")
        st.rerun()

    st.markdown("---")
    st.markdown("#### 📤 Export Your Data")
    purchases = db.get_purchases(user["id"])
    if purchases:
        df = pd.DataFrame(purchases)
        c1, c2 = st.columns(2)
        with c1:
            csv_buf = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download CSV", data=csv_buf, file_name="finance_bro_purchases.csv", mime="text/csv")
        with c2:
            excel_buf = io.BytesIO()
            with pd.ExcelWriter(excel_buf, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Purchases")
            st.download_button("⬇️ Download Excel", data=excel_buf.getvalue(), file_name="finance_bro_purchases.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.caption("No purchase history to export yet.")

    st.markdown("---")
    if st.button("🗑️ Reset App (delete local database)", type="secondary"):
        st.session_state.confirm_reset = True
    if st.session_state.get("confirm_reset"):
        st.warning("This deletes ALL local data permanently.")
        if st.button("Yes, wipe everything", type="primary"):
            import os
            db_path = db.DB_PATH
            st.session_state.clear()
            if os.path.exists(db_path):
                os.remove(db_path)
            st.rerun()


# --------------------------------------------------------------------------
# MAIN ROUTER
# --------------------------------------------------------------------------
def main():
    if st.session_state.user_id is None:
        latest = db.get_latest_user()
        if latest:
            st.session_state.user_id = latest["id"]

    if st.session_state.user_id is None:
        render_onboarding()
        return

    user = db.get_user(st.session_state.user_id)
    if user is None:
        st.session_state.user_id = None
        st.rerun()
        return

    page = render_sidebar(user)

    if page == " Dashboard":
        render_dashboard(user)
    elif page == " Purchase Analyzer":
        render_purchase_analyzer(user)
    elif page == " Future You Simulator":
        render_future_you(user)
    elif page == " Personality Quiz":
        render_quiz(user)
    elif page == " Streaks & Badges":
        render_streaks(user)
    elif page == " AI Money Bro":
        render_chatbot(user)
    elif page == " Insights":
        render_insights(user)
    elif page == " Profile & Export":
        render_profile(user)


if __name__ == "__main__":
    main()
