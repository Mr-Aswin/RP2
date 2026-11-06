from __future__ import annotations

import re

import pandas as pd
import streamlit as st


def render_header():
    st.markdown(
        """
        <div class="topbar">
            <div class="brand-group">
                <div class="brand-mark">S</div>
                <div>
                    <h1 class="project-title">SentimentForge</h1>
                    <p class="project-tagline">Understand the emotion behind every review.</p>
                </div>
            </div>
            <div class="header-badges">
                <span class="badge">DistilBERT</span>
                <span class="badge">IMDb 50K Reviews</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_review_form():
    with st.form("review_form"):
        st.markdown('<div class="analysis-form">', unsafe_allow_html=True)
        review = st.text_area(
            "Movie review",
            key="movie_review",
            value=st.session_state.get("movie_review", ""),
            placeholder="Example: This film was beautifully shot, emotionally intense, and surprisingly moving from start to finish.",
            help="Paste or type the raw review text exactly as written. No preprocessing is applied before prediction.",
            height=240,
        )

        count = len(review)
        word_count = len(re.findall(r"\S+", review)) if review else 0
        st.markdown(
            f"""
            <div class="count-row">
                <span>{count} characters</span>
                <span>{word_count} words</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_submit, col_clear = st.columns([1, 1])
        with col_submit:
            submit = st.form_submit_button("Analyze", use_container_width=True)
        with col_clear:
            clear = st.form_submit_button("Clear", use_container_width=True, type="secondary")

        if clear:
            st.session_state.movie_review = ""
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        return review, submit


def render_result_card(result):
    prediction = result["prediction"]
    is_positive = prediction == "POSITIVE"
    pill_color = "#22c55e" if is_positive else "#ef4444"
    label = "POSITIVE REVIEW" if is_positive else "NEGATIVE REVIEW"
    confidence = result["confidence"] * 100
    positive_probability = result["positive_probability"] * 100
    negative_probability = result["negative_probability"] * 100

    st.markdown(
        f"""
        <div class="result-card">
            <div class="result-pill" style="background: rgba(255,255,255,0.02); color: {pill_color}; border-color: {pill_color}33;">
                <span style="width:10px;height:10px;border-radius:50%;background:{pill_color};display:inline-block;"></span>
                {label}
            </div>
            <div class="result-metrics">
                <div class="metric-box">
                    <span class="metric-label">Positive probability</span>
                    <span class="metric-value" style="color:#4ade80;">{positive_probability:.2f}%</span>
                </div>
                <div class="metric-box">
                    <span class="metric-label">Negative probability</span>
                    <span class="metric-value" style="color:#f87171;">{negative_probability:.2f}%</span>
                </div>
                <div class="metric-box">
                    <span class="metric-label">Prediction confidence</span>
                    <span class="metric-value" style="color:#a78bfa;">{confidence:.2f}%</span>
                </div>
            </div>
            <div class="note">Confidence represents the model's estimated probability for the predicted class, not a guarantee.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    chart_data = pd.DataFrame(
        {
            "Class": ["Positive", "Negative"],
            "Probability": [positive_probability, negative_probability],
        }
    ).set_index("Class")

    st.bar_chart(chart_data, height=220)


def render_warning_message():
    st.warning("Please enter a movie review before analyzing your sentiment.")
