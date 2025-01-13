
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage


class Prompt:
    def __init__(self,query:str):
        self.system_message = """
            System: You have access to documents with the following columns: 'Year,Average expenditure,Percent change'.
            Given a user question about the data, write the Python code to answer it.
            If the question requires complex data analysis, use a Python REPL.
            If the question is about specific data points, use a retriever.
            Don't assume you have access to any libraries other than built-in Python ones and pandas.
            Make sure to refer only to the variables mentioned above.
            Be careful to not query for columns that do not exist. 
            """
        self.messages = [
            SystemMessage(content=self.system_message),
            HumanMessage(content=query)
        ]
                

