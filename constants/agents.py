"""Constants for agent configuration and behavior."""

# 에이전트 이름
AGENT_NAMES = {
    "ORCHESTRATOR": "orchestrator",
    "PERSONALIZE": "personalize",
    "QUERY_WRITER": "query_writer",
    "SEARCHER": "searcher",
    "DB_CONSTRUCTOR": "db_constructor",
    "RESEARCHER": "researcher",
    "CRITIC": "critic",
    "SCRIPT_WRITER": "script_writer",
    "TTS": "tts"
}

# 에이전트 실행 순서
AGENT_EXECUTION_ORDER = [
    "orchestrator",
    "personalize",
    "searcher",
    "query_writer",
    "db_constructor",
    "researcher",
    "critic",
    "script_writer",
    "tts"
]

# 에이전트별 타임아웃 (초)
AGENT_TIMEOUTS = {
    "orchestrator": 30,
    "personalize": 120,  # MCP 통합으로 인해 더 긴 시간
    "query_writer": 60,
    "searcher": 180,  # 웹 크롤링으로 인해 더 긴 시간
    "db_constructor": 300,  # 벡터 DB 구축으로 인해 더 긴 시간
    "researcher": 120,
    "critic": 60,
    "script_writer": 90,
    "tts": 180  # 음성 생성으로 인해 더 긴 시간
}

# 에이전트별 재시도 횟수
AGENT_RETRY_ATTEMPTS = {
    "orchestrator": 1,
    "personalize": 3,  # MCP 연결 실패 시 재시도
    "query_writer": 2,
    "searcher": 3,  # 네트워크 오류 시 재시도
    "db_constructor": 2,
    "researcher": 2,
    "critic": 1,
    "script_writer": 2,
    "tts": 2
}

# 에이전트별 우선순위
AGENT_PRIORITIES = {
    "orchestrator": 1,
    "personalize": 2,
    "searcher": 2,
    "query_writer": 3,
    "db_constructor": 3,
    "researcher": 4,
    "critic": 5,
    "script_writer": 6,
    "tts": 7
}

# 에이전트별 필수 입력
AGENT_REQUIRED_INPUTS = {
    "orchestrator": ["user_query"],
    "personalize": ["workflow_status"],
    "query_writer": ["current_progress", "personal_info", "research_context"],
    "searcher": ["workflow_status"],
    "db_constructor": ["data_chunks", "search_scope"],
    "researcher": ["rag_query", "vector_db"],
    "critic": ["research_results"],
    "script_writer": ["research_results", "approval_status"],
    "tts": ["podcast_script", "script_metadata"]
}

# 에이전트별 출력 키
AGENT_OUTPUT_KEYS = {
    "orchestrator": ["workflow_status", "next_agents"],
    "personalize": ["personal_info", "research_context", "current_progress"],
    "query_writer": ["rag_query", "search_scope", "research_priorities"],
    "searcher": ["crawled_data", "search_sources", "data_chunks"],
    "db_constructor": ["vector_db", "embedding_stats", "db_metadata"],
    "researcher": ["research_results", "search_strategy", "rag_metrics"],
    "critic": ["critic_feedback", "approval_status", "quality_score"],
    "script_writer": ["podcast_script", "script_metadata", "conversation_flow"],
    "tts": ["audio_file", "tts_metadata", "voice_quality"]
}

# 에이전트별 설명
AGENT_DESCRIPTIONS = {
    "orchestrator": "전체 워크플로우를 조정하고 다음 단계를 결정하는 에이전트",
    "personalize": "Slack, Notion, Gmail에서 개인화된 정보를 수집하는 에이전트",
    "query_writer": "개인화된 정보를 바탕으로 RAG 검색 쿼리를 생성하는 에이전트",
    "searcher": "웹 크롤링을 통해 최신 AI 연구 정보를 수집하는 에이전트",
    "db_constructor": "수집된 정보를 벡터 데이터베이스로 구축하는 에이전트",
    "researcher": "RAG 시스템을 통해 정보를 검색하고 분석하는 에이전트",
    "critic": "연구 결과의 품질을 평가하고 검토하는 에이전트",
    "script_writer": "연구 결과를 팟캐스트 대본으로 변환하는 에이전트",
    "tts": "팟캐스트 대본을 자연스러운 음성으로 변환하는 에이전트"
}
