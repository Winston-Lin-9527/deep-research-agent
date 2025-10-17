import getpass
import os
from typing import TypedDict, Annotated, Sequence
from dotenv import load_dotenv 

from langchain_core.messages import AIMessage, HumanMessage, BaseMessage, trim_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, END, MessagesState, StateGraph
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition

from src.pdf_vector_store_manager import pdf_vector_store_mgr

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

prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "you are a helpful AI assistant, your name is gemini \
            If the user's query asks about uploaded documents, call the retrieve_tool. \
            Otherwise, respond directly as a general assistant."
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# tools
@tool
def retrieve_tool(query: str):
    """ retrieve information from uploaded documents """
    # just a wrapper
    return pdf_vector_store_mgr.similarity_search(query=query)


local_tools = [retrieve_tool]
tools_set = local_tools # + mcp_tools
llm_with_tools = llm.bind_tools(tools_set)

# --- Minimal LangGraph workflow exposed as `simple_chat` ---



# node 1 
def call_model(state: MessagesState):
    """Call the LLM with the running message history and append the AI reply."""
    # You can optionally insert a system message or prompt template here.
    prompt = prompt_template.invoke({"messages": state["messages"]})
    response = llm_with_tools.invoke(prompt)
    
    return {
        "messages": [AIMessage(
            content=response.content,
            additional_kwargs={"metadata": {"type": "simple_reply"}}
        )],  # append the AI response to the message history
    }

# node 2
tool_node = ToolNode(tools=tools_set)

# node 3
def generate(state: MessagesState):
    # collect all the retrieved context
    recent_tool_msgs = []
    for msg in reversed(state['messages']):
        if msg.type == 'tool':
            recent_tool_msgs.append(msg)
        else:
            break
    tool_msgs = recent_tool_msgs[::-1] # reverse
    
    context_combined = "\n\n".join(doc.content for doc in tool_msgs)
    system_message_content = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        f"{context_combined}"
    )
    
    # non tool calls
    conversation_msgs = [
        msg
        for msg in state["messages"]
        if msg.type in ('system', 'human')
        or msg.type == 'ai' and not msg.tool_calls
    ]
    past_convo = [SystemMessage(system_message_content)] + conversation_msgs
    
    response = llm.invoke(past_convo)
    return {"messages" : [response]}



workflow = StateGraph(state_schema=MessagesState)
workflow.add_node("call_model", call_model)
workflow.add_node("tools", tool_node)
workflow.add_node("generate", generate)

workflow.add_edge(START, "call_model")
workflow.add_conditional_edges(
    "call_model",
    tools_condition,
    {END: END, "tools": "tools"}
)
workflow.add_edge("tools", "generate") # todo: make it able to loop back to call_model, would need to add grade() and rewrite_query()
workflow.add_edge("generate", END)

# Enable memory so the server can preserve state per thread_id
# memory = MemorySaver()
simple_chat = workflow.compile()
