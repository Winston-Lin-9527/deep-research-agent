"""
State definitions and structured schemas for the researcher agent workflow.

"""

import operator
from typing_extensions import TypedDict, List, Sequence, Annotated
from pydantic import BaseModel, Field

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class ResearcherAgentState(TypedDict):
    """State container for the researcher agent graph.

    Keys:
        research_topic: String describing the topic or question to research.
        tool_call_iterations: Counter for how many tool-use loops have run.
        researcher_messages: Ordered conversation history for the researcher
            node.
        raw_notes: Accumulated free-form notes captured during research.
    """
    research_topic: str
    tool_call_iterations: int
    researcher_messages: Annotated[Sequence[BaseMessage], add_messages]
    raw_notes: Annotated[List[str], operator.add] # just the tool and AI messages, no Human messages
    

class ResearcherOutputState(TypedDict): # or should be called a schema?
    compressed_research: str    # final finding
    raw_notes: Annotated[List[str], operator.add]
    researcher_messages: Annotated[Sequence[BaseMessage], add_messages]
    
    
# ------- schemas -------

# class ClarifyWithUser(BaseModel):
#     """Schema for user clarification decisions during scoping phase."""
#     need_clarification: bool = Field(
#         description="Whether the user needs to be asked a clarifying question.",
#     )
#     question: str = Field(
#         description="A question to ask the user to clarify the report scope",
#     )
#     verification: str = Field(
#         description="Verify message that we will start research after the user has provided the necessary information.",
#     )

# class ResearchQuestion(BaseModel):
#     """Schema for research brief generation."""
#     research_brief: str = Field(
#         description="A research question that will be used to guide the research.",
#     )

class SummarySchema(BaseModel):
    """Schema for webpage content summarization."""
    summary: str = Field(description="Concise summary of the webpage content")
    key_excerpts: str = Field(description="Important quotes and excerpts from the content")
