import streamlit as st

def set_theme():
    """Manage dark mode / light mode toggle and apply UI styles."""
    if "theme" not in st.session_state:
        st.session_state.theme = "Light"

    theme_toggle = st.sidebar.radio("Theme", ["Light", "Dark"], index=0 if st.session_state.theme == "Light" else 1)

    if theme_toggle != st.session_state.theme:
        st.session_state.theme = theme_toggle
        st.rerun()  # Forces UI refresh

    if st.session_state.theme == "Dark":
        st.markdown(
            """
            <style>
                body { background-color: #121212 !important; color: white !important; }
                .stTextInput>div>div>input, .stTextArea>div>textarea, .stSelectbox>div>div>select { 
                    background-color: #333 !important; color: white !important; 
                }
                .stButton>button { background-color: #444 !important; color: white !important; }
                .stDataFrame, .stTable { background-color: #1e1e1e !important; color: white !important; }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
                body { background-color: white !important; color: black !important; }
            </style>
            """,
            unsafe_allow_html=True
        )
