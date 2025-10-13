import os
import getpass
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage, filter_messages
from pydantic import BaseModel, Field
from typing import Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from src.prompts import research_agent_prompt, compress_research_system_prompt, compress_research_human_message
from src.research_states import ResearcherAgentState
from src.utils import tavily_search_tool, think_tool, get_today_str



# ===== CONFIGURATION =====
tools = [tavily_search_tool, think_tool]
tools_by_name = {tool.name: tool for tool in tools}

# Initialize model
load_dotenv()
if not os.environ.get("GOOGLE_API_KEY"):
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter API key for Google Gemini: ")
model = init_chat_model("gemini-2.5-flash-lite", model_provider="google_genai")
model_with_tools = model.bind_tools(tools)
summarize_model = init_chat_model("gemini-2.5-flash-lite", model_provider="google_genai")
compress_model = init_chat_model("gemini-2.5-flash-lite", model_provider="google_genai")


# ===== workflow nodes =====

def llm_call(state: ResearcherAgentState):
    
    # Ensure the model receives at least one HumanMessage; Gemini rejects empty contents
    prior_messages = state.get("researcher_messages", [])
    if not prior_messages:
        # Seed with the research topic if available
        research_topic = state.get("research_topic", "")
        if research_topic:
            prior_messages = [HumanMessage(content=research_topic)]
        else:
            # Fallback to a generic instruction to avoid empty contents
            prior_messages = [HumanMessage(content="Conduct initial scoping for the research topic.")]

    system_instruction = SystemMessage(content=research_agent_prompt.format(date=get_today_str()))

    return {
        "researcher_messages": [
            model_with_tools.invoke(
                [system_instruction] + prior_messages
            )
        ]
    }

def tool_node(state: ResearcherAgentState):
    tool_calls = state['researcher_messages'][-1].tool_calls

    observations = []
    for tool_call in tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call['args'])
        observations.append(observation)
    
    tool_outputs = [
        ToolMessage(
            content=observation,
            name=tool_call["name"],
            tool_call_id=tool_call["id"],
        ) for observation, tool_call in zip(observations, tool_calls)
    ]

    # add to state messages
    return {"researcher_messages": tool_outputs}

def compress_research(state: ResearcherAgentState):
    """ Takes all AI and tool outputs and compresses them into a summary suitable for the supervisor's decision making """
    system_message = compress_research_system_prompt.format(date=get_today_str())
    human_instruction = HumanMessage(content=compress_research_human_message.format(research_topic=state.get("research_topic", "No topic specified")))
    messages = [system_message] + state.get("researcher_messages", []) + human_instruction

    compressed_research = compress_model.invoke(messages)

    raw_notes = [
        str(m.content) for m in filter_messages(
            state["researcher_messages"],
            include_types=["tool", "ai"] # only tool and AI messages
        )
    ]

    return {
        "compressed_research": compressed_research,
        "raw_notes": ['\n'.join(raw_notes)]
    }


# ROUTING LOGIC
def should_continue(state: ResearcherAgentState) -> Literal["tool_node", "compress_research"]:

    last_message = state["researcher_messages"][-1]

    if last_message.tool_calls == []:
        return "compress_research"
    else:
        return "tool_node" # there are more tool calls to be made
    

# ====== GRAPH construction ======

agent_builder = StateGraph(ResearcherAgentState)
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node)
agent_builder.add_node("compress_research", compress_research)

agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    {
        "tool_node": "tool_node",
        "compress_research": "compress_research",
    }
)
agent_builder.add_edge("tool_node", "llm_call") # loop back to LLM after tool use
agent_builder.add_edge("compress_research", END)
research_agent = agent_builder.compile()



# from langchain_core.messages import HumanMessage

# # Example brief
# research_brief = """I want to identify and evaluate the coffee shops in San Francisco that are considered the best based specifically  
# on coffee quality. My research should focus on analyzing and comparing coffee shops within the San Francisco area, 
# using coffee quality as the primary criterion. I am open regarding methods of assessing coffee quality (e.g.,      
# expert reviews, customer ratings, specialty coffee certifications), and there are no constraints on ambiance,      
# location, wifi, or food options unless they directly impact perceived coffee quality. Please prioritize primary    
# sources such as the official websites of coffee shops, reputable third-party coffee review organizations (like     
# Coffee Review or Specialty Coffee Association), and prominent review aggregators like Google or Yelp where direct  
# customer feedback about coffee quality can be found. The study should result in a well-supported list or ranking of
# the top coffee shops in San Francisco, emphasizing their coffee quality according to the latest available data as  
# of July 2025."""

# result = research_agent.invoke({"researcher_messages": [HumanMessage(content=f"{research_brief}.")]})
# print(result['researcher_messages'])