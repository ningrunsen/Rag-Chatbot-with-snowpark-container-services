import streamlit as st
# import snowflake.connector # removed
from snowflake.snowpark import Session
from st_snowauth.st_snowauth import snowauth_session

def create_snowflake_session():
    session, _ = snowauth_session()
    return session
session = create_snowflake_session()

def store_feedback(name, email, bugs, feedback, priority):
    table = st.secrets.adminPageSettings.snowflake.feedback_bug_reporter
    query = f"""
        INSERT INTO {table} (name, email, bugs, feedback, priority, timestamp)
        VALUES ('{name}', '{email}', '{bugs}', '{feedback}', '{priority}', CURRENT_TIMESTAMP)
    """
    session.sql(query).collect()

def generate_email(name):
    name_parts = name.lower().split()
    if len(name_parts) >= 2:
        return f"{name_parts[0]}.{name_parts[1]}@sdggroup.com"
    return ""

def update_email():
    st.session_state.email = generate_email(st.session_state.name)

def report_bugs():
    st.title("Bug / Feedback Reporter")

    st.write("We value your feedback. Please fill out the form below to report any bugs or provide suggestions.")
    st.info("Enter your full name to automatically fill in your SDG email address.")

    # Pre-fill name and email
    if "name" not in st.session_state:
        st.session_state.name = "Enter Name"
    if "email" not in st.session_state:
        st.session_state.email = "your.email@sdggroup.com"

    name = st.text_input("Name", value=st.session_state.name, key="name", on_change=update_email)
    email = st.text_input("Email", value=st.session_state.email, key="email")

    bugs = st.text_area("Bugs")
    feedback = st.text_area("Feedback")
    priority = st.selectbox("Priority", ["Low", "Medium", "High", "None"])

    if st.button("Submit"):
        if name and email and (bugs or feedback):
            try:
                store_feedback(name, email, bugs, feedback, priority)
                st.success("Thank you for your response!")
            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.error("Please fill out all required fields (Name, Email, and either Feedback or Bugs).")