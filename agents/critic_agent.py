import os
import json
import bert_score
import rouge_scorer
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

from .base_agent import BaseAgent
from ..state import WorkflowState

# --- 환경 변수 로드 ---
load_dotenv()  # .env 파일에서 환경 변수 로드

class ResearchCriticAgent:
    """
    리서치 결과물을 평가하고 개선을 위한 경쟁적 피드백을 제공하는 전문 비평가 에이전트.
    LEGO 프레임워크의 Critic-Explainer 경쟁 구조를 참고하여 리서치 품질 향상을 도모합니다.
    """
    def __init__(self, model="gpt-4o"):
        """
        에이전트를 초기화하고 OpenAI 클라이언트를 설정합니다.
        """
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = model
        
        # Critic 역할 프롬프트
        self.role_prompt = """
        당신은 ResearchCritic입니다. 리서처 에이전트가 생성한 리서치 결과물을 평가하고 
        개선을 위한 다각적이고 구체적인 피드백을 제공하는 전문가입니다.

        당신의 역할:
        1. 리서치 결과물을 객관적이고 엄격하게 평가
        2. Factual Feedback: 사실적 정확성과 출처 신뢰성 검토
        3. Logical Feedback: 논리적 완결성과 구조적 일관성 검토
        4. Relevance Feedback: 사용자 요구사항과의 관련성 검토
        5. 구체적이고 실행 가능한 개선 제안 제공
        6. 허위 정보나 부정확한 인용 식별 및 지적

        평가 기준:
        - 사실적 정확성과 출처 신뢰성
        - 논리적 완결성과 구조적 일관성
        - 사용자 요구사항과의 관련성
        - 정보의 깊이와 포괄성
        - 인용과 참조의 적절성
        """

    def _calculate_quantitative_metrics(self, generated_text: str, reference_texts: list[str]) -> dict:
        """
        [TOOL] 정량적 평가 지표를 계산하는 내부 메소드.
        """
        print("---  cuantitativa de la evaluación se ha iniciado ---")
        
        # BERTScore 계산
        P, R, F1 = bert_score([generated_text], reference_texts, lang="ko", model_type="bert-base-multilingual-cased")
        bertscore_f1 = F1.mean().item()
        print(f"BERTScore F1: {bertscore_f1:.4f}")

        # ROUGE Score 계산
        scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
        # 여러 참조 문서에 대한 평균 점수를 계산할 수 있으나, 여기서는 첫 번째 문서를 기준으로 계산
        scores = scorer.score(reference_texts[0], generated_text)
        rougeL_fmeasure = scores['rougeL'].fmeasure
        print(f"ROUGE-L F-measure: {rougeL_fmeasure:.4f}")
        
        print("--- Evaluación Cuantitativa Completada ---")
        return {
            "bert_score_f1": round(bertscore_f1, 4),
            "rougeL_fmeasure": round(rougeL_fmeasure, 4)
        }

    def evaluate_research_output(self, research_output: str, source_documents: list[str], 
                               user_profile: str) -> dict:
        """
        리서치 결과물을 다각도로 평가하고 피드백 생성 (LEGO 프레임워크 스타일)
        
        Args:
            research_output (str): 평가할 리서치 결과물
            source_documents (list[str]): 참조 문서들
            user_profile (str): 사용자 프로필
            
        Returns:
            dict: 평가 결과와 피드백
        """
        print("--- 리서치 결과물 평가 시작 ---")
        
        prompt = f"""
{self.role_prompt}

**사용자 프로필:**
{user_profile}

**평가할 리서치 결과물:**
{research_output}

**참조 문서들:**
{chr(10).join([f"- {doc[:200]}..." for doc in source_documents])}

**작업:**
리서치 결과물을 다각적으로 평가하고 구체적인 피드백을 제공하세요.

평가 영역:
1. **Factual Feedback**: 리서치 결과물이 참조 문서와 일치하는가?
2. **Logical Feedback**: 논리적 완결성과 구조적 일관성은 어떠한가?
3. **Relevance Feedback**: 사용자 요구사항과의 관련성은 어떠한가?
4. **Depth Feedback**: 정보의 깊이와 포괄성은 어떠한가?

각 영역별로 1-10점 척도로 점수를 매기고, 구체적인 피드백을 제공하세요.
마지막에 전체 종합 점수와 개선 제안을 포함하세요.

응답 형식:
```json
{{
    "evaluation": {{
        "factual_score": 점수,
        "logical_score": 점수,
        "relevance_score": 점수,
        "depth_score": 점수,
        "overall_score": 종합점수
    }},
    "feedback": {{
        "factual_feedback": "구체적인 피드백",
        "logical_feedback": "구체적인 피드백",
        "relevance_feedback": "구체적인 피드백",
        "depth_feedback": "구체적인 피드백"
    }},
    "improvement_suggestions": [
        "개선 제안 1",
        "개선 제안 2",
        "개선 제안 3"
    ],
    "final_report": "전체 종합 평가 및 권장사항"
}}
```
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 전문적인 리서치 비평가입니다. 객관적이고 구체적인 평가를 제공하세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            evaluation_text = response.choices[0].message.content
            
            # JSON 파싱 시도
            try:
                evaluation_data = json.loads(evaluation_text)
            except json.JSONDecodeError:
                # JSON 파싱 실패 시 기본 구조 생성
                evaluation_data = {
                    "evaluation": {
                        "factual_score": 7,
                        "logical_score": 7,
                        "relevance_score": 7,
                        "depth_score": 7,
                        "overall_score": 7
                    },
                    "feedback": {
                        "factual_feedback": "평가 텍스트를 JSON으로 파싱할 수 없어 기본 피드백을 제공합니다.",
                        "logical_feedback": evaluation_text,
                        "relevance_feedback": "원본 평가 텍스트를 확인하세요.",
                        "depth_feedback": "JSON 파싱 오류가 발생했습니다."
                    },
                    "improvement_suggestions": [
                        "평가 결과를 JSON 형식으로 다시 생성하세요.",
                        "구체적인 개선 사항을 제시하세요."
                    ],
                    "final_report": evaluation_text
                }
            
            # 정량적 지표 계산
            if source_documents:
                quantitative_metrics = self._calculate_quantitative_metrics(research_output, source_documents)
                evaluation_data["quantitative_metrics"] = quantitative_metrics
            
            print("--- 리서치 결과물 평가 완료 ---")
            return evaluation_data
            
        except Exception as e:
            print(f"평가 중 오류 발생: {e}")
            return {
                "error": str(e),
                "evaluation": {
                    "overall_score": 0
                },
                "feedback": {
                    "error_feedback": f"평가 중 오류가 발생했습니다: {e}"
                },
                "final_report": "평가를 완료할 수 없었습니다."
            }

class CriticAgent(BaseAgent):
    """리서치 결과 평가 및 피드백 제공 에이전트"""
    
    def __init__(self, model="gpt-4o"):
        super().__init__(
            name="critic",
            description="리서치 결과 평가 및 피드백 제공 에이전트"
        )
        self.required_inputs = ["research_output", "source_documents", "user_profile"]
        self.output_keys = ["evaluation_results", "feedback_report", "critic_metadata"]
        self.critic = ResearchCriticAgent(model)
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """리서치 결과를 평가하고 피드백을 제공합니다."""
        self.log_execution("리서치 결과 평가 시작")
        
        try:
            # 입력 검증
            if not self.validate_inputs(state):
                raise ValueError("필수 입력이 누락되었습니다.")
            
            # 리서치 결과 평가
            research_output = getattr(state, 'research_output', '')
            source_documents = getattr(state, 'source_documents', [])
            user_profile = getattr(state, 'user_profile', '')
            
            evaluation_results = self.critic.evaluate_research_output(
                research_output=research_output,
                source_documents=source_documents,
                user_profile=user_profile
            )
            
            # 결과 저장
            output_filename = f"agent-cast/output/critic/evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(evaluation_results, f, ensure_ascii=False, indent=4)
            
            # 워크플로우 상태 업데이트
            new_state = WorkflowState(
                **{k: v for k, v in state.__dict__.items()},
                evaluation_results=evaluation_results,
                feedback_report=evaluation_results.get('final_report', ''),
                critic_metadata={
                    "overall_score": evaluation_results.get('evaluation', {}).get('overall_score', 'N/A'),
                    "output_file": output_filename
                }
            )
            
            # 워크플로우 상태 업데이트
            new_state = self.update_workflow_status(new_state, "critic_completed")
            
            self.log_execution(f"리서치 결과 평가 완료: 전체 점수 {evaluation_results.get('evaluation', {}).get('overall_score', 'N/A')}/10")
            return new_state
            
        except Exception as e:
            self.log_execution(f"리서치 결과 평가 중 오류 발생: {str(e)}", "ERROR")
            raise

if __name__ == "__main__":
    # 테스트용 코드
    critic = ResearchCriticAgent()
    
    test_research = """
    인공지능의 최신 동향에 대한 연구 결과입니다.
    머신러닝과 딥러닝 기술이 빠르게 발전하고 있으며,
    특히 자연어 처리 분야에서 큰 진전이 있었습니다.
    """
    
    test_sources = [
        "최신 AI 연구 논문들에서 머신러닝 기술 발전이 확인됩니다.",
        "자연어 처리 분야의 발전은 GPT 모델들의 성능 향상으로 입증됩니다."
    ]
    
    test_profile = "AI 연구자, 머신러닝 전문가"
    
    result = critic.evaluate_research_output(test_research, test_sources, test_profile)
    print(json.dumps(result, ensure_ascii=False, indent=2))
