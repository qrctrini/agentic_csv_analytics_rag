from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langgraph.graph import MessagesState, END
from langgraph.types import Command
from typing import Literal,Any
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langchain.tools import Tool
from loguru import logger
import json


# agents
from src.agents.document_processor import DocumentProcessor
from src.agents.supervisor import Supervisor
from src.agents.vector_store import VectorStore

# helpers
from src.utils.utils import get_project_filepath
from src.agents.supervisor import supervisor_node, Supervisor
from src.utils.agent_state import State
import ast
supervisor = Supervisor()

# ----------------------   create document processor node -----------------------
# create tools
dp = DocumentProcessor()
tools = [
    Tool(
        name="process_documents_tool",
        func=dp.run,
        description="Load and process documents"
    )
]
# create agent
document_processor_agent = create_react_agent(supervisor.llm, tools=tools)
# create node
def document_processor_node(state: MessagesState) -> Command[Literal["supervisor"]]:    
    response= document_processor_agent.invoke(state)
    #documents = response['messages'][-2].content
    return Command(
        update={
            "messages":[

                HumanMessage(content=[response["messages"][-2].content],name='document_processor')
            ]
        },
        goto='supervisor',
        
    )

# ----------------------   create vector store node -----------------------
# create tool
vs = VectorStore()
tools = [
    Tool(
        name="vector_store_tool",
        func=vs.run,
        description="Store data from document_processor in vector database"
    )
]
# create agent
vector_store_agent = create_react_agent(supervisor.llm, tools=tools)
#create node
def vector_store_node(state: MessagesState) -> Command[Literal["supervisor"]]:
    #read the last message in the message history.
    logger.warning(f'state={state}')
    result = vector_store_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=HumanMessage(content=""" When all files are loaded in to the vector store,
                    then perform indepth analysis on the data in the vector store.
                    Provide information about trends, outliers, aggregations and 
                    any thing else useful.""")
                , name="vector_store")
            ]
        },
        goto="supervisor",
    )

class CreateNode:
    def __init__(self,name:str,llm:Any):
        self.name = name
        self.llm = llm

    def node(self,state:MessagesState) -> Command[Literal["supervisor"]]:
        """
        Create Node

        Return:
            node(Command): 
        """
        agent = create_react_agent(supervisor.llm, tools=tools)
        logger.warning(f'state={state}')
        result = agent.invoke(state)
        return Command(
            update={
                "messages": [
                    HumanMessage(content=result, name=self.name),
                
                ]
            },
            goto="supervisor",
        )
    
analysis = CreateNode(name='analysis',llm=supervisor.llm)



if __name__ == '__main__':
    builder = StateGraph(MessagesState)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("document_processor", document_processor_node)
    builder.add_node("vector_store", vector_store_node)
    builder.add_node("analysis",analysis.node)
    
    builder.add_edge(START, "supervisor")
    graph = builder.compile()

    for s in graph.stream({
            
            "messages": [
                HumanMessage(content=f"""
                    load_files from 'dir_path':{get_project_filepath()}/data/csv/
                    """),
            ]
        },
        # Maximum number of steps to take in the graph
        {"recursion_limit": 100},
        ):
        print(s)
        print("----")