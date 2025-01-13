from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import MessagesState, END
from typing import TypedDict, Annotated, List
from typing_extensions import TypedDict
from typing_extensions import TypedDict
import operator


class State(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

# class State(TypedDict):
#     document_processor: list
#     vector_store: dict
#     query: str
#     insurance_analysis:str
#     next: str