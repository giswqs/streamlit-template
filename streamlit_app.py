import streamlit as st
from streamlit_option_menu import option_menu
from apps import home, heatmap, upload  # import your app modules here

st.set_page_config(layout="wide")

# A dictionary of apps in the format of {"App title": "App icon"}
# More icons can be found here: https://icons.getbootstrap.com
apps = {"Home": "house", "Heatmap": "map", "Upload": "cloud-upload"}

titles = [title.lower() for title in list(apps.keys())]
params = st.experimental_get_query_params()

if "page" in params:
    default_index = int(titles.index(params["page"][0].lower()))
else:
    default_index = 0

with st.sidebar:
    selected = option_menu(
        "Main Menu",
        options=list(apps.keys()),
        icons=list(apps.values()),
        menu_icon="cast",
        default_index=default_index,
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

# Place each app module under the apps folder
if selected == "Home":
    home.app()
elif selected == "Heatmap":
    heatmap.app()
elif selected == "Upload":
    upload.app()
