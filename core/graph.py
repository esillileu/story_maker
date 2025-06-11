from langgraph.graph import StateGraph
from core.state import NarrativeState
from core.nodes import (
    present_situation,
    decide_speaker,
    npc_flow,
    user_flow,
    judge_event_end,
    wrapup
)

def create_graph():
    """
    Create and return the state graph for the narrative flow.
    """
    builder = StateGraph(NarrativeState)
    builder.add_node("PresentSituation", present_situation)
    builder.add_node("DecideSpeaker", decide_speaker)
    builder.add_node("NPCFlow", npc_flow)
    builder.add_node("UserFlow", user_flow)
    builder.add_node("JudgeEventEnd", judge_event_end)
    builder.add_node("Wrapup", wrapup)

    builder.set_entry_point("PresentSituation")
    builder.add_edge("PresentSituation", "DecideSpeaker")

    builder.add_conditional_edges(
        "DecideSpeaker",
        lambda state: state.turn,
        {
            "npc": "NPCFlow",
            "user": "UserFlow"
        }
    )

    builder.add_edge("NPCFlow", "JudgeEventEnd")
    builder.add_edge("UserFlow", "JudgeEventEnd")

    builder.add_conditional_edges(
        "JudgeEventEnd",
        lambda state: "Wrapup" if state.event_complete else "DecideSpeaker",
        {
            "Wrapup": "Wrapup",
            "DecideSpeaker": "DecideSpeaker"
        }
    )

    return builder.compile()

