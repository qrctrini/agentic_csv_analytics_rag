from typing import Dict, Any, List
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool
from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from typing import Annotated
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from langchain_experimental.tools import PythonREPLTool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import create_retriever_tool
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import RetrievalQA
import psycopg
from datetime import time
import logging
import os
import random
import json
from loguru import logger
from dotenv import load_dotenv 
load_dotenv()


# project import
from src.agents.vector_store import VectorStore
from src.utils.prompt import Prompt
from src.utils.utils import get_project_filepath, save_dict_to_json_file, load_config_params_for_node


# setup loggers
logger_native = logging.getLogger(__name__)
logger.add(
    f"{get_project_filepath()}/logs/analysis.log",
    rotation=time(0, 0),
    format="{time} {level} {message}",
    level="WARNING"
    )

class InsuranceAnalysisAgent:
    def __init__(self):
        """
        Initialize the analysis agent with necessary componentsvector_store: Initialized VectorStore instance
        Args:
            
        """
        self.name = "analysis"
        self.vector_store = VectorStore()
        self.vector_store.init_store()
        self.model_name = "claude-3-sonnet-20240229"
        self.llm = ChatAnthropic(model_name=self.model_name,api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.temperature = 0.5
        self.memory = MemorySaver()
        self.thread_id = self._generate_thread_id()
        self.configs = load_config_params_for_node(self.name)

        # Initialize retrieval chain
        self.retrieval_chain = self._create_retrieval_chain()

        # Initialize tools
        self.tools = self._create_tools()

        # Initialize agent
        self.agent = self._create_agent()

        # helper user queries
        self.query_prepend = "You are a data analyst.Use the retreiver to access the insurance data in the vector store. If needed use the python tool to use pandas for deep analysis."
        self.queries = [
            
            "What's the trend in auto insurance costs over the last 3 years?",
            "Compare insurance costs between different regions",
            "What factors most influence insurance costs?",
            "Generate a summary of key findings from the data"
        ]

    def _create_retrieval_chain(self) -> RetrievalQAWithSourcesChain:
        """
        Create retrieval chain for document querying

        Returns:
            Initialized RetrievalQAWithSourcesChain
        """
        #: Implement retrieval chain creation
        retriever = self.vector_store.vector_store.as_retriever()
        chain = RetrievalQAWithSourcesChain.from_llm(llm=self.llm, retriever=retriever)
        return chain

    def _create_tools(self) -> List[Tool]:
        """
        Create tools for the agent

        Returns:
            List of Tool objects
        """
        tools = [
            Tool(
                name="search_documents",
                func=self.vector_store.similarity_search,
                description="Analyze insurance documents for trends, anomalies, patterns"
            ),
          
            PythonREPLTool()
        ]
        return tools

    def _create_agent(self) -> AgentExecutor:
        """
        Create the agent executor

        Returns:
            Initialized AgentExecutor
        """
        # Create the agent
        # model = ChatAnthropic(model_name=self.model_name)
        agent_executor = create_react_agent(self.llm, self.tools)
        return agent_executor
    
    def _generate_thread_id(self) -> str:
        """
        Generate random integer -> cast as string to use for thread id

        Args:
            -
        Returns:
            thread_id(str) - randomly generated integer cast as strin
        """
        return str(random.randint(1000,5000))

    def analyze_trends(self,query:str) -> str:
        """
        TODO: Analyze insurance trends

        Args:
            query: Analysis query

        Returns:
            Analysis results
        """
        #logger.info(f"Analyzing trends for query: {query}")
        # Use the agent
        config = {"configurable": {"thread_id": self.thread_id}}
        messages,counter = {},0

        # for query_add in self.queries:
        #     query = f'{query_add}::{query}'
        #     for chunk in self.agent.stream({"messages":query}, config):
        #         if 'agent' in chunk:
        #             message = chunk['agent']['messages'][0].content
        #             messages[counter] = message
        #             print(f'{type(message)=}...{message=}\n\n')
        #             counter += 1
        for chunk in self.agent.stream({"messages":query}, config):
            if 'agent' in chunk:
                message = chunk['agent']['messages'][0].content
                messages[counter] = message
                print(f'{type(message)=}...{message=}\n\n')
                counter += 1
                    
        savepath = f'{get_project_filepath()}/data/output/analysis_node_output.json'
        save_dict_to_json_file(dct=messages,dir_path=savepath)
        return messages
        
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main agent function to be called by the supervisor

        Args:
            state: Current state of the system

        Returns:
            Updated state
        """
        # Update state with results
        output = self.analyze_trends(query=state)  
    
        return {
            "messages":'FINISH',
            "answer":output,
        }
     
