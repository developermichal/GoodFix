from typing import List, Dict, Any
from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable

class GraphState:
    messages: List[BaseMessage] = []
    data: Dict[str, Any] = {}


class GraphChain:
    def __init__(self):
        self.chain = None

    def add(self, runnable: Runnable):
        if self.chain is None:
            self.chain = runnable
        else:
            self.chain = self.chain | runnable

    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if self.chain is None:
            return input_data
        return self.chain.invoke(input_data)