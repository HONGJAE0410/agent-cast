"""State management for the router graph.

This module defines the state structures and reduction functions used in the
router graph.

"""

from dataclasses import dataclass, field
from typing import Annotated, Sequence, Dict, Any, List, Optional

from langchain_core.documents import Document
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages

#########################  Router Builder State  ###############################


@dataclass(kw_only=True)
class BuilderState:
    status: str = field(
        default="refresh",
        metadata={
            "description": "The status of the builder state.",
        },
    )


#############################  Router State  ###################################


# Optional, the InputState is a restricted version of the State that is used to
# define a narrower interface to the outside world vs. what is maintained
# internally.
@dataclass(kw_only=True)
class InputState:
    """Represents the input state for the agent.

    This class defines the structure of the input state, which includes
    the messages exchanged between the user and the agent. It serves as
    a restricted version of the full State, providing a narrower interface
    to the outside world compared to what is maintained internally.
    """

    messages: Annotated[Sequence[AnyMessage], add_messages]
    """Messages track the primary execution state of the agent.

    Typically accumulates a pattern of Human/AI/Human/AI messages; if
    you were to combine this template with a tool-calling ReAct agent pattern,
    it may look like this:

    1. HumanMessage - user input
    2. AIMessage with .tool_calls - agent picking tool(s) to use to collect
         information
    3. ToolMessage(s) - the responses (or errors) from the executed tools
    
        (... repeat steps 2 and 3 as needed ...)
    4. AIMessage without .tool_calls - agent responding in unstructured
        format to the user.

    5. HumanMessage - user responds with the next conversational turn.

        (... repeat steps 2-5 as needed ... )
    
    Merges two lists of messages, updating existing messages by ID.

    By default, this ensures the state is "append-only", unless the
    new message has the same ID as an existing message.

    Returns:
        A new list of messages with the messages from `right` merged into `left`.
        If a message in `right` has the same ID as a message in `left`, the
        message from `right` will replace the message from `left`."""


# This is the primary state of your agent, where you can store any information


def add_queries(existing: Sequence[str], new: Sequence[str]) -> Sequence[str]:
    """Combine existing queries with new queries.

    Args:
        existing (Sequence[str]): The current list of queries in the state.
        new (Sequence[str]): The new queries to be added.

    Returns:
        Sequence[str]: A new list containing all queries from both input sequences.
    """
    return list(existing) + list(new)


@dataclass(kw_only=True)
class State(InputState):
    """The state of your graph / agent."""

    queries: Annotated[list[str], add_queries] = field(default_factory=list)
    """A list of search queries that the agent has generated."""

    retrieved_docs: list[Document] = field(default_factory=list)
    """Populated by the retriever. This is a list of documents that the agent can reference."""

    current_mcp_server: str = field(default="")

    current_tool: dict[str, str] = field(default_factory=dict)

    summarized_memory: str = field(
        default="",
        metadata={"description": "Persistent conversation memory."}
    )


#############################  Multi-Agent Workflow State  #####################


@dataclass
class WorkflowState:
    """멀티 에이전트 워크플로우의 상태를 관리하는 클래스."""
    
    # 기본 정보
    user_query: str = ""
    topic: str = ""
    target_audience: str = ""
    
    # 개인화 정보
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    user_context: Dict[str, Any] = field(default_factory=dict)
    
    # 쿼리 및 검색
    search_queries: List[str] = field(default_factory=list)
    search_results: List[Dict[str, Any]] = field(default_factory=list)
    
    # 데이터베이스 및 연구
    vector_db_data: List[Dict[str, Any]] = field(default_factory=list)
    research_results: List[Dict[str, Any]] = field(default_factory=list)
    
    # 품질 검토
    quality_scores: Dict[str, float] = field(default_factory=dict)
    quality_feedback: List[str] = field(default_factory=list)
    
    # 최종 결과
    final_script: str = ""
    audio_file_path: str = ""
    
    # 워크플로우 상태
    workflow_status: Dict[str, Any] = field(default_factory=lambda: {
        "current_step": "initialized",
        "completed_steps": 0,
        "total_steps": 8,
        "status": "running",
        "errors": [],
        "warnings": []
    })
    
    # 메타데이터
    execution_start_time: Optional[float] = None
    execution_end_time: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_step(self, step_name: str, **kwargs):
        """워크플로우 단계를 업데이트합니다."""
        self.workflow_status["current_step"] = step_name
        self.workflow_status["completed_steps"] += 1
        
        # 추가 데이터 업데이트
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def add_error(self, error_message: str):
        """에러를 추가합니다."""
        self.workflow_status["errors"].append(error_message)
    
    def add_warning(self, warning_message: str):
        """경고를 추가합니다."""
        self.workflow_status["warnings"].append(warning_message)
    
    def is_complete(self) -> bool:
        """워크플로우가 완료되었는지 확인합니다."""
        return self.workflow_status["completed_steps"] >= self.workflow_status["total_steps"]
    
    def get_progress(self) -> float:
        """진행률을 반환합니다 (0.0 ~ 1.0)."""
        return self.workflow_status["completed_steps"] / self.workflow_status["total_steps"]
