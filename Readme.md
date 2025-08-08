# LangChain NL2SQL Chatbot

This project is an interactive Streamlit application that translates natural language questions into SQL queries, executes them against a PostgreSQL database, and returns the results—all powered by LangChain, Groq LLMs, and LangSmith observability.

---

## 🔧 Tech Stack

* **Python 3.10+** – Core language for application logic
* **Streamlit** – Lightweight web UI framework for building the chat interface
* **LangChain Core & Community** – Orchestrates prompt templates, chains, and tooling
* **Groq LLM (ChatGroq)** – High-performance language model for SQL generation and answer synthesis
* **PostgreSQL** – Relational database storing the `sales_data` table
* **psycopg2** – Python adapter for PostgreSQL connectivity
* **Chroma** – Vector store for few‑shot example selection
* **HuggingFace Embeddings** – Semantic embeddings for example similarity
* **LangSmith** – Observability and tracing for chains, prompts, and tool calls
* **python-dotenv** – Loads environment variables from a `.env` file

---

## ⚙️ How It Works

When a user submits a query, the application performs the following steps:

1. **Receive User Input** – The Streamlit frontend captures the natural language question.
2. **Build/Retrieve Chain** – The `invoke_chain()` helper initializes (or retrieves) a cached LangChain `Runnable` chain that combines prompt templates, LLM calls, and tooling.
3. **System Prompt & Few‑Shot** – A system-level prompt (`extended_prompt`) injects database schema details and additional instructions to the LLM. Few‑shot examples (some examples that are provided to the LLM) are selected via a `SemanticSimilarityExampleSelector` over Chroma + Embeddings.
4. **Generate SQL** – ChatGroq generates a syntactically valid SQL statement tailored to PostgreSQL, prefaced with `SQLQuery:`.
5. **Extract SQL** – A small parser isolates the `SQLQuery` from the LLM’s response.
6. **Execute Query** – `QuerySQLDatabaseTool` runs the extracted SQL against the Postgres database and returns raw results.
7. **Format Response** – A final prompt template (`answer_prompt`) wraps the SQL result into a concise, human‑readable answer, always presenting the numeric result first.
8. **Render in UI** – The formatted answer is displayed back in the Streamlit chat interface for the user.
9. **Error Handling** – If the generated SQL query is invalid or fails to execute, no result is returned and the Streamlit UI will display that there was an error in execution.
10. **Security**: For additional security, LLM is only given read access with the ability to only send 25 rows (max) to a user - this limits the susceptibility of the LLM modifying the database, which is crucial to any enterprise

---

## 📊 Observability with LangSmith

All chain steps, prompt executions, and tool calls are traced via LangSmith. Use the LangSmith UI to inspect individual prompt inputs/outputs and database queries in real time.

---

## 🛠️ Deployment

Deploy the Streamlit app on any platform that supports Docker or Python applications (e.g., Streamlit Cloud, Heroku, AWS Elastic Beanstalk). Ensure environment variables (`.env`) and the Postgres connection string are configured.

---

## 🔗 Useful Links

* [LangChain Documentation](https://python.langchain.com/)
* [Groq Chat Models](https://github.com/groq-ai)
* [LangSmith Docs](https://developers.openai.com/langsmith)
* [Streamlit Guides](https://docs.streamlit.io/)
