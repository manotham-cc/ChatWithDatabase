from dotenv import load_dotenv
import mysql.connector  # Use mysql.connector instead of langchain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
import streamlit as st
import json
def init_database(user: str, password: str, host: str, port: str, database: str):
    # Establish a connection to the MySQL database
    connection = mysql.connector.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    )
    return connection
def get_schema(db):
    cursor = db.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    schema_json = {}

    for table in tables:
        table_name = table[0]
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()

        schema_json[table_name] = []
        for column in columns:
            field, col_type, nullable, key, default, extra = column
            schema_json[table_name].append({
                "column": field,
                "type": col_type,
                "nullable": nullable,
                "key": key if key else None,
                "default": default,
                "extra": extra if extra else None
            })

    cursor.close()
    return json.dumps(schema_json, indent=2)
def get_sql_chain(db):
    template = """You are
     a soc analyst at a company. You are interacting with a user who is asking you questions about the company's database.
    Based on the table schema below, write a SQL query that would answer the user's question. Take the conversation history into account.
    <SCHEMA>{schema}</SCHEMA>
    Conversation History: {chat_history}
    Write only the SQL query and nothing else. Do not wrap the SQL query in any other text, not even backticks.
        Question: {question}
        SQL Query:
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    return (
        RunnablePassthrough.assign(schema=lambda _: get_schema(db))  # Assign schema dynamically
        | prompt  # Use the prompt template
        | llm  # Generate SQL using the language model
        | StrOutputParser()  # Parse the output as a string
    )
def fetch_database(user_query: str, db, chat_history: list):
    sql_chain = get_sql_chain(db)
    sql_query = sql_chain.invoke({"question": user_query, "chat_history": chat_history})
    # Execute the SQL query and fetch results
    cursor = db.cursor()
    cursor.execute(sql_query)
    response = cursor.fetchall()
    cursor.close()
    return response, sql_query
def get_response(user_query: str, db, chat_history: list):
    template = """
        You are a data analyst at a company. You are interacting with a user who is asking you questions about the company's database.
        Based on the table schema below, question, sql query, and sql response, write a natural language response.
        <SCHEMA>{schema}</SCHEMA>          
        Conversation History: {chat_history}
        SQL Query: <SQL>{query}</SQL>
        User question: {question}
        SQL Response: {response}
    """
        # Fetch results and SQL
    response_data, sql_query = fetch_database(user_query, db, chat_history)
    prompt = ChatPromptTemplate.from_template(template)
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
    chain = (
        RunnablePassthrough.assign(query = lambda _ :sql_query, schema=lambda _: get_schema(db), response=lambda _ :response_data)  # Fetch schema dynamically
        | prompt  # Use the prompt template
        | llm  # Generate the response using the language model
        | StrOutputParser()  # Parse the output as a string
    )
    return chain.invoke({"question": user_query, "chat_history": chat_history})
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello! I'm a SQL assistant. Ask me anything about your database.")
    ]
st.set_page_config(page_title="Chatbot", page_icon=":guardsman:", layout="wide")
st.title("Chatbot")
st.write("Ask me anything about the database!")
with st.sidebar:
    st.header("Settings")
    st.write("Welcome to the SQL chat assistant! Connect to your MySQL database and start asking questions.")
    st.text_input("Username", key = "username",value = "root")
    st.text_input("Password",type = "password", key = "password",value = "CSS222")
    st.text_input("Host",key = "host",value = "localhost")
    st.text_input("Port", key = "port",value = "3306")
    st.text_input("Database", key ="database",value ="splunk_mock_data")

    if st.button("Connect"):
        with  st.spinner("Conecting to database..."):
        # Initialize the database connection
            db = init_database(  
            st.session_state["username"], 
            st.session_state["password"],
            st.session_state["host"], 
            st.session_state["port"], 
            st.session_state["database"]
            )
            st.session_state.db = db 
            st.success("Connected to the database!")
for message in st.session_state.chat_history:
    if isinstance(message,AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message,HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)

user_query = st.chat_input("Type a message...")
if user_query is not None and user_query.strip() != "":
    # Add user query to chat history
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    
    # Display user query in the chat
    with st.chat_message("Human"):
        st.markdown(user_query)
        
    # Generate and display AI response
    with st.chat_message("AI"):
        response = get_response(user_query, st.session_state.db, st.session_state.chat_history)
        st.markdown(response)
        
    # Add AI response to chat history
    st.session_state.chat_history.append(AIMessage(content=response))    
log = []          
print("Chat history:")
for message in st.session_state.chat_history:
    if isinstance(message, HumanMessage):
        log.append(f"Human: {message.content}")
    elif isinstance(message, AIMessage):
        log.append(f"AI: {message.content}")
print("\n".join(log))        
# db = init_database("root", "CSS222", "localhost", "3306", "splunk_mock_data")
# # Example usage:
# user_query = "Show me the column in database and show what you query"
# chat_history = []  # This would be your conversation history
# print(get_response(user_query, db, chat_history))
