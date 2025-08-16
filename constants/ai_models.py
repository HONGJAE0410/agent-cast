"""Constants for AI models and services configuration."""

from typing import Any, Dict, Literal

# OpenAI 모델
OPENAI_MODELS = {
    "GPT_4O": "openai/gpt-4o",
    "GPT_4O_MINI": "openai/gpt-4o-mini",
    "GPT_4_TURBO": "openai/gpt-4-turbo",
    "GPT_3_5_TURBO": "openai/gpt-3.5-turbo",
    "TEXT_EMBEDDING_3_LARGE": "openai/text-embedding-3-large",
    "TEXT_EMBEDDING_3_SMALL": "openai/text-embedding-3-small",
    "TTS_1": "openai/tts-1",
    "TTS_1_HD": "openai/tts-1-hd"
}

# Anthropic 모델
ANTHROPIC_MODELS = {
    "CLAUDE_3_OPUS": "anthropic/claude-3-opus",
    "CLAUDE_3_SONNET": "anthropic/claude-3-sonnet",
    "CLAUDE_3_HAIKU": "anthropic/claude-3-haiku"
}

# Google 모델
GOOGLE_MODELS = {
    "GEMINI_PRO": "google/gemini-pro",
    "GEMINI_PRO_VISION": "google/gemini-pro-vision",
    "GEMMA_2B": "google/gemma-2b",
    "GEMMA_7B": "google/gemma-7b"
}

# 임베딩 모델
EMBEDDING_MODELS = {
    "OPENAI_TEXT_EMBEDDING_3_LARGE": "openai/text-embedding-3-large",
    "OPENAI_TEXT_EMBEDDING_3_SMALL": "openai/text-embedding-3-small",
    "COHERE_EMBED": "cohere/embed",
    "HUGGINGFACE_ALL_MINILM_L6_V2": "huggingface/all-MiniLM-L6-v2"
}

# TTS 모델
TTS_MODELS = {
    "OPENAI_TTS_1": "openai/tts-1",
    "OPENAI_TTS_1_HD": "openai/tts-1-hd",
    "ELEVENLABS_MULTILINGUAL": "elevenlabs/multilingual",
    "AZURE_NEURAL": "azure/neural"
}

# 벡터 데이터베이스
VECTOR_DB_PROVIDERS = {
    "MILVUS": "milvus",
    "PINECONE": "pinecone",
    "WEAVIATE": "weaviate",
    "CHROMA": "chroma",
    "QDRANT": "qdrant"
}

# 벡터 DB 설정
VECTOR_DB_CONFIGS = {
    "milvus": {
        "host": "localhost",
        "port": 19530,
        "collection_name": "ai_research_data",
        "dimension": 3072,
        "index_type": "IVF_FLAT",
        "metric_type": "COSINE"
    },
    "pinecone": {
        "environment": "us-west1-gcp",
        "index_name": "ai-research-data",
        "dimension": 3072,
        "metric": "cosine"
    },
    "weaviate": {
        "url": "http://localhost:8080",
        "class_name": "AIRearchData",
        "vectorizer": "text2vec-openai",
        "module_config": {
            "text2vec-openai": {
                "model": "ada",
                "modelVersion": "002",
                "type": "text"
            }
        }
    }
}

# 웹 크롤링 도구
WEB_CRAWLING_TOOLS = {
    "SELENIUM": "selenium",
    "REQUESTS_HTML": "requests_html",
    "SCRAPY": "scrapy",
    "BEAUTIFUL_SOUP": "beautiful_soup",
    "PLAYWRIGHT": "playwright"
}

# 웹 크롤링 설정
WEB_CRAWLING_CONFIGS = {
    "selenium": {
        "headless": True,
        "timeout": 30,
        "implicit_wait": 10,
        "page_load_timeout": 60
    },
    "requests_html": {
        "timeout": 30,
        "retries": 3,
        "user_agent": "Mozilla/5.0 (compatible; AI-Research-Bot/1.0)"
    },
    "scrapy": {
        "concurrent_requests": 16,
        "download_delay": 1,
        "randomize_download_delay": True
    }
}

# 품질 평가 가중치
QUALITY_WEIGHTS = {
    "factual_accuracy": 0.3,
    "source_verification": 0.25,
    "logical_consistency": 0.2,
    "data_freshness": 0.15,
    "completeness": 0.1
}
