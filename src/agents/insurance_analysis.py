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

import logging
import os
import random
from dotenv import load_dotenv 
load_dotenv()

logger = logging.getLogger(__name__)

# project import
from src.agents.vector_store import VectorStore
from src.utils.prompt import Prompt


class InsuranceAnalysisAgent:
    def __init__(self):
        """
        Initialize the analysis agent with necessary componentsvector_store: Initialized VectorStore instance
        Args:
            
        """
        self.vector_store = VectorStore()
        self.vector_store.init_store()
        self.model_name = "claude-3-sonnet-20240229"
        self.llm = ChatAnthropic(model_name=self.model_name,api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.temperature = 0
        self.memory = MemorySaver()
        self.thread_id = self._generate_thread_id()

        # Initialize retrieval chain
        self.retrieval_chain = self._create_retrieval_chain()

        # Initialize tools
        self.tools = self._create_tools()

        # Initialize agent
        self.agent = self._create_agent()

        # queries
        self.query_prepend = "You are a data analyst.Use the retreiver to access the insurance data in the vector store. If needed use the python tool to use pandas for deep analysis."
        self.queries = [
            
            "What trends can you identify in this data?",
            "What type of charts or graphs would best represent this data?",
            "Based on this data, what future trends can we expect?",
            "Identify and highlight the predominant themes from the data",
            "What are the biggest year to year changes in the dataset?",
            "What are the positive things to note from the dataset?"
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
        retriever = self.vector_store.vector_store.as_retriever()
        tools = [
            # Tool(
            #     name="search_documents",
            #     func=self._create_retrieval_chain,
            #     description="Analyze insurance documents for trends, anomalies, "
            # ),
            create_retriever_tool(
                retriever=retriever,
                name="vector_store_retriever",
                description="Retrieves relevant documents vector store."
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
        agent_executor = create_react_agent(self.llm, self.tools, checkpointer=self.memory)
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

    def analyze_trends(self, query: str) -> str:
        """
        TODO: Analyze insurance trends

        Args:
            query: Analysis query

        Returns:
            Analysis results
        """
        logger.info(f"Analyzing trends for query: {query}")
        # Use the agent
        config = {"configurable": {"thread_id": self.thread_id}}
        messages = []
        for query in self.queries:
            query = f'{self.query_prepend}.{query}'
            logger.warning(f'query:{query}')
            chunk = self.agent.invoke(query)
            logger.info(f'{type(chunk)=}...{chunk=}\n\n')
            # for chunk in self.agent.stream({"messages":query}, config):
            #     #if 'agent' in chunk:
            #     logger.info(f'{type(chunk)=}...{chunk=}\n\n')
            #     # message = chunk['agent']['messages']
            #     # messages.append(message)
            #     # logger.info(f'{type(chunk)=}...{chunk=}\n\n')
           
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
        logger.warning(f'inside analyze: {state}')
        output = self.analyze_trends(query=state)  
        logger.info(f'output:{output}')
    
        return {
            "messages":'FINISH',
            "answer":output,
        }
     
    

if __name__ == '__main__':
    ins = InsuranceAnalysisAgent()
   
    state = ins.run(state=["you are a data analyst. Perform analysis."])
    logger.info(f'state={state}')