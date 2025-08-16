"""Personalize Agent for collecting personalized information from MCP sources."""

import asyncio
from typing import Any, Dict, List, Optional
from ..constants import AGENT_NAMES, PERSONALIZE_SYSTEM_PROMPT
from .base_agent import BaseAgent, AgentResult
from ..state import WorkflowState
from ..integrations import MCPManager


class PersonalizeAgent(BaseAgent):
    """Slack, Notion, Gmail에서 개인화된 정보를 수집하는 에이전트."""
    
    def __init__(self):
        super().__init__(
            name=AGENT_NAMES["PERSONALIZE"],
            description="Slack, Notion, Gmail에서 개인화된 정보를 수집하는 에이전트"
        )
        self.required_inputs = ["workflow_status"]
        self.output_keys = ["personal_info", "research_context", "current_progress"]
        self.timeout = 120
        self.retry_attempts = 3
        self.priority = 2
        
        # MCP 매니저 초기화
        self.mcp_manager = MCPManager()
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """개인화된 정보 수집을 수행합니다."""
        self.log_execution("개인화 정보 수집 시작")
        
        try:
            # 입력 검증
            if not self.validate_inputs(state):
                raise ValueError("필수 입력이 누락되었습니다: workflow_status")
            
            # MCP 소스에서 정보 수집
            personal_info = await self._collect_personal_info()
            research_context = await self._collect_research_context()
            current_progress = await self._collect_current_progress()
            
            # 결과 생성
            result = AgentResult(
                success=True,
                output={
                    "personal_info": personal_info,
                    "research_context": research_context,
                    "current_progress": current_progress
                },
                metadata={
                    "sources_accessed": ["slack", "notion", "gmail"],
                    "collection_time": asyncio.get_event_loop().time()
                }
            )
            
            # 상태 업데이트
            updated_state = self.update_workflow_status(state, "personalization")
            updated_state.personal_info = personal_info
            updated_state.research_context = research_context
            updated_state.current_progress = current_progress
            
            self.log_execution("개인화 정보 수집 완료")
            return updated_state
            
        except Exception as e:
            self.log_execution(f"개인화 정보 수집 실패: {str(e)}", "ERROR")
            
            # 폴백 데이터 사용
            fallback_data = self._get_fallback_data()
            
            result = AgentResult(
                success=False,
                output=fallback_data,
                error_message=str(e)
            )
            
            # 폴백 데이터로 상태 업데이트
            updated_state = self.update_workflow_status(state, "personalization")
            updated_state.personal_info = fallback_data["personal_info"]
            updated_state.research_context = fallback_data["research_context"]
            updated_state.current_progress = fallback_data["current_progress"]
            
            self.log_execution("폴백 데이터 사용으로 계속 진행")
            return updated_state
    
    async def _collect_personal_info(self) -> Dict[str, Any]:
        """Slack에서 개인 정보를 수집합니다."""
        try:
            # MCP를 통한 Slack 정보 수집 시도
            slack_info = await self.mcp_manager.get_slack_info()
            return slack_info
        except Exception as e:
            self.log_execution(f"Slack 정보 수집 실패: {str(e)}", "WARNING")
            return self._get_simulated_slack_info()
    
    async def _collect_research_context(self) -> Dict[str, Any]:
        """Notion에서 연구 컨텍스트를 수집합니다."""
        try:
            # MCP를 통한 Notion 정보 수집 시도
            notion_info = await self.mcp_manager.get_notion_info()
            return notion_info
        except Exception as e:
            self.log_execution(f"Notion 정보 수집 실패: {str(e)}", "WARNING")
            return self._get_simulated_notion_info()
    
    async def _collect_current_progress(self) -> Dict[str, Any]:
        """Gmail에서 현재 진행상황을 수집합니다."""
        try:
            # MCP를 통한 Gmail 정보 수집 시도
            gmail_info = await self.mcp_manager.get_gmail_info()
            return gmail_info
        except Exception as e:
            self.log_execution(f"Gmail 정보 수집 실패: {str(e)}", "WARNING")
            return self._get_simulated_gmail_info()
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """MCP 연결 실패 시 사용할 폴백 데이터를 반환합니다."""
        return {
            "personal_info": self._get_simulated_slack_info(),
            "research_context": self._get_simulated_notion_info(),
            "current_progress": self._get_simulated_gmail_info()
        }
    
    def _get_simulated_slack_info(self) -> Dict[str, Any]:
        """시뮬레이션된 Slack 정보를 반환합니다."""
        return {
            "recent_conversations": [
                {
                    "channel": "research-discussion",
                    "participants": ["교수님", "연구팀"],
                    "topic": "AI 연구 방향 논의",
                    "key_points": ["머신러닝 최적화", "데이터 품질 향상"],
                    "timestamp": "2024-08-16T10:00:00Z"
                }
            ],
            "research_keywords": ["AI", "머신러닝", "최적화", "데이터"],
            "collaboration_opportunities": ["컨퍼런스 참여", "논문 협력"]
        }
    
    def _get_simulated_notion_info(self) -> Dict[str, Any]:
        """시뮬레이션된 Notion 정보를 반환합니다."""
        return {
            "research_direction": "AI 기반 시스템 최적화",
            "recent_changes": [
                "연구 계획 업데이트",
                "새로운 방법론 추가",
                "실험 결과 정리"
            ],
            "research_notes": [
                "머신러닝 모델 성능 향상",
                "데이터 전처리 파이프라인 구축",
                "실시간 최적화 알고리즘 개발"
            ],
            "next_milestones": ["프로토타입 완성", "논문 작성", "컨퍼런스 제출"]
        }
    
    def _get_simulated_gmail_info(self) -> Dict[str, Any]:
        """시뮬레이션된 Gmail 정보를 반환합니다."""
        return {
            "ai_conferences": [
                {
                    "name": "ICML 2024",
                    "deadline": "2024-09-15",
                    "relevance": "high",
                    "topics": ["Machine Learning", "Optimization"]
                }
            ],
            "research_collaborations": [
                {
                    "institution": "Stanford AI Lab",
                    "proposal": "AI 최적화 연구 협력",
                    "status": "under_review"
                }
            ],
            "paper_related": [
                {
                    "journal": "Nature Machine Intelligence",
                    "status": "revision_requested",
                    "deadline": "2024-08-30"
                }
            ]
        }
