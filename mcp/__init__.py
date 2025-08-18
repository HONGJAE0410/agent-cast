"""MCP package for external service connections."""

from .base_mcp import BaseMCP
from .slack_mcp import SlackMCP
from .notion_mcp import NotionMCP
from .gmail_mcp import GmailMCP
from .mcp_manager import MCPManager

__all__ = [
    "BaseMCP",
    "SlackMCP",
    "NotionMCP",
    "GmailMCP",
    "MCPManager"
]
