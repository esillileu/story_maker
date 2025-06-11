from typing import Literal, List, Dict
from pydantic import BaseModel

class Character(BaseModel):
    name:str = "" 
    generated_at:str = ""
    persona:str = ""
    instructions:str =  ""
    knowledge_groups:List[str] = []

class Event(BaseModel):
    event_id:str = "E_000"
    situation_id:str  = "S_000",
    situation_summary:str='',
    event_summary:str='', 
    story_summary:str=''

class Situation(BaseModel):
    situation_id:str = 'S_000'
    situation:str = ""
    characters:List[str] = []

class Timeline(BaseModel):
    timeline_id:str = "TL_000"
    timeline:List[str] = []


class NarrativeState(BaseModel):
    player_name:str = '수정'
    
    event:str = ""
    event_id:str = "E_000"
    event_list:List = ["E_000"]

    story:str = ""
    story_id:str = "TL_000"

    situation: str = ""
    situation_id:str=""
    characters: List = []
    
    turn: Literal["npc", "user", ""] = "npc"
    npc_count:int = 0

    speaker: str = ""
    speaker_character: Character|None = None
    output:str = ""
    user_intent:str = ""
    context: List[Dict] = []
    memory: List[str] = []
    event_complete: bool = False
    pending_user_input: str = ""
    

    def add_context(self, role:Literal['system', 'assistant', 'user'], content:str) -> None:
        context = self.context.copy()
        context.append({"role": role, "content":content})
        return self.model_copy(update={'context':context})

    def add_ai_context(self, content:str)->None:
        self.add_context('assistant', content)

    def add_user_context(self, content:str)->None:
        self.add_context('user', content)

    def add_memory(self, text: str) -> None:
        mem = self.memory.copy()
        mem.append(text)
        return self.model_copy(update={'memory': mem})

class SituationPresenterOutput(BaseModel):
    situation: str
    characters: List[str]

class CharacterMakerOutput(BaseModel):
    persona:str = ""
    instructions:str =  ""

    
class EventSummaryOutput(BaseModel):
    event: str
    story: List[str]
