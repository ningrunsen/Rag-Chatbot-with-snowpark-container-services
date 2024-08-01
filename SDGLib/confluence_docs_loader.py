import streamlit as st
import pandas as pd
from snowflake.snowpark import Session
from langchain_community.document_loaders import ConfluenceLoader
from st_snowauth.st_snowauth import snowauth_session

def create_snowflake_session():
    """
    Creates a Snowflake session using the snowauth_session function.
    """
    session, user_info = snowauth_session()
    return session, user_info

def load_save_pages():
    """
    Loads pages from Confluence, extracts relevant data, and saves it to a Snowflake table.
    """
    try:
        # Get Confluence secrets
        CONFLUENCE_SPACE_NAME = st.secrets.confluence_secrets.CONFLUENCE_SPACE_NAME
        CONFLUENCE_SPACE_KEY = st.secrets.confluence_secrets.CONFLUENCE_SPACE_KEY
        CONFLUENCE_USERNAME = st.secrets.confluence_secrets.CONFLUENCE_USERNAME
        CONFLUENCE_API_KEY = st.secrets.confluence_secrets.CONFLUENCE_API_KEY

        # Get Snowflake settings
        CONFLUENCE_DATASET = st.secrets.adminPageSettings.snowflake.confluence_dataset

        # Load data from Confluence
        loader = ConfluenceLoader(
            url=CONFLUENCE_SPACE_NAME,
            username=CONFLUENCE_USERNAME,
            api_key=CONFLUENCE_API_KEY
        )

        docs = loader.load(
            space_key=CONFLUENCE_SPACE_KEY,
            limit=50,
            # include_attachments=True, # uncomment to include png, jpeg, .. -- Kinda doesnt work
            max_pages=1000,
            keep_markdown_format=True
        )

        # extract data and create a df
        extracted_data = []
        for doc in docs:
            flattened_doc = {
                'doc_id': doc.metadata.get('id', ''),
                'doc_title': doc.metadata.get('title', ''),
                'doc_content': doc.page_content,
                'source': doc.metadata.get('source', ''),
                'published': doc.metadata.get('when', '')
            }
            extracted_data.append(flattened_doc)

        # create df
        confluence_extracted_df = pd.DataFrame(extracted_data)

        # create Snowflake session
        session, user_info = create_snowflake_session()

        # Set the current database and schema
        confluence_database, confluence_schema, confluence_table = CONFLUENCE_DATASET.split('.')
        session.use_database(confluence_database)
        session.use_schema(confluence_schema)

        # define temporary table name
        temp_table = f"TEMP_{confluence_table}"

        # Convert Pandas DF to Snowpark DF
        snowpark_df = session.create_dataframe(confluence_extracted_df)

        # Define table creation SQL
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {confluence_table} (
            "doc_id" STRING,
            "doc_title" STRING,
            "doc_content" STRING,
            "source" STRING,
            "published" TIMESTAMP_NTZ
        )
        """

        # Execute table creation
        session.sql(create_table_sql).collect()

        # Create a temporary table to store the new data
        snowpark_df.write.mode("overwrite").save_as_table(temp_table)

        # Define the merge SQL
        merge_sql = f"""
        MERGE INTO {confluence_table} AS target
        USING {temp_table} AS source
        ON target."doc_id" = source."doc_id"
        WHEN MATCHED THEN
            UPDATE SET
                target."doc_title" = source."doc_title",
                target."doc_content" = source."doc_content",
                target."source" = source."source",
                target."published" = source."published"
        WHEN NOT MATCHED THEN
            INSERT ("doc_id", "doc_title", "doc_content", "source", "published")
            VALUES (source."doc_id", source."doc_title", source."doc_content", source."source", source."published")
        """

        # Execute the merge SQL
        session.sql(merge_sql).collect()

        # Drop the temporary table
        session.sql(f"DROP TABLE IF EXISTS {temp_table}").collect()

        return "Confluence data has been saved to Snowflake"

    except KeyError as e:
        st.error(f"KeyError: {str(e)}. Please check your secrets.toml configuration.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    load_save_pages()