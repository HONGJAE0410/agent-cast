"""Searcher Agent for web crawling and information collection."""

import asyncio
from typing import Any, Dict, List
from ..constants import AGENT_NAMES, SEARCHER_SYSTEM_PROMPT
from .base_agent import BaseAgent, AgentResult
from ..state import WorkflowState


class SearcherAgent(BaseAgent):
    """웹 크롤링을 통해 최신 AI 연구 정보를 수집하는 에이전트."""
    
    def __init__(self):
        super().__init__(
            name=AGENT_NAMES["SEARCHER"],
            description="웹 크롤링을 통해 최신 AI 연구 정보를 수집하는 에이전트"
        )
        self.required_inputs = ["workflow_status"]
        self.output_keys = ["crawled_data", "search_sources", "data_chunks"]
        self.timeout = 180
        self.retry_attempts = 3
        self.priority = 2
        
        # 검색 대상 소스들
        self.search_sources = [
            "arxiv.org",
            "techcrunch.com",
            "aitimes.kr",
            "pytorch.kr",
            "ai.kr",
            "openai.com/blog",
            "google.ai/blog"
        ]
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """웹 크롤링을 통한 정보 수집을 수행합니다."""
        self.log_execution("웹 크롤링 정보 수집 시작")
        
        try:
            # 입력 검증
            if not self.validate_inputs(state):
                raise ValueError("필수 입력이 누락되었습니다: workflow_status")
            
            # 웹 크롤링 수행
            crawled_data = await self._perform_web_crawling()
            search_sources = self._get_search_sources_info()
            data_chunks = self._chunk_crawled_data(crawled_data)
            
            # 결과 생성
            result = AgentResult(
                success=True,
                output={
                    "crawled_data": crawled_data,
                    "search_sources": search_sources,
                    "data_chunks": data_chunks
                },
                metadata={
                    "crawling_method": "simulated",
                    "sources_accessed": len(search_sources),
                    "total_chunks": len(data_chunks)
                }
            )
            
            # 상태 업데이트
            updated_state = self.update_workflow_status(state, "search")
            updated_state.crawled_data = crawled_data
            updated_state.search_sources = search_sources
            updated_state.data_chunks = data_chunks
            
            self.log_execution("웹 크롤링 정보 수집 완료")
            return updated_state
            
        except Exception as e:
            self.log_execution(f"웹 크롤링 정보 수집 실패: {str(e)}", "ERROR")
            
            # 폴백 데이터 사용
            fallback_data = self._get_fallback_data()
            
            result = AgentResult(
                success=False,
                output=fallback_data,
                error_message=str(e)
            )
            
            # 폴백 데이터로 상태 업데이트
            updated_state = self.update_workflow_status(state, "search")
            updated_state.crawled_data = fallback_data["crawled_data"]
            updated_state.search_sources = fallback_data["search_sources"]
            updated_state.data_chunks = fallback_data["data_chunks"]
            
            self.log_execution("폴백 데이터 사용으로 계속 진행")
            return updated_state
    
    async def _perform_web_crawling(self) -> List[Dict[str, Any]]:
        """웹 크롤링을 수행합니다."""
        # 실제 구현에서는 여기에 실제 웹 크롤링 로직이 들어갑니다
        # 현재는 시뮬레이션된 데이터를 반환합니다
        
        await asyncio.sleep(1)  # 크롤링 시간 시뮬레이션
        
        return [
            {
                "source": "arxiv.org",
                "title": "Efficient Large Language Model Training with Dynamic Batching",
                "authors": ["Zhang, L.", "Wang, Y.", "Chen, X."],
                "abstract": "We propose a novel dynamic batching strategy for training large language models...",
                "url": "https://arxiv.org/abs/2408.00123",
                "published_date": "2024-08-01",
                "category": "cs.AI",
                "relevance_score": 0.95
            },
            {
                "source": "techcrunch.com",
                "title": "OpenAI Releases GPT-4o Mini: Smaller, Faster, More Efficient",
                "authors": ["TechCrunch Staff"],
                "abstract": "OpenAI has announced the release of GPT-4o Mini, a more efficient version...",
                "url": "https://techcrunch.com/2024/08/15/openai-gpt4o-mini",
                "published_date": "2024-08-15",
                "category": "AI News",
                "relevance_score": 0.88
            },
            {
                "source": "aitimes.kr",
                "title": "한국 AI 연구진, 새로운 최적화 알고리즘 개발",
                "authors": ["김연구원", "이박사"],
                "abstract": "한국과학기술원(KIST) 연구진이 머신러닝 모델의 성능을 크게 향상시키는...",
                "url": "https://aitimes.kr/news/articleView.html?idxno=12345",
                "published_date": "2024-08-14",
                "category": "AI Research",
                "relevance_score": 0.92
            },
            {
                "source": "pytorch.kr",
                "title": "PyTorch 2.2 성능 최적화 가이드",
                "authors": ["PyTorch Korea Community"],
                "abstract": "PyTorch 2.2에서 제공하는 새로운 최적화 기능들을 활용하여 모델 성능을...",
                "url": "https://pytorch.kr/tutorials/optimization/",
                "published_date": "2024-08-10",
                "category": "Tutorial",
                "relevance_score": 0.85
            }
        ]
    
    def _get_search_sources_info(self) -> List[Dict[str, Any]]:
        """검색 소스 정보를 반환합니다."""
        return [
            {
                "name": "arXiv",
                "url": "arxiv.org",
                "type": "research_papers",
                "access_method": "api",
                "rate_limit": "1000 requests/hour",
                "last_accessed": "2024-08-16T10:00:00Z"
            },
            {
                "name": "TechCrunch",
                "url": "techcrunch.com",
                "type": "tech_news",
                "access_method": "web_scraping",
                "rate_limit": "10 requests/minute",
                "last_accessed": "2024-08-16T10:05:00Z"
            },
            {
                "name": "AI Times Korea",
                "url": "aitimes.kr",
                "type": "ai_news",
                "access_method": "web_scraping",
                "rate_limit": "20 requests/minute",
                "last_accessed": "2024-08-16T10:10:00Z"
            },
            {
                "name": "PyTorch Korea",
                "url": "pytorch.kr",
                "type": "community",
                "access_method": "web_scraping",
                "rate_limit": "30 requests/minute",
                "last_accessed": "2024-08-16T10:15:00Z"
            }
        ]
    
    def _chunk_crawled_data(self, crawled_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """크롤링된 데이터를 청킹합니다."""
        chunks = []
        
        for item in crawled_data:
            # 제목과 초록을 분리하여 청킹
            title_chunk = {
                "chunk_id": f"{item['source']}_{item['title'][:20]}_title",
                "content": item["title"],
                "metadata": {
                    "source": item["source"],
                    "type": "title",
                    "url": item["url"],
                    "published_date": item["published_date"],
                    "relevance_score": item["relevance_score"]
                },
                "chunk_size": len(item["title"])
            }
            chunks.append(title_chunk)
            
            # 초록을 적절한 크기로 청킹
            abstract = item["abstract"]
            if len(abstract) > 200:
                # 긴 초록을 여러 청크로 분할
                words = abstract.split()
                chunk_size = 50
                for i in range(0, len(words), chunk_size):
                    chunk_words = words[i:i + chunk_size]
                    chunk_text = " ".join(chunk_words)
                    
                    abstract_chunk = {
                        "chunk_id": f"{item['source']}_{item['title'][:20]}_abstract_{i//chunk_size}",
                        "content": chunk_text,
                        "metadata": {
                            "source": item["source"],
                            "type": "abstract",
                            "url": item["url"],
                            "published_date": item["published_date"],
                            "relevance_score": item["relevance_score"],
                            "chunk_part": i // chunk_size + 1
                        },
                        "chunk_size": len(chunk_text)
                    }
                    chunks.append(abstract_chunk)
            else:
                # 짧은 초록은 하나의 청크로
                abstract_chunk = {
                    "chunk_id": f"{item['source']}_{item['title'][:20]}_abstract",
                    "content": abstract,
                    "metadata": {
                        "source": item["source"],
                        "type": "abstract",
                        "url": item["url"],
                        "published_date": item["published_date"],
                        "relevance_score": item["relevance_score"]
                    },
                    "chunk_size": len(abstract)
                }
                chunks.append(abstract_chunk)
        
        return chunks
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """폴백 데이터를 반환합니다."""
        return {
            "crawled_data": [
                {
                    "source": "fallback",
                    "title": "AI Research Information (Fallback)",
                    "authors": ["System"],
                    "abstract": "Fallback data for AI research information collection.",
                    "url": "https://example.com",
                    "published_date": "2024-08-16",
                    "category": "fallback",
                    "relevance_score": 0.5
                }
            ],
            "search_sources": [
                {
                    "name": "Fallback Source",
                    "url": "example.com",
                    "type": "fallback",
                    "access_method": "fallback",
                    "rate_limit": "unlimited",
                    "last_accessed": "2024-08-16T10:00:00Z"
                }
            ],
            "data_chunks": [
                {
                    "chunk_id": "fallback_chunk",
                    "content": "Fallback data for AI research information collection.",
                    "metadata": {
                        "source": "fallback",
                        "type": "fallback",
                        "url": "https://example.com",
                        "published_date": "2024-08-16",
                        "relevance_score": 0.5
                    },
                    "chunk_size": 50
                }
            ]
        }
