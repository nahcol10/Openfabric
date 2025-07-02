import os
from datetime import datetime
import json
from memory import SYSTEM_INSTRUCTION
from langchain_community.chat_message_histories.redis import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_ollama import ChatOllama
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


# Setup path to store logs
LOG_FILE = os.path.join(os.path.dirname(__file__), "..", "datastore", "short_term_log.jsonl")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# 1. Function to log short-term messages with timestamp
def log_short_term(session_id: str, role: str, content: str):
    entry = {
        "session_id": session_id,
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

# Create a prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_INSTRUCTION),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)

# Initialize the language model
llm = ChatOllama(
    model="llama3.2",
    base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
)

# Create the conversational chain
chain = prompt | llm


# Simple in-memory chat history fallback
class SimpleChatHistory(BaseChatMessageHistory):
    def __init__(self):
        self._messages = []
    
    @property
    def messages(self):
        return self._messages
    
    def add_message(self, message):
        self._messages.append(message)
    
    def clear(self):
        self._messages.clear()

# Function to get or create a RedisChatMessageHistory instance with TTL
def get_redis_history(session_id: str) -> BaseChatMessageHistory:
    try:
        # Set TTL to 30 minutes (1800 seconds)
        return RedisChatMessageHistory(session_id, url=REDIS_URL, ttl=1800)
    except Exception as e:
        print(f"Redis connection failed, using in-memory fallback: {e}")
        # Return a simple in-memory chat history as fallback
        return SimpleChatHistory()


# Create a runnable with message history
chain_with_history = RunnableWithMessageHistory(
    chain, get_redis_history, input_messages_key="input", history_messages_key="history"
)

# # Use the chain in a conversation
# response1 = chain_with_history.invoke(
#     {"input": "My name is ALice Smith. I live in New York. My favorite food is pizza."},
#     config={"configurable": {"session_id": "alice_123"}},
# )
# print("AI Response 1:", response1.content)

# response2 = chain_with_history.invoke(
#     {"input": "What's my name name?"}, config={"configurable": {"session_id": "alice_123"}}
# )
# print("AI Response 2:", response2.content)


# 7. Run example conversation
# if __name__ == "__main__":
#     session_id = "alice_123"

#     user_input1 = "My name is ALice Smith. I live in New York. My favorite food is pizza."
#     log_short_term(session_id, "user", user_input1)

#     response1 = chain_with_history.invoke(
#         {"input": user_input1},
#         config={"configurable": {"session_id": session_id}},
#     )
#     print("AI Response 1:", response1.content)
#     log_short_term(session_id, "ai", response1.content)

#     user_input2 = "What's my name name?"
#     log_short_term(session_id, "user", user_input2)

#     response2 = chain_with_history.invoke(
#         {"input": user_input2},
#         config={"configurable": {"session_id": session_id}},
#     )
#     print("AI Response 2:", response2.content)
#     log_short_term(session_id, "ai", response2.content)
