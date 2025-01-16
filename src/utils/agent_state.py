from langchain_core.messages import BaseMessage, HumanMessage, RemoveMessage
from langgraph.graph import MessagesState, END
from typing import TypedDict, Annotated, List, Any
from typing_extensions import TypedDict,Sequence
import operator


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    dir_path:str = None
    documents:Any = None
    answer:Any = None
    query:str = None
    next: str 
    
