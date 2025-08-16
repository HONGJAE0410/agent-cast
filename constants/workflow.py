"""Constants for workflow configuration and behavior."""

# 워크플로우 상태
WORKFLOW_STATUS = {
    "INITIALIZING": "initializing",
    "RUNNING": "running",
    "PAUSED": "paused",
    "COMPLETED": "completed",
    "FAILED": "failed",
    "CANCELLED": "cancelled"
}

# 워크플로우 단계
WORKFLOW_STEPS = {
    "ORCHESTRATION": "orchestration",
    "PERSONALIZATION": "personalization",
    "SEARCH": "search",
    "QUERY_WRITING": "query_writing",
    "DB_CONSTRUCTION": "db_construction",
    "RESEARCH": "research",
    "CRITIQUE": "critique",
    "SCRIPT_WRITING": "script_writing",
    "TTS": "tts"
}

# 워크플로우 단계별 설명
WORKFLOW_STEP_DESCRIPTIONS = {
    "orchestration": "오케스트레이션",
    "personalization": "개인화 정보 수집",
    "search": "정보 탐색",
    "query_writing": "쿼리 작성",
    "db_construction": "DB 구축",
    "research": "리서치",
    "critique": "비평",
    "script_writing": "스크립트 작성",
    "tts": "음성 변환"
}

# 워크플로우 단계별 순서
WORKFLOW_STEP_ORDER = [
    "orchestration",
    "personalization",
    "search",
    "query_writing",
    "db_construction",
    "research",
    "critique",
    "script_writing",
    "tts"
]

# 워크플로우 단계별 타임아웃 (초)
WORKFLOW_STEP_TIMEOUTS = {
    "orchestration": 30,
    "personalization": 120,
    "search": 180,
    "query_writing": 60,
    "db_construction": 300,
    "research": 120,
    "critique": 60,
    "script_writing": 90,
    "tts": 180
}

# 워크플로우 단계별 재시도 횟수
WORKFLOW_STEP_RETRIES = {
    "orchestration": 1,
    "personalization": 3,
    "search": 3,
    "query_writing": 2,
    "db_construction": 2,
    "research": 2,
    "critique": 1,
    "script_writing": 2,
    "tts": 2
}

# 워크플로우 실행 모드
WORKFLOW_EXECUTION_MODES = {
    "SEQUENTIAL": "sequential",
    "PARALLEL": "parallel",
    "HYBRID": "hybrid"
}

# 워크플로우 병렬 실행 가능한 단계들
WORKFLOW_PARALLEL_STEPS = [
    ["personalization", "search"]  # 개인화와 탐색은 병렬로 실행 가능
]

# 워크플로우 조건부 실행
WORKFLOW_CONDITIONAL_STEPS = {
    "critique": {
        "condition": "quality_score >= 0.8",
        "on_success": "script_writing",
        "on_failure": "research"  # 품질이 낮으면 리서치 단계로 돌아감
    }
}

# 워크플로우 에러 처리
WORKFLOW_ERROR_HANDLING = {
    "max_retries": 3,
    "retry_delay": 5,  # 초
    "fallback_steps": ["personalization", "search"],
    "error_notification": True
}

# 워크플로우 모니터링
WORKFLOW_MONITORING = {
    "progress_tracking": True,
    "performance_metrics": True,
    "resource_usage": True,
    "logging_level": "INFO"
}

# 워크플로우 결과 저장
WORKFLOW_RESULT_STORAGE = {
    "save_intermediate_results": True,
    "save_final_result": True,
    "result_format": "json",
    "compression": True
}
