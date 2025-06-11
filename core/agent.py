from typing import Literal, List, Tuple
from state import NarrativeState

def generate_situation():
    '''컨텍스트, 플래그'''
    return "설원에 이상한 남자가 도착했다."

def find_characters()->List['str']:
    return ['클리엘(사용자)', '리에나', '바스티온']


count = 0
def select_speaker(state:NarrativeState) -> Tuple[Literal['user', 'npc'], str]:  
    if state.turn == 'user':
        count = (count+1)%len(state.characters-1)
        return 'npc', state.characters[count]
    else:
        return 'user', '클리엘(사용자)'

def get_memory():
    '''여기 메모리 메니저'''
    return 0