''' 

1. User clarification + scoping
2. Multi-agent research 
3. final report 

'''

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import START, END, StateGraph

from src.multi_agent_supervisor import supervisor_agent
from src.prompts import final_report_generation_prompt
from src.scoping_agent import clarify_with_user, write_research_brief
from src.scoping_states import AgentState
from src.utils import get_today_str


from langchain.chat_models import init_chat_model
report_writing_model = init_chat_model("gemini-2.5-flash-lite", model_provider="google_genai")


# ===== REPORT GEN ======
async def final_report_generation(state: AgentState):
    notes = state.get("notes", [])
    findings = '\n'.join(notes)
    
    final_report_prompt = final_report_generation_prompt.format(
        research_brief=state.get("research_brief", ""),
        findings=findings,
        date=get_today_str()
    )
    
    final_report = await report_writing_model.ainvoke([HumanMessage(content=final_report_prompt)])
    
    return {
        "final_report": final_report.content,
        "messages": [AIMessage(content="here's the final report: " + final_report.content)]
    }

    
deep_research_builder = StateGraph(AgentState)
deep_research_builder.add_node("clarify_with_user", clarify_with_user)
deep_research_builder.add_node("write_research_brief", write_research_brief)
deep_research_builder.add_node("supervisor_subgraph", supervisor_agent)
deep_research_builder.add_node("final_report_generation", final_report_generation)

deep_research_builder.add_edge(START, "clarify_with_user")
# since clarify_with_user uses Command to navigate to next node
# deep_research_builder.add_edge("clarify_with_user", "write_research_brief")
deep_research_builder.add_edge("write_research_brief", "supervisor_subgraph")
deep_research_builder.add_edge("supervisor_subgraph", "final_report_generation")
deep_research_builder.add_edge("final_report_generation", END)

deep_research_agent = deep_research_builder.compile()