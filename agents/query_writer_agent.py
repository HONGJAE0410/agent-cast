"""Query Writer Agent for generating RAG search queries."""

from typing import Any, Dict, List
from ..constants import AGENT_NAMES, QUERY_WRITER_SYSTEM_PROMPT
from .base_agent import BaseAgent, AgentResult
from ..state import WorkflowState


class QueryWriterAgent(BaseAgent):
    """개인화된 정보를 바탕으로 RAG 검색 쿼리를 생성하는 에이전트."""
    
    def __init__(self):
        super().__init__(
            name=AGENT_NAMES["QUERY_WRITER"],
            description="개인화된 정보를 바탕으로 RAG 검색 쿼리를 생성하는 에이전트"
        )
        self.required_inputs = ["current_progress", "personal_info", "research_context"]
        self.output_keys = ["rag_query", "search_scope", "research_priorities"]
        self.timeout = 60
        self.retry_attempts = 2
        self.priority = 3
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """RAG 검색 쿼리 생성을 수행합니다."""
        self.log_execution("RAG 검색 쿼리 생성 시작")
        
        try:
            # 입력 검증
            if not self.validate_inputs(state):
                raise ValueError("필수 입력이 누락되었습니다: current_progress, personal_info, research_context")
            
            # 개인화된 정보 분석
            personal_info = state.personal_info
            research_context = state.research_context
            current_progress = state.current_progress
            
            # RAG 쿼리 생성
            rag_query = self._generate_rag_query(personal_info, research_context, current_progress)
            search_scope = self._define_search_scope(personal_info, research_context)
            research_priorities = self._determine_research_priorities(personal_info, research_context)
            
            # 결과 생성
            result = AgentResult(
                success=True,
                output={
                    "rag_query": rag_query,
                    "search_scope": search_scope,
                    "research_priorities": research_priorities
                },
                metadata={
                    "query_generation_method": "rule_based",
                    "personalization_level": "high"
                }
            )
            
            # 상태 업데이트
            updated_state = self.update_workflow_status(state, "query_writing")
            updated_state.rag_query = rag_query
            updated_state.search_scope = search_scope
            updated_state.research_priorities = research_priorities
            
            self.log_execution("RAG 검색 쿼리 생성 완료")
            return updated_state
            
        except Exception as e:
            self.log_execution(f"RAG 검색 쿼리 생성 실패: {str(e)}", "ERROR")
            
            # 기본 쿼리 생성
            fallback_query = self._generate_fallback_query()
            
            result = AgentResult(
                success=False,
                output=fallback_query,
                error_message=str(e)
            )
            
            # 폴백 쿼리로 상태 업데이트
            updated_state = self.update_workflow_status(state, "query_writing")
            updated_state.rag_query = fallback_query["rag_query"]
            updated_state.search_scope = fallback_query["search_scope"]
            updated_state.research_priorities = fallback_query["research_priorities"]
            
            self.log_execution("기본 쿼리 사용으로 계속 진행")
            return updated_state
    
    def _generate_rag_query(self, personal_info: Dict, research_context: Dict, current_progress: Dict) -> Dict[str, Any]:
        """개인화된 정보를 바탕으로 RAG 쿼리를 생성합니다."""
        # Slack에서 수집된 키워드 활용
        research_keywords = personal_info.get("research_keywords", [])
        
        # Notion에서 수집된 연구 방향 활용
        research_direction = research_context.get("research_direction", "")
        
        # Gmail에서 수집된 컨퍼런스 정보 활용
        conferences = current_progress.get("ai_conferences", [])
        
        # 쿼리 구성
        primary_queries = [
            f"{research_direction} 최신 연구 동향",
            f"{' '.join(research_keywords)} 최신 논문",
            "AI 최적화 알고리즘 발전 방향",
            "머신러닝 성능 향상 기법"
        ]
        
        secondary_queries = [
            "AI 연구 컨퍼런스 2024",
            "머신러닝 최적화 논문",
            "데이터 품질 향상 방법",
            "실시간 AI 시스템 최적화"
        ]
        
        return {
            "primary_queries": primary_queries,
            "secondary_queries": secondary_queries,
            "keywords": research_keywords,
            "research_area": research_direction,
            "conference_focus": [conf["name"] for conf in conferences if conf.get("relevance") == "high"]
        }
    
    def _define_search_scope(self, personal_info: Dict, research_context: Dict) -> Dict[str, Any]:
        """검색 범위를 정의합니다."""
        return {
            "time_range": "2023-2024",  # 최근 2년
            "sources": [
                "arxiv.org",
                "papers.ssrn.com",
                "scholar.google.com",
                "ieee.org",
                "acm.org"
            ],
            "languages": ["en", "ko"],
            "document_types": ["research_paper", "conference_proceedings", "technical_report"],
            "priority_sources": ["arxiv.org", "ieee.org"]  # 우선 검색할 소스
        }
    
    def _determine_research_priorities(self, personal_info: Dict, research_context: Dict) -> List[Dict[str, Any]]:
        """연구 우선순위를 결정합니다."""
        priorities = []
        
        # Slack 대화에서 파악된 우선순위
        conversations = personal_info.get("recent_conversations", [])
        for conv in conversations:
            if "key_points" in conv:
                for point in conv["key_points"]:
                    priorities.append({
                        "topic": point,
                        "priority": "high",
                        "source": "slack_conversation",
                        "deadline": None
                    })
        
        # Notion 연구 노트에서 파악된 우선순위
        research_notes = research_context.get("research_notes", [])
        for note in research_notes:
            priorities.append({
                "topic": note,
                "priority": "medium",
                "source": "notion_research_notes",
                "deadline": None
            })
        
        # Gmail 컨퍼런스 정보에서 파악된 우선순위
        conferences = personal_info.get("ai_conferences", [])
        for conf in conferences:
            if conf.get("relevance") == "high":
                priorities.append({
                    "topic": f"{conf['name']} 준비",
                    "priority": "high",
                    "source": "gmail_conference",
                    "deadline": conf.get("deadline")
                })
        
        # 우선순위별 정렬
        priority_order = {"high": 1, "medium": 2, "low": 3}
        priorities.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        return priorities
    
    def _generate_fallback_query(self) -> Dict[str, Any]:
        """기본 쿼리를 생성합니다."""
        return {
            "rag_query": {
                "primary_queries": ["AI 연구 동향 2024", "머신러닝 최신 기법"],
                "secondary_queries": ["AI 최적화 알고리즘", "데이터 품질 향상"],
                "keywords": ["AI", "머신러닝", "최적화"],
                "research_area": "AI 기반 시스템 최적화",
                "conference_focus": []
            },
            "search_scope": {
                "time_range": "2023-2024",
                "sources": ["arxiv.org", "ieee.org"],
                "languages": ["en"],
                "document_types": ["research_paper"],
                "priority_sources": ["arxiv.org"]
            },
            "research_priorities": [
                {
                    "topic": "AI 연구 동향 파악",
                    "priority": "high",
                    "source": "fallback",
                    "deadline": None
                }
            ]
        }
