import os
from dotenv import load_dotenv
import psycopg2
from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langsmith import traceable
from langchain_core.prompts import PromptTemplate
from langchain.chains import create_sql_query_chain
from langchain_community.chat_message_histories.in_memory import ChatMessageHistory
# importing tools to execute the query
from langchain_community.tools.sql_database.tool import (
    QuerySQLDatabaseTool
)
#chain generation of sql query and execution togeher
from operator import itemgetter
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
# Create a prompt template for the SQL query generation
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from prompts import final_prompt, answer_prompt
load_dotenv()

db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")

dbase = SQLDatabase.from_uri(os.getenv("POSTGRES_URI"))

# # List all tables
# print("📦 Tables in DB:", dbase.get_usable_table_names())

# # Get full schema for all tables
# print("🧠 Full schema:")
# print(dbase.get_table_info())

from langchain.chains.sql_database.prompt import SQL_PROMPTS, PROMPT

default_prompt = SQL_PROMPTS.get(dbase.dialect, PROMPT)

extended_prompt = PromptTemplate(
    input_variables=default_prompt.input_variables,
    template=
   
    """
--  INSTRUCTIONS [IMPORTANT]:
-- 1)Postgres is case‑sensitive for quoted identifiers; USE ILIKE OPERATOR for REGIONS and for CATEGORIES use ILIKE without '%' sign
--    [IMPORTANT] you should use ILIKE to match user inputs to columns for Regions and Segments.
---- For product categories they are saved in the schema as 'Category-1','Category-2', etc USE ILIKE WITHOUT '%' sign

-- 2) ALWAYS include the raw SQL result in your final answer.


-- 3) If it’s a single‐value query (SUM, COUNT…), answer in the form:
--      <value>
--    or as a sentence, e.g. “West region has 12345 total volume sales.”


-- 5) Postgres is case‑sensitive for quoted identifiers; column names are all Capitalized.


-- 6) End every SQL statement with a semicolon.


-- 7) LIMIT any listing queries to at most 25 rows.


-- 8) Always check GROUP BY rules: every non‑aggregated column in SELECT must appear in GROUP BY.


-- 9) make sure the values are in line with the schema and the sample rows you received


-- HERE IS YOUR SCHEMA (table names + columns):
{{schema}}


"""  # ← end of your extra text
+
default_prompt.template  # ← the rest of the built‑in prompt

)

import re
from langchain_core.runnables import RunnableLambda

def extract_sql_from_response(raw_response: str) -> str:
    """
    Extracts the SQL query from a LangChain-generated multi-line response.

    Args:
        raw_response (str): The raw response string from LLM (e.g., includes 'SQLQuery:')

    Returns:
        str | None: The extracted SQL query, or None if not found.
    """
    # 1) try to pull out after the “SQLQuery:” label
    m = re.search(r'SQLQuery:\s*(.*)', raw_response, re.DOTALL)
    if m:
        return m.group(1).strip()

    # 2) try to pull code fences, e.g. ```sql ... ```
    m2 = re.search(r'```(?:sql)?\s*(.*?)\s*```', raw_response, re.DOTALL | re.IGNORECASE)
    if m2:
        return m2.group(1).strip()

    # 3) otherwise assume the entire response _is_ the SQL
    return raw_response.strip()

sql_cleaner = RunnableLambda(lambda x: extract_sql_from_response(x))



def get_chain():
    print("Creating chain")
    db = SQLDatabase.from_uri(os.getenv("POSTGRES_URI"))    
    llm = ChatGroq(model_name="llama3-8b-8192", temperature=0.0)
    generate_query_chain=create_sql_query_chain(llm,dbase,final_prompt)
    execute_query = QuerySQLDatabaseTool(db=dbase)
    rephrase_answer = answer_prompt | llm | StrOutputParser()
    chain = (
    RunnablePassthrough()
    .assign(
        question=itemgetter("question")
    )
   .assign(
        query=lambda x: sql_cleaner.invoke(
            generate_query_chain.invoke({"question": x["question"], "table_info": dbase.get_table_info()})
        )
    )
    .assign(
        result=lambda x: execute_query.invoke({"query": x["query"]})
    )
    | rephrase_answer)


    return chain


# def create_history(messages):
#     history = ChatMessageHistory()
#     for message in messages:
#         if message["role"] == "user":
#             history.add_user_message(message["content"])
#         else:
#             history.add_ai_message(message["content"])
#     return history

def invoke_chain(question):
    chain = get_chain()
    # history = create_history(messages)
    response = chain.invoke({"question": question})
    # history.add_user_message(question)
    # history.add_ai_message(response)
    return response