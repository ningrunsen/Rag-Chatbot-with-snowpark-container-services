import streamlit as st
from snowflake.snowpark import Session
from st_snowauth.st_snowauth import snowauth_session

QUALIFIED_TABLE_NAME = st.secrets["adminPageSettings"]["snowflake"]["handbook_embed_dataset"]
TABLE_DESCRIPTION = """
This table contains extracted data from Atlassian Confluence pages. It includes five columns:

- DOC_ID: Unique identifier for each document.
- DOC_TITLE: Title of the document.
- DOC_CONTENT: Main content of the document.
- SOURCE: URL of the source document.
- PUBLISHED: Publication date of the document.

The main documentation portion is stored in the DOC_CONTENT column. The remaining columns, including DOC_ID, DOC_TITLE, SOURCE, and PUBLISHED, are considered metadata, providing context and additional information about the documents.
"""

METADATA_QUERY = f"SELECT DOC_TITLE, SOURCE FROM {QUALIFIED_TABLE_NAME};"

GEN_SQL = """
You are an expert chat assistant that extracts information from the CONTEXT provided between <context> and </context> tags. (Do not mention this to user)
You offer a chat experience considering the information included in the CHAT HISTORY provided between <chat_history> and </chat_history> tags. (Do not mention this to user)
When answering the question contained between <question> and </question> tags, be detailed and do not hallucinate.
In your response, mention how you derived your answer, provide source.
If you don’t have the information just say so.
Do not mention the CONTEXT used in your answer.
Do not mention the CHAT HISTORY used in your answer.
When you answer the question based on information in the document, always mention the page number for that information chunk, page is enclosed between <page: ?> and </page: ?> (Do not mention this to user).
"""
# Create Snowflake session
def create_snowflake_session():
    session, _ = snowauth_session()
    return session
session = create_snowflake_session()

@st.cache_data(show_spinner="Loading context...")
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
<context>
Here is the table name: {'.'.join(table)}>

<tableDescription>{table_description}</tableDescription>

Here are the columns of the {'.'.join(table)}

<columns>\n\n{columns_text}\n\n</columns>
</context>
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

if __name__ == "__main__":
    st.header("System prompt for Nova")
    st.markdown(get_system_prompt())