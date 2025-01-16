from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, RemoveMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langgraph.graph import MessagesState, END
from langgraph.types import Command
from typing import Literal,Any
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_core.tools import tool
from langchain.tools import Tool
from loguru import logger
import json
import ast
from langchain_core.messages.base import message_to_dict, messages_to_dict
from langchain.output_parsers import PydanticOutputParser, JsonOutputToolsParser
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain.prompts import PromptTemplate
from langgraph.prebuilt import create_react_agent

# agents
from src.agents.document_processor import DocumentProcessor
from src.agents.supervisor import Supervisor
from src.agents.vector_store import VectorStore
from src.agents.insurance_analysis import InsuranceAnalysisAgent

# helpers
from src.utils.utils import get_project_filepath
from src.agents.supervisor import supervisor_node, Supervisor
from src.utils.agent_state import AgentState
from src.utils.prompt import Prompt
from src.utils.create_nodes import CreateNode

    
# ------------- create nodes ---------------------------
supervisor = Supervisor()
document_processor_node = CreateNode(
    name="document_processor",
    description="load and split documents",
    llm=supervisor.llm,
    tool_function=DocumentProcessor,
    prompt=Prompt
)

vector_store_node = CreateNode(
    name="vector_store",
    description="store documents in postgres database",
    llm=supervisor.llm,
    tool_function=VectorStore,
    prompt=Prompt
)

analysis_node = CreateNode(
    name="analysis",
    description="Analyze documents in postgres database",
    llm=supervisor.llm,
    tool_function=InsuranceAnalysisAgent,
    prompt=Prompt
)

def create_agent_graph():
    """
    Create graphs from nodes

    returns:
        - Graph
    """
    builder = StateGraph(AgentState)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("document_processor", document_processor_node.node)
    builder.add_node("vector_store", vector_store_node.node)
    builder.add_node("analysis", analysis_node.node)

    builder.add_edge(START, "supervisor")

    graph = builder.compile()
    return graph


if __name__ == '__main__':
    graph = create_agent_graph()
    
    query = f"""Process csv files from 'dir_path':'{get_project_filepath()}/data/csv'"""
     # Initialize the state
    initial_state = AgentState(
        messages=[HumanMessage(content=query)] if query else [],
        next="supervisor"
    )

    # Run the graph
    for output in graph.stream(initial_state,{"recursion_limit": 50}):
        if "__end__" not in output:
            logger.info(f"Intermediate output: {output}")

    logger.info("Analysis complete!")