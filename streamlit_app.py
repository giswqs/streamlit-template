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

    st.sidebar.title("About")
    st.sidebar.info(
        """
        This web [app](https://share.streamlit.io/giswqs/streamlit-template) is maintained by [Qiusheng Wu](https://wetlands.io). You can follow me on social media:
            [GitHub](https://github.com/giswqs) | [Twitter](https://twitter.com/giswqs) | [YouTube](https://www.youtube.com/c/QiushengWu) | [LinkedIn](https://www.linkedin.com/in/qiushengwu).
        
        Source code: <https://github.com/giswqs/streamlit-template>

        More icons: <https://icons.getbootstrap.com>
    """
    )

if selected == "Home":
    home.app()
elif selected == "Heatmap":
    heatmap.app()
