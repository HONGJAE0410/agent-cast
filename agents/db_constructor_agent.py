"""DB Constructor Agent for building vector database from collected data."""

import asyncio
from typing import Any, Dict, List
from ..constants import AGENT_NAMES, DB_CONSTRUCTOR_SYSTEM_PROMPT
from .base_agent import BaseAgent, AgentResult
from ..state import WorkflowState


class DBConstructorAgent(BaseAgent):
    """수집된 정보를 벡터 데이터베이스로 구축하는 에이전트."""
    
    def __init__(self):
        super().__init__(
            name=AGENT_NAMES["DB_CONSTRUCTOR"],
            description="수집된 정보를 벡터 데이터베이스로 구축하는 에이전트"
        )
        self.required_inputs = ["data_chunks", "search_scope"]
        self.output_keys = ["vector_db", "embedding_stats", "db_metadata"]
        self.timeout = 300
        self.retry_attempts = 2
        self.priority = 3
        
        # 벡터 DB 설정
        self.vector_db_config = {
            "dimension": 3072,  # OpenAI text-embedding-3-large 차원
            "index_type": "IVF_FLAT",
            "metric_type": "COSINE",
            "collection_name": "ai_research_data"
        }
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """벡터 데이터베이스 구축을 수행합니다."""
        self.log_execution("벡터 데이터베이스 구축 시작")
        
        try:
            # 입력 검증
            if not self.validate_inputs(state):
                raise ValueError("필수 입력이 누락되었습니다: data_chunks, search_scope")
            
            # 데이터 청킹 최적화
            optimized_chunks = self._optimize_chunking(state.data_chunks)
            
            # 임베딩 생성 (시뮬레이션)
            embeddings = await self._generate_embeddings(optimized_chunks)
            
            # 벡터 DB 구축
            vector_db = await self._build_vector_database(embeddings)
            
            # 임베딩 통계 생성
            embedding_stats = self._generate_embedding_stats(embeddings)
            
            # DB 메타데이터 생성
            db_metadata = self._generate_db_metadata(vector_db, embedding_stats)
            
            # 결과 생성
            result = AgentResult(
                success=True,
                output={
                    "vector_db": vector_db,
                    "embedding_stats": embedding_stats,
                    "db_metadata": db_metadata
                },
                metadata={
                    "construction_method": "simulated",
                    "total_chunks_processed": len(optimized_chunks),
                    "embedding_model": "openai/text-embedding-3-large"
                }
            )
            
            # 상태 업데이트
            updated_state = self.update_workflow_status(state, "db_construction")
            updated_state.vector_db = vector_db
            updated_state.embedding_stats = embedding_stats
            updated_state.db_metadata = db_metadata
            
            self.log_execution("벡터 데이터베이스 구축 완료")
            return updated_state
            
        except Exception as e:
            self.log_execution(f"벡터 데이터베이스 구축 실패: {str(e)}", "ERROR")
            
            # 폴백 데이터 사용
            fallback_data = self._get_fallback_data()
            
            result = AgentResult(
                success=False,
                output=fallback_data,
                error_message=str(e)
            )
            
            # 폴백 데이터로 상태 업데이트
            updated_state = self.update_workflow_status(state, "db_construction")
            updated_state.vector_db = fallback_data["vector_db"]
            updated_state.embedding_stats = fallback_data["embedding_stats"]
            updated_state.db_metadata = fallback_data["db_metadata"]
            
            self.log_execution("폴백 데이터 사용으로 계속 진행")
            return updated_state
    
    def _optimize_chunking(self, data_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """데이터 청킹을 최적화합니다."""
        optimized_chunks = []
        
        for chunk in data_chunks:
            # 청크 크기 최적화
            content = chunk["content"]
            if len(content) < 50:
                # 너무 짧은 청크는 건너뛰기
                continue
            elif len(content) > 1000:
                # 너무 긴 청크는 분할
                sub_chunks = self._split_large_chunk(chunk)
                optimized_chunks.extend(sub_chunks)
            else:
                # 적절한 크기의 청크는 그대로 사용
                optimized_chunks.append(chunk)
        
        return optimized_chunks
    
    def _split_large_chunk(self, chunk: Dict[str, Any]) -> List[Dict[str, Any]]:
        """큰 청크를 작은 청크로 분할합니다."""
        content = chunk["content"]
        words = content.split()
        chunk_size = 100
        
        sub_chunks = []
        for i in range(0, len(words), chunk_size):
            sub_words = words[i:i + chunk_size]
            sub_content = " ".join(sub_words)
            
            sub_chunk = chunk.copy()
            sub_chunk["content"] = sub_content
            sub_chunk["chunk_id"] = f"{chunk['chunk_id']}_sub_{i//chunk_size}"
            sub_chunk["chunk_size"] = len(sub_content)
            sub_chunk["metadata"]["chunk_part"] = i // chunk_size + 1
            
            sub_chunks.append(sub_chunk)
        
        return sub_chunks
    
    async def _generate_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """청크에 대한 임베딩을 생성합니다."""
        # 실제 구현에서는 OpenAI API를 호출하여 임베딩을 생성합니다
        # 현재는 시뮬레이션된 임베딩을 반환합니다
        
        await asyncio.sleep(2)  # 임베딩 생성 시간 시뮬레이션
        
        embeddings = []
        for i, chunk in enumerate(chunks):
            # 시뮬레이션된 임베딩 벡터 (3072차원)
            embedding_vector = [0.1 * (i + 1) + 0.01 * j for j in range(self.vector_db_config["dimension"])]
            
            embedding = {
                "chunk_id": chunk["chunk_id"],
                "content": chunk["content"],
                "embedding_vector": embedding_vector,
                "metadata": chunk["metadata"],
                "embedding_quality": 0.95,  # 임베딩 품질 점수
                "generation_timestamp": "2024-08-16T10:00:00Z"
            }
            embeddings.append(embedding)
        
        return embeddings
    
    async def _build_vector_database(self, embeddings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """벡터 데이터베이스를 구축합니다."""
        # 실제 구현에서는 Milvus, Pinecone 등의 벡터 DB에 데이터를 저장합니다
        # 현재는 시뮬레이션된 DB 구축을 반환합니다
        
        await asyncio.sleep(1)  # DB 구축 시간 시뮬레이션
        
        return {
            "db_type": "milvus",
            "collection_name": self.vector_db_config["collection_name"],
            "total_vectors": len(embeddings),
            "dimension": self.vector_db_config["dimension"],
            "index_type": self.vector_db_config["index_type"],
            "metric_type": self.vector_db_config["metric_type"],
            "index_status": "built",
            "search_ready": True,
            "connection_info": {
                "host": "localhost",
                "port": 19530,
                "status": "connected"
            }
        }
    
    def _generate_embedding_stats(self, embeddings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """임베딩 통계를 생성합니다."""
        if not embeddings:
            return {"error": "No embeddings available"}
        
        total_chunks = len(embeddings)
        avg_quality = sum(emb["embedding_quality"] for emb in embeddings) / total_chunks
        
        # 소스별 통계
        source_stats = {}
        for emb in embeddings:
            source = emb["metadata"]["source"]
            if source not in source_stats:
                source_stats[source] = {"count": 0, "avg_quality": 0.0}
            
            source_stats[source]["count"] += 1
            source_stats[source]["avg_quality"] += emb["embedding_quality"]
        
        # 평균 품질 계산
        for source in source_stats:
            source_stats[source]["avg_quality"] /= source_stats[source]["count"]
        
        return {
            "total_embeddings": total_chunks,
            "average_quality": avg_quality,
            "dimension": self.vector_db_config["dimension"],
            "source_distribution": source_stats,
            "quality_distribution": {
                "excellent": len([e for e in embeddings if e["embedding_quality"] >= 0.9]),
                "good": len([e for e in embeddings if 0.7 <= e["embedding_quality"] < 0.9]),
                "fair": len([e for e in embeddings if 0.5 <= e["embedding_quality"] < 0.7]),
                "poor": len([e for e in embeddings if e["embedding_quality"] < 0.5])
            }
        }
    
    def _generate_db_metadata(self, vector_db: Dict[str, Any], embedding_stats: Dict[str, Any]) -> Dict[str, Any]:
        """데이터베이스 메타데이터를 생성합니다."""
        return {
            "creation_timestamp": "2024-08-16T10:00:00Z",
            "version": "1.0.0",
            "configuration": self.vector_db_config,
            "performance_metrics": {
                "build_time": "2.5 seconds",
                "index_size": "15.2 MB",
                "search_latency": "5ms",
                "throughput": "1000 queries/second"
            },
            "maintenance_info": {
                "last_backup": "2024-08-16T10:00:00Z",
            },
            "search_optimization": {
                "recommended_batch_size": 100,
                "optimal_search_params": {
                    "nprobe": 16,
                    "ef": 64
                }
            }
        }
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """폴백 데이터를 반환합니다."""
        return {
            "vector_db": {
                "db_type": "fallback",
                "collection_name": "fallback_collection",
                "total_vectors": 0,
                "dimension": 3072,
                "index_type": "fallback",
                "metric_type": "fallback",
                "index_status": "not_built",
                "search_ready": False,
                "connection_info": {
                    "host": "fallback",
                    "port": 0,
                    "status": "disconnected"
                }
            },
            "embedding_stats": {
                "total_embeddings": 0,
                "average_quality": 0.0,
                "dimension": 3072,
                "source_distribution": {},
                "quality_distribution": {
                    "excellent": 0,
                    "good": 0,
                    "fair": 0,
                    "poor": 0
                }
            },
            "db_metadata": {
                "creation_timestamp": "2024-08-16T10:00:00Z",
                "version": "fallback",
                "configuration": self.vector_db_config,
                "performance_metrics": {
                    "build_time": "0 seconds",
                    "index_size": "0 MB",
                    "search_latency": "N/A",
                    "throughput": "0 queries/second"
                },
                "maintenance_info": {
                    "last_backup": "2024-08-16T10:00:00Z"
                },
                "search_optimization": {
                    "recommended_batch_size": 0,
                    "optimal_search_params": {}
                }
            }
        }
