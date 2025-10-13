import getpass
import os
from typing import TypedDict, Annotated, Sequence
from dotenv import load_dotenv 

from langchain_core.messages import AIMessage, HumanMessage, BaseMessage, trim_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, MessagesState, StateGraph
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv() # load from .env file

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)


# --- Minimal LangGraph workflow exposed as `simple_chat` ---

# Option A: Use built-in MessagesState for a simple chat loop

def call_model(state: MessagesState):
    """Call the LLM with the running message history and append the AI reply."""
    # You can optionally insert a system message or prompt template here.
    ai = llm.invoke(state["messages"])  # pass the accumulated messages directly
    return {"messages": [ai]}


workflow = StateGraph(state_schema=MessagesState)
workflow.add_node("model", call_model)
workflow.add_edge(START, "model")
workflow.add_edge("model", END)

# Enable memory so the server can preserve state per thread_id
# memory = MemorySaver()
simple_chat = workflow.compile()

