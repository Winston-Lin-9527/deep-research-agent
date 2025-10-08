


import operator
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langgraph.graph import add_messages
from pydantic import BaseModel, Field


class SupervisorState(TypedDict):
   supervisor_messages: Annotated[Sequence[BaseMessage], add_messages]
   
   # the overall research direction
   research_brief: str
   
   notes: Annotated[list[str], operator.add] = []
   raw_notes: Annotated[list[str], operator.add] = []
   
   research_iterations: int 
   
   
@tool
class ConductResearch(BaseModel):
    """Tool for delegating a research task to a specialized sub-agent."""
    research_topic: str = Field(
        description="The topic to research. Should be a single topic, and should be described in high detail (at least a paragraph).",
    ) 
    
@tool 
class ResearchComplete(BaseModel):
    """Tool for indicating that the research process is complete."""
    pass