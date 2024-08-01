# README # 

# How to Run locally 

## Cloning the Repository and Opening in VS Code

1. Create a folder where you want to clone the repository.
2. Open the created folder in Visual Studio Code (VS Code).
3. Open a terminal in VS Code (you can use the integrated terminal) and run the following command to clone the repository:
   ```bash
   git clone https://github.com/hpsdg/sdg_chatbot.git
   ```
4. Navigate to the cloned repository:
   ```bash
   cd sdg_chatbot
   ```

## Installing Required Libraries

1. Ensure you have **Python 3.11.9** installed on your system.
2. Create a virtual environment named `sdg_chatbot_env` by running the following command:
   ```bash
   python -m venv sdg_chatbot_env 
   ```
3. Activate the virtual environment:

   - For Command Prompt:
     ```bash
     sdg_chatbot_env\Scripts\activate
     ```
   - For PowerShell:
     ```bash
     .\sdg_chatbot_env\Scripts\Activate.ps1
     ```
   - For macOS/Linux:
     ```bash
     source sdg_chatbot_env/bin/activate
     ```
   - Or if you have Conda installed:
     ```bash
     conda activate sdg_chatbot_env
     ```
4. Install the required libraries from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

## **Before You Run**

1. Create a folder named `.streamlit` in the root directory of the project:
   ```bash
   mkdir .streamlit
   ```

2. Inside the `.streamlit` folder, create a file named `secrets.toml` and add the following content:

   ```toml
   # DEV
   [snowauth]

   # I will send this

   ```

3. Also in the `secrets.toml`, add the following content:

   ```toml
   [connections.snowflake]
    user = "<your_user>"
    password = "<your_password>"
    account = "sdggrouppartner.us-east-1"
    role = "DATA_QUALITY_ADMIN"
    warehouse = "DEMO_WH"
    database = "DATA_QUALITY_DB"
    schema = "NVS_LLM_INPUT"
   ```

## Running the Application

To run the SDG Chatbot application, execute the following command in your terminal:

```bash
streamlit run sdg_chatbot.py
```

This will start the Streamlit server and open the application in your default web browser.