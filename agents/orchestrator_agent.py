"""Orchestrator Agent for coordinating the multi-agent workflow."""

from typing import Any, Dict, List
from ..constants import AGENT_NAMES, WORKFLOW_STEP_ORDER
from .base_agent import BaseAgent, AgentResult
from ..state import WorkflowState


class OrchestratorAgent(BaseAgent):
    """전체 워크플로우를 조정하고 다음 단계를 결정하는 에이전트."""
    
    def __init__(self):
        super().__init__(
            name=AGENT_NAMES["ORCHESTRATOR"],
            description="전체 워크플로우를 조정하고 다음 단계를 결정하는 에이전트"
        )
        self.required_inputs = ["user_query"]
        self.output_keys = ["workflow_status", "next_agents"]
        self.timeout = 30
        self.retry_attempts = 1
        self.priority = 1
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """워크플로우 오케스트레이션을 수행합니다."""
        self.log_execution("워크플로우 오케스트레이션 시작")
        
        try:
            # 입력 검증
            if not self.validate_inputs(state):
                raise ValueError("필수 입력이 누락되었습니다: user_query")
            
            # 워크플로우 상태 초기화
            workflow_status = {
                "status": "running",
                "current_step": "orchestration",
                "total_steps": len(WORKFLOW_STEP_ORDER),
                "completed_steps": 0,
                "start_timestamp": state.workflow_status.get("start_timestamp"),
                "current_timestamp": state.workflow_status.get("start_timestamp")
            }
            
            # 다음 실행할 에이전트들 결정
            next_agents = self._determine_next_agents(state)
            
            # 결과 생성
            result = AgentResult(
                success=True,
                output={
                    "workflow_status": workflow_status,
                    "next_agents": next_agents
                },
                metadata={
                    "total_steps": len(WORKFLOW_STEP_ORDER),
                    "step_order": WORKFLOW_STEP_ORDER
                }
            )
            
            # 상태 업데이트
            updated_state = self.update_workflow_status(state, "orchestration")
            updated_state.workflow_status = workflow_status
            updated_state.next_agents = next_agents
            
            self.log_execution(f"오케스트레이션 완료. 다음 에이전트: {next_agents}")
            return updated_state
            
        except Exception as e:
            self.log_execution(f"오케스트레이션 실패: {str(e)}", "ERROR")
            result = AgentResult(
                success=False,
                output={},
                error_message=str(e)
            )
            
            # 에러 상태로 업데이트
            workflow_status = state.workflow_status.copy()
            workflow_status["status"] = "failed"
            workflow_status["error"] = str(e)
            
            updated_state = self.update_workflow_status(state, "orchestration")
            updated_state.workflow_status = workflow_status
            return updated_state
    
    def _determine_next_agents(self, state: WorkflowState) -> List[str]:
        """다음에 실행할 에이전트들을 결정합니다."""
        # 기본적으로 개인화와 탐색을 병렬로 실행
        next_agents = [
            AGENT_NAMES["PERSONALIZE"],
            AGENT_NAMES["SEARCHER"]
        ]
        
        # 사용자 쿼리에 따라 우선순위 조정
        user_query = state.user_query.lower()
        
        if "최신" in user_query or "trend" in user_query:
            # 최신 동향이 중요하면 탐색을 우선
            next_agents = [
                AGENT_NAMES["SEARCHER"],
                AGENT_NAMES["PERSONALIZE"]
            ]
        elif "개인" in user_query or "personal" in user_query:
            # 개인화가 중요하면 개인화를 우선
            next_agents = [
                AGENT_NAMES["PERSONALIZE"],
                AGENT_NAMES["SEARCHER"]
            ]
        
        return next_agents
