"""Base MCP integration class for external service connections."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import asyncio
import logging

from constants.mcp import MCP_CONNECTION_STATUS, MCP_ERROR_CODES


@dataclass
class MCPConnectionInfo:
    """MCP 연결 정보를 나타내는 데이터 클래스."""
    server_type: str
    status: str
    last_connected: Optional[str] = None
    error_count: int = 0
    last_error: Optional[str] = None


class BaseMCP(ABC):
    """모든 MCP 서비스의 기본 클래스."""
    
    def __init__(self, server_type: str, config: Dict[str, Any]):
        self.server_type = server_type
        self.config = config
        self.connection_info = MCPConnectionInfo(
            server_type=server_type,
            status=MCP_CONNECTION_STATUS["DISCONNECTED"]
        )
        self.logger = logging.getLogger(f"mcp.{server_type}")
        
        # 연결 설정
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 1.0)
        self.timeout = config.get("timeout", 30)
    
    @abstractmethod
    async def connect(self) -> bool:
        """MCP 서버에 연결합니다."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """MCP 서버 연결을 해제합니다."""
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """연결 상태를 확인합니다."""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """서버 상태를 확인합니다."""
        pass
    
    def get_connection_status(self) -> MCPConnectionInfo:
        """현재 연결 상태를 반환합니다."""
        return self.connection_info
    
    def update_connection_status(self, status: str, error: Optional[str] = None):
        """연결 상태를 업데이트합니다."""
        self.connection_info.status = status
        
        if status == MCP_CONNECTION_STATUS["CONNECTED"]:
            self.connection_info.last_connected = self._get_current_timestamp()
            self.connection_info.error_count = 0
            self.connection_info.last_error = None
        elif status == MCP_CONNECTION_STATUS["FAILED"]:
            self.connection_info.error_count += 1
            self.connection_info.last_error = error
    
    async def execute_with_retry(self, operation, *args, **kwargs) -> Any:
        """재시도 로직을 포함하여 작업을 실행합니다."""
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if not await self.is_connected():
                    await self.connect()
                
                result = await operation(*args, **kwargs)
                self.update_connection_status(MCP_CONNECTION_STATUS["CONNECTED"])
                return result
                
            except Exception as e:
                last_error = str(e)
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # 지수 백오프
                else:
                    self.update_connection_status(MCP_CONNECTION_STATUS["FAILED"], str(e))
                    raise e
        
        # 모든 재시도 실패
        raise Exception(f"Operation failed after {self.max_retries} retries. Last error: {last_error}")
    
    def _get_current_timestamp(self) -> str:
        """현재 타임스탬프를 반환합니다."""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def _validate_config(self, required_keys: List[str]) -> bool:
        """설정의 필수 키가 있는지 검증합니다."""
        for key in required_keys:
            if key not in self.config:
                self.logger.error(f"Missing required config key: {key}")
                return False
        return True
    
    def _log_operation(self, operation: str, success: bool, details: Optional[str] = None):
        """작업 로그를 기록합니다."""
        level = logging.INFO if success else logging.ERROR
        message = f"Operation '{operation}' {'succeeded' if success else 'failed'}"
        if details:
            message += f": {details}"
        
        self.logger.log(level, message)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """에러 요약을 반환합니다."""
        return {
            "server_type": self.server_type,
            "status": self.connection_info.status,
            "error_count": self.connection_info.error_count,
            "last_error": self.connection_info.last_error,
            "last_connected": self.connection_info.last_connected
        }
