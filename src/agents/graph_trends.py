from typing import Dict, Any, List
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.tools import Tool, BaseTool
from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from typing import Optional
from pydantic import Field
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
#from langchain_experimental.tools import PythonREPLTool
from langchain.prompts import PromptTemplate

from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain.memory import ConversationBufferMemory
from langchain_experimental.tools import PythonAstREPLTool
from langchain_core.messages import RemoveMessage, AIMessage
from langchain_core.callbacks.manager import CallbackManagerForToolRun
from langchain_experimental.tools.python.tool import sanitize_input
from loguru import logger
import os
import random
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt

from dotenv import load_dotenv 
load_dotenv()

# project import
from src.agents.vector_store import VectorStore
from src.utils.prompt import Prompt


class PythonREPLTool(BaseTool):
    """Tool for running python code in a REPL."""

    name: str = "Python_REPL"
    description: str = (
        "A Python shell. Use this to execute python commands. "
        "Input should be a valid python command. "
        "If you want to see the output of a value, you should print it out "
        "with `print(...)`."
    )
    python_repl: PythonREPL = tool("PythonREPL")
    sanitize_input: bool = True

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> Any:
        
        """Use the tool."""
        if self.sanitize_input:
            query = sanitize_input(query)
        result = self.python_repl.run(query)

        logger.warning(f'***************************************************************************')

        plt.savefig('zz_graph.png')
        plt.close()
        plt.savefig('/tmp/zz_graph.png')
        plt.close()
        
        # Check if the result is a matplotlib figure
        if isinstance(result, plt.Figure):
            # Save the figure to a file
            result.savefig('/tmp/zz_graph.png')


        
        return self.python_repl.run(query)



class CreateDataframeAgent:
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
        self.thread_id = self._generate_thread_id()
        self.graph_save_location = '/tmp'

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
                description="Search through documents"
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
    
    def _create_dataframe_agent(self,filename: str):
        """
        Create an agent that can access and use a large language model (LLM).

        Args:
            filename: The path to the CSV file that contains the data.

        Returns:
            An agent that can access and use the LLM.
        """


        # Read the CSV file into a Pandas DataFrame.
        df = pd.read_csv(filename)

        # Create a Pandas DataFrame agent.
        return create_pandas_dataframe_agent(self.llm, df, verbose=False)

    def clear_agent_memory(self):

        # Initialize a new memory object
        memory = ConversationBufferMemory()

        # When you want to clear the memory, simply reinitialize it
        memory = ConversationBufferMemory()

        # Pass this new memory object to your agent
        return memory
    

    def create_dataframe(self, query:str):
        
        query = """
            Query the vector database and retrieve data.
            The response should be in JSON format.
            There response should have three columns: ["Year","Average expenditure","Percent change"]
            The response should look as follows:
            {"table": {"columns": ["column1", "column2", ...], "data": [[value1, value2, ...], [value1, value2, ...], ...]}}
            Generate a  a line graph of the trendline using "Year" and "Percent change".
            If you cannot display the graph, save it to "/tmp/zzzgraph.png"
        """
        query = """
            Query the database and retrieve data.
            Generate a  a line graph of the trendline using "Year" and "Percent change".
        """

        tools = [
            Tool(
                name="search_documents",
                func=self.vector_store.similarity_search,
                description="query the database for 'Year' and 'Percent change' data ",
            ),
            PythonREPLTool()
        ]
        config = {"configurable": {"thread_id": self.thread_id}}
        agent = create_react_agent(self.llm, tools)
        
        response = agent.invoke({"messages":[query]},config=config)
        logger.warning(f'type={type(response)},....,response={response}')
        self.find_required_output(response,ToolMessage)
        
        return response
    
    def find_required_output(self, response:dict, type:BaseMessage):
        for idx,message in enumerate(response["messages"]):
            if isinstance(message,type):
                logger.info(f"""
                ___________________________________
                        index={idx}
                -----------------------------------  
                ***
                {message.content}
                ****
                {response["messages"][-1]}
                """)


    def query_agent(self,agent, query):
        """
        Query an agent and return the response as a string.

        Args:
            agent: The agent to query.
            query: The query to ask the agent.

        Returns:
            The response from the agent as a string.
        """

        prompt = (
            """
                For the following query, if it requires drawing a table, reply as follows:
                {"table": {"columns": ["column1", "column2", ...], "data": [[value1, value2, ...], [value1, value2, ...], ...]}}

                If the query requires creating a bar chart, reply as follows:
                {"bar": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}

                If the query requires creating a line chart, reply as follows:
                {"line": {"columns": ["A", "B", "C", ...], "data": [25, 24, 10, ...]}}

                There can only be two types of chart, "bar" and "line".

                If it is just asking a question that requires neither, reply as follows:
                {"answer": "answer"}
                Example:
                {"answer": "The title with the highest rating is 'Gilead'"}

                If you do not know the answer, reply as follows:
                {"answer": "I do not know."}

                Return all output as a string.

                All strings in "columns" list and data list, should be in double quotes,

                For example: {"columns": ["title", "ratings_count"], "data": [["Gilead", 361], ["Spider's Web", 5164]]}

                Lets think step by step.

                Below is the query.
                Query: 
                """
            + query
        )

        # Run the prompt through the agent.
        response = agent.run(prompt)

        # Convert the response to a string.
        return response.__str__()

    
    def _generate_thread_id(self) -> str:
        """
        Generate random integer -> cast as string to use for thread id

        Args:
            -
        Returns:
            thread_id(str) - randomly generated integer cast as strin
        """
        return str(random.randint(1000,5000))

    def graph_trends(self, query: str) -> str:
        """
        TODO: Analyze insurance trends

        Args:
            query: Analysis query

        Returns:
            Analysis results
        """
        logger.info(f"query: {query}")
        # Use the agent
        config = {"configurable": {"thread_id": self.thread_id}}
        response = self.agent.invoke(messages=query,config=config)
        return response
    
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
            logger.warning(f'inside analyze really: {state["query"]}')
            output = self.create_dataframe(query=state)  
            #logger.info(f'output:{output}')
        
            return output
        return None
    

    

if __name__ == '__main__':
    ins = CreateDataframeAgent()
    query = """ Query the database and retrieve data.
            Get "Year" and "Percent change" data from the vector database.
            The intermediate response should look as follows:
            {"data": {"columns": ["column1", "column2", ...], "data": [[value1, value2, ...], [value1, value2, ...], ...]}}
            Use the python tools to create charts.
            Generate and save a line charts of any trend using "Year" and "Percent change".
            Save the graphs to "/tmp/zz_graph.png"
            """
    state = ins.run(state={'query':query,"messages":[]})
