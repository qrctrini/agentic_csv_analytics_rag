from pydantic import BaseModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

class Agent(BaseModel):
    name:str
    system_prompt:SystemMessage
    prompt:HumanMessage
