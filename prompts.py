import streamlit as st
from snowflake.snowpark import Session
from st_snowauth.st_snowauth import snowauth_session

QUALIFIED_TABLE_NAME = st.secrets["adminPageSettings"]["snowflake"]["confluence_dataset"]
TABLE_DESCRIPTION = """
This table contains extracted data from Atlassian Confluence pages. It includes five columns:

- DOC_ID: Unique identifier for each document.
- DOC_TITLE: Title of the document.
- DOC_CONTENT: Main content of the document.
- SOURCE: URL of the source document.
- PUBLISHED: Publication date of the document.

The main documentation portion is stored in the DOC_CONTENT column. The remaining columns, including DOC_ID, DOC_TITLE, SOURCE, and PUBLISHED, are considered metadata, providing context and additional information about the documents.
"""

# This query is optional if running Nova on your own table, especially a wide table.
# Since this is a deep table, it's useful to tell Nova what variables are available.
# Similarly, if you have a table with semi-structured data (like JSON), it could be used to provide hints on available keys.
# If altering, you may also need to modify the formatting logic in get_table_context() below.
METADATA_QUERY = f"SELECT DOC_TITLE, SOURCE FROM {QUALIFIED_TABLE_NAME};"

GEN_SQL = """
You will be acting as an AI Snowflake SQL Expert named Nova.
Your goal is to provide information based on the data extracted from Confluence pages.
You will be replying to users who will be confused if you don't respond in the character of Nova.
You are given one table, the table name is in <tableName> tag, the columns are in <columns> tag.
If the user asks questions about the data from Confluence pages, you will provide information based on the document content (DOC_CONTENT) and include metadata (mainly SOURCE) in your responses.

{context}

Here are 6 critical rules for the interaction you must abide:
<rules>
1. You MUST provide information based on the document content (DOC_CONTENT) and include metadata (mainly SOURCE).
2. If I don't tell you to find a limited set of results in the query or question, you MUST limit the number of responses to 10.
3. Text / string where clauses must be fuzzy match e.g ilike %keyword%
4. Make sure to generate a single response, not multiple. 
5. You should only use the table columns given in <columns>, and the table given in <tableName>, you MUST NOT hallucinate about the table names.
6. DO NOT put numerical at the very front of variable names.

For each question from the user, make sure to include relevant information based on DOC_CONTENT and provide the SOURCE as metadata.

To get started, please briefly introduce yourself. Then provide the available metrics for this table in a list format. Lastly, provide 3 example questions using bullet points, but do not answer them. Only give example questions the user can ask.

Here's more context:
The table_name serves as an extensive collection of documentation crucial for managing SQL pipelines and understanding virtualization techniques. It covers a wide range of topics, including the activation and deactivation of SQL pipelining and virtualization, methods for comparing SQL data, and adherence to data validation standards. This guide is ideal for professionals seeking specific information on optimizing virtualization pipelines and managing edit flow settings in SQL environments.
When users ask questions, provide answers based on the information in the DOC_CONTENT column, including relevant excerpts. Towards the end of the message, direct the user to the relevant source URL.
"""
# Create Snowflake session
def create_snowflake_session():
    session, _ = snowauth_session()
    return session
session = create_snowflake_session()

@st.cache_data(show_spinner="Loading Nova's context...")
def get_table_context(table_name: str, table_description: str, metadata_query: str = None):
    table = table_name.split(".")
    # conn = st.connection("snowflake")
    # columns = conn.query(f"""
    #     SELECT COLUMN_NAME, DATA_TYPE FROM {table[0].upper()}.INFORMATION_SCHEMA.COLUMNS
    #     WHERE TABLE_SCHEMA = '{table[1].upper()}' AND TABLE_NAME = '{table[2].upper()}'
    #     """, show_spinner=False,
    # )
    # columns = "\n".join(
    #     [
    #         f"- **{columns['COLUMN_NAME'][i]}**: {columns['DATA_TYPE'][i]}"
    #         for i in range(len(columns["COLUMN_NAME"]))
    #     ]
    # )
    columns_query = f"""
        SELECT COLUMN_NAME, DATA_TYPE FROM {table[0].upper()}.INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = '{table[1].upper()}' AND TABLE_NAME = '{table[2].upper()}'
    """
    columns = session.sql(columns_query).to_pandas()
    columns_text = "\n".join(
        [
            f"- **{columns['COLUMN_NAME'][i]}**: {columns['DATA_TYPE'][i]}"
            for i in range(len(columns["COLUMN_NAME"]))
        ]
    )
    context = f"""
Here is the table name: {'.'.join(table)}>

<tableDescription>{table_description}</tableDescription>

Here are the columns of the {'.'.join(table)}

<columns>\n\n{columns_text}\n\n</columns>
    """
    if metadata_query:
        # metadata = conn.query(metadata_query, show_spinner=False)
        metadata = session.sql(metadata_query).to_pandas()
        metadata = "\n".join(
            [
                f"- **{metadata['DOC_TITLE'][i]}**: {metadata['SOURCE'][i]}"
                for i in range(len(metadata["DOC_TITLE"]))
            ]
        )
        context = context + f"\n\nAvailable variables by DOC_TITLE:\n\n{metadata}"
    return context

def get_system_prompt(): 
    table_context = get_table_context(
        table_name=QUALIFIED_TABLE_NAME,
        table_description=TABLE_DESCRIPTION,
        metadata_query=METADATA_QUERY
    )
    return GEN_SQL.format(context=table_context)

# do `streamlit run prompts.py` to view the initial system prompt in a Streamlit app
if __name__ == "__main__":
    st.header("System prompt for Nova")
    st.markdown(get_system_prompt())