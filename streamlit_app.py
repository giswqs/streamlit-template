import streamlit as st
from streamlit_option_menu import option_menu
from apps import home, heatmap, upload, test, change_detection, Timelapse, ChangeDetection  # import your app modules here

st.sidebar.title("Usage")
st.sidebar.info(
    """
    1) Enter Latitude and Longitude of the area you want to view
    2) Set the start and end dates for the images
    3) select the layers to display on the left and right map panes
    """
)

st.sidebar.title("Instructions")
st.sidebar.info(
    """
    1) Enter Latitude and Longitude of the area you want to view
    2) Set your date ranges
    3) To view the change detection, set either the "New Bare Ground" or the "New Built-Up area" to the left or right map panes
    """
)


# A dictionary of apps in the format of {"App title": "App icon"}
# More icons can be found here: https://icons.getbootstrap.com

apps = [
    # {"func": home.app, "title": "Home", "icon": "house"},
    # {"func": heatmap.app, "title": "Heatmap", "icon": "map"},
    # {"func": upload.app, "title": "Upload", "icon": "cloud-upload"},
    # {"func": test.app, "title": "Test", "icon": "cloud-upload"},
    # {"func": change_detection.app, "title": "Change", "icon": "map"},
    # {"func": Timelapse.app, "title": "Timelapse", "icon": "map"},
    {"func": ChangeDetection.app, "title": "Change Detection", "icon": "map"}
]

titles = [app["title"] for app in apps]
titles_lower = [title.lower() for title in titles]
icons = [app["icon"] for app in apps]

params = st.experimental_get_query_params()

if "page" in params:
    default_index = int(titles_lower.index(params["page"][0].lower()))
else:
    default_index = 0

with st.sidebar:
    selected = option_menu(
        "Main Menu",
        options=titles,
        icons=icons,
        menu_icon="cast",
        default_index=default_index,
    )

    st.sidebar.title("About")
    st.sidebar.info(
        """
        test
    """
    )

for app in apps:
    if app["title"] == selected:
        app["func"]()
        break
