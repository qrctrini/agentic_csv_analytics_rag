
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate, SystemMessagePromptTemplate
from typing import Any

class Prompt:
    def __init__(self):
        self.system_prompt_template = PromptTemplate(

                template=  """
                ONLY respond to the part of query relevant to your purpose.
                IGNORE tasks you can't complete. 
                Use the following context to answer your query 
                if available: \n {messages} \n
                """,
                input_variables=["messages"],
            )

        #define system message
        self.system_message_prompt = SystemMessagePromptTemplate(prompt=self.system_prompt_template)

        self.prompt = ChatPromptTemplate.from_messages(
            [self.system_message_prompt,
                MessagesPlaceholder(variable_name="messages"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
                

