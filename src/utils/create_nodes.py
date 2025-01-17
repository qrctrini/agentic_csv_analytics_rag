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
from langchain_core.messages.base import message_to_dict, messages_to_dict
from langchain.output_parsers import PydanticOutputParser, JsonOutputToolsParser
from langchain.output_parsers.json import SimpleJsonOutputParser
from langchain.prompts import PromptTemplate
from langgraph.prebuilt import create_react_agent
from langchain.chains.combine_documents import create_stuff_documents_chain

# helpers
from src.utils.agent_state import AgentState
from src.utils.prompt import Prompt
from src.utils.utils import save_dict_to_json_file

class CreateNode:
    """
    Create langgraph nodes utility function
    """
    def __init__(self,name:str, description:str, llm:Any,tool_function:Any,prompt:Prompt):
        self.name = name
        self.tf = tool_function()
        self.tools = [Tool(
            name=f"{self.name}_tool",
            func=self.tf.run,
            description=description
        )]
        self.prompt = prompt()
        self.agent = create_react_agent(llm, tools=self.tools)
        self.dct = {
            "document_processor":-2,
            "vector_store":-2,
            "analysis":-2
        }
       

    def node(self,state: AgentState) -> Command[Literal["supervisor"]]:  
        """
        Create nodes for langgraph graph construction

        Args:
            state(AgentState): Message and state

        Returns:
            Command: Messages and next step for supervisor to make decision

        """
        logger.warning(f'{self.name} .... state:{state}')
        response = self.agent.invoke(state)
        new_message = response['messages'][self.dct[self.name]].content
        logger.info(f'{self.name}...type={type(new_message)} response={new_message}')
        if self.name == "analysis":
            save_dict_to_json_file({"analysis_node_response":new_message},'/tmp/analysis_node_response')
        return Command(
            update={
                "messages":[
                    HumanMessage(content=new_message,name=self.name)
                ],
                
            },
            goto='supervisor',
        )
    