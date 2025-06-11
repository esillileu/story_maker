from core.nodes import (
    present_situation, 
    decide_speaker, 
    npc_flow, 
    user_flow, 
    judge_event_end
)
from core.state import NarrativeState
from core.logconfig import config_logging

config_logging()
state = NarrativeState(
            event="고양이가 사라졌다",
            story="수정은 시장에서 고양이를 찾아다니고 있다",
            flags={"has_map": True},
            situation="",
            turn="",
            speaker="",
            characters=[],
            context=[],
            event_complete=False
        )

state = present_situation(state)
state = decide_speaker(state)
state = npc_flow(state)
state = judge_event_end(state)
state = decide_speaker(state)
state = user_flow(state)
state = judge_event_end(state)
