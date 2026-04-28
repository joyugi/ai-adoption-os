import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="AI Adoption OS",
    page_icon="🤖",
    layout="wide"
)

st.title("AI Adoption OS: Internal Knowledge Assistant")
st.caption("A PM-grade prototype for evaluating adoption, trust, governance, and usage telemetry for an enterprise AI assistant.")

kb = pd.read_csv("prototype/sample_data/knowledge_base.csv")

if "events" not in st.session_state:
    st.session_state.events = []

st.sidebar.header("Use Case")
st.sidebar.write(
    "Scenario: A mid-size company is piloting an internal AI assistant to help GTM, HR, Ops, and Support teams answer policy and process questions faster."
)

st.sidebar.header("Product Principle")
st.sidebar.write(
    "The goal is not just answer generation. The goal is trusted adoption, appropriate use, human oversight, and measurable business value."
)

question = st.text_input("Ask a policy or process question:")

def find_answer(user_question):
    user_question_lower = user_question.lower()

    best_match = None
    best_score = 0

    for _, row in kb.iterrows():
        kb_question = row["question"].lower()
        kb_category = row["category"].lower()

        score = 0

        for word in user_question_lower.split():
            clean_word = word.strip("?.!,").lower()

            if len(clean_word) <= 2:
                continue

            if clean_word in kb_question:
                score += 2

            if clean_word in kb_category:
                score += 1

        if score > best_score:
            best_score = score
            best_match = row

    if best_score >= 2:
        return best_match

    return None

if question:
    result = find_answer(question)

    if result is not None:
        st.subheader("Assistant Response")
        st.write(result["answer"])

        col1, col2, col3 = st.columns(3)
        col1.metric("Confidence Label", "Medium" if result["risk_level"] == "Medium" else "Requires Review")
        col2.metric("Risk Level", result["risk_level"])
        col3.metric("Source", result["source"])

        if result["risk_level"] == "High":
            st.warning("This is a high-risk or policy-sensitive topic. Verify before acting and escalate if needed.")
        else:
            st.info("Use this response as a starting point. Verify against the cited source before making decisions.")

        st.divider()
        st.subheader("Human-in-the-Loop Feedback")

        action = st.radio(
            "What did the user do with the response?",
            ["Accepted", "Edited before use", "Rejected", "Escalated to human owner"]
        )

        helpfulness = st.slider("User-rated helpfulness", 1, 5, 3)
        time_saved = st.slider("Estimated time saved in minutes", 0, 30, 5)
        rejection_reason = st.selectbox(
            "Reason, if edited/rejected/escalated",
            [
                "Not applicable",
                "Answer unclear",
                "Source missing or weak",
                "Policy-sensitive",
                "Low confidence",
                "Wrong workflow moment",
                "Needed human judgment"
            ]
        )

        if st.button("Log adoption event"):
            st.session_state.events.append({
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "question": question,
                "category": result["category"],
                "risk_level": result["risk_level"],
                "source": result["source"],
                "action": action,
                "helpfulness": helpfulness,
                "time_saved_minutes": time_saved,
                "rejection_reason": rejection_reason
            })
            st.success("Adoption event logged.")

    else:
        st.subheader("Assistant Response")
        st.error("No reliable answer found in the approved knowledge base.")
        st.warning("Escalate this question to the appropriate human owner. This is a source coverage gap.")

        if st.button("Log unanswered query"):
            st.session_state.events.append({
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "question": question,
                "category": "Unknown",
                "risk_level": "Unknown",
                "source": "No approved source found",
                "action": "Escalated to human owner",
                "helpfulness": 1,
                "time_saved_minutes": 0,
                "rejection_reason": "Source coverage gap"
            })
            st.success("Unanswered query logged.")

st.divider()
st.subheader("Adoption Telemetry")

if st.session_state.events:
    events_df = pd.DataFrame(st.session_state.events)
    events_df.index = events_df.index + 1
    events_df.index.name = "#"

    st.dataframe(events_df, width="stretch")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Uses", len(events_df))
    col2.metric("Acceptance Rate", f"{(events_df['action'].eq('Accepted').mean() * 100):.0f}%")
    col3.metric("Escalation Rate", f"{(events_df['action'].eq('Escalated to human owner').mean() * 100):.0f}%")
    col4.metric("Avg. Helpfulness", f"{events_df['helpfulness'].mean():.1f}/5")

    st.download_button(
        "Download adoption telemetry CSV",
        events_df.to_csv(index=False),
        "adoption_telemetry.csv",
        "text/csv"
    )
else:
    st.write("No adoption events logged yet.")