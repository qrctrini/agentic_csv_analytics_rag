from typing import Literal, TypedDict
from langchain_anthropic import ChatAnthropic
from langgraph.graph import MessagesState
from langgraph.types import Command
from utils.agent import Agent

# Define the members of the team
members = []

# Define the supervisor's system prompt
system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    f" following workers: {members}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH."
)
