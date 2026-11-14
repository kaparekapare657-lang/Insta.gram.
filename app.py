import streamlit as st

st.set_page_config(
    page_title="Text Examples",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
        body {
            margin: 0;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 600px;
        }
        a {
            display: block;
            margin: 0.4rem 0;
            font-size: 1rem;
            font-weight: 600;
            color: #111;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
    """,
    unsafe_allow_html=True
)

examples = [
    ("PLAIN", "examples/plain/"),
    ("FADE", "examples/fade/"),
    ("SHIMMER", "examples/shimmer/"),
    ("SLIDE", "examples/slide/"),
    ("CHAOS", "examples/chaos/"),
]

for label, href in examples:
    st.markdown(f'<a href="{href}" target="_self">{label}</a>', unsafe_allow_html=True)