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
                description="Search through insurance documents"
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
        for chunk in self.agent.stream({"messages":query}, config):
            if 'agent' in chunk:
                message = chunk['agent']['messages']
                messages.append(message)
                logger.info(f'{type(chunk)=}...{chunk=}\n\n')
           
        return messages
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main agent function to be called by the supervisor

        Args:
            state: Current state of the system

        Returns:
            Updated state
        """
        # -- Implement agent logic
        # Extract query from state
        #query = state.get('query')
        # Run analysis
        # if query is not None:
        #     output = self.analyze_trends(query=query)       
        # Update state with results
        if state:
            logger.warning(f'inside analyze really: {state}')
            output = self.analyze_trends(query=state)  
            logger.info(output)
        
            return f'FINISH - {output}'
        return 'FINISH'
    

# if __name__ == '__main__':
#     ins = InsuranceAnalysisAgent()
#     query = 'What is a important trend in Average expenditure?'
#     p = Prompt(query)
#     print(f'p={p.messages}')
#     state = ins.run(state={'query':p.messages})
#     logger.info(f'state={state}')