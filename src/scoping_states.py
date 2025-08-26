from typing import Optional
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field

# states
class AgentState(MessagesState):
    """
    main state for the system
    """
    # < messages > - contained in parent class
    
    # Research brief - generated from the prompting
    research_brief: Optional[str]
    
    # todo more
    


# schemas
class AgentInputSchema(MessagesState):
    """ input schema for the first invoke """
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
    