"""MCP Manager for coordinating multiple MCP integrations."""

import asyncio
from typing import Any, Dict, List, Optional
from .base_mcp_integration import BaseMCPIntegration
from .slack_mcp_integration import SlackMCPIntegration
from .notion_mcp_integration import NotionMCPIntegration
from .gmail_mcp_integration import GmailMCPIntegration


class MCPManager:
    """여러 MCP 통합을 조정하는 매니저 클래스."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.integrations: Dict[str, BaseMCPIntegration] = {}
        self.connection_status: Dict[str, str] = {}
        
        # 기본 통합 초기화
        self._initialize_integrations()
    
    def _initialize_integrations(self):
        """MCP 통합들을 초기화합니다."""
        # Slack 통합
        slack_config = self.config.get("slack", {})
        self.integrations["slack"] = SlackMCPIntegration(slack_config)
        
        # Notion 통합
        notion_config = self.config.get("notion", {})
        self.integrations["notion"] = NotionMCPIntegration(notion_config)
        
        # Gmail 통합
        gmail_config = self.config.get("gmail", {})
        self.integrations["gmail"] = GmailMCPIntegration(gmail_config)
    
    async def connect_all(self) -> Dict[str, bool]:
        """모든 MCP 통합에 연결합니다."""
        results = {}
        
        for name, integration in self.integrations.items():
            try:
                success = await integration.connect()
                results[name] = success
                self.connection_status[name] = "connected" if success else "failed"
            except Exception as e:
                results[name] = False
                self.connection_status[name] = "failed"
                print(f"Failed to connect to {name}: {e}")
        
        return results
    
    async def disconnect_all(self) -> Dict[str, bool]:
        """모든 MCP 통합 연결을 해제합니다."""
        results = {}
        
        for name, integration in self.integrations.items():
            try:
                success = await integration.disconnect()
                results[name] = success
                self.connection_status[name] = "disconnected" if success else "failed"
            except Exception as e:
                results[name] = False
                print(f"Failed to disconnect from {name}: {e}")
        
        return results
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """모든 MCP 통합의 상태를 확인합니다."""
        results = {}
        
        for name, integration in self.integrations.items():
            try:
                health = await integration.health_check()
                results[name] = health
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "message": f"Health check failed: {str(e)}",
                    "timestamp": self._get_current_timestamp()
                }
        
        return results
    
    def get_integration(self, name: str) -> Optional[BaseMCPIntegration]:
        """지정된 이름의 MCP 통합을 반환합니다."""
        return self.integrations.get(name)
    
    def get_connection_status(self) -> Dict[str, str]:
        """모든 통합의 연결 상태를 반환합니다."""
        return self.connection_status.copy()
    
    async def is_any_connected(self) -> bool:
        """하나라도 연결된 통합이 있는지 확인합니다."""
        for integration in self.integrations.values():
            if await integration.is_connected():
                return True
        return False
    
    # Slack 관련 메서드들
    async def get_slack_info(self) -> Dict[str, Any]:
        """Slack 정보를 가져옵니다."""
        slack_integration = self.integrations.get("slack")
        if not slack_integration:
            raise ValueError("Slack integration not available")
        
        try:
            # 워크스페이스 정보
            workspace_info = await slack_integration.get_workspace_info()
            
            # 채널 정보
            channels = await slack_integration.get_channels()
            
            # 최근 활동
            recent_activity = await slack_integration.get_recent_activity()
            
            # AI 연구 관련 메시지 검색
            ai_messages = await slack_integration.search_messages("AI research optimization")
            
            return {
                "workspace_info": workspace_info,
                "channels": channels,
                "recent_activity": recent_activity,
                "ai_research_messages": ai_messages,
                "connection_status": await slack_integration.is_connected()
            }
            
        except Exception as e:
            print(f"Failed to get Slack info: {e}")
            # 폴백 데이터 반환
            return self._get_fallback_slack_info()
    
    def _get_fallback_slack_info(self) -> Dict[str, Any]:
        """Slack 연결 실패 시 사용할 폴백 데이터를 반환합니다."""
        return {
            "workspace_info": {
                "workspace_name": "AI Research Team (Fallback)",
                "member_count": 25,
                "status": "fallback"
            },
            "channels": [
                {
                    "name": "research-discussion",
                    "topic": "AI 연구 논의 및 아이디어 공유",
                    "member_count": 15
                }
            ],
            "recent_activity": {
                "total_messages": 45,
                "active_channels": 3,
                "trending_topics": ["AI 최적화", "동적 배칭", "머신러닝 성능"]
            },
            "ai_research_messages": [
                {
                    "text": "AI 최적화 알고리즘에 대한 논의가 정말 흥미로웠어요.",
                    "channel": "research-discussion",
                    "timestamp": "2024-08-16T09:30:00Z"
                }
            ],
            "connection_status": False
        }
    
    # Notion 관련 메서드들
    async def get_notion_info(self) -> Dict[str, Any]:
        """Notion 정보를 가져옵니다."""
        notion_integration = self.integrations.get("notion")
        if not notion_integration:
            raise ValueError("Notion integration not available")
        
        try:
            # 워크스페이스 정보
            workspace_info = await notion_integration.get_workspace_info()
            
            # 데이터베이스 정보
            databases = await notion_integration.get_databases()
            
            # AI 연구 관련 페이지 검색
            ai_pages = await notion_integration.search_pages("AI research")
            
            # 최근 변경사항
            recent_changes = await notion_integration.get_recent_changes()
            
            return {
                "workspace_info": workspace_info,
                "databases": databases,
                "ai_research_pages": ai_pages,
                "recent_changes": recent_changes,
                "connection_status": await notion_integration.is_connected()
            }
            
        except Exception as e:
            print(f"Failed to get Notion info: {e}")
            # 폴백 데이터 반환
            return self._get_fallback_notion_info()
    
    def _get_fallback_notion_info(self) -> Dict[str, Any]:
        """Notion 연결 실패 시 사용할 폴백 데이터를 반환합니다."""
        return {
            "workspace_info": {
                "workspace_name": "AI Research Workspace (Fallback)",
                "member_count": 15,
                "status": "fallback"
            },
            "databases": [
                {
                    "title": "AI Research Projects",
                    "description": "AI 연구 프로젝트 관리",
                    "last_edited": "2024-08-16T10:00:00Z"
                }
            ],
            "ai_research_pages": [
                {
                    "title": "AI 연구 방향 및 계획",
                    "last_edited": "2024-08-16T10:00:00Z",
                    "status": "fallback"
                }
            ],
            "recent_changes": [
                {
                    "page_title": "AI 연구 방향 및 계획",
                    "change_type": "content_updated",
                    "timestamp": "2024-08-16T10:00:00Z"
                }
            ],
            "connection_status": False
        }
    
    # Gmail 관련 메서드들
    async def get_gmail_info(self) -> Dict[str, Any]:
        """Gmail 정보를 가져옵니다."""
        gmail_integration = self.integrations.get("gmail")
        if not gmail_integration:
            raise ValueError("Gmail integration not available")
        
        try:
            # 프로필 정보
            profile_info = await gmail_integration.get_profile_info()
            
            # 라벨 정보
            labels = await gmail_integration.get_labels()
            
            # AI 연구 관련 메시지 검색
            ai_messages = await gmail_integration.search_messages("AI research")
            
            # 컨퍼런스 관련 메시지 검색
            conference_messages = await gmail_integration.search_messages("conference")
            
            # 최근 활동
            recent_activity = await gmail_integration.get_recent_activity()
            
            return {
                "profile_info": profile_info,
                "labels": labels,
                "ai_research_messages": ai_messages,
                "conference_messages": conference_messages,
                "recent_activity": recent_activity,
                "connection_status": await gmail_integration.is_connected()
            }
            
        except Exception as e:
            print(f"Failed to get Gmail info: {e}")
            # 폴백 데이터 반환
            return self._get_fallback_gmail_info()
    
    def _get_fallback_gmail_info(self) -> Dict[str, Any]:
        """Gmail 연결 실패 시 사용할 폴백 데이터를 반환합니다."""
        return {
            "profile_info": {
                "email_address": "ai.researcher@gmail.com",
                "name": "AI Researcher (Fallback)",
                "messages_total": 15420,
                "status": "fallback"
            },
            "labels": [
                {
                    "name": "AI Research",
                    "messagesTotal": 234,
                    "messagesUnread": 12
                }
            ],
            "ai_research_messages": [
                {
                    "snippet": "AI 연구 논의를 위한 미팅 일정 조율",
                    "labelIds": ["INBOX", "Label_1234567890"]
                }
            ],
            "conference_messages": [
                {
                    "snippet": "ICML 2024 컨퍼런스 참가 등록 마감일 안내",
                    "labelIds": ["INBOX", "Label_1234567891"]
                }
            ],
            "recent_activity": {
                "total_messages": 45,
                "trending_topics": ["AI Research", "Conference Registration"]
            },
            "connection_status": False
        }
    
    async def get_all_info(self) -> Dict[str, Any]:
        """모든 MCP 통합에서 정보를 가져옵니다."""
        try:
            # 병렬로 모든 정보 수집
            tasks = [
                self.get_slack_info(),
                self.get_notion_info(),
                self.get_gmail_info()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return {
                "slack": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
                "notion": results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])},
                "gmail": results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])},
                "overall_status": {
                    "total_integrations": len(self.integrations),
                    "connected_count": sum(1 for status in self.connection_status.values() if status == "connected"),
                    "connection_status": self.connection_status
                }
            }
            
        except Exception as e:
            print(f"Failed to get all info: {e}")
            return {
                "error": f"Failed to collect information: {str(e)}",
                "overall_status": {
                    "total_integrations": len(self.integrations),
                    "connected_count": 0,
                    "connection_status": self.connection_status
                }
            }
    
    def _get_current_timestamp(self) -> str:
        """현재 타임스탬프를 반환합니다."""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def get_summary(self) -> Dict[str, Any]:
        """MCP 매니저의 요약 정보를 반환합니다."""
        return {
            "total_integrations": len(self.integrations),
            "integration_names": list(self.integrations.keys()),
            "connection_status": self.connection_status,
            "config_keys": list(self.config.keys()) if self.config else []
        }
