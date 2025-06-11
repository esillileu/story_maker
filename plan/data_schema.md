# timeline 관리
## dialogs
```json
{
  "_id": ObjectId,
  "event_id": "E_001",           // 이 로그가 속한 사건 ID
  "role":  "narration",  // narration | user | system | npc 
  "content": "리에나가 검을 꺼내 들었다." // 실제 텍스트
}
```

## timelines
```json
{
  "_id": "TL_0001",              // 타임라인 ID (문자열 혹은 ObjectId 가능)
  "event_ids": ["E_001", "E_002", "E_003"]  // 이 타임라인에 속한 사건들의 ID 순서
}
```

## evnets
```json
{
  "_id": "E_001",                      // 사건 ID
  "situation_id": "S_001",            // 사건이 발생한 상황의 ID
  "situation_summary": "리에나가 카이엘에게 칼을 겨눈다",
  "reaction_summary": "카이엘은 무기를 꺼내지 않고 조용히 노려본다",
  "flags": {                            // 변경 로그  
    { "flag_id": "F_0001", "value": true },
    { "flag_id": "F_0002", "value": true }
  }
}
```

## flags
```json
{
  "_id": "F_0001",         // 플래그 ID (키 역할)
  "alias": "kai_is_alert", 
  "description": "카이엘이 경계 상태인지 여부",
  "possible_values": [true, false]  // 가능한 값들 (bool, enum 등)
}
```
# 지식 관리 
+ 지식과 기억을 구분하여 관리
    + 지식은 정보
    + 기억은 개인 판단
+ 지식은 흭듣 로그를 통해 관리
+ 심도에 따라 접근 여부 다름 
    + 캐릭터 상태의 지식 그룹
    ```
    ├─ depth: common       → 전체 캐릭터
    ├─ depth: regional     → 특정 지역 소속 캐릭터
    ├─ depth: factional    → 특정 세력/조직 구성원
    ├─ depth: private      → 개인만 인지
    └─ depth: secret       → 사건 후 특정 인물만 인지 (지식 로그 필요)
    ```
## knowledge
```json
{
  "_id": "K_0001",
  "alias": "truth_about_kaiel", 
  "description": "카이엘이 황제의 숨겨진 아들이라는 사실",
  "type": "fact",                   // "fact" | "rumor" | "lie" 등
  "access_group": "imperial_military", // 접근 가능한 지식 그룹 (depth 대체)
  "scope": "secret",               // 지식의 공개 범위 의미: "common" | "regional" | "factional" | "private" | "secret"
  "visibility_rules": {
    "auto_known_by": ["kaiel"],     // 자동 인지 인물
    "requires_event": true          // 특정 사건 이후에만 인지 가능
  }
}
```

## knowledge_logs
```json
{
  "_id": ObjectId,
  "character_id": "riena",
  "knowledge_id": "K_0001",
  "event_id": "E_010",
  "status": "acquired",  // or "forgotten"
  "via":  "dialogue" | "inference" | "accidental" | "report",  // reveal | deduction | guess | observation
  "timestamp": "2025-05-23T14:55:00"
}
```

## memory_logs
> 지식이 아닌 모든 기억들
```json
{
  "_id": ObjectId,
  "character_id": "kaiel",  // 기억 인물
  "target": { 
    "type": "character", // 인물, 사건, 장소, 사물, 집단에 대해 
    "id": "riena"
  },         
  "event_id": "E_005",      // 사건을 얻게 된 이벤트
  "emotion": "리에나의 반역준비에 대해 혼란"        
}
```

# 캐릭터 관리
+ 캐릭터 상태는 사건에 따라 업데이트.
    + 사건 등장 인물에 대해 매 사건 종료마다 업데이트
        + 배경, 인격, 특징, 지식 그룹 
    + 인물 등장 시 최신 페르소나 가져오기

```json
{
  "_id": "카이엘_E0000",
  "generated_at" : "E0000", 
  "name": "카이엘",
  "persona": "당신은 카이엘입니다. 눈으로 뒤덮인 북부의 버려진 성에서 홀로 깨어난 인물로, 이름 외에는 아무런 기억이 없습니다. 그러나 손에 익은 검술과 단련된 반사신경은 당신이 평범한 과거를 지니지 않았음을 암시합니다. 제국군과 리에나 기사단에 얽힌 단편적인 기억을 가지고 있으나, 자신의 정체는 아직 명확하지 않습니다. 당신은 말이 적고 감정을 드러내지 않으며, 타인을 즉각적으로 적대하지 않고 침묵으로 관망합니다. 진실을 밝히기보다는 감추고, 상대가 먼저 드러내기를 기다리는 성향을 지녔습니다. 내면에 일관된 판단 기준을 가지고 있으며, 조용히 그 실마리를 좇고 있습니다.",
  "instructions": "응답은 항상 3인칭 제한 시점의 소설 형식으로 작성합니다. 문장은 단문 위주로 구성하고, 감정 표현은 최대한 억제합니다. 카이엘은 말수가 적고 감정을 잘 드러내지 않으며, 상황에 즉각 반응하기보다는 침묵과 관찰을 우선시합니다. 대사는 필요할 때만 간결하게 사용하며, 그의 과거나 정체에 대해서는 단서를 제공하되 직접적으로 설명하지 않습니다. 서술은 차분하고 절제되어야 하며, 그의 판단과 내면은 독자가 추론할 수 있도록 암시적으로 표현합니다.",
  "knowledge_groups": [
    "north",
    "imperial_military",
    "riena_knights"
  ]
}
```