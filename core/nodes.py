from core.state import NarrativeState, Character, Event, Situation, Timeline
from core.logconfig import log
from core.agent import (
    situation_presenter, 
    speaker_selector, 
    character_maker, 
    character_actor, 
    consistency_checker,
    intent_analyzer, 
    event_summary, 
    story_summary,
    end_judge,
    memory_extractor,

)
from core.db import (
    get_character, 
    store_character, 
    get_stories, 
    get_next_situation_id, 
    get_next_event_id, 
    get_next_timeline_id, 
    store_event, 
    store_situation, 
    store_timeline,
    store_memory,
    get_characters_name
)

@log.instrument
def present_situation(state: NarrativeState) -> NarrativeState:
    prompt = str(
        state.model_dump_json()
        + '\n name_list:' + str(get_characters_name())
        + '\n memory:' + str(state.memory)
    )
    result = situation_presenter.run_sync(prompt).output
    situation_id = get_next_situation_id()
    store_situation(Situation(
        situation_id=situation_id, 
        situation=result.situation, 
        characters=result.characters+[state.player_name, "narration"]
    ))

    return state.model_copy(update={
        "situation": result.situation,
        "characters": result.characters+[state.player_name, "narration"],
        "situation_id":situation_id 
    })

@log.instrument
def decide_speaker(state: NarrativeState) -> NarrativeState:
    if state.speaker == "":
        return state.model_copy(update={
            "turn": 'npc', 
            "speaker": 'narration'
        })
    
    if state.npc_count == 2 :
        return state.model_copy(update={
            "turn": 'user', 
            "speaker": state.player_name
        })
    

    speaker = speaker_selector.run_sync(str(state.model_dump_json())).output
    turn = 'user' if speaker == state.player_name else 'npc'

    return state.model_copy(update={
        "turn": turn, 
        "speaker": speaker
    })

@log.instrument
def npc_flow(state: NarrativeState) -> NarrativeState:
    character = get_character(state.speaker)
    if character == None:
        pi = character_maker.run_sync(str(state.model_dump_json())).output
        character = Character(**{
            'name' : state.speaker, 
            'generated_at' : state.event_id, 
            'persona' : pi.persona, 
            'instructions' : pi.instructions 
        })
        store_character(character)

    while True:
        output = character_actor(character).run_sync(str(state.model_dump_json())).output
        in1 = str(character.model_dump_json())
        in2 = str(state.context)
        if consistency_checker.run_sync(f"캐릭터:{in1}\n컨텍스트:{in2}\n대사:{output}"): 
            break
    return state.model_copy(update={"output": output,  
                            "context": state.context+[{"role":"assistant", 'content':output}], 
                            "npc_count":state.npc_count +1})

@log.instrument
def user_flow(state: NarrativeState) -> NarrativeState:
    if state.pending_user_input:
        user_input = state.pending_user_input
    else:
        user_input = input()
    state = state.model_copy(update={"output": user_input, "pending_user_input": ""})
    user_intent = intent_analyzer.run_sync(str(state.model_dump_json())).output
    return state.model_copy(update={"output": user_input, "user_intent":user_intent,
                            "context": state.context+[{"role":"user", 'content':user_input}],
                            "npc_count":0})

@log.instrument
def judge_event_end(state: NarrativeState) -> NarrativeState:
    wrapup = end_judge.run_sync(str(state.model_dump_json())).output
    return state.model_copy(update={"event_complete": wrapup})

@log.instrument
def wrapup(state: NarrativeState) -> NarrativeState:
    event = event_summary.run_sync(str(state.model_dump_json())).output
    story = story_summary.run_sync(str(get_stories(state.event_list)+[event])).output

    mem_input = {"event": event, "story": story, "prev_memory": state.memory}
    memory = memory_extractor.run_sync(str(mem_input)).output
    state = state.add_memory(memory)

    store_event(Event(
        event_id=state.event_id,
        situation_id=state.situation_id,
        situation_summary = state.situation,
        event_summary=event,
        story_summary=story
    ))
    store_timeline(Timeline(
        timeline_id=state.story_id,
        timeline=state.event_list+[state.event_id]
    ))
    store_memory(state.story_id, state.memory)
    next_event_id = get_next_event_id()
    next_story_id = get_next_timeline_id()
    # update_knowledge(knowledges)
    # flags_updater(flags)

    return state.model_copy(update = {        
        "event":event, 
        'event_id':next_event_id, 
        'event_list':state.event_list +[next_event_id], 
        'story':story, 
        'story_id':next_story_id, 

        'situation': "",
        'situation_id':"",
        'characters': [],
        
        'turn':  "npc",
        
        'speaker': "", 
        'speaker_character': None, 
        'output':"", 
        'user_intent':"", 
        'context': [],
        'memory': state.memory,
        'event_complete': False,
        'pending_user_input': ""
    })

