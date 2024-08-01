# import snowflake.connector # removed logic
import streamlit as st
def similar_context(session, question, doc_type):
    """
    Retrieves the most relevant context chunks from Snowflake based on the similarity to the given question.
    
    Args:
    session: Snowflake Snowpark session object.
    question: The input question for which context chunks are to be retrieved.
    doc_type: The type of document selected by the user.
    
    Returns:
    A concatenated string of the most similar context chunks.
    """
    # Determine the table name, column name, and limit based on the document type
    if doc_type == 'Confluence Data':
        table_name = st.secrets["adminPageSettings"]["snowflake"]["confluence_embed_dataset"]
        embedding_column = "EMBEDDING"
        limit = 3
    elif doc_type == 'SDG Handbook Data':
        table_name = st.secrets["adminPageSettings"]["snowflake"]["handbook_embed_dataset"]
        embedding_column = "EMBEDDING" #CHUNK_VEC
        limit = 3
    else:
        raise ValueError("Invalid document type selected.")
    
    # Escape single quotes in the question to prevent SQL injection issues
    escaped_question = question.replace("'", "''")
    
    # SQL query to fetch and concatenate the top context chunks based on similarity
    context_query = f"""
    -- Get content chunk by using vector distance function
    with CONTEXT as (
        select 
            CHUNK_CONTENT,
            {embedding_column}, -- Use the appropriate column for the embedding
            VECTOR_COSINE_SIMILARITY({embedding_column}, SNOWFLAKE.CORTEX.EMBED_TEXT_768('e5-base-v2', '{escaped_question}')) as SIMILARITY
        from 
            {table_name}
        order by 
            SIMILARITY desc
        limit {limit}
    ),
    -- Concatenate the top context chunks into one string
    CONCATENATED_CONTEXT as (
        select 
            LISTAGG(CHUNK_CONTENT, ' ') WITHIN GROUP (ORDER BY SIMILARITY desc) as FULL_CONTEXT
        from 
            CONTEXT
    )
    select 
        CONCATENATED_CONTEXT.FULL_CONTEXT
    from 
        CONCATENATED_CONTEXT;
    """

    result = session.sql(context_query).collect()
    full_context = result[0]['FULL_CONTEXT']
    
    return full_context