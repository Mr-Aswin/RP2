from __future__ import annotations

import re

import streamlit as st


def render_header():
    st.markdown(
        """
        <div class="sf-hero">
            <h1>REAL-TIME SENTIMENT ANALYSIS</h1>
            <p>Understand the emotion behind every movie review.</p>
            <div class="sf-badges">
                <span class="sf-badge"><span class="sf-check">✓</span> Instant results</span>
                <span class="sf-badge"><span class="sf-check">✓</span> Fine-tuned DistilBERT</span>
                <span class="sf-badge"><span class="sf-check">✓</span> IMDb review analysis</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _clear_review():
    st.session_state.movie_review = ""
    st.session_state.prediction_result = None
    st.session_state.prediction_error = None


def render_review_form():
    with st.form("review_form"):
        st.markdown(
            """
            <div class="sf-panel-heading"><span class="sf-panel-icon">↕</span> Analyze text</div>
            <p class="sf-panel-caption">Paste a movie review and let the model read its overall tone.</p>
            """,
            unsafe_allow_html=True,
        )
        review = st.text_area(
            "Movie review",
            key="movie_review",
            value=st.session_state.get("movie_review", ""),
            placeholder="Example: This film was beautifully shot, emotionally intense, and surprisingly moving from start to finish.",
            help="Enter the review as written. The same saved DistilBERT model powers both interfaces.",
            height=275,
        )

        count = len(review)
        word_count = len(re.findall(r"\S+", review)) if review else 0
        st.markdown(
            f"""
            <div class="sf-count-row">
                <span>{count:,} characters</span>
                <span>{word_count:,} words</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_submit, col_clear = st.columns([2, 1])
        with col_submit:
            submit = st.form_submit_button("✦  Analyze sentiment", use_container_width=True)
        with col_clear:
            st.form_submit_button(
                "Clear",
                use_container_width=True,
                type="secondary",
                on_click=_clear_review,
            )

        return review, submit


def render_result_card(result):
    if not result:
        st.markdown(
            """
            <div class="sf-result-top">
                <p class="sf-result-label">Overall sentiment</p>
                <span class="sf-result-icon" aria-hidden="true">⌁</span>
            </div>
            <div class="sf-empty-state">
                <div class="sf-empty-icon">✦</div>
                <p class="sf-empty-title">Your result will appear here</p>
                <p class="sf-empty-copy">Add a review on the left and analyze it to see the model's sentiment and confidence.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    prediction = result["prediction"]
    is_positive = prediction == "POSITIVE"
    confidence = result["confidence"] * 100
    positive_probability = result["positive_probability"] * 100
    negative_probability = result["negative_probability"] * 100
    sentiment_class = "positive" if is_positive else "negative"
    sentiment_text = "Positive" if is_positive else "Negative"
    gauge_color = "#35d49a" if is_positive else "#ff657a"

    st.markdown(
        f"""
        <div class="sf-result-top">
            <div>
                <p class="sf-result-label">Model prediction</p>
                <p class="sf-result-sentiment {sentiment_class}">{sentiment_text}</p>
            </div>
            <span class="sf-result-icon" aria-hidden="true">⌁</span>
        </div>
        <div class="sf-gauge-wrap">
            <div class="sf-gauge" style="--gauge-value:{confidence:.2f}%;--gauge-color:{gauge_color};">
                <div class="sf-gauge-inner">
                    <span class="sf-gauge-value">{confidence:.1f}%</span>
                    <span class="sf-gauge-caption">CONFIDENCE</span>
                </div>
            </div>
        </div>
        <div class="sf-probability-list">
            <div>
                <div class="sf-probability-head"><span>Positive</span><span class="sf-probability-value">{positive_probability:.2f}%</span></div>
                <div class="sf-progress"><div class="sf-progress-fill positive" style="width:{positive_probability:.2f}%;"></div></div>
            </div>
            <div>
                <div class="sf-probability-head"><span>Negative</span><span class="sf-probability-value">{negative_probability:.2f}%</span></div>
                <div class="sf-progress"><div class="sf-progress-fill negative" style="width:{negative_probability:.2f}%;"></div></div>
            </div>
        </div>
        <p class="sf-footnote">Confidence is the model's estimated probability for its predicted class, not a guarantee.</p>
        """,
        unsafe_allow_html=True,
    )


def render_warning_message():
    st.warning("Please enter a movie review before analyzing your sentiment.")
