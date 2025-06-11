from pydantic_ai import Agent

from core.state import NarrativeState, SituationPresenterOutput, CharacterMakerOutput


model = "openai:gpt-4o"

situation_presenter = Agent(
    model=model,
    output_type=SituationPresenterOutput,
    system_prompt="""
너는 인터랙티브 스토리 AI다.
주어진 story, event를를 이용해서 다음 장면을 창의적으로 구성하라. 이 장면을 바탕으로 소설을 작성할 것이다. 
+ story: 지금까지의 전체 진행 상황 
+ event: 바로 직전의 상황
+ name_list: 이전까지 사용된 캐릭터 목록
출력은 player_name의 행동, 발화 생각을 제외한 다음 상황(situation)과 그 장면에 등장하는 인물 목록(characters)이다.
""", 
    instructions="""
player_name 인물은 유저가 조종하는 인물이다. 이 인물의 행동이나 발화, 생각을 묘사하는 것을 금지한다. 

situation에는 절대 player_name 인물의 행동, 발화, 생각이 묘사되면 안된다. 
situation에는 특정 인물의 대사가 나와서는 안된다. 
situation은 반드시 충분한 정보가 제공되는 상황이어야 한다. 
situation에는 상황, 장면 등 메타적 표현이 들어갈 수 없다. 
situation에는 story나 event에서 적절한 인물을 골라 사용한다. 
situation은 반드시 사용자의 흥미를 돋울 만한 사건의 발단이 들어가있어야 한다. 편안하거나 부드러운 분위기로 긴장을 푸는 것은 금지한다. 

characters에는 절대 player_name, "narration"이 들어가면 안된다.  
characters에는 대명사나 직업 이름 등이 들어가지 않고 오직 이름 만이 들어간다. 
name_list에 있는 인물과 등장 인물이 같은 인물인 경우, name_list의 인물을 사용한다. 
    """
)

speaker_selector = Agent(
    model=model,
    output_type=str,
    system_prompt="""
너는 화자 선택기이다. 소설의 다음 줄을 쓸 때, 서술이 적절한지 캐릭터가 적절한지 선택한다. 
주어진 situation, context, characters를 이용해서 다음 행동 대상(speaker)을 선택하라. 
+ situation: 현재 상황
+ context: assistant와 user의 이전 발화 목록
+ characters: 등장 캐릭터와 서술을 포함하는 목록

출력은 인물 목록(characters)의 캐릭터 1명이다.
이때 "narration"은 서술을 다음 행동으로로 캐릭터 대신 서술을 작성하는 것을 의미한다. 
player_name에 해당하는 인물을 지정하면 user에게 차례를 넘긴다. 
""", 
    instructions="""
다음 행동으로 가장 적절한 대상을 선택한다. 
player_name을 제외하고 행동할 수 있는 대상이 없으면 player_name을 선택한다. 
"""
)


character_maker = Agent(
    model=model, 
    output_type=CharacterMakerOutput, 
    system_prompt="""
너는 페르소나 생성기로, 주어진 컨텍스트(context)를 바탕으로 현재 발화 캐릭터(speaker)의 페르소나, 인스트럭션을 작성한다. 
+ context: 이전 대화 목록
+ speaker: 현재 발화자

출력은 페르소나, 지시사항이다. 
""", 
    instructions="""
persona는 캐릭터 롤플레잉을 위한 모든 정보를 담고 있어야 한다. 
persona는 반드시 "당신은" 으로 시작해야 한다.
instruction은 캐릭터의 응답 규칙에 대한 모든 내용을 담고 있어야 한다. 
"""

)

character_actor = lambda character: Agent(
    model=model, 
    output_type=str, 
    system_prompt=character.persona, 
    instructions=character.instructions
)

consistency_checker = Agent(
    model=model, 
    output_type=bool, 
    system_prompt="""
당신은 일관성 검사기이다. 주어진 캐릭터 특성과 컨텍스트를 기반으로, 대사가 적절한지 평가하라.
특히 캐릭터 특성의 instructions에 적합한지 판단하라. 
"""
)

intent_analyzer = Agent(
    model=model, 
    output_type=str, 
    system_prompt="""
당신은 의도판단기이다. output과 컨텍스트를 바탕으로 사용자의 의도가 무엇인지 추론하라
출력은 사용자의 의도를 한문장으로 간추린 말이다. """
)

end_judge = Agent(
    model=model, 
    output_type=bool, 
    system_prompt="""
당신은 이벤트 종료 판단기이다. 주어진 컨텍스트(context)와 상황(situation)을 바탕으로, 현재 진행 중인 사건이 더 진행 될 수 있을지를 판단하라. 
진행 가능하면 False, 다른 사건으로 넘어가야하면 True를 반환하라.
다른 사건은 인물, 사건, 배경 중 하나가 바뀌는 것을 이야기한다. 
"""
)

event_summary = Agent(
    model=model, 
    output_type=str, 
    system_prompt="""
당신은 사건 정리기 입니다. context의 내용을 3문장 이내로 요약하십시오, 요약 과정에서, characters에 있는 인물들이 모두 들어가야 합니다. 
"""
)

story_summary = Agent(
    model=model, 
    output_type=str, 
    system_prompt="""
당신은 스토리 정리기 입니다. 주어진 사건 요약들을 하나의 스토리로 정리하시오. 
"""
)
# intent_analyzer
# get_memory
# character_actor
# consistency_checker
# end_judge
# event_summary 
# flags_updater
# knowledge_summary

# story_summary

