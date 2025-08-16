"""TTS Agent for converting podcast scripts to audio."""

import asyncio
from typing import Any, Dict, List
from ..constants import AGENT_NAMES, TTS_SYSTEM_PROMPT
from .base_agent import BaseAgent, AgentResult
from ..state import WorkflowState


class TTSAgent(BaseAgent):
    """팟캐스트 대본을 자연스러운 음성으로 변환하는 에이전트."""
    
    def __init__(self):
        super().__init__(
            name=AGENT_NAMES["TTS"],
            description="팟캐스트 대본을 자연스러운 음성으로 변환하는 에이전트"
        )
        self.required_inputs = ["podcast_script", "script_metadata"]
        self.output_keys = ["audio_file", "tts_metadata", "voice_quality"]
        self.timeout = 180
        self.retry_attempts = 2
        self.priority = 7
        
        # TTS 설정
        self.tts_config = {
            "voice_settings": {
                "host_a": {
                    "gender": "male",
                    "age": "adult",
                    "tone": "professional",
                    "speed": 1.0,
                    "pitch": 0.0
                },
                "host_b": {
                    "gender": "female",
                    "age": "adult",
                    "tone": "friendly",
                    "speed": 1.0,
                    "pitch": 0.0
                }
            },
            "audio_format": "mp3",
            "sample_rate": 22050,
            "bitrate": "128k"
        }
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """TTS 음성 생성을 수행합니다."""
        self.log_execution("TTS 음성 생성 시작")
        
        try:
            # 입력 검증
            if not self.validate_inputs(state):
                raise ValueError("필수 입력이 누락되었습니다: podcast_script, script_metadata")
            
            # 대본을 화자별로 분할
            speaker_segments = self._split_script_by_speaker(state.podcast_script)
            
            # 각 화자별 음성 생성 (시뮬레이션)
            audio_segments = await self._generate_audio_segments(speaker_segments)
            
            # 오디오 세그먼트 결합
            final_audio = await self._combine_audio_segments(audio_segments)
            
            # TTS 메타데이터 생성
            tts_metadata = self._generate_tts_metadata(audio_segments, final_audio)
            
            # 음성 품질 평가
            voice_quality = self._evaluate_voice_quality(audio_segments, final_audio)
            
            # 결과 생성
            result = AgentResult(
                success=True,
                output={
                    "audio_file": final_audio,
                    "tts_metadata": tts_metadata,
                    "voice_quality": voice_quality
                },
                metadata={
                    "tts_method": "simulated",
                    "total_segments": len(audio_segments),
                    "audio_format": self.tts_config["audio_format"]
                }
            )
            
            # 상태 업데이트
            updated_state = self.update_workflow_status(state, "tts")
            updated_state.audio_file = final_audio
            updated_state.tts_metadata = tts_metadata
            updated_state.voice_quality = voice_quality
            
            self.log_execution("TTS 음성 생성 완료")
            return updated_state
            
        except Exception as e:
            self.log_execution(f"TTS 음성 생성 실패: {str(e)}", "ERROR")
            
            # 폴백 데이터 사용
            fallback_data = self._get_fallback_data()
            
            result = AgentResult(
                success=False,
                output=fallback_data,
                error_message=str(e)
            )
            
            # 폴백 데이터로 상태 업데이트
            updated_state = self.update_workflow_status(state, "tts")
            updated_state.audio_file = fallback_data["audio_file"]
            updated_state.tts_metadata = fallback_data["tts_metadata"]
            updated_state.voice_quality = fallback_data["voice_quality"]
            
            self.log_execution("폴백 데이터 사용으로 계속 진행")
            return updated_state
    
    def _split_script_by_speaker(self, podcast_script: Dict[str, Any]) -> List[Dict[str, Any]]:
        """대본을 화자별로 분할합니다."""
        segments = []
        
        for section in ["introduction", "main_content", "conclusion"]:
            section_content = podcast_script.get(section, [])
            for line in section_content:
                speaker = line.get("speaker", "Unknown")
                content = line.get("content", "")
                duration = line.get("duration", 0)
                emotion = line.get("emotion", "neutral")
                
                # 화자 매핑
                voice_setting = self._map_speaker_to_voice(speaker)
                
                segment = {
                    "speaker": speaker,
                    "content": content,
                    "duration": duration,
                    "emotion": emotion,
                    "voice_setting": voice_setting,
                    "section": section,
                    "estimated_audio_duration": duration  # 초 단위
                }
                segments.append(segment)
        
        return segments
    
    def _map_speaker_to_voice(self, speaker: str) -> Dict[str, Any]:
        """화자를 음성 설정에 매핑합니다."""
        if "호스트 A" in speaker or "남성" in speaker:
            return self.tts_config["voice_settings"]["host_a"]
        elif "호스트 B" in speaker or "여성" in speaker:
            return self.tts_config["voice_settings"]["host_b"]
        else:
            # 기본 설정
            return self.tts_config["voice_settings"]["host_a"]
    
    async def _generate_audio_segments(self, speaker_segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """각 화자별 오디오 세그먼트를 생성합니다."""
        # 실제 구현에서는 OpenAI TTS API를 호출하여 음성을 생성합니다
        # 현재는 시뮬레이션된 오디오 세그먼트를 반환합니다
        
        await asyncio.sleep(3)  # TTS 생성 시간 시뮬레이션
        
        audio_segments = []
        for i, segment in enumerate(speaker_segments):
            # 시뮬레이션된 오디오 파일 정보
            audio_segment = {
                "segment_id": f"segment_{i:03d}",
                "speaker": segment["speaker"],
                "content": segment["content"],
                "voice_setting": segment["voice_setting"],
                "audio_file": f"audio_segment_{i:03d}.{self.tts_config['audio_format']}",
                "file_size": self._estimate_file_size(segment["duration"]),
                "duration": segment["duration"],
                "quality_metrics": {
                    "clarity": 0.95,
                    "naturalness": 0.92,
                    "emotion_match": 0.88,
                    "pronunciation": 0.94
                },
                "metadata": {
                    "section": segment["section"],
                    "emotion": segment["emotion"],
                    "generation_timestamp": "2024-08-16T10:00:00Z"
                }
            }
            audio_segments.append(audio_segment)
        
        return audio_segments
    
    def _estimate_file_size(self, duration: int) -> str:
        """오디오 파일 크기를 추정합니다."""
        # MP3 128kbps 기준으로 계산
        bitrate = 128 * 1024  # bits per second
        total_bits = bitrate * duration
        total_bytes = total_bits / 8
        
        if total_bytes < 1024:
            return f"{total_bytes:.0f} B"
        elif total_bytes < 1024 * 1024:
            return f"{total_bytes / 1024:.1f} KB"
        else:
            return f"{total_bytes / (1024 * 1024):.1f} MB"
    
    async def _combine_audio_segments(self, audio_segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """오디오 세그먼트를 결합합니다."""
        # 실제 구현에서는 오디오 파일을 실제로 결합합니다
        # 현재는 시뮬레이션된 결합 결과를 반환합니다
        
        await asyncio.sleep(1)  # 결합 시간 시뮬레이션
        
        total_duration = sum(segment["duration"] for segment in audio_segments)
        total_file_size = sum(self._parse_file_size(segment["file_size"]) for segment in audio_segments)
        
        combined_audio = {
            "file_name": f"podcast_episode_{asyncio.get_event_loop().time():.0f}.{self.tts_config['audio_format']}",
            "file_size": self._format_file_size(total_file_size),
            "duration": total_duration,
            "format": self.tts_config["audio_format"],
            "sample_rate": self.tts_config["sample_rate"],
            "bitrate": self.tts_config["bitrate"],
            "segments_count": len(audio_segments),
            "combined_timestamp": "2024-08-16T10:00:00Z",
            "audio_quality": {
                "overall_quality": 0.93,
                "consistency": 0.91,
                "transitions": 0.89
            }
        }
        
        return combined_audio
    
    def _parse_file_size(self, file_size_str: str) -> float:
        """파일 크기 문자열을 바이트 단위로 파싱합니다."""
        if "KB" in file_size_str:
            return float(file_size_str.replace(" KB", "")) * 1024
        elif "MB" in file_size_str:
            return float(file_size_str.replace(" MB", "")) * 1024 * 1024
        elif "B" in file_size_str:
            return float(file_size_str.replace(" B", ""))
        else:
            return 0.0
    
    def _format_file_size(self, bytes_size: float) -> str:
        """바이트 크기를 읽기 쉬운 형태로 포맷합니다."""
        if bytes_size < 1024:
            return f"{bytes_size:.0f} B"
        elif bytes_size < 1024 * 1024:
            return f"{bytes_size / 1024:.1f} KB"
        else:
            return f"{bytes_size / (1024 * 1024):.1f} MB"
    
    def _generate_tts_metadata(self, audio_segments: List[Dict[str, Any]], final_audio: Dict[str, Any]) -> Dict[str, Any]:
        """TTS 메타데이터를 생성합니다."""
        # 화자별 통계
        speaker_stats = {}
        for segment in audio_segments:
            speaker = segment["speaker"]
            if speaker not in speaker_stats:
                speaker_stats[speaker] = {
                    "segments": 0,
                    "total_duration": 0,
                    "total_content_length": 0
                }
            
            speaker_stats[speaker]["segments"] += 1
            speaker_stats[speaker]["total_duration"] += segment["duration"]
            speaker_stats[speaker]["total_content_length"] += len(segment["content"])
        
        # 품질 통계
        quality_scores = [segment["quality_metrics"] for segment in audio_segments]
        avg_quality = {
            "clarity": sum(q["clarity"] for q in quality_scores) / len(quality_scores),
            "naturalness": sum(q["naturalness"] for q in quality_scores) / len(quality_scores),
            "emotion_match": sum(q["emotion_match"] for q in quality_scores) / len(quality_scores),
            "pronunciation": sum(q["pronunciation"] for q in quality_scores) / len(quality_scores)
        }
        
        return {
            "generation_info": {
                "total_segments": len(audio_segments),
                "total_duration": final_audio["duration"],
                "generation_timestamp": "2024-08-16T10:00:00Z",
                "tts_engine": "simulated_openai_tts"
            },
            "speaker_analysis": speaker_stats,
            "quality_analysis": {
                "average_scores": avg_quality,
                "overall_quality": final_audio["audio_quality"]["overall_quality"],
                "consistency": final_audio["audio_quality"]["consistency"]
            },
            "technical_specs": {
                "format": final_audio["format"],
                "sample_rate": final_audio["sample_rate"],
                "bitrate": final_audio["bitrate"],
                "file_size": final_audio["file_size"]
            }
        }
    
    def _evaluate_voice_quality(self, audio_segments: List[Dict[str, Any]], final_audio: Dict[str, Any]) -> Dict[str, Any]:
        """음성 품질을 평가합니다."""
        if not audio_segments:
            return {"error": "No audio segments available"}
        
        # 개별 세그먼트 품질 분석
        segment_qualities = []
        for segment in audio_segments:
            quality = segment["quality_metrics"]
            segment_qualities.append({
                "segment_id": segment["segment_id"],
                "speaker": segment["speaker"],
                "overall_score": sum(quality.values()) / len(quality),
                "strengths": [k for k, v in quality.items() if v >= 0.9],
                "weaknesses": [k for k, v in quality.items() if v < 0.8]
            })
        
        # 전체 품질 평가
        overall_quality = final_audio["audio_quality"]["overall_quality"]
        
        # 품질 등급 결정
        if overall_quality >= 0.9:
            quality_grade = "excellent"
        elif overall_quality >= 0.8:
            quality_grade = "good"
        elif overall_quality >= 0.7:
            quality_grade = "fair"
        else:
            quality_grade = "poor"
        
        return {
            "overall_grade": quality_grade,
            "overall_score": overall_quality,
            "segment_analysis": segment_qualities,
            "recommendations": self._generate_quality_recommendations(segment_qualities, overall_quality),
            "quality_distribution": {
                "excellent": len([s for s in segment_qualities if s["overall_score"] >= 0.9]),
                "good": len([s for s in segment_qualities if 0.8 <= s["overall_score"] < 0.9]),
                "fair": len([s for s in segment_qualities if 0.7 <= s["overall_score"] < 0.8]),
                "poor": len([s for s in segment_qualities if s["overall_score"] < 0.7])
            }
        }
    
    def _generate_quality_recommendations(self, segment_qualities: List[Dict[str, Any]], overall_quality: float) -> List[str]:
        """품질 개선 권장사항을 생성합니다."""
        recommendations = []
        
        # 전체 품질 기반 권장사항
        if overall_quality < 0.8:
            recommendations.append("전체적인 음성 품질을 향상시키기 위해 TTS 모델을 업그레이드하세요.")
        
        # 세그먼트별 권장사항
        poor_segments = [s for s in segment_qualities if s["overall_score"] < 0.8]
        if poor_segments:
            recommendations.append(f"{len(poor_segments)}개의 세그먼트에서 품질이 낮게 나타났습니다. 재생성을 고려하세요.")
        
        # 감정 매칭 개선
        emotion_issues = [s for s in segment_qualities if "emotion_match" in s["weaknesses"]]
        if emotion_issues:
            recommendations.append("감정 표현이 부족한 세그먼트에 대해 감정 강화를 적용하세요.")
        
        # 발음 개선
        pronunciation_issues = [s for s in segment_qualities if "pronunciation" in s["weaknesses"]]
        if pronunciation_issues:
            recommendations.append("발음이 부정확한 세그먼트에 대해 발음 교정을 적용하세요.")
        
        return recommendations
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """폴백 데이터를 반환합니다."""
        return {
            "audio_file": {
                "file_name": "fallback_podcast.mp3",
                "file_size": "0 B",
                "duration": 0,
                "format": "mp3",
                "sample_rate": 22050,
                "bitrate": "128k",
                "segments_count": 0,
                "combined_timestamp": "2024-08-16T10:00:00Z",
                "audio_quality": {
                    "overall_quality": 0.0,
                    "consistency": 0.0,
                    "transitions": 0.0
                }
            },
            "tts_metadata": {
                "generation_info": {
                    "total_segments": 0,
                    "total_duration": 0,
                    "generation_timestamp": "2024-08-16T10:00:00Z",
                    "tts_engine": "fallback"
                },
                "speaker_analysis": {},
                "quality_analysis": {
                    "average_scores": {},
                    "overall_quality": 0.0,
                    "consistency": 0.0
                },
                "technical_specs": {
                    "format": "mp3",
                    "sample_rate": 22050,
                    "bitrate": "128k",
                    "file_size": "0 B"
                }
            },
            "voice_quality": {
                "overall_grade": "poor",
                "overall_score": 0.0,
                "segment_analysis": [],
                "recommendations": ["TTS 생성에 실패했습니다. 다시 시도하세요."],
                "quality_distribution": {
                    "excellent": 0,
                    "good": 0,
                    "fair": 0,
                    "poor": 1
                }
            }
        }
