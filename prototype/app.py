from datetime import datetime

import plotly.express as px
import streamlit as st

import llm
import retrieval
import telemetry

st.set_page_config(
    page_title="AI Adoption OS",
    page_icon="🤖",
    layout="wide"
)

telemetry.init_db()

st.title("AI Adoption OS: Internal Knowledge Assistant")
st.caption("A PM-grade prototype for evaluating adoption, trust, governance, and usage telemetry for an enterprise AI assistant.")

st.sidebar.header("Use Case")
st.sidebar.write(
    "Scenario: A mid-size company is piloting an internal AI assistant to help GTM, HR, Ops, and Support teams answer policy and process questions faster."
)

st.sidebar.header("Product Principle")
st.sidebar.write(
    "The goal is not just answer generation. The goal is trusted adoption, appropriate use, human oversight, and measurable business value."
)

st.sidebar.header("Answer Mode")
if llm.is_available():
    st.sidebar.success("AI-generated answers (Claude)")
else:
    st.sidebar.info("Retrieval-only fallback mode")

if not llm.is_available():
    st.info(
        "Running in retrieval-only mode — set ANTHROPIC_API_KEY in a .env file "
        "for AI-generated answers. See .env.example."
    )

question = st.text_input("Ask a policy or process question:")

if question:
    matches = retrieval.search(question, top_k=3)
    top_row, top_score = matches[0]
    confidence = retrieval.confidence_label(top_score)

    if confidence is not None:
        answered_by = "fallback"
        answer_text = top_row["answer"]

        if llm.is_available():
            sources = [row.to_dict() for row, score in matches
                       if retrieval.confidence_label(score) is not None]
            with st.spinner("Generating grounded answer..."):
                llm_result = llm.generate_answer(question, sources)
            if llm_result is not None:
                answered_by = "llm"
                answer_text = llm_result["answer"]

        st.subheader("Assistant Response")
        st.write(answer_text)
        if llm.is_available() and answered_by == "fallback":
            st.warning("AI generation failed — showing best-matching approved source instead.")

        col1, col2, col3 = st.columns(3)
        col1.metric("Confidence", confidence, help=f"Retrieval similarity: {top_score:.2f}")
        col2.metric("Risk Level", top_row["risk_level"])
        col3.metric("Source", top_row["source"])

        if top_row["risk_level"] == "High":
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
            telemetry.log_event({
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "question": question,
                "category": top_row["category"],
                "risk_level": top_row["risk_level"],
                "confidence": confidence,
                "source": top_row["source"],
                "action": action,
                "helpfulness": helpfulness,
                "time_saved_minutes": time_saved,
                "rejection_reason": rejection_reason,
                "answered_by": answered_by
            })
            st.success("Adoption event logged.")

    else:
        st.subheader("Assistant Response")
        st.error("No reliable answer found in the approved knowledge base.")
        st.warning("Escalate this question to the appropriate human owner. This is a source coverage gap.")

        if st.button("Log unanswered query"):
            telemetry.log_event({
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "question": question,
                "category": "Unknown",
                "risk_level": "Unknown",
                "confidence": "None",
                "source": "No approved source found",
                "action": "Escalated to human owner",
                "helpfulness": 1,
                "time_saved_minutes": 0,
                "rejection_reason": "Source coverage gap",
                "answered_by": "none"
            })
            st.success("Unanswered query logged.")

st.divider()
st.subheader("Adoption Telemetry")

events_df = telemetry.load_events()

if not events_df.empty:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Uses", len(events_df))
    col2.metric("Acceptance Rate", f"{(events_df['action'].eq('Accepted').mean() * 100):.0f}%")
    col3.metric("Escalation Rate", f"{(events_df['action'].eq('Escalated to human owner').mean() * 100):.0f}%")
    col4.metric("Avg. Helpfulness", f"{events_df['helpfulness'].mean():.1f}/5")

    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        action_counts = events_df["action"].value_counts().reset_index()
        action_counts.columns = ["action", "count"]
        st.plotly_chart(
            px.bar(action_counts, x="action", y="count", title="Actions Breakdown"),
            use_container_width=True
        )
    with chart_col2:
        category_counts = events_df["category"].value_counts().reset_index()
        category_counts.columns = ["category", "count"]
        st.plotly_chart(
            px.bar(category_counts, x="category", y="count", title="Usage by Category"),
            use_container_width=True
        )

    unanswered = events_df[events_df["rejection_reason"] == "Source coverage gap"]
    if not unanswered.empty:
        st.subheader("Top Unanswered Questions (Coverage Gaps)")
        gap_counts = unanswered["question"].value_counts().reset_index()
        gap_counts.columns = ["question", "times asked"]
        st.dataframe(gap_counts, width="stretch")

    with st.expander("All adoption events"):
        display_df = events_df.drop(columns=["id"])
        display_df.index = range(1, len(display_df) + 1)
        display_df.index.name = "#"
        st.dataframe(display_df, width="stretch")

    st.download_button(
        "Download adoption telemetry CSV",
        events_df.to_csv(index=False),
        "adoption_telemetry.csv",
        "text/csv"
    )
else:
    st.write("No adoption events logged yet.")
