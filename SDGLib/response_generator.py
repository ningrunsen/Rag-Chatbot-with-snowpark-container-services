# import snowflake.connector # Removed logic
from SDGLib.find_context_chunks import similar_context

def create_cortex_response(session, question, model_name, doc_type):
    """
    Generates a detailed response using Snowflake Cortex based on the provided context and question.
    
    Args:
    session: Snowflake Snowpark session object.
    question: The input question for which the response is to be generated.
    model_name: The name of the model to be used for generating the response.
    doc_type: The type of document selected by the user.
    
    Returns:
    A string containing the generated response.
    """
    # Fetch the most relevant context chunks for the given question
    full_context = similar_context(session, question, doc_type)
    
    # Escape single quotes in the question and context to prevent SQL injection issues
    escaped_question = question.replace("'", "''")
    escaped_full_context = full_context.replace("'", "''")
    
    # SQL query to generate a response using Snowflake Cortex with the provided context and question
    complete_query = f"""
    SELECT 
        snowflake.cortex.complete('{model_name}', 
                                  'Use the provided context to answer the question. Be detailed. ' ||
                                  '###\n                                   CONTEXT: ' ||
                                  '{escaped_full_context}' ||
                                  '###\n                                  QUESTION: ' || '{escaped_question}' ||
                                  'ANSWER: ') AS response
    """
    
    result = session.sql(complete_query).collect()
    response = result[0]['RESPONSE']
    
    return response