"""Constants for MCP (Model Context Protocol) integration."""

from typing import Any, Dict, Literal

# MCP 서버 타입
MCP_SERVER_TYPES = {
    "SLACK": "slack",
    "NOTION": "notion",
    "GMAIL": "gmail",
    "GITHUB": "github",
    "CALENDAR": "calendar"
}

# MCP 연결 상태
MCP_CONNECTION_STATUS = {
    "CONNECTED": "connected",
    "DISCONNECTED": "disconnected",
    "CONNECTING": "connecting",
    "FAILED": "failed",
    "TIMEOUT": "timeout"
}

# MCP 에러 코드
MCP_ERROR_CODES = {
    "CONNECTION_FAILED": "connection_failed",
    "AUTHENTICATION_FAILED": "authentication_failed",
    "PERMISSION_DENIED": "permission_denied",
    "RATE_LIMIT_EXCEEDED": "rate_limit_exceeded",
    "SERVER_UNAVAILABLE": "server_unavailable",
    "TIMEOUT": "timeout",
    "UNKNOWN_ERROR": "unknown_error"
}

# MCP 재시도 전략
MCP_RETRY_STRATEGY = {
    "max_attempts": 3,
    "base_delay": 1.0,  # 초
    "max_delay": 30.0,  # 초
    "exponential_backoff": True,
    "jitter": True
}

# MCP 연결 풀 설정
MCP_CONNECTION_POOL = {
    "max_connections": 10,
    "min_connections": 2,
    "connection_timeout": 30,
    "idle_timeout": 300,
    "max_lifetime": 3600
}

# MCP 헬스체크 설정
MCP_HEALTH_CHECK = {
    "enabled": True,
    "interval": 300,  # 5분
    "timeout": 10,
    "max_failures": 3
}

# MCP 로깅 설정
MCP_LOGGING = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "mcp.log",
    "max_file_size": "10MB",
    "backup_count": 5
}

# MCP 보안 설정
MCP_SECURITY = {
    "enable_ssl": True,
    "verify_certificates": True,
    "allowed_origins": ["localhost", "127.0.0.1"],
    "max_request_size": "10MB"
}

# MCP 성능 설정
MCP_PERFORMANCE = {
    "request_timeout": 60,
    "max_response_size": "10MB",
    "compression_enabled": True,
    "caching_enabled": True,
    "cache_ttl": 300
}
