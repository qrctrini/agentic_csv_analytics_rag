from langchain.agents import AgentOutputParser
from loguru import logger

class MyCustomOutputParser(AgentOutputParser):
    def parse(self, input, output):
        # Implement your parsing logic here
        # For example, print the output
        logger.info("Custom parser output:", output)
        return super().parse(input, output)

