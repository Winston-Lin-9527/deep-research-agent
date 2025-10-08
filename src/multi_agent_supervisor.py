import asyncio
from langgraph.graph import END, START, StateGraph
from typing_extensions import Literal
from langchain.chat_models import init_chat_model
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage, filter_messages
from langgraph.graph.state import Command

from src.multi_agent_supervisor_state import (
    SupervisorState, 
    ConductResearch, 
    ResearchComplete
)
from src.research_agent import research_agent
from src.utils import get_today_str, think_tool
from src.prompts import lead_researcher_prompt

def get_notes_from_tool_calls(messages: list[BaseMessage]) -> list[str]:
    return [tool_msg.content for tool_msg in filter_messages(messages, include_types=["tool"])]



supervisor_tools = [ConductResearch, ResearchComplete, think_tool]
supervisor_model = init_chat_model("gemini-2.5-flash-lite", model_provider="google_genai")
supervisor_model_with_tools = supervisor_model.bind_tools(supervisor_tools)

# max # of tool calls for each research agent 
max_researcher_iterations = 6

# max concurrency
max_concurrent_researhcers = 3


# ========== nodes ==========

async def llm_call(state: SupervisorState) -> Command[Literal["supervisor_tools"]]:
    # look at current research brief research brief and supervisor messages to determine next step
    
    system_message = lead_researcher_prompt.format(
        date=get_today_str(),
        max_researcher_iterations=max_researcher_iterations,
        max_concurrent_researhcers=max_concurrent_researhcers
    )
    
    supervisor_messages = state.get("supervisor_messages", [])
    
    msgs = [SystemMessage(content=system_message)] + supervisor_messages
    
    response = await supervisor_model.ainvoke(msgs)
    
    return Command(
        goto="supervisor_tools",
        update={
            "supervisor_messages": [response],
            "research_iterations": state.get("research_iterations", 0)+1
        }
    )
    
async def supervisor_tools(state: SupervisorState) -> Command[Literal["llm_call", "__end__"]]:
    # handles:
    # 1. think_tool calls before and after other tool calls
    # 2. spawn sub research agents
    # 3. Aggregate research results
    
    supervisor_messages = state.get("supervisor_messages", [])
    research_iterations = state.get("research_iterations", 0)
    most_recent_message = supervisor_messages[-1]
    
    tool_messages = []
    all_raw_notes = []
    next_step = "supervisor"
    should_end = False
    
    exceeded_max_iterations = (research_iterations >= max_researcher_iterations)
    no_tool_calls = (not most_recent_message.tool_calls)
    research_completed = any(
        tool_call['name'] == "ResearchComplete"
        for tool_call in most_recent_message.tool_calls
    )
    
    if exceeded_max_iterations or no_tool_calls or research_completed:
        should_end = True
        next_step = END
        
    else:
        # Execute ALL tool calls before deciding next step
        try:
            # Separate think_tool calls from ConductResearch calls
            think_tool_calls = [
                tool_call for tool_call in most_recent_message.tool_calls 
                if tool_call["name"] == "think_tool"
            ]
            
            conduct_research_calls = [
                tool_call for tool_call in most_recent_message.tool_calls 
                if tool_call["name"] == "ConductResearch"
            ]

            # Handle think_tool calls (synchronous)
            for tool_call in think_tool_calls:
                observation = think_tool.invoke(tool_call["args"])
                tool_messages.append(
                    ToolMessage(
                        content=observation,
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"]
                    )
                )

            # Handle ConductResearch calls (asynchronous)
            if conduct_research_calls:
                # Launch parallel research agents
                coros = [
                    research_agent.ainvoke({
                        "researcher_messages": [
                            HumanMessage(content=tool_call["args"]["research_topic"])
                        ],
                        "research_topic": tool_call["args"]["research_topic"]
                    }) 
                    for tool_call in conduct_research_calls
                ]

                # Wait for all research to complete
                tool_results = await asyncio.gather(*coros)

                # Format research results as tool messages
                # Each sub-agent returns compressed research findings in result["compressed_research"]
                # We write this compressed research as the content of a ToolMessage, which allows
                # the supervisor to later retrieve these findings via get_notes_from_tool_calls()
                research_tool_messages = [
                    ToolMessage(
                        content=result.get("compressed_research", "Error synthesizing research report"),
                        name=tool_call["name"],
                        tool_call_id=tool_call["id"]
                    ) for result, tool_call in zip(tool_results, conduct_research_calls)
                ]
                
                tool_messages.extend(research_tool_messages)

                # Aggregate raw notes from all research
                all_raw_notes = [
                    "\n".join(result.get("raw_notes", [])) 
                    for result in tool_results
                ]
                
        except Exception as e:
            print(f"Error in supervisor tools: {e}")
            should_end = True
            next_step = END
    
    # Single return point with appropriate state updates
    if should_end:
        return Command(
            goto=next_step,
            update={
                "notes": get_notes_from_tool_calls(supervisor_messages),
                "research_brief": state.get("research_brief", "")
            }
        )
    else:
        return Command(
            goto=next_step,
            update={
                "supervisor_messages": tool_messages,
                "raw_notes": all_raw_notes
            }
        )
        
    
   # ======= graph construction =======
   
supervisor_builder = StateGraph(SupervisorState)
supervisor_builder.add_node(llm_call, "llm_call")    
supervisor_builder.add_node(supervisor_tools, "supervisor_tools") 
supervisor_builder.add_edge(START, llm_call)
supervisor_agent = supervisor_builder.compile()

    