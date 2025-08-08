from examples import get_example_selector
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder,FewShotChatMessagePromptTemplate,PromptTemplate
from dotenv import load_dotenv
import os
from langchain_community.utilities import SQLDatabase
from langchain.chains.sql_database.prompt import SQL_PROMPTS, PROMPT

from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)

load_dotenv()

dbase = SQLDatabase.from_uri(os.getenv("POSTGRES_URI"))
default_prompt = SQL_PROMPTS.get(dbase.dialect, PROMPT)

extended_prompt = PromptTemplate(
    input_variables=default_prompt.input_variables,
    template=
    """
-- ADDITIONAL INSTRUCTIONS:

-- Postgres is case-sensitive when using quoted identifiers.
--The columns names in the schema are in lower case.
-- be sure to check the schema for the correct column names.
--Use the correct table names and column names as per the schema.
-- For product categories they are saved in the schema as 'Category-1','Category-2', etc DO NOT USE THE ALIKE OPERATOR HERE
-- INSTEAD convert any user inputs with category-1 as Category-1 (applicable to all product categories)

--If unsure of the column names like product category, region, or area manager, use the ILIKE operator to search for similar names.
-- Check the syntax of SQL statements and ensure they follow the rules of Postgres
-- • When you use GROUP BY, **every** column in your SELECT list that is _not_ wrapped in an aggregate
--   (e.g. SUM, COUNT) **must** also appear in the GROUP BY clause.
-- Make Sure to follow the conventions of GROUP BY CLAUSE

--Always end your SQL statements with a semicolon
--IF REQUIRED LIMIT YOUR SQL QUERIES TO 25 ONLY in addtion to the 5 mentioned in the system prompt

-- for area manager codes MAKE SURE the user input is converted to the example format spacing "AM - GOA" to use the ilike operator properly



-- HERE IS YOUR SCHEMA (table names + columns):
{{schema}}


"Below are a number of examples of questions and their corresponding SQL queries."

"""  # ← end of your extra text
 # ← the rest of the built‑in prompt
 + default_prompt.template 

)

system_instructions = SystemMessagePromptTemplate.from_template(
    extended_prompt.template
)

# Wrap the built‑in schema prompt too (if desired)
system_schema = SystemMessagePromptTemplate.from_template(
    default_prompt.template
)

example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}\nSQLQuery:"),
        ("ai", "{query}"),
    ]
)
few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    example_selector=get_example_selector(),
    input_variables=["input","top_k"],
)

final_prompt = ChatPromptTemplate.from_messages(
    [
        system_instructions,           # your ADDITIONAL INSTRUCTIONS block
        system_schema,
        few_shot_prompt,
        # MessagesPlaceholder(variable_name="messages"),
        HumanMessagePromptTemplate.from_template("{input}"),
    ]
)

answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result:

Question: {question}
SQL Query: {query}
SQL Result: {result}

Please do the following:
IF The SQL Result is blank: Return an error message stating "No Data Returned"

Else:

First, state the {result} exactly as mentioned in a markdown table

Then, ALSO , answer the original question in plain language (THIS IS MANDATORY), referencing the table you just showed.

If the result set is empty, reply simply with “No data returned.”

Answer: """

)
