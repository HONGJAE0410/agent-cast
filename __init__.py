"""Multi-agent workflow system for AI research podcast generation."""

from .agents import (
    OrchestratorAgent,
    PersonalizeAgent,
    QueryWriterAgent,
    SearcherAgent,
    DBConstructorAgent,
    ResearcherAgent,
    CriticAgent,
    ScriptWriterAgent,
    TTSAgent
)

from .integrations import (
    MCPManager,
    SlackMCPIntegration,
    NotionMCPIntegration,
    GmailMCPIntegration
)

from .constants import (
    AGENT_NAMES,
    WORKFLOW_STEPS,
    WORKFLOW_STEP_ORDER,
    MCP_SERVER_TYPES,
    LLM_MODELS,
    EMBEDDING_MODELS,
    VECTOR_DB_PROVIDERS,
    TTS_PROVIDERS,
    QUALITY_THRESHOLDS,
    CHUNKING_CONFIGS,
    PERSONALIZE_SYSTEM_PROMPT,
    QUERY_WRITER_SYSTEM_PROMPT,
    SEARCHER_SYSTEM_PROMPT,
    DB_CONSTRUCTOR_SYSTEM_PROMPT,
    RESEARCHER_SYSTEM_PROMPT,
    CRITIC_SYSTEM_PROMPT,
    SCRIPT_WRITER_SYSTEM_PROMPT,
    TTS_SYSTEM_PROMPT
)

from .orchestrator_graph import main_workflow
from .state import WorkflowState
from .run_workflow import run_workflow, run_step_by_step

__version__ = "1.0.0"
__author__ = "AI Research Team"
__description__ = "Multi-agent workflow system for AI research podcast generation"

__all__ = [
    # Agents
    "OrchestratorAgent",
    "PersonalizeAgent",
    "QueryWriterAgent",
    "SearcherAgent",
    "DBConstructorAgent",
    "ResearcherAgent",
    "CriticAgent",
    "ScriptWriterAgent",
    "TTSAgent",
    
    # Integrations
    "MCPManager",
    "SlackMCPIntegration",
    "NotionMCPIntegration",
    "GmailMCPIntegration",
    
    # Constants
    "AGENT_NAMES",
    "WORKFLOW_STEPS",
    "WORKFLOW_STEP_ORDER",
    "MCP_SERVER_TYPES",
    "LLM_MODELS",
    "EMBEDDING_MODELS",
    "VECTOR_DB_PROVIDERS",
    "TTS_PROVIDERS",
    "QUALITY_THRESHOLDS",
    "CHUNKING_CONFIGS",
    "PERSONALIZE_SYSTEM_PROMPT",
    "QUERY_WRITER_SYSTEM_PROMPT",
    "SEARCHER_SYSTEM_PROMPT",
    "DB_CONSTRUCTOR_SYSTEM_PROMPT",
    "RESEARCHER_SYSTEM_PROMPT",
    "CRITIC_SYSTEM_PROMPT",
    "SCRIPT_WRITER_SYSTEM_PROMPT",
    "TTS_SYSTEM_PROMPT",
    
    # Core components
    "main_workflow",
    "WorkflowState",
    "run_workflow",
    "run_step_by_step"
]
