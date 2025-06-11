import os
from pymongo import MongoClient
from core.state import Character, Event, Situation, Timeline, NarrativeState
import logging

cluster = 'test4'
mongo_cluster = MongoClient(os.getenv('MONGO_CLUSTER_URI'))
characater_collection = mongo_cluster[cluster]['character']
event_collection = mongo_cluster[cluster]['event']
situation_collection = mongo_cluster[cluster]['situation']
timeline_collection = mongo_cluster[cluster]['timeline']
memory_collection = mongo_cluster[cluster]['memory']
sample_data = {
    "_id": "narration_E_000",
    "generated_at" : "E_000", 
    "name": "narration",
    "persona": """
    당신은 소설의 서술자입니다. 
    이전의 컨텍스트에 맞춰 소설의 서술을 생성하세요. 
    당신은 숙련된 이야기꾼으로, 단순히 서로 지지하는 인간적인 스토리를 혐오합니다. 
    인간의 본성적 선함을 신뢰하지 않으며, 캐릭터의 개별 욕망으로 전개되는 스토리를 지향합니다. 
    """,
    "instructions": """
    출력은 소설의 서술 처럼 작성합니다. 
    출력에는 따옴표나 대사가 없어야 합니다. 
    출력은 3인칭으로 player_name을 제외한 인물의 행동, 상황, 외견 등 대사로 표현 불가능한 것들을 디테일하게 표현합니다. 
    서술에는 절대 player_name 캐릭터의 행동이나 대사, 생각은 들어갈 수 없습니다. 
    player_name의 행동이나 생각이 나오면 그 즉시 생성을 멈춥니다. 
    """,
    "knowledge_groups": [
        "north",
        "imperial_military",
        "riena_knights"
    ]
}


def get_character(name) -> Character:
    result = characater_collection.find({"name":name}, None)
    try:
        log = str(result[0]).replace("\n", "")
    except:
        return None
    logging.info(f"DB_loaded: {name}: {log}")
    return Character(**result[0])

def get_characters_name() -> Character:
    result = characater_collection.find({}, None)

    return [i['name'] for i in result]

def store_character(character:Character):
    character_dict = character.model_dump()
    character_dict["_id"] = character_dict['name']+'_'+character_dict['generated_at']
    insert_result = characater_collection.insert_one(character_dict)
    log = str(insert_result).replace("\n", "")
    logging.info(f"DB_stored: {insert_result.inserted_id}: {log}")

def store_event(event:Event):
    event_dict = event.model_dump()
    event_dict["_id"] = event_dict['event_id']
    insert_result = event_collection.insert_one(event_dict)
    log = str(insert_result).replace("\n", "")
    logging.info(f"DB_stored: {insert_result.inserted_id}: {log}")

def store_situation(situation:Situation):
    situation_dict = situation.model_dump()
    situation_dict["_id"] = situation_dict['situation_id']
    insert_result = situation_collection.insert_one(situation_dict)
    log = str(insert_result).replace("\n", "")
    logging.info(f"DB_stored: {insert_result.inserted_id}: {log}")

def store_timeline(timeline:Timeline):
    timeline_dict = timeline.model_dump()
    timeline_dict["_id"] = timeline_dict['timeline_id']
    insert_result = timeline_collection.insert_one(timeline_dict)
    log = str(insert_result).replace("\n", "")
    logging.info(f"DB_stored: {insert_result.inserted_id}: {log}")

def store_memory(timeline_id: str, memory: list):
    memory_collection.update_one(
        {"timeline_id": timeline_id},
        {"$set": {"memory": memory, "timeline_id": timeline_id}},
        upsert=True
    )

def get_memory(timeline_id: str) -> list:
    doc = memory_collection.find_one({"timeline_id": timeline_id})
    if doc:
        return doc.get("memory", [])
    return []

def list_timelines():
    result = timeline_collection.find({}, {"timeline_id": 1})
    return [doc["timeline_id"] for doc in result]

def get_stories(event_list):
    summaries = []
    for event_id in event_list:
        event = event_collection.find_one({'event_id':event_id})
        if event != None:
            summaries.append(event['event_summary'])
    return summaries

def get_latest_id(collection, id_name) -> int:
    # 모든 event_id를 불러와 숫자 부분만 추출 후 최대값 계산
    files = collection.find({})
    max_id = -1
    for file in files:
        try:
            num = int(file[id_name].split('_')[1])
            if num > max_id:
                max_id = num
        except:
            continue
    if max_id == -1:
        return 0
    logging.info(f"{max_id:03d}")

    return max_id

def get_next_id(collection, id_name) -> int:
    return get_latest_id(collection, id_name)+1

def get_next_event_id():
    max_id = get_next_id(event_collection, 'event_id')
    return f"E_{max_id:03d}"

def get_next_situation_id():
    max_id = get_next_id(situation_collection, 'situation_id')
    logging.info(f"S_{max_id:03d}")
    return f"S_{max_id:03d}"

def get_next_timeline_id():
    max_id = get_next_id(timeline_collection, 'timeline_id')
    return f"TL_{max_id:03d}"

def get_latest_event_id():
    max_id = get_latest_id(event_collection, 'event_id')
    return f"E_{max_id:03d}"

def get_latest_situation_id():
    max_id = get_latest_id(situation_collection, 'situation_id')
    return f"S_{max_id:03d}"

def get_latest_timeline_id():
    max_id = get_latest_id(timeline_collection, 'timeline_id')
    return f"TL_{max_id:03d}"

def get_state(tl):
    timeline = timeline_collection.find_one({'timeline_id':tl})

    event_id = timeline['timeline'][-1]
    event = event_collection.find_one({'event_id':event_id})
    memory = get_memory(tl)

    return NarrativeState(**{
            "event":event['event_summary'],
            'event_id':get_next_event_id(),
            'event_list':timeline['timeline'],
            'story':event['story_summary'],
            'story_id':get_next_timeline_id(),

            'situation': "",
            'situation_id':"",
            'characters': [],
            
            'turn':  "npc",
            
            'speaker': "", 
            'speaker_character': None,
            'output':"",
            'user_intent':"",
            'context': [],
            'memory': memory,
            'event_complete': False,
            'pending_user_input': ""
        })

def get_latest_state():
    return get_state(get_latest_timeline_id())

try:
    store_character(Character(**sample_data))
except:
    pass

if __name__ == "__main__":
    sample_data = {
        "_id": "narration_E0000",
        "generated_at" : "E0000", 
        "name": "narration",
        "persona": """
        당신은 소설의 서술자입니다. 
        이전의 컨텍스트에 맞춰 소설의 서술을 생성하세요. 
        당신은 숙련된 이야기꾼으로, 단순히 서로 지지하는 인간적인 스토리를 혐오합니다. 
        인간의 본성적 선함을 신뢰하지 않으며, 캐릭터의 개별 욕망으로 전개되는 스토리를 지향합니다. 
        """,
        "instructions": """
        출력은 소설의 서술 처럼 작성합니다. 
        출력에는 따옴표나 대사가 없어야 합니다. 
        출력은 3인칭으로 player_name을 제외한 인물의 행동, 상황, 외견 등 대사로 표현 불가능한 것들을 디테일하게 표현합니다. 
        서술에는 절대 player_name 캐릭터의 행동이나 대사, 생각은 들어갈 수 없습니다. 
        player_name의 행동이나 생각이 나오면 그 즉시 생성을 멈춥니다. 
        """,
        "knowledge_groups": [
            "north",
            "imperial_military",
            "riena_knights"
        ]
    }
    store_character(Character(**sample_data))
