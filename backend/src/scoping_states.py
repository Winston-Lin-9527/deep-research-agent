import operator
from typing_extensions import Annotated, Optional, Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph import MessagesState, add_messages
from pydantic import BaseModel, Field

# states
class AgentState(MessagesState):
    """
    main state for the system
    """
    # < messages > - contained in parent class
    
    # Research brief generated from user conversation history
    research_brief: Optional[str]
    # Messages exchanged with the supervisor agent for coordination
    supervisor_messages: Annotated[Sequence[BaseMessage], add_messages]
    # Raw unprocessed research notes collected during the research phase
    raw_notes: Annotated[list[str], operator.add] = []
    # Processed and structured notes ready for report generation
    notes: Annotated[list[str], operator.add] = []
    # Final formatted research report
    final_report: str
    


# schemas
class AgentInputSchema(MessagesState):
    """ input schema for the first invoke, contains only the messages from user input """
    pass

class ClarifyWithUserSchema(BaseModel):
    """ schema for decision making and questions for prompting agent """
    
    need_further_clarification: bool = Field(
        description = "Whether the user needs to be asked a further question",
    )
    question: str = Field(
        description="A question to ask the user to clarify the report scope",
    )
    verification: str = Field(
        description="Verify message that we will start research after the user has provided the necessary information.",
    )
    
class ResearchQuestionSchema(BaseModel):
    """Schema for structured research brief generation. from prompting agent to researching agent """
    
    research_brief: str = Field(
        description="A research question that will be used to guide the research.",
    )
    