import streamlit as st 
import pandas as pd
import time
import os

# Set images path 
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, 'static')
page_icon_path = os.path.join(static_dir, 'sdg-icon.png')
page_icon_svg_path = os.path.join(static_dir, 'sdg-icon.svg')

# Set Page Configurations
st.set_page_config(
    page_title="SDG Chatbot", 
    page_icon=page_icon_path,
    initial_sidebar_state="expanded",
)

# import snowflake.connector # Removed logic
from SDGLib import response_generator, custom_sidebar #confluence_docs_loader, process_confluence_data, 
from streamlit_navigation_bar import st_navbar
from st_snowauth.st_snowauth import snowauth_session
from pages import bug, help, home, admin_page, about, logout
from collections import Counter
import re

# Import both prompt functions
from prompts import get_system_prompt as get_system_prompt_confluence
from prompts_handbook import get_system_prompt as get_system_prompt_handbook


# Caching the Snowflake session
@st.cache_resource
def create_snowflake_session():
    session, user_info = snowauth_session()
    return session, user_info
# Create or get the cached Snowflake session
session, user_info = create_snowflake_session()

# Test Snowflake connection
@st.cache_data
def test_snowflake_connection():
    try:
        # session, user_info  = create_snowflake_session()
        result = session.sql("SELECT CURRENT_TIMESTAMP()").collect()
        timestamp = result[0]['CURRENT_TIMESTAMP()']
        formatted_timestamp = timestamp.strftime("%Y-%m-%d : %H:%M:%S")
        return f"Snowflake connection successful: {formatted_timestamp}"
    except Exception as e:
        return f"Snowflake connection failed: {str(e)}"

def summarize_question_with_history(chat_history, question, model_name):
    prompt = f"""
    Based on the chat history below and the question, generate a concise query that extends the question
    with the provided chat history. The query should be in natural language. 
    Answer with only the query. Do not add any explanation, assumptions, or additional details not present in the chat history.
    
    <chat_history>
    {chat_history}
    </chat_history>
    <question>
    {question}
    </question>
    """

    # Escape single quotes in the prompt to prevent SQL injection issues
    escaped_prompt = prompt.replace("'", "''")

    cmd = f"""
        SELECT snowflake.cortex.complete('{model_name}', '{escaped_prompt}') AS response
    """
    
    # session = create_snowflake_session()
    df_response = session.sql(cmd).collect()

    summary = df_response[0]['RESPONSE']

    if st.session_state.debug:
        st.sidebar.text("Summary of Question Asked:")
        st.sidebar.caption(summary)

    summary = summary.replace("'", "")
    return summary.strip()  # Ensure no extra spaces

def is_related_to_previous_question(current_question, previous_question, previous_response):
    def tokenize(text):
        words = re.findall(r'\w+', text.lower())
        return Counter(words)
    
    current_words = tokenize(current_question)
    previous_question_words = tokenize(previous_question)
    previous_response_words = tokenize(previous_response)

    common_words_question = sum((current_words & previous_question_words).values())
    common_words_response = sum((current_words & previous_response_words).values())

    threshold = 2  # You can adjust this threshold
    return (common_words_question >= threshold) or (common_words_response >= threshold)

def initialize_session_state(get_system_prompt):
    if 'button_clicked' not in st.session_state:
        st.session_state['button_clicked'] = False
    if 'started' not in st.session_state:
        st.session_state['started'] = True # False # Made T, since "Start Now" button was removed
    if 'messages' not in st.session_state:
        st.session_state['messages'] = [{"role": "system", "content": get_system_prompt()}]
    if 'first_question' not in st.session_state:
        st.session_state['first_question'] = True

