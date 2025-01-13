from typing import Dict, Any, List
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool
from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda

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
            # TODO: Add more tools for analysis
        ]
        return tools

    def _create_agent(self) -> AgentExecutor:
        """
        Create the agent executor

        Returns:
            Initialized AgentExecutor
        """
        # Create the agent
        model = ChatAnthropic(model_name=self.model_name)
        agent_executor = create_react_agent(model, self.tools, checkpointer=self.memory)
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
                print(f'{type(chunk)=}...{chunk=}\n\n')
           
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
        query = state.get('query')
        # Run analysis
        if query is not None:
            output = self.analyze_trends(query=query)       
        # Update state with results
        state['response'] = output
        return state
    


if __name__ == '__main__':
    ins = InsuranceAnalysisAgent()
    query = 'How many distinct years are in this dataset?'
    # messages = [
    #     SystemMessage(content="""
    #         System: You have access to documents with the following columns: 'Year,Average expenditure,Percent change'.
    #         Given a user question about the data, write the Python code to answer it.
    #         If the question requires complex data analysis, use a Python REPL.
    #         If the question is about specific data points, use a retriever.
    #         Don't assume you have access to any libraries other than built-in Python ones and pandas.
    #         Make sure to refer only to the variables mentioned above.
    #         Be careful to not query for columns that do not exist. 
    #         """),
    #     HumanMessage(content=query)
    # ]
    p = Prompt(query)
    print(f'p={p.messages}')
    state = ins.run(state={'query':p.messages})
    logger.info(f'state={state}')