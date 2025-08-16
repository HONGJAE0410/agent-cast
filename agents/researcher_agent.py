"""Researcher Agent for RAG-based information retrieval and analysis."""

import asyncio
from typing import Any, Dict, List
from ..constants import AGENT_NAMES, RESEARCHER_SYSTEM_PROMPT
from .base_agent import BaseAgent, AgentResult
from ..state import WorkflowState


class ResearcherAgent(BaseAgent):
    """RAG 시스템을 통해 정보를 검색하고 분석하는 에이전트."""
    
    def __init__(self):
        super().__init__(
            name=AGENT_NAMES["RESEARCHER"],
            description="RAG 시스템을 통해 정보를 검색하고 분석하는 에이전트"
        )
        self.required_inputs = ["rag_query", "vector_db"]
        self.output_keys = ["research_results", "search_strategy", "rag_metrics"]
        self.timeout = 120
        self.retry_attempts = 2
        self.priority = 4
        
        # 검색 설정
        self.search_config = {
            "top_k": 10,
            "similarity_threshold": 0.7,
            "max_results": 20
        }
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """RAG 기반 정보 검색 및 분석을 수행합니다."""
        self.log_execution("RAG 기반 정보 검색 및 분석 시작")
        
        try:
            # 입력 검증
            if not self.validate_inputs(state):
                raise ValueError("필수 입력이 누락되었습니다: rag_query, vector_db")
            
            # RAG 검색 수행
            search_results = await self._perform_rag_search(state.rag_query, state.vector_db)
            
            # 검색 결과 분석
            research_results = self._analyze_search_results(search_results)
            
            # 검색 전략 생성
            search_strategy = self._generate_search_strategy(state.rag_query, search_results)
            
            # RAG 메트릭 계산
            rag_metrics = self._calculate_rag_metrics(search_results, state.rag_query)
            
            # 결과 생성
            result = AgentResult(
                success=True,
                output={
                    "research_results": research_results,
                    "search_strategy": search_strategy,
                    "rag_metrics": rag_metrics
                },
                metadata={
                    "search_method": "vector_similarity",
                    "total_results": len(search_results),
                    "query_complexity": "medium"
                }
            )
            
            # 상태 업데이트
            updated_state = self.update_workflow_status(state, "research")
            updated_state.research_results = research_results
            updated_state.search_strategy = search_strategy
            updated_state.rag_metrics = rag_metrics
            
            self.log_execution("RAG 기반 정보 검색 및 분석 완료")
            return updated_state
            
        except Exception as e:
            self.log_execution(f"RAG 기반 정보 검색 및 분석 실패: {str(e)}", "ERROR")
            
            # 폴백 데이터 사용
            fallback_data = self._get_fallback_data()
            
            result = AgentResult(
                success=False,
                output=fallback_data,
                error_message=str(e)
            )
            
            # 폴백 데이터로 상태 업데이트
            updated_state = self.update_workflow_status(state, "research")
            updated_state.research_results = fallback_data["research_results"]
            updated_state.search_strategy = fallback_data["search_strategy"]
            updated_state.rag_metrics = fallback_data["rag_metrics"]
            
            self.log_execution("폴백 데이터 사용으로 계속 진행")
            return updated_state
    
    async def _perform_rag_search(self, rag_query: Dict[str, Any], vector_db: Dict[str, Any]) -> List[Dict[str, Any]]:
        """RAG 검색을 수행합니다."""
        # 실제 구현에서는 벡터 DB에서 유사도 검색을 수행합니다
        # 현재는 시뮬레이션된 검색 결과를 반환합니다
        
        await asyncio.sleep(2)  # 검색 시간 시뮬레이션
        
        # 시뮬레이션된 검색 결과
        search_results = [
            {
                "chunk_id": "arxiv_001_title",
                "content": "Efficient Large Language Model Training with Dynamic Batching",
                "similarity_score": 0.95,
                "source": "arxiv.org",
                "metadata": {
                    "type": "research_paper",
                    "authors": ["Zhang, L.", "Wang, Y.", "Chen, X."],
                    "published_date": "2024-08-01",
                    "category": "cs.AI"
                },
                "relevance": "high"
            },
            {
                "chunk_id": "techcrunch_001_abstract",
                "content": "OpenAI has announced the release of GPT-4o Mini, a more efficient version...",
                "similarity_score": 0.88,
                "source": "techcrunch.com",
                "metadata": {
                    "type": "news_article",
                    "authors": ["TechCrunch Staff"],
                    "published_date": "2024-08-15",
                    "category": "AI News"
                },
                "relevance": "medium"
            },
            {
                "chunk_id": "aitimes_001_abstract",
                "content": "한국과학기술원(KIST) 연구진이 머신러닝 모델의 성능을 크게 향상시키는...",
                "similarity_score": 0.92,
                "source": "aitimes.kr",
                "metadata": {
                    "type": "research_news",
                    "authors": ["김연구원", "이박사"],
                    "published_date": "2024-08-14",
                    "category": "AI Research"
                },
                "relevance": "high"
            }
        ]
        
        # 유사도 점수별 정렬
        search_results.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        return search_results[:self.search_config["top_k"]]
    
    def _analyze_search_results(self, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """검색 결과를 분석합니다."""
        if not search_results:
            return {"error": "No search results available"}
        
        # 소스별 분석
        source_analysis = {}
        for result in search_results:
            source = result["source"]
            if source not in source_analysis:
                source_analysis[source] = {
                    "count": 0,
                    "avg_similarity": 0.0,
                    "relevance_distribution": {"high": 0, "medium": 0, "low": 0}
                }
            
            source_analysis[source]["count"] += 1
            source_analysis[source]["avg_similarity"] += result["similarity_score"]
            source_analysis[source]["relevance_distribution"][result["relevance"]] += 1
        
        # 평균 유사도 계산
        for source in source_analysis:
            source_analysis[source]["avg_similarity"] /= source_analysis[source]["count"]
        
        # 전체 통계
        total_results = len(search_results)
        avg_similarity = sum(r["similarity_score"] for r in search_results) / total_results
        
        # 키워드 추출 및 분석
        keywords = self._extract_keywords(search_results)
        
        return {
            "summary": {
                "total_results": total_results,
                "average_similarity": avg_similarity,
                "high_relevance_count": len([r for r in search_results if r["relevance"] == "high"]),
                "medium_relevance_count": len([r for r in search_results if r["relevance"] == "medium"]),
                "low_relevance_count": len([r for r in search_results if r["relevance"] == "low"])
            },
            "source_analysis": source_analysis,
            "keywords": keywords,
            "trends": self._identify_trends(search_results),
            "recommendations": self._generate_recommendations(search_results)
        }
    
    def _extract_keywords(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """검색 결과에서 키워드를 추출합니다."""
        # 간단한 키워드 추출 (실제로는 NLP 라이브러리 사용)
        all_text = " ".join([r["content"] for r in search_results])
        words = all_text.lower().split()
        
        # 일반적인 단어 제거
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # 단어 빈도 계산
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # 상위 키워드 추출
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return [
            {"keyword": word, "frequency": freq, "relevance": "high" if freq > 2 else "medium"}
            for word, freq in top_keywords
        ]
    
    def _identify_trends(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """검색 결과에서 트렌드를 식별합니다."""
        trends = []
        
        # 최신 논문 트렌드
        recent_papers = [r for r in search_results if r["metadata"]["type"] == "research_paper"]
        if recent_papers:
            trends.append({
                "type": "research_trend",
                "description": "최신 AI 연구 논문에서 동적 배칭과 효율성 최적화가 주요 주제",
                "evidence": [r["content"] for r in recent_papers[:3]],
                "confidence": 0.85
            })
        
        # 뉴스 트렌드
        news_articles = [r for r in search_results if r["metadata"]["type"] == "news_article"]
        if news_articles:
            trends.append({
                "type": "news_trend",
                "description": "AI 모델의 효율성과 성능 향상이 주요 뉴스 주제",
                "evidence": [r["content"] for r in news_articles[:2]],
                "confidence": 0.78
            })
        
        return trends
    
    def _generate_recommendations(self, search_results: List[Dict[str, Any]]) -> List[str]:
        """검색 결과를 바탕으로 권장사항을 생성합니다."""
        recommendations = []
        
        # 고유성 기반 권장사항
        unique_sources = set(r["source"] for r in search_results)
        if len(unique_sources) < 3:
            recommendations.append("더 다양한 소스에서 정보를 수집하여 검색 범위를 확장하세요.")
        
        # 품질 기반 권장사항
        high_quality_results = [r for r in search_results if r["similarity_score"] >= 0.9]
        if len(high_quality_results) < 5:
            recommendations.append("검색 쿼리를 더 구체적으로 만들어 관련성 높은 결과를 얻으세요.")
        
        # 최신성 기반 권장사항
        recent_results = [r for r in search_results if "2024" in str(r["metadata"].get("published_date", ""))]
        if len(recent_results) < 3:
            recommendations.append("최신 정보를 더 많이 포함하도록 검색 범위를 조정하세요.")
        
        return recommendations
    
    def _generate_search_strategy(self, rag_query: Dict[str, Any], search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """검색 전략을 생성합니다."""
        return {
            "query_optimization": {
                "primary_queries": rag_query.get("primary_queries", []),
                "secondary_queries": rag_query.get("secondary_queries", []),
                "keywords": rag_query.get("keywords", [])
            },
            "search_parameters": {
                "top_k": self.search_config["top_k"],
                "similarity_threshold": self.search_config["similarity_threshold"],
                "max_results": self.search_config["max_results"]
            },
            "filtering_strategy": {
                "source_filter": "all",
                "date_filter": "recent",
                "type_filter": "all"
            },
            "ranking_strategy": {
                "primary_factor": "similarity_score",
                "secondary_factor": "relevance",
                "boost_factors": ["recency", "source_authority"]
            }
        }
    
    def _calculate_rag_metrics(self, search_results: List[Dict[str, Any]], rag_query: Dict[str, Any]) -> Dict[str, Any]:
        """RAG 메트릭을 계산합니다."""
        if not search_results:
            return {"error": "No search results available"}
        
        # 정확도 메트릭
        high_relevance_count = len([r for r in search_results if r["relevance"] == "high"])
        precision = high_relevance_count / len(search_results) if search_results else 0
        
        # 다양성 메트릭
        unique_sources = len(set(r["source"] for r in search_results))
        diversity_score = unique_sources / len(search_results) if search_results else 0
        
        # 최신성 메트릭
        recent_count = len([r for r in search_results if "2024" in str(r["metadata"].get("published_date", ""))])
        recency_score = recent_count / len(search_results) if search_results else 0
        
        return {
            "precision": precision,
            "diversity_score": diversity_score,
            "recency_score": recency_score,
            "overall_quality": (precision + diversity_score + recency_score) / 3,
            "query_coverage": len(rag_query.get("primary_queries", [])) / max(len(search_results), 1),
            "source_distribution": {
                "research_papers": len([r for r in search_results if r["metadata"]["type"] == "research_paper"]),
                "news_articles": len([r for r in search_results if r["metadata"]["type"] == "news_article"]),
                "other": len([r for r in search_results if r["metadata"]["type"] not in ["research_paper", "news_article"]])
            }
        }
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """폴백 데이터를 반환합니다."""
        return {
            "research_results": {
                "summary": {
                    "total_results": 0,
                    "average_similarity": 0.0,
                    "high_relevance_count": 0,
                    "medium_relevance_count": 0,
                    "low_relevance_count": 0
                },
                "source_analysis": {},
                "keywords": [],
                "trends": [],
                "recommendations": ["검색을 다시 시도하거나 쿼리를 수정하세요."]
            },
            "search_strategy": {
                "query_optimization": {"primary_queries": [], "secondary_queries": [], "keywords": []},
                "search_parameters": self.search_config,
                "filtering_strategy": {"source_filter": "all", "date_filter": "recent", "type_filter": "all"},
                "ranking_strategy": {"primary_factor": "similarity_score", "secondary_factor": "relevance", "boost_factors": []}
            },
            "rag_metrics": {
                "precision": 0.0,
                "diversity_score": 0.0,
                "recency_score": 0.0,
                "overall_quality": 0.0,
                "query_coverage": 0.0,
                "source_distribution": {"research_papers": 0, "news_articles": 0, "other": 0}
            }
        }
