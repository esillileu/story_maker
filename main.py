from core.state import NarrativeState
from core.graph import create_graph 
from core.logconfig import config_logging

config_logging()
state = NarrativeState()
graph = create_graph()
fianl_state = graph.invoke(input = state)