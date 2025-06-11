from core.state import NarrativeState
from core.logconfig import log
from core.agent import (
    generate_situation, 
    find_characters, 
    select_speaker, 
    analyze_intent,
    get_memory,
    act_character,
    check_consistent, 
    judge_end,
    summary_event,    
    update_flags, 
    summary_knowledge,
    summary_story,
)
from core.db import (
    update_knowledge,
    update_story,
    update_event
)

@log.instrument
def present_situation(state: NarrativeState) -> NarrativeState:
    situation = generate_situation()
    characters = find_characters()
    return state.model_copy(
        update={
            "situation": situation, 
            "characters": characters
        })

@log.instrument
def decide_speaker(state: NarrativeState) -> NarrativeState:
    turn, speaker = select_speaker()
    return state.model_copy(
        update={
            "turn": turn, 
            "speaker": speaker
            })

@log.instrument
def npc_flow(state: NarrativeState) -> NarrativeState:
    memory = get_memory()
    while True:
        output = act_character(memory)
        if check_consistent(): break
    return state.model_copy(update={"npc_output": output})

@log.instrument
def user_flow(state: NarrativeState) -> NarrativeState:
    user_input = get_user_input()
    user_input = analyze_intent(user_input)
    return state.model_copy(update={"user_input": user_input})

@log.instrument
def judge_event_end(state: NarrativeState) -> NarrativeState:
    wrapup = judge_end()
    return state.model_copy(update={"event_complete": wrapup})

@log.instrument
def wrapup(state: NarrativeState) -> NarrativeState:
    event = summary_event()
    flags = update_flags()
    knowledges = summary_knowledge()
    story = summary_story()

    update_knowledge(knowledges)
    update_event(event)
    update_flags(flags)
    update_story(story)

    return state.model_copy(update = )

