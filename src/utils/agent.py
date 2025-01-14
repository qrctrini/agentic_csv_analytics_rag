from pydantic import BaseModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from typing_extensions import TypedDict

class Agent(BaseModel):
    name:str
    system_prompt:SystemMessage
    prompt:HumanMessage
