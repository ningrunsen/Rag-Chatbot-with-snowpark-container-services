import streamlit as st
# from streamlit_theme import st_theme 


def apply_custom_sidebar():
    # CSS for the sidebar -> has Logo and New Chat option

    # Set sidebar logo based of theme settings
    # logo_path= ("https://github.com/hpsdg/sdg_chatbot/blob/main/static/sdg-logo-white.png"
    # if is_dark_mode
    # else "https://github.com/hpsdg/sdg_chatbot/blob/main/static/sdg-logo.png"
    # )

    # Set images path -- cant figure out what the path should be (like how I did in main script with dir)
    # Had to create new github repo, with public images
    # sidebar_logo_path = "https://raw.githubusercontent.com/hpsdg/sdg_images/main/sdg-logo.png"
    sidebar_logo_path = "https://raw.githubusercontent.com/hpsdg/sdg_images/main/sdg-logo-blue.png"

    with st.sidebar:
        st.markdown(
            """
            <style>
                section[data-testid="stSidebar"] {
                    width: 300px !important; 
                }
                .custom-sidebar {
                    display: flex;
                    flex-direction: row;
                    align-items: flex-start;
                    justify-content: space-between; 
                }
                .sidebar-logo {
                    max-width: 200px; /* sidebar logo size */
                }
                .sidebar-restart-button {
                    display: flex;
                    align-items: center;
                    justify-content: flex-end; /* new chat button to the right */
                }
                .sidebar-restart-button button {
                    background: none;
                    border: none;
                    cursor: pointer;
                    /* filter: { "invert(1)" if is_dark_mode else "none }; new chat icon, if dark mode, turns white */
                }
                .sidebar-restart-button img {
                    width: 30px;
                    height: 30px;
                }
                div[data-testid="stSidebarUserContent"] {
                    padding-top: 0rem !important;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Add the custom HTML for the sidebar
        sidebar_logo = sidebar_logo_path
        sidebar_html = f"""
            <div class="custom-sidebar">
                <div class="sidebar-logo">
                    <img src="{sidebar_logo}" width="210" height="110">  <!-- logo size -->
                </div>
                <div class="sidebar-restart-button">
                    <form action="/" method="get">
                        <button type="submit" name="restart" value="clicked">
                            <img src="https://cdn3.iconfinder.com/data/icons/feather-5/24/edit-1024.png" alt="New Chat">
                        </button>
                    </form>
                </div>
            </div>
        """
        st.sidebar.markdown(sidebar_html, unsafe_allow_html=True)