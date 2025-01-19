from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, RemoveMessage, BaseMessage
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
from langchain.schema import messages_to_dict, message_to_dict

# agents
from src.agents.document_processor import DocumentProcessor
from src.agents.supervisor import Supervisor
from src.agents.vector_store import VectorStore
from src.agents.insurance_analysis import InsuranceAnalysisAgent

# helpers
from src.utils.utils import get_project_filepath, save_dict_to_json_file, load_config_params_for_node
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


def ragrunner(csv_folderpath:str=None,query:str=None) -> None: 
    """
    Run the entire thing using his function

    Args:
        csv_folderpath: location of csv files
        query: user query on data
    """
    #csv_folderpath = f'{get_project_filepath()}/data/csv'
    if csv_folderpath is not None:
        analysis_prepend = f"1) Process csv files from 'dir_path':'{csv_folderpath}'. 2) Goto vector_store: Send the processed documents to vector_store as ONLY ONE big JSON array with keys : 'content','metadata' 3) Go to vector_store to save documents first. Then Use the analysis node to answer this question"
    else:
        analysis_prepend = f"Use the analysis node to answer this question:"
    
    if query is None:
        query = f"Perform in-depth analysis on the data in the vector store collection"
    query = f"{analysis_prepend}: {query}"
    logger.info(f'{query=}')

    # initialize the graph
    graph = create_agent_graph()
    # Initialize the state
    initial_state = AgentState(
        messages=[HumanMessage(content=query)] if query else [],
        next="supervisor"
    )

    # Run the graph
    for output in graph.stream(initial_state,{"recursion_limit": 50}):
        if "__end__" not in output:
            logger.info(f"{type(output)}....Intermediate output: {output}")

    status_update = "Analysis complete!"
    logger.info(f'{status_update=}')

if __name__ == "__main__":
    ragrunner(
        csv_folderpath=f"{get_project_filepath()}/data/csv",
        query="What's the trend in auto insurance costs over the last 3 years?"
        )