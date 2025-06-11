from core.db import get_latest_state, get_state
from core.graph import create_graph 
from core.logconfig import config_logging

config_logging()
state = get_latest_state()
graph = create_graph()
fianl_state = graph.invoke(input = state)