def show_chatbot_page():
    custom_sidebar.apply_custom_sidebar()

    # Sidebar for model selection
    model_options = ['mixtral-8x7b', 'snowflake-arctic', 'mistral-large', 'llama3-8b', 'llama3-70b', 'reka-flash', 'mistral-7b', 'llama2-70b-chat', 'gemma-7b']
    selected_model = st.sidebar.selectbox('Select a model', model_options, index=model_options.index('mixtral-8x7b'))
    st.session_state.model_name = selected_model

    # Sidebar for document type selection
    doc_type_options = ['Confluence Data', 'SDG Handbook Data']
    selected_doc_type = st.sidebar.selectbox('Select Document Type', doc_type_options, index=1)
    st.session_state.doc_type = selected_doc_type

    # Select the appropriate get_system_prompt function
    if selected_doc_type == 'Confluence Data':
        get_system_prompt = get_system_prompt_confluence
    else:
        get_system_prompt = get_system_prompt_handbook

    # Checkbox for chat history
    use_chat_history = st.sidebar.checkbox('Do you want me to remember the chat history?', key="use_chat_history", value=True)

    # Checkbox for debug summary (potentially redundant)
    st.sidebar.checkbox('Debug: Click to see summary generated of previous conversation', key="debug", value=True)

    if not use_chat_history:
        st.session_state.clear()

    # Initialize session state
    initialize_session_state(get_system_prompt)

    st.markdown("<h1 style='text-align: center;'>SDG Chatbot</h1>", unsafe_allow_html=True)
    st.write(f"Welcome, {user_info['username']}!") # TEMP

    # Commenting out "Start Now", as the welcome msg is now removed
    # if st.button("Start Now"):
    #     st.session_state["started"] = True

    if st.session_state.get("started"):
        connection_status = test_snowflake_connection()
        st.success(connection_status)
        
        # Prompt for user input and save
        if prompt := st.chat_input(placeholder="Type your message here..."):
            st.session_state.messages.append({"role": "user", "content": prompt})

        # Simulate streaming responses from Snowflake Cortex
        def simulate_streaming_response(prompt, model_name, doc_type):
            if st.session_state.first_question:
                extended_query = prompt
                st.session_state.first_question = False
            else:
                chat_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages if msg['role'] != "system"])
                if len(st.session_state.messages) > 1:
                    previous_question = st.session_state.messages[-2]["content"]
                    previous_response = st.session_state.messages[-1]["content"]
                    if is_related_to_previous_question(prompt, previous_question, previous_response):
                        extended_query = summarize_question_with_history(chat_history, prompt, model_name)
                    else:
                        extended_query = prompt
                else:
                    extended_query = prompt

            # session = create_snowflake_session()
            full_response = response_generator.create_cortex_response(session, extended_query, model_name, doc_type)
            chunk_size = 100 
            for i in range(0, len(full_response), chunk_size):
                time.sleep(0.1) 
                yield full_response[i:i+chunk_size]

        # Display the existing chat messages
        for message in st.session_state.messages:
            if message["role"] != "system": 
                with st.chat_message(message["role"]):
                    st.write(message["content"])

        # Generate a new response if last message is from user
        if st.session_state.messages[-1]["role"] == "user":
            user_message = st.session_state.messages[-1]["content"]
            with st.chat_message("assistant"):
                response_container = st.empty()
                response = ""
                for chunk in simulate_streaming_response(user_message, selected_model, selected_doc_type):
                    response += chunk
                    response_container.markdown(response + "█")
                response_container.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

# Navbar rendering
def render_navbar():
    pages = ["Chatbot", "Get Help", "Report a bug", "About", "Admin", "Logout"]
    logo_path = page_icon_svg_path
    styles = {
        "nav": {
            "background-color": "royalblue",
            "justify-content": "center",
        },
        "img": {
            "padding-right": "14px",
        },
        "span": {
            "color": "white",
            "padding": "14px",
        },
        "active": {
            "background-color": "darkblue",
            "color": "var(--text-color)",
            "font-weight": "normal",
            "padding": "14px",
        }
    }
    options = {
        "show_menu": True,
    }

    return st_navbar(
        pages,
        selected="Chatbot",
        logo_path=logo_path,
        styles=styles,
        options=options,
    )

# Render the navbar
page = render_navbar()

functions = {
    "Home": home.show_home,
    "Chatbot": show_chatbot_page,
    "Get Help": help.get_help,
    "Report a bug": bug.report_bugs, 
    "About": about.show_about,
    "Admin": admin_page.show_admin_page,
    "Logout": logout.perform_logout
}

go_to = functions.get(page)
if go_to:
    go_to()