"""Script Writer Agent for creating podcast scripts from research content."""

import os
import anthropic
import argparse
from dotenv import load_dotenv

from .base_agent import BaseAgent
from ..state import WorkflowState

# --- 환경 변수 로드 ---
load_dotenv()  # .env 파일에서 환경 변수 로드

def read_research_file(filepath):
    """지정된 경로의 리서치 텍스트 파일을 읽어 내용을 반환합니다."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"오류: 파일을 찾을 수 없습니다 - {filepath}")
        return None
    except Exception as e:
        print(f"오류: 파일을 읽는 중 문제가 발생했습니다 - {e}")
        return None

def generate_podcast_script(research_content, api_key):
    """리서치 내용을 바탕으로 팟캐스트 대본을 생성합니다."""
    
    # Claude API 클라이언트 설정
    client = anthropic.Anthropic(api_key=api_key)
    
    # 프롬프트 구성
    prompt = f"""## 지시문
    아래의 리서치 결과를 바탕으로 2명의 화자가 정보를 알기 쉽게 전달하는 팟캐스트의 대본을 작성해주세요.
    앞뒤의 설명 없이 **대본**만 작성하면 됩니다.

    ## 제약조건
    - 대본의 분량은 10,000자입니다.
    - 화자1이 진행자, 화자2가 리서치 역할을 합니다.
    - 화자1이 질문하고 화두를 던지면, 화자2가 답변하며 인사이트를 공유합니다.
    - 적절하게 감탄사나 반응하는 리액션도 넣습니다.
    - 출력포맷의 인물은 Joe와 Jane이라 부르지만 실제 대본에서는 서로를 김민열, 배한준이라는 이름으로 부릅니다.
    - 시작할 때 소개하는 팟캐스트의 제목은 "비타민 트렌드"입니다.

    ## 리서치 결과
    {research_content}

    ## 출력 포맷
    Joe: ...
    Jane: ...
    Joe: ..."""

    try:
        print("팟캐스트 대본을 생성하는 중...")
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        if response.content and len(response.content) > 0:
            return response.content[0].text
        else:
            print("오류: 대본 생성에 실패했습니다.")
            return None
            
    except Exception as e:
        print(f"오류: 대본 생성 중 문제가 발생했습니다 - {e}")
        return None

def save_script_to_file(script_content, output_filename="podcast_script.txt"):
    """생성된 대본을 파일로 저장합니다."""
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(script_content)
        print(f"대본이 '{output_filename}' 파일로 저장되었습니다.")
        return True
    except Exception as e:
        print(f"오류: 파일 저장 중 문제가 발생했습니다 - {e}")
        return False

def main():
    """메인 실행 함수"""
    # 명령행 인자 설정
    parser = argparse.ArgumentParser(description="리서치 결과를 바탕으로 팟캐스트 대본을 생성합니다.")
    parser.add_argument("research_file", type=str, help="리서치 결과 텍스트 파일의 경로")
    parser.add_argument("--output", "-o", type=str, default="podcast_script.txt", 
                       help="출력 파일명 (기본값: podcast_script.txt)")
    parser.add_argument("--api-key", type=str, help="Claude API 키")
    args = parser.parse_args()

    # API 키 입력 받기
    api_key = args.api_key
    if not api_key:
        api_key = input("Claude API 키를 입력하세요: ").strip()
        if not api_key:
            print("오류: API 키가 필요합니다.")
            return

    # 리서치 파일 읽기
    research_content = read_research_file(args.research_file)
    if not research_content:
        return

    # 팟캐스트 대본 생성
    script = generate_podcast_script(research_content, api_key)
    if not script:
        return

    # 대본을 파일로 저장
    save_script_to_file(script, args.output)

class ScriptWriterAgent(BaseAgent):
    """팟캐스트 대본 작성 에이전트"""
    
    def __init__(self, api_key: str = None):
        super().__init__(
            name="script_writer",
            description="팟캐스트 대본 작성 에이전트"
        )
        self.required_inputs = ["research_content"]
        self.output_keys = ["podcast_script", "script_metadata"]
        self.api_key = api_key
    
    async def process(self, state: WorkflowState) -> WorkflowState:
        """리서치 내용을 바탕으로 팟캐스트 대본을 생성합니다."""
        self.log_execution("팟캐스트 대본 작성 시작")
        
        try:
            # 입력 검증
            if not self.validate_inputs(state):
                raise ValueError("필수 입력이 누락되었습니다.")
            
            # 리서치 내용 가져오기
            research_content = getattr(state, 'research_content', '')
            if not research_content:
                raise ValueError("대본을 작성할 리서치 내용이 없습니다.")
            
            # API 키 확인
            if not self.api_key:
                self.api_key = os.environ.get("ANTHROPIC_API_KEY")
                if not self.api_key:
                    raise ValueError("Anthropic API 키가 필요합니다.")
            
            # 팟캐스트 대본 생성
            podcast_script = generate_podcast_script(research_content, self.api_key)
            if not podcast_script:
                raise ValueError("팟캐스트 대본 생성에 실패했습니다.")
            
            # 결과 저장
            output_filename = f"agent-cast/output/script_writer/podcast_script_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            save_script_to_file(podcast_script, output_filename)
            
            # 워크플로우 상태 업데이트
            new_state = WorkflowState(
                **{k: v for k, v in state.__dict__.items()},
                podcast_script=podcast_script,
                script_metadata={
                    "script_length": len(podcast_script),
                    "output_file": output_filename
                }
            )
            
            # 워크플로우 상태 업데이트
            new_state = self.update_workflow_status(new_state, "script_writer_completed")
            
            self.log_execution(f"팟캐스트 대본 작성 완료: {len(podcast_script)}자")
            return new_state
            
        except Exception as e:
            self.log_execution(f"팟캐스트 대본 작성 중 오류 발생: {str(e)}", "ERROR")
            raise

if __name__ == "__main__":
    main()
