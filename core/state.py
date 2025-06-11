from typing import Literal, List, Dict
from pydantic import BaseModel

class NarrativeState(BaseModel):
    event:str = ''
    story:str =''
    flags:List[str, any] = []
    situation: str = ""
    turn: Literal["npc", "user"] = "npc"
    speaker: str = ""
    characters: List = []
    context: List[Dict[Literal['system', 'assistant', 'user'], str]] = []
    event_complete: bool = False

    def add_context(self, role:Literal['system', 'assistant', 'user'], content:str) -> None:
        context = self.context.copy()
        context.append({"role": role, "content":content})
        return self.model_copy(update={'context':context})

    def add_ai_context(self, content:str)->None:
        self.add_context('assistant', content)

    def add_user_context(self, content:str)->None:
        self.add_context('user', content)