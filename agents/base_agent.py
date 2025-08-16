"""Base agent class for the multi-agent workflow system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages

from ..state import WorkflowState


@dataclass
class AgentResult:
    """에이전트 실행 결과를 나타내는 데이터 클래스."""
    success: bool
    output: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class BaseAgent(ABC):
    """모든 에이전트의 기본 클래스."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.required_inputs: List[str] = []
        self.output_keys: List[str] = []
        self.timeout: int = 60
        self.retry_attempts: int = 1
        self.priority: int = 1
    
    @abstractmethod
    async def process(self, state: WorkflowState) -> WorkflowState:
        """에이전트의 주요 처리 로직을 구현합니다."""
        pass
    
    def validate_inputs(self, state: WorkflowState) -> bool:
        """필수 입력이 있는지 검증합니다."""
        for required_input in self.required_inputs:
            if not hasattr(state, required_input) or getattr(state, required_input) is None:
                return False
        return True
    
    def prepare_output(self, result: AgentResult) -> Dict[str, Any]:
        """에이전트 결과를 워크플로우 상태에 맞게 준비합니다."""
        output = {}
        for key in self.output_keys:
            if key in result.output:
                output[key] = result.output[key]
        return output
    
    def update_workflow_status(self, state: WorkflowState, step_name: str) -> WorkflowState:
        """워크플로우 상태를 업데이트합니다."""
        if not hasattr(state, 'workflow_status'):
            return state
        
        workflow_status = state.workflow_status.copy()
        workflow_status["current_step"] = step_name
        workflow_status["completed_steps"] += 1
        
        # 상태 업데이트
        return WorkflowState(
            **{k: v for k, v in state.__dict__.items() if k != 'workflow_status'},
            workflow_status=workflow_status
        )
    
    def log_execution(self, message: str, level: str = "INFO"):
        """에이전트 실행 로그를 기록합니다."""
        print(f"[{self.name}] {level}: {message}")
    
    def get_agent_info(self) -> Dict[str, Any]:
        """에이전트 정보를 반환합니다."""
        return {
            "name": self.name,
            "description": self.description,
            "required_inputs": self.required_inputs,
            "output_keys": self.output_keys,
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts,
            "priority": self.priority
        }
