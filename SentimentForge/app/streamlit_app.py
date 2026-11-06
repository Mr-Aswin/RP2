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
    render_header()

    if "prediction_result" not in st.session_state:
        st.session_state.prediction_result = None
    if "prediction_error" not in st.session_state:
        st.session_state.prediction_error = None

    input_column, result_column = st.columns(2, gap="large")

    with input_column:
        with st.container(border=True):
            review_text, submit = render_review_form()
            if submit:
                if not review_text.strip():
                    st.session_state.prediction_error = "Please enter a movie review before analyzing."
                    st.session_state.prediction_result = None
                else:
                    try:
                        st.session_state.prediction_result = predict_sentiment(review_text)
                        st.session_state.prediction_error = None
                    except Exception as exc:  # pragma: no cover - user-facing guard.
                        st.session_state.prediction_result = None
                        st.session_state.prediction_error = f"Unable to analyze the review: {exc}"

            if st.session_state.prediction_error:
                st.error(st.session_state.prediction_error)

    with result_column:
        with st.container(border=True):
            render_result_card(st.session_state.prediction_result)


if __name__ == "__main__":
    main()
