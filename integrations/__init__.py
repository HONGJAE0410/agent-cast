"""Integrations package for MCP and external service connections."""

from .base_mcp_integration import BaseMCPIntegration
from .slack_mcp_integration import SlackMCPIntegration
from .notion_mcp_integration import NotionMCPIntegration
from .gmail_mcp_integration import GmailMCPIntegration
from .mcp_manager import MCPManager

__all__ = [
    "BaseMCPIntegration",
    "SlackMCPIntegration",
    "NotionMCPIntegration",
    "GmailMCPIntegration",
    "MCPManager"
]
