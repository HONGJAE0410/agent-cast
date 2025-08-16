"""Script Writer Agent for converting research results to podcast scripts."""

from typing import Any, Dict, List
from ..constants import AGENT_NAMES, SCRIPT_WRITER_SYSTEM_PROMPT
from .base_agent import BaseAgent, AgentResult
from ..state import WorkflowState


class ScriptWriterAgent(BaseAgent):
    """연구 결과를 팟캐스트 대본으로 변환하는 에이전트."""
    
    def __init__(self):
        super().__init__(
            name=AGENT_NAMES["SCRIPT_WRITER"],
            description="연구 결과를 팟캐스트 대본으로 변환하는 에이전트"
        )
        self.required_inputs = ["research_results", "approval_status"]
        self.output_keys = ["podcast_script", "script_metadata", "conversation_flow"]
        self.timeout = 90
        self.retry_attempts = 2
        self.priority = 6
        
        # 대본 설정
        self.script_config = {
            "target_duration": 15,  # 분
            "hosts": ["호스트 A (남성)", "호스트 B (여성)"],
            "style": "전문적이면서도 친근한 대화체",
            "structure": ["인트로", "본론", "결론"]
        }
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """팟캐스트 대본 생성을 수행합니다."""
        self.log_execution("팟캐스트 대본 생성 시작")
        
        try:
            # 입력 검증
            if not self.validate_inputs(state):
                raise ValueError("필수 입력이 누락되었습니다: research_results, approval_status")
            
            # 승인 상태 확인
            if state.approval_status != "approved":
                self.log_execution("연구 결과가 승인되지 않아 기본 대본을 생성합니다", "WARNING")
                script_data = self._generate_fallback_script()
            else:
                # 승인된 연구 결과로 대본 생성
                script_data = self._generate_podcast_script(state.research_results)
            
            # 대본 메타데이터 생성
            script_metadata = self._generate_script_metadata(script_data)
            
            # 대화 흐름 분석
            conversation_flow = self._analyze_conversation_flow(script_data)
            
            # 결과 생성
            result = AgentResult(
                success=True,
                output={
                    "podcast_script": script_data,
                    "script_metadata": script_metadata,
                    "conversation_flow": conversation_flow
                },
                metadata={
                    "script_generation_method": "research_based" if state.approval_status == "approved" else "fallback",
                    "target_duration": self.script_config["target_duration"],
                    "hosts_count": len(self.script_config["hosts"])
                }
            )
            
            # 상태 업데이트
            updated_state = self.update_workflow_status(state, "script_writing")
            updated_state.podcast_script = script_data
            updated_state.script_metadata = script_metadata
            updated_state.conversation_flow = conversation_flow
            
            self.log_execution("팟캐스트 대본 생성 완료")
            return updated_state
            
        except Exception as e:
            self.log_execution(f"팟캐스트 대본 생성 실패: {str(e)}", "ERROR")
            
            # 폴백 데이터 사용
            fallback_data = self._get_fallback_data()
            
            result = AgentResult(
                success=False,
                output=fallback_data,
                error_message=str(e)
            )
            
            # 폴백 데이터로 상태 업데이트
            updated_state = self.update_workflow_status(state, "script_writing")
            updated_state.podcast_script = fallback_data["podcast_script"]
            updated_state.script_metadata = fallback_data["script_metadata"]
            updated_state.conversation_flow = fallback_data["conversation_flow"]
            
            self.log_execution("폴백 데이터 사용으로 계속 진행")
            return updated_state
    
    def _generate_podcast_script(self, research_results: Dict[str, Any]) -> Dict[str, Any]:
        """연구 결과를 바탕으로 팟캐스트 대본을 생성합니다."""
        if "error" in research_results:
            return self._generate_fallback_script()
        
        # 대본 구성 요소 추출
        summary = research_results.get("summary", {})
        trends = research_results.get("trends", [])
        keywords = research_results.get("keywords", [])
        source_analysis = research_results.get("source_analysis", {})
        
        # 인트로 생성
        intro = self._generate_intro(summary, keywords)
        
        # 본론 생성
        main_content = self._generate_main_content(trends, source_analysis, summary)
        
        # 결론 생성
        conclusion = self._generate_conclusion(summary, trends)
        
        # 전체 대본 구성
        script = {
            "title": self._generate_title(keywords, trends),
            "introduction": intro,
            "main_content": main_content,
            "conclusion": conclusion,
            "total_estimated_duration": self._estimate_duration(intro, main_content, conclusion),
            "key_points": self._extract_key_points(trends, summary),
            "keywords": [k["keyword"] for k in keywords[:5]] if keywords else [],
            "sources": list(source_analysis.keys()) if source_analysis else []
        }
        
        return script
    
    def _generate_title(self, keywords: List[Dict[str, Any]], trends: List[Dict[str, Any]]) -> str:
        """팟캐스트 제목을 생성합니다."""
        if trends:
            # 트렌드를 바탕으로 제목 생성
            main_trend = trends[0]
            trend_desc = main_trend.get("description", "")
            if "AI" in trend_desc or "머신러닝" in trend_desc:
                return "AI 연구 최신 동향: 머신러닝 최적화와 효율성 향상"
            elif "효율성" in trend_desc:
                return "AI 시스템 효율성 향상의 최신 연구 동향"
        
        if keywords:
            # 키워드를 바탕으로 제목 생성
            top_keywords = [k["keyword"] for k in keywords[:3]]
            return f"AI 연구 동향: {' '.join(top_keywords)} 중심으로"
        
        return "AI 연구 최신 동향과 트렌드"
    
    def _generate_intro(self, summary: Dict[str, Any], keywords: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """인트로를 생성합니다."""
        total_results = summary.get("total_results", 0)
        high_quality_count = summary.get("high_relevance_count", 0)
        
        intro_script = [
            {
                "speaker": "호스트 A (남성)",
                "content": f"안녕하세요, AI 연구 동향을 다루는 팟캐스트에 오신 것을 환영합니다. 오늘은 {total_results}개의 연구 결과를 바탕으로 최신 AI 동향을 살펴보겠습니다.",
                "duration": 15,
                "emotion": "friendly"
            },
            {
                "speaker": "호스트 B (여성)",
                "content": "네, 특히 오늘은 고품질의 연구 결과가 {high_quality_count}개나 있어서 정말 흥미로운 내용을 다룰 수 있을 것 같아요.",
                "duration": 12,
                "emotion": "excited"
            }
        ]
        
        if keywords:
            top_keyword = keywords[0]["keyword"]
            intro_script.append({
                "speaker": "호스트 A (남성)",
                "content": f"주요 키워드로는 '{top_keyword}'가 가장 많이 언급되었는데, 이는 현재 AI 연구의 핵심 주제임을 보여줍니다.",
                "duration": 18,
                "emotion": "professional"
            })
        
        return intro_script
    
    def _generate_main_content(self, trends: List[Dict[str, Any]], source_analysis: Dict[str, Any], summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """본론을 생성합니다."""
        main_content = []
        
        # 트렌드 분석
        if trends:
            main_content.append({
                "speaker": "호스트 B (여성)",
                "content": "먼저 최신 AI 연구 트렌드를 살펴보겠습니다.",
                "duration": 8,
                "emotion": "professional"
            })
            
            for i, trend in enumerate(trends[:3]):  # 상위 3개 트렌드만
                trend_desc = trend.get("description", "")
                confidence = trend.get("confidence", 0.0)
                
                main_content.append({
                    "speaker": "호스트 A (남성)" if i % 2 == 0 else "호스트 B (여성)",
                    "content": f"{i+1}번째 트렌드는 '{trend_desc}'입니다. 이에 대한 신뢰도는 {confidence:.1%}입니다.",
                    "duration": 20,
                    "emotion": "analytical"
                })
        
        # 소스 분석
        if source_analysis:
            main_content.append({
                "speaker": "호스트 B (여성)",
                "content": "정보 소스에 대해서도 살펴보겠습니다.",
                "duration": 8,
                "emotion": "professional"
            })
            
            source_count = len(source_analysis)
            main_content.append({
                "speaker": "호스트 A (남성)",
                "content": f"총 {source_count}개의 다양한 소스에서 정보를 수집했는데, 이는 연구 결과의 신뢰성을 높여줍니다.",
                "duration": 18,
                "emotion": "analytical"
            })
        
        # 통계 정보
        if summary:
            total_results = summary.get("total_results", 0)
            avg_similarity = summary.get("average_similarity", 0.0)
            
            main_content.append({
                "speaker": "호스트 B (여성)",
                "content": f"전체적으로 {total_results}개의 검색 결과를 분석했고, 평균 유사도 점수는 {avg_similarity:.1%}로 나타났습니다.",
                "duration": 16,
                "emotion": "analytical"
            })
        
        return main_content
    
    def _generate_conclusion(self, summary: Dict[str, Any], trends: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """결론을 생성합니다."""
        conclusion = [
            {
                "speaker": "호스트 A (남성)",
                "content": "오늘 AI 연구 동향에 대해 살펴보았는데, 전반적으로 매우 흥미로운 발전이 이루어지고 있음을 확인할 수 있었습니다.",
                "duration": 18,
                "emotion": "reflective"
            }
        ]
        
        if trends:
            main_trend = trends[0]
            trend_desc = main_trend.get("description", "")
            conclusion.append({
                "speaker": "호스트 B (여성)",
                "content": f"특히 '{trend_desc}'는 앞으로 AI 분야에서 중요한 역할을 할 것으로 예상됩니다.",
                "duration": 16,
                "emotion": "optimistic"
            })
        
        conclusion.append({
            "speaker": "호스트 A (남성)",
            "content": "다음 에피소드에서는 더 구체적인 AI 기술과 그 응용 사례에 대해 다루도록 하겠습니다.",
            "duration": 15,
            "emotion": "friendly"
        })
        
        conclusion.append({
            "speaker": "호스트 B (여성)",
            "content": "시청해주셔서 감사합니다. 다음 시간에 만나요!",
            "duration": 8,
            "emotion": "friendly"
        })
        
        return conclusion
    
    def _estimate_duration(self, intro: List[Dict[str, Any]], main_content: List[Dict[str, Any]], conclusion: List[Dict[str, Any]]) -> int:
        """전체 대본의 예상 재생 시간을 계산합니다."""
        total_seconds = 0
        
        for section in [intro, main_content, conclusion]:
            for line in section:
                total_seconds += line.get("duration", 0)
        
        # 분 단위로 변환
        return round(total_seconds / 60, 1)
    
    def _extract_key_points(self, trends: List[Dict[str, Any]], summary: Dict[str, Any]) -> List[str]:
        """주요 포인트를 추출합니다."""
        key_points = []
        
        if trends:
            for trend in trends[:3]:
                key_points.append(trend.get("description", ""))
        
        if summary:
            total_results = summary.get("total_results", 0)
            if total_results > 0:
                key_points.append(f"총 {total_results}개의 연구 결과 분석")
        
        return key_points
    
    def _generate_script_metadata(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """대본 메타데이터를 생성합니다."""
        return {
            "generation_timestamp": "2024-08-16T10:00:00Z",
            "script_version": "1.0",
            "total_lines": sum(
                len(script_data.get(section, [])) 
                for section in ["introduction", "main_content", "conclusion"]
            ),
            "estimated_duration": script_data.get("total_estimated_duration", 0),
            "hosts": self.script_config["hosts"],
            "style": self.script_config["style"],
            "structure": self.script_config["structure"],
            "language": "ko",
            "target_audience": "AI 연구자 및 관심자"
        }
    
    def _analyze_conversation_flow(self, script_data: Dict[str, Any]) -> Dict[str, Any]:
        """대화 흐름을 분석합니다."""
        all_lines = []
        for section in ["introduction", "main_content", "conclusion"]:
            all_lines.extend(script_data.get(section, []))
        
        if not all_lines:
            return {"error": "No script content available"}
        
        # 화자별 통계
        speaker_stats = {}
        for line in all_lines:
            speaker = line.get("speaker", "Unknown")
            if speaker not in speaker_stats:
                speaker_stats[speaker] = {"lines": 0, "total_duration": 0}
            
            speaker_stats[speaker]["lines"] += 1
            speaker_stats[speaker]["total_duration"] += line.get("duration", 0)
        
        # 감정 분포
        emotion_stats = {}
        for line in all_lines:
            emotion = line.get("emotion", "neutral")
            emotion_stats[emotion] = emotion_stats.get(emotion, 0) + 1
        
        return {
            "total_lines": len(all_lines),
            "speaker_distribution": speaker_stats,
            "emotion_distribution": emotion_stats,
            "average_line_duration": sum(line.get("duration", 0) for line in all_lines) / len(all_lines),
            "conversation_balance": "balanced" if len(speaker_stats) == 2 else "unbalanced"
        }
    
    def _generate_fallback_script(self) -> Dict[str, Any]:
        """기본 대본을 생성합니다."""
        return {
            "title": "AI 연구 동향 개요",
            "introduction": [
                {
                    "speaker": "호스트 A (남성)",
                    "content": "안녕하세요, AI 연구 동향을 다루는 팟캐스트입니다.",
                    "duration": 8,
                    "emotion": "friendly"
                }
            ],
            "main_content": [
                {
                    "speaker": "호스트 B (여성)",
                    "content": "오늘은 AI 연구의 일반적인 동향에 대해 이야기하겠습니다.",
                    "duration": 12,
                    "emotion": "professional"
                }
            ],
            "conclusion": [
                {
                    "speaker": "호스트 A (남성)",
                    "content": "감사합니다. 다음 시간에 만나요!",
                    "duration": 6,
                    "emotion": "friendly"
                }
            ],
            "total_estimated_duration": 0.4,
            "key_points": ["AI 연구 동향 개요"],
            "keywords": ["AI", "연구", "동향"],
            "sources": []
        }
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """폴백 데이터를 반환합니다."""
        fallback_script = self._generate_fallback_script()
        
        return {
            "podcast_script": fallback_script,
            "script_metadata": self._generate_script_metadata(fallback_script),
            "conversation_flow": {
                "total_lines": 3,
                "speaker_distribution": {"호스트 A (남성)": {"lines": 2, "total_duration": 14}, "호스트 B (여성)": {"lines": 1, "total_duration": 12}},
                "emotion_distribution": {"friendly": 2, "professional": 1},
                "average_line_duration": 8.7,
                "conversation_balance": "balanced"
            }
        }
