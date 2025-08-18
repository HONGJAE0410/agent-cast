"""Configuration constants for the multi-agent workflow system."""

from .ai_models import (
    OPENAI_MODELS,
    ANTHROPIC_MODELS,
    GOOGLE_MODELS,
    EMBEDDING_MODELS,
    TTS_MODELS,
    VECTOR_DB_PROVIDERS,
    VECTOR_DB_CONFIGS,
    WEB_CRAWLING_TOOLS,
    WEB_CRAWLING_CONFIGS,
    QUALITY_WEIGHTS
)

# LLM 모델 통합 (누락된 상수 추가)
LLM_MODELS = {
    **OPENAI_MODELS,
    **ANTHROPIC_MODELS,
    **GOOGLE_MODELS
}

# TTS 제공자 (누락된 상수 추가)
TTS_PROVIDERS = {
    "OPENAI": "openai",
    "ELEVENLABS": "elevenlabs",
    "GOOGLE": "google",
    "AZURE": "azure"
}

# 청킹 설정
CHUNKING_CONFIGS = {
    "default": {
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "separators": ["\n\n", "\n", ". ", "! ", "? "],
        "min_chunk_size": 100,
        "max_chunk_size": 2000
    },
    "research_papers": {
        "chunk_size": 800,
        "chunk_overlap": 150,
        "separators": ["\n\n", "\n", ". ", "! ", "? "],
        "min_chunk_size": 200,
        "max_chunk_size": 1500
    },
    "news_articles": {
        "chunk_size": 600,
        "chunk_overlap": 100,
        "separators": ["\n\n", "\n", ". ", "! ", "? "],
        "min_chunk_size": 150,
        "max_chunk_size": 1200
    }
}

# 품질 임계값
QUALITY_THRESHOLDS = {
    "minimum_quality_score": 0.7,
    "excellent_quality_score": 0.9,
    "factual_accuracy_threshold": 0.8,
    "source_verification_threshold": 0.75,
    "logical_consistency_threshold": 0.8,
    "data_freshness_threshold": 0.6,
    "completeness_threshold": 0.7
}

# 로깅 설정
LOGGING_CONFIGS = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "workflow.log",
    "max_file_size": "50MB",
    "backup_count": 10,
    "console_output": True
}

# 워크플로우 설정
WORKFLOW_CONFIGS = {
    "max_execution_time": 3600,  # 1시간
    "checkpoint_interval": 300,  # 5분마다 체크포인트
    "parallel_execution": True,
    "error_recovery": True,
    "progress_tracking": True
}

# MCP 서버 기본 설정
MCP_SERVER_DEFAULTS = {
    "slack": {
        "command": "slack-mcp-server",
        "args": ["--token", "YOUR_SLACK_BOT_TOKEN"],
        "env": {"SLACK_BOT_TOKEN": "YOUR_SLACK_BOT_TOKEN"},
        "cwd": None,
        "timeout": 30
    },
    "notion": {
        "command": "notion-mcp-server",
        "args": ["--token", "YOUR_NOTION_INTEGRATION_TOKEN"],
        "env": {"NOTION_INTEGRATION_TOKEN": "YOUR_NOTION_INTEGRATION_TOKEN"},
        "cwd": None,
        "timeout": 30
    },
    "gmail": {
        "command": "gmail-mcp-server",
        "args": ["--credentials", "path/to/credentials.json"],
        "env": {"GOOGLE_APPLICATION_CREDENTIALS": "path/to/credentials.json"},
        "cwd": None,
        "timeout": 30
    }
}

# 웹 크롤링 도구 설정
WEB_CRAWLING_TOOL_CONFIGS = {
    "selenium": {
        "webdriver_path": "/usr/local/bin/chromedriver",
        "browser_options": ["--headless", "--no-sandbox", "--disable-dev-shm-usage"],
        "implicit_wait": 10,
        "page_load_timeout": 60
    },
    "requests_html": {
        "browser": "chromium",
        "browser_args": ["--no-sandbox", "--disable-dev-shm-usage"],
        "timeout": 30,
        "retries": 3
    },
    "scrapy": {
        "settings": {
            "ROBOTSTXT_OBEY": True,
            "CONCURRENT_REQUESTS": 16,
            "DOWNLOAD_DELAY": 1,
            "COOKIES_ENABLED": False
        }
    }
}
