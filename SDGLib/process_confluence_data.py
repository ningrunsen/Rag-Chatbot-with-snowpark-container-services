import streamlit as st
import pandas as pd
from snowflake.snowpark import Session
import math
from st_snowauth.st_snowauth import snowauth_session

def create_snowflake_session():
    """
    Creates a Snowflake session using the snowauth_session function.
    """
    session, _ = snowauth_session()
    return session

def chunk_and_store():
    """
    Connects to Snowflake, retrieves Confluence data, splits the document content into chunks,
    and stores/updates the chunks in a Snowflake table (CONFLUENCE_DATA_CHUNKS). Also generates embeddings for the chunks.
    """
    try:
        # Get dataset paths from secrets
        confluence_dataset = st.secrets.adminPageSettings.snowflake.confluence_dataset
        confluence_embed_dataset = st.secrets.adminPageSettings.snowflake.confluence_embed_dataset

        # Create Snowflake session
        session = create_snowflake_session()

        # Set the current database and schema for fetching data
        confluence_database, confluence_schema, confluence_table = confluence_dataset.split('.')
        session.use_database(confluence_database)
        session.use_schema(confluence_schema)

        # Fetch data from the CONFLUENCE_DATA table
        fetch_sql = f"""
        SELECT * 
        FROM {confluence_table}
        """
        rows = session.sql(fetch_sql).to_pandas()

        # Set the current database and schema for storing chunks
        embed_database, embed_schema, embed_table = confluence_embed_dataset.split('.')
        session.use_database(embed_database)
        session.use_schema(embed_schema)

        # Create the CONFLUENCE_DATA_CHUNKS table
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {embed_table} (
            "DOC_ID" STRING,
            "DOC_TITLE" STRING,
            "CHUNK_NUMBER" INTEGER,
            "CHUNK_CONTENT" STRING,
            "EMBEDDING" VECTOR(FLOAT, 768),
            "SOURCE" STRING,
            "PUBLISHED" TIMESTAMP_NTZ
        )
        """
        session.sql(create_table_sql).collect()

        # Split document content into chunks and insert/merge into the CONFLUENCE_DATA_CHUNKS table
        chunk_size = 1000
        temp_table = f"TEMP_{embed_table}"

        all_chunk_data = []
        for row in rows.itertuples(index=False):
            doc_id, doc_title, doc_content, source, published = row
            num_chunks = math.ceil(len(doc_content) / chunk_size)
            for i in range(num_chunks):
                chunk_content = doc_content[i * chunk_size: (i + 1) * chunk_size]
                chunk_number = i + 1
                all_chunk_data.append((doc_id, doc_title, chunk_number, chunk_content, source, published))

        # Convert chunk data to DataFrame
        chunk_df = pd.DataFrame(all_chunk_data, columns=["DOC_ID", "DOC_TITLE", "CHUNK_NUMBER", "CHUNK_CONTENT", "SOURCE", "PUBLISHED"])
        # print(f"Chunk DataFrame: \n{chunk_df.head()}")
        snowpark_chunk_df = session.create_dataframe(chunk_df)

        # Write chunk data to temporary table
        snowpark_chunk_df.write.mode("overwrite").save_as_table(temp_table)

        # Merge chunk data into the CONFLUENCE_DATA_CHUNKS table
        merge_sql = f"""
        MERGE INTO {embed_table} AS target
        USING {temp_table} AS source
        ON target."DOC_ID" = source."DOC_ID" AND target."CHUNK_NUMBER" = source."CHUNK_NUMBER"
        WHEN MATCHED THEN
            UPDATE SET
                target."DOC_TITLE" = source."DOC_TITLE",
                target."CHUNK_CONTENT" = source."CHUNK_CONTENT",
                target."SOURCE" = source."SOURCE",
                target."PUBLISHED" = source."PUBLISHED"
        WHEN NOT MATCHED THEN
            INSERT ("DOC_ID", "DOC_TITLE", "CHUNK_NUMBER", "CHUNK_CONTENT", "SOURCE", "PUBLISHED")
            VALUES (source."DOC_ID", source."DOC_TITLE", source."CHUNK_NUMBER", source."CHUNK_CONTENT", source."SOURCE", source."PUBLISHED")
        """
        session.sql(merge_sql).collect()

        # Drop the temporary table
        drop_temp_table_sql = f"DROP TABLE IF EXISTS {temp_table}"
        session.sql(drop_temp_table_sql).collect()

        # Update embeddings for chunks without embeddings
        update_embedding_sql = f"""
        UPDATE {embed_table}
        SET "EMBEDDING" = SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', "CHUNK_CONTENT")
        WHERE "EMBEDDING" IS NULL
        """
        session.sql(update_embedding_sql).collect()

        return "Document chunks and embeddings have been saved to Snowflake"

    except KeyError as e:
        st.error(f"KeyError: {str(e)}. Please check your secrets.toml configuration.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    chunk_and_store()