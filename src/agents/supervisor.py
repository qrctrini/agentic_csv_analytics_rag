from typing import Literal, Any
from typing_extensions import TypedDict
from langchain_anthropic import ChatAnthropic
from langgraph.graph import MessagesState, END
from langgraph.types import Command
from pydantic import BaseModel
import os
from dotenv import load_dotenv 
load_dotenv()

from src.utils.agent_state import State

# Our team supervisor is an LLM node. It just picks the next agent to process
# and decides when the work is completed

class Router(TypedDict):
    """Worker to route to next. If no workers needed, route to FINISH."""
    next: Literal["document_processor", "vector_store","analysis","FINISH"]


class Supervisor(BaseModel):
    members:list = ["document_processor", "vector_store","analysis"]
    system_prompt:list = (
        "You are a supervisor tasked with managing a conversation between the"
        f" following workers: {members}. Given the following user request,"
        " respond with the worker to act next. Each worker will perform a"
        " task and respond with their results and status. When finished,"
        " respond with FINISH. Submit the messages to each note as a string without splitting it up "
    )
    llm:Any = ChatAnthropic(api_key=os.getenv('ANTHROPIC_API_KEY'), model="claude-3-5-sonnet-latest")


def supervisor_node(state: MessagesState) -> Command:
    supervisor = Supervisor()
    messages = [
        {"role": "system", "content": supervisor.system_prompt,"documents":None},
    ] + state["messages"]
    response = supervisor.llm.with_structured_output(Router).invoke(messages)
    goto = response["next"]
    if goto == "FINISH":
        goto = END

    return Command(goto=goto)

