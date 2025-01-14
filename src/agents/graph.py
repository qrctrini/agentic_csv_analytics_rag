from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langgraph.graph import MessagesState, END
from langgraph.types import Command
from typing import Literal
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langchain.tools import Tool

# agents
from src.agents.document_processor import DocumentProcessor
from src.agents.supervisor import Supervisor

# helpers
from src.utils.utils import get_project_filepath
from src.agents.supervisor import supervisor_node, Supervisor

supervisor = Supervisor()

# create document processor node
dp = DocumentProcessor()

tools = [
    Tool(
        name="process_documents",
        func=dp.run,
        description="Load and process documents"
    )
]


document_processor_agent = create_react_agent(supervisor.llm, tools=tools)
def document_processor_node(state: MessagesState) -> Command[Literal["supervisor"]]:
    #read the last message in the message history.
    
    result = document_processor_agent.invoke(state)
    return Command(
        update={
            "messages": [
                HumanMessage(content=result["messages"][-1].content, name="document_processor")
            ]
        },
        goto="supervisor",
    )

if __name__ == '__main__':
    builder = StateGraph(MessagesState)
    builder.add_edge(START, "supervisor")
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("document_processor", document_processor_node)
    graph = builder.compile()

    for s in graph.stream(
        {"messages": [("user", f"{get_project_filepath()}/data/csv")]}, subgraphs=True
    ):
        print(s)
        print("----")