import streamlit as st
import pandas as pd
# from snowflake.connector import connect # removed logic
from snowflake.snowpark import Session
import snowflake
from streamlit_option_menu import option_menu 
from SDGLib import confluence_docs_loader, process_confluence_data, admin_settings 
from st_snowauth.st_snowauth import snowauth_session

# Create Snowflake connection
@st.cache_data(ttl=600)  # Cache the connection for 10 minutes
def create_and_test_snowflake_connection():
    try:
        session, _ = snowauth_session()
        result = session.sql("SELECT CURRENT_TIMESTAMP()").collect()
        timestamp = result[0]['CURRENT_TIMESTAMP()']
        formatted_timestamp = timestamp.strftime("%Y-%m-%d : %H:%M:%S")
        return f"Snowflake connection successful: {formatted_timestamp}"
    except Exception as e:
        return f"Snowflake connection failed: {str(e)}"
    
def show_admin_page():
    # Create Sidebar 
    with st.sidebar:
        # Same CSS as Chatbot
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
                div[data-testid="stSidebarUserContent"] {
                    padding-top: 0rem !important;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )
        # Create the option menu
        selected = option_menu(
            menu_title="Settings",
            options=["Home","Confluence", "Stage", "Manual"],
            icons=["house","cloud", "folder", "upload"], 
            menu_icon="gear",  # Menu icon
            default_index=0,
            styles={
            #     "container": {"padding": "0px", "background-color": "#262730"},
                "menu_title": {"color": "blue", "font-size": "5px"},
                "icon": {"color": "white", "font-size": "15px"}
            #     "nav-link": {"font-size": "18px", "text-align": "left", "margin": "0px", "--hover-color": "#eee"},
            #     "nav-link-selected": {"background-color": "#ff4b4b"},
            }
        )

    content_placeholder = st.empty()    

    # Page 1 | Sidebar
    if selected == "Home":
        with content_placeholder.container():
            st.title("Admin Settings Menu Options")

            # Confluence Data Processing
            st.markdown("### **Confluence Data Processing**")
            st.write("""
            * Loads pages from Confluence and extracts relevant data.
            * Splits the document content into manageable chunks.
            * Saves the chunks in a Snowflake table (CONFLUENCE_DATA_CHUNKS).
            * Generates embeddings for the chunks to facilitate analysis.
            """)

            # Stage Data Processing
            st.markdown("### **Stage Data Processing**")
            st.write("""
            * Connects to the staging area in Snowflake Stages (S3 bucket location).
            * Extracts content from various formats: PPTx, DOCx, PDF, and TXT files.
            """)

            # Manual Data Processing
            st.markdown("### **Manual Data Processing**")
            st.write("""
            * Provides a user interface for uploading PPTx, DOCx, PDF, and TXT files.
            * Extracts key information from the uploaded documents.
            """)

    # Page 2 | Sidebar
    if selected == "Confluence": 
        with content_placeholder.container():   
            st.title("Confluence Loader")
            # Test the Snowflake connection and display the status
            connection_status = create_and_test_snowflake_connection()
            workspace_key = st.secrets["confluence_secrets"]["CONFLUENCE_SPACE_KEY"]
            st.info(f"""**Notice:** Currently using `'{workspace_key}'` space. If you intend to use another workspace, please contact the project owner 
                    to update the API in the secrets configuration.""")
            # horizontal layout for the buttons
            col1, col2, col3 = st.columns(3)

            with col1:
                load_and_save = st.button("Load and Save Pages")
                st.caption("Save original data without chunking or vectorizing.")

            with col2:
                chunk_and_store = st.button("Chunk and Store Data")
                st.caption("Chunk text and vectorize data for better LLM querying.")

            with col3:
                show_dataframe = st.button("Show DataFrame")
                st.caption("Display the chunked dataset.")

            # Outputs section
            output_section = st.empty()

            if load_and_save:
                with st.spinner('Loading and saving pages...'):
                    status_message = confluence_docs_loader.load_save_pages()
                with output_section:
                    st.success(status_message)

            if chunk_and_store:
                with st.spinner('Chunking and storing data...'):
                    status_message = process_confluence_data.chunk_and_store()
                with output_section:
                    st.success(status_message)

            if show_dataframe:
                with st.spinner('Fetching data...'):
                    df = admin_settings.get_data_from_snowflake()
                with output_section:
                    st.dataframe(df)

    # Page 3 | Sidebar
    if selected == "Stage":
        with content_placeholder.container():
            st.title("Stage Documents")
            # Test the Snowflake connection and display the status
            connection_status = create_and_test_snowflake_connection()
            st.success(connection_status)
            admin_settings.stage_documents_handler()

    # Page 4 | Sidebar
    if selected == "Manual":
        with content_placeholder.container():
            st.title("Manual Upload")
            # Test the Snowflake connection and display the status
            connection_status = create_and_test_snowflake_connection()
            st.success(connection_status)
            admin_settings.upload_documents_handler()