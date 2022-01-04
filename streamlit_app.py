import streamlit as st
from streamlit_option_menu import option_menu
from apps import home, heatmap  # import your app modules here

st.set_page_config(layout="wide")

with st.sidebar:
    selected = option_menu(
        "Main Menu",
        ["Home", "Heatmap"],
        icons=["house", "map"],
        menu_icon="cast",
        default_index=1,
    )
    st.markdown(
        """
    More icons, see <https://icons.getbootstrap.com>
    """
    )

if selected == "Home":
    home.app()
elif selected == "Heatmap":
    heatmap.app()
