from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import MessagesState, END
from typing import TypedDict, Annotated


class AgentState(TypedDict):
    
    next:str 
