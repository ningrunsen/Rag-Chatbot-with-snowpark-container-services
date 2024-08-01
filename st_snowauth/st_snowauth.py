# Code from https://github.com/sfc-gh-bhess/st_snowauth/blob/main/st_snowauth/st_snowauth.py
# Have to use over the package, as there is a user defined layout
from urllib.parse import urlencode, quote
import requests
import base64
import streamlit as st
from snowflake.snowpark import Session
import string
import random

_STKEY = 'SNOW_SESSION'
_DEFAULT_SECKEY = 'snowauth'

@st.cache_resource(ttl=300)
def qparms_cache(key):
    return {}

def logout():
    if _STKEY in st.session_state:
        st.session_state[_STKEY].close()
        del st.session_state[_STKEY]

def string_num_generator(size):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))

def validate_config(config):
    required_config_options = ['authorization_endpoint',
                               'token_endpoint',
                               'redirect_uri',
                               'client_id',
                               'client_secret',
                               'account']
    return all([k in config for k in required_config_options])

def show_auth_link(config, label):
    state_parameter = string_num_generator(15)
    qp_dict = {
        'redirect_uri': config['redirect_uri'],
        'client_id': config['client_id'],
        'response_type': 'code',
        'state': state_parameter
    }
    if 'role' in config:
        qp_dict['scope'] = f"session:role-encoded:{quote(config['role'])}"
    query_params = urlencode(qp_dict)
    request_url = f"{config['authorization_endpoint']}?{query_params}"
    if len(st.query_params) > 0:
        qpcache = qparms_cache(state_parameter)
        qpcache.update(st.query_params.to_dict())
    # st.markdown(f'<a href="{request_url}" target="_self">{label}</a>', unsafe_allow_html=True)
    # st.stop()   

    # Custom CSS for login page w/ Dark mode compability 
    css = """
    <style>
    body {
        font-family: Arial, sans-serif;
        background-color: var(--background-color);
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        margin: 0;
    }
    .container {
        background-color: var(--background-secondary-color);
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);  /* Can't add for dark mode */
        padding: 40px;
        width: 350px;
        text-align: center;
        margin: auto;
        border: 1px solid var(--border-color, #111111);  /* Stays white for dark mode */
    }
    .header {
        background-color: #E3F2FD;  
        border-radius: 10px 10px 0 0;
        padding: 20px;
    }
    .header img {
        height: 80px;
    }
    .title {
        font-size: 24px;
        margin: 20px 0 10px;
        color: var(--text-color);
    }
    .date-time {
        color: #888888;
        margin-bottom: 30px;
    }
    .snowflake-button {
        position: relative;
        padding: 10px 10px 10px 60px;
        background-color: #3580f2;  
        border-radius: 16px;
        border: 1px solid #d9d9d9;
        color: white;
        font-size: 20px;
        cursor: pointer;
        width: 100%;
        text-align: left;
        margin-bottom: 20px;
    }
    .snowflake-button::before {
        content: '';
        position: absolute;
        left: 10px;
        top: 50%;
        transform: translateY(-50%);
        width: 35px;
        height: 35px;
        background: url('https://cdn.icon-icons.com/icons2/2699/PNG/512/snowflake_logo_icon_167979.png') center/cover no-repeat;
        filter: brightness(0) invert(1);
    }
    .snowflake-button > span {
        position: relative;
        z-index: 1;
    }
    .snowflake-button:hover {
        background-color: #012d70;
    }
    .snowflake-button:focus {
        outline: none;
    }
    button {
        padding: 10px 20px;
        background-color: #3580f2; 
        border-radius: 16px;
        border: 1px solid #d9d9d9;
        color: white;
        font-size: 20px;
        cursor: pointer;
        width: 100%;
        margin-bottom: 20px;
    }
    button:hover {
        background-color: #012d70;
    }
    button:focus {
        outline: none;
    }
    .signin-option {
        display: flex;
        align-items: center;
        border: 1px solid #DDDDDD;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        cursor: pointer;
    }
    .signin-option img {
        width: 20px;
        margin-right: 10px;
    }
    .signin-option:hover {
        background-color: #F5F5F5;
    }
    .signin-option span {
        flex-grow: 1;
        text-align: left;
        color: var(--text-color);
    }
    .continue {
        color: var(--text-color);
        margin-top: 20px;
        cursor: pointer;
    }
    .continue:hover {
        text-decoration: underline;
    }

    /* Dark mode adjustments */
    :root {
        --border-color: #FFFFFF;
    }
    </style>
    """

    # Custom HTML for login page w/ Dark mode compability 
    # <! Can't do ` <a href="{request_url}" target="_self"> `, have to open in New Tab (code line 191)
    html_content = f"""
    <div class="container">
        <div class="header">
            <img src="https://raw.githubusercontent.com/hpsdg/sdg_images/024d9735509867ba7d38a4c8da7eebcbf7cc9f3a/sdg-logo.png" alt="Logo">
        </div>
        <div class="title">SDG Chatbot</div>
        <a href="{request_url}">
            <button class="snowflake-button">Sign in with Snowflake</button>
        </a>
        <div class="continue">Continue without signing in</div>
    </div>
    """

    # Render the form
    st.markdown(css, unsafe_allow_html=True)
    st.markdown(html_content, unsafe_allow_html=True)

    st.stop()

def snowauth_session(config=None, label="Login to Snowflake"):
    # Show our custom sidebar
    # custom_sidebar.apply_custom_sidebar()

    if not config:
        config = _DEFAULT_SECKEY
    if isinstance(config, str):
        config = st.secrets[config]
    if _STKEY in st.session_state:
        session = st.session_state[_STKEY]
        if session._conn._conn.is_closed():
            logout()
    if _STKEY not in st.session_state:
        if not validate_config(config):
            st.error("Invalid OAuth Configuration")
            st.stop()
        if 'code' not in st.query_params:
            show_auth_link(config, label)
        code = st.query_params['code']
        state = st.query_params['state']
        st.query_params.clear()
        st.query_params.update(qparms_cache(state))
        qparms_cache(state).clear()
        theaders = {
            'Authorization': 'Basic {}'.format(base64.b64encode('{}:{}'.format(config["client_id"], config["client_secret"]).encode()).decode()),
            'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'
        }
        tdata = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': config['redirect_uri']
        }
        try:
            ret = requests.post(config["token_endpoint"],
                                headers=theaders,
                                data=urlencode(tdata).encode("utf-8")
                                )
            ret.raise_for_status()
        except requests.exceptions.RequestException as e:
            st.error(e)
            show_auth_link(config, label)
        token = ret.json()

        snow_configs = {
            'account': config['account'],
            'authenticator': 'oauth',
            'token': token['access_token']
        }
        if 'connection' in config:
            snow_configs = {**config['connection'], **snow_configs}
        del token
        try:
            st.session_state[_STKEY] = Session.builder.configs(snow_configs).create()
        except Exception as e:
            st.error(f"Error connecting to Snowflake: \n{str(e)}")
            show_auth_link(config, label)

    session = st.session_state[_STKEY]
    user_info = {
        'username': session.get_current_user(),
        'roles': session.get_current_role(),
        'database': session.get_current_database(),
        'schema': session.get_current_schema()
    }
    # st.sidebar.button("Logout", on_click=logout)
    return session, user_info