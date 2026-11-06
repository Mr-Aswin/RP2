from __future__ import annotations

import streamlit as st

try:
    from app.components import render_header, render_review_form, render_result_card, render_warning_message
    from app.predictor import predict_sentiment
    from app.styles import CSS
except ImportError:  # pragma: no cover - fallback for direct script execution
    from components import render_header, render_review_form, render_result_card, render_warning_message
    from predictor import predict_sentiment
    from styles import CSS


st.set_page_config(
    page_title="SentimentForge",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)


st.markdown(CSS, unsafe_allow_html=True)


def main():
    st.markdown('<div class="sentimentforge-shell">', unsafe_allow_html=True)
    render_header()

    st.markdown('<div class="page-card">', unsafe_allow_html=True)
    review_text, submit = render_review_form()

    if submit:
        if not review_text.strip():
            render_warning_message()
        else:
            try:
                result = predict_sentiment(review_text)
                render_result_card(result)
            except Exception as exc:  # pragma: no cover - user-facing guard.
                st.error(f"Unable to analyze the review: {exc}")

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
