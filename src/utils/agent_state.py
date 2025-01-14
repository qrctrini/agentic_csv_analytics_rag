from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import MessagesState, END
from typing import TypedDict, Annotated, List, Any
from typing_extensions import TypedDict,Sequence
import operator


class State(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    dir_path:str = None
    documents:Any = []
    answer:Any = []
    query:str = None
    next: str 
    
    agent_history: Annotated[Sequence[BaseMessage], operator.add]
