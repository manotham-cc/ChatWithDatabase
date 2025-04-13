# ChatWithDatabase
AI-powered SQL assistant built with Streamlit, LangChain, and Groq. Connect to a MySQL database, ask natural language questions, and get SQL queries and results instantly—no SQL expertise required.
# ChatWithDatabase

**AI-powered SQL assistant** built with [Streamlit](https://streamlit.io/), [LangChain](https://www.langchain.com/), and [Groq](https://groq.com/).

Connect to your MySQL database and interact with it using natural language. No SQL expertise required—just ask your question and get the SQL query and results instantly!

---

## 🚀 Features

- 🔌 **Connect to MySQL**: Securely link to your MySQL database.
- 🧠 **AI-Powered Queries**: Ask questions in plain English, get accurate SQL queries.
- 📊 **Instant Results**: See both the generated SQL and the query results side by side.
- 🛠️ **Built with Modern Tools**: Utilizes Streamlit for UI, LangChain for prompt orchestration, and Groq for ultra-fast LLM inference.

---

## 📦 Tech Stack

- **Frontend**: Streamlit
- **LLM Orchestration**: LangChain
- **Inference Backend**: Groq (LLM provider)
- **Database**: MySQL

---

## 🖥️ Getting Started

### Prerequisites

- Python 3.10+
- MySQL database
- API keys for Groq and other services (if required)

### Installation

1. **Clone the repo**

```bash
git clone https://github.com/manotham-cc/ChatWithDatabase.git
cd ChatWithDatabase
```


```bash
pip install -r requirements.txt

```
Set environment variables

Create a .env file in the root directory and add:
GROQ_API_KEY=your_groq_api_key
form https://console.groq.com
```bash
streamlit run app.py
```
