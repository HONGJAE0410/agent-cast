"""Main script for running the multi-agent workflow."""

import asyncio
import sys
from datetime import datetime
from typing import Dict, Any

from .state import WorkflowState
from .constants import WORKFLOW_STEPS, WORKFLOW_STEP_DESCRIPTIONS, WORKFLOW_STEP_ORDER
from .orchestrator_graph import main_workflow


def _get_agent_for_step(step_name: str):
    """단계 이름에 해당하는 에이전트를 동적으로 가져옵니다."""
    try:
        if step_name == "orchestrator":
            from .agents import OrchestratorAgent
            return OrchestratorAgent()
        elif step_name == "personalize":
            from .agents import PersonalizeAgent
            return PersonalizeAgent()
        elif step_name == "query_writer":
            from .agents import QueryWriterAgent
            return QueryWriterAgent()
        elif step_name == "searcher":
            from .agents import SearcherAgent
            return SearcherAgent()
        elif step_name == "db_constructor":
            from .agents import DBConstructorAgent
            return DBConstructorAgent()
        elif step_name == "researcher":
            from .agents import ResearcherAgent
            return ResearcherAgent()
        elif step_name == "critic":
            from .agents import CriticAgent
            return CriticAgent()
        elif step_name == "script_writer":
            from .agents import ScriptWriterAgent
            return ScriptWriterAgent()
        elif step_name == "tts":
            from .agents import TTSAgent
            return TTSAgent()
        else:
            raise ValueError(f"Unknown step: {step_name}")
    except ImportError as e:
        print(f"Failed to import agent for step {step_name}: {e}")
        return None


async def run_workflow(user_query: str) -> Dict[str, Any]:
    """멀티 에이전트 워크플로우를 실행합니다."""
    
    print("🚀 멀티 에이전트 워크플로우 시작")
    print(f"📝 사용자 쿼리: {user_query}")
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    # 초기 상태 생성
    initial_state = WorkflowState(
        user_query=user_query,
        workflow_status={
            "status": "starting",
            "current_step": "initialization",
            "total_steps": len(WORKFLOW_STEP_ORDER),
            "completed_steps": 0,
            "start_timestamp": datetime.now().isoformat()
        }
    )
    
    print(f"📊 워크플로우 정보:")
    print(f"   총 단계 수: {len(WORKFLOW_STEP_ORDER)}")
    print(f"   단계 순서: {' -> '.join(WORKFLOW_STEP_ORDER)}")
    print("-" * 60)
    
    try:
        # 워크플로우 실행
        print("🔄 워크플로우 실행 중...")
        result = await main_workflow.ainvoke(initial_state)
        
        print("✅ 워크플로우 실행 완료!")
        print(f"⏰ 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 결과 요약
        print("\n📋 결과 요약:")
        if hasattr(result, 'audio_file') and result.audio_file:
            print(f"   🎵 오디오 파일: {result.audio_file.get('file_name', 'N/A')}")
            print(f"   ⏱️  재생 시간: {result.audio_file.get('duration', 0)}초")
        
        if hasattr(result, 'podcast_script') and result.podcast_script:
            print(f"   📝 팟캐스트 제목: {result.podcast_script.get('title', 'N/A')}")
            print(f"   ⏱️  예상 재생 시간: {result.podcast_script.get('total_estimated_duration', 0)}분")
        
        if hasattr(result, 'quality_score') and result.quality_score:
            print(f"   🎯 품질 점수: {result.quality_score:.2f}")
        
        return result
        
    except Exception as e:
        print(f"❌ 워크플로우 실행 실패: {e}")
        print(f"⏰ 실패 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        raise


async def run_step_by_step(user_query: str) -> Dict[str, Any]:
    """단계별로 워크플로우를 실행합니다."""
    
    print("🚀 단계별 워크플로우 실행 시작")
    print(f"📝 사용자 쿼리: {user_query}")
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    # 초기 상태 생성
    current_state = WorkflowState(
        user_query=user_query,
        workflow_status={
            "status": "running",
            "current_step": "initialization",
            "total_steps": len(WORKFLOW_STEP_ORDER),
            "completed_steps": 0,
            "start_timestamp": datetime.now().isoformat()
        }
    )
    
    print(f"📊 워크플로우 정보:")
    print(f"   총 단계 수: {len(WORKFLOW_STEP_ORDER)}")
    print(f"   단계 순서: {' -> '.join(WORKFLOW_STEP_ORDER)}")
    print("-" * 60)
    
    try:
        # 각 단계별 실행
        for i, step_name in enumerate(WORKFLOW_STEP_ORDER):
            step_description = WORKFLOW_STEP_DESCRIPTIONS.get(step_name, step_name)
            
            print(f"\n🔄 단계 {i+1}/{len(WORKFLOW_STEP_ORDER)}: {step_name}")
            print(f"   📖 설명: {step_description}")
            print(f"   ⏰ 시작 시간: {datetime.now().strftime('%H:%M:%S')}")
            
            try:
                # 해당 단계의 에이전트 가져오기
                agent = _get_agent_for_step(step_name)
                if agent is None:
                    print(f"   ❌ 에이전트를 찾을 수 없음: {step_name}")
                    continue
                
                # 단계 실행
                current_state = await agent.process(current_state)
                
                # 상태 업데이트
                current_state.workflow_status["completed_steps"] = i + 1
                current_state.workflow_status["current_step"] = step_name
                
                print(f"   ✅ 단계 완료: {step_name}")
                print(f"   ⏰ 완료 시간: {datetime.now().strftime('%H:%M:%S')}")
                
                # 중간 결과 출력
                if hasattr(current_state, 'personal_info') and current_state.personal_info:
                    print(f"   📊 개인화 정보 수집 완료")
                if hasattr(current_state, 'crawled_data') and current_state.crawled_data:
                    print(f"   🌐 웹 크롤링 완료: {len(current_state.crawled_data)}개 데이터")
                if hasattr(current_state, 'vector_db') and current_state.vector_db:
                    print(f"   🗄️  벡터 DB 구축 완료")
                if hasattr(current_state, 'research_results') and current_state.research_results:
                    print(f"   🔍 연구 결과 분석 완료")
                if hasattr(current_state, 'podcast_script') and current_state.podcast_script:
                    print(f"   📝 팟캐스트 대본 생성 완료")
                if hasattr(current_state, 'audio_file') and current_state.audio_file:
                    print(f"   🎵 오디오 생성 완료")
                
            except Exception as e:
                print(f"   ❌ 단계 실행 실패: {step_name} - {e}")
                print(f"   ⏰ 실패 시간: {datetime.now().strftime('%H:%M:%S')}")
                # 에러가 발생해도 다음 단계로 진행
                continue
        
        print("\n✅ 단계별 워크플로우 실행 완료!")
        print(f"⏰ 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 최종 결과 요약
        print("\n📋 최종 결과 요약:")
        if hasattr(current_state, 'audio_file') and current_state.audio_file:
            print(f"   🎵 오디오 파일: {current_state.audio_file.get('file_name', 'N/A')}")
            print(f"   ⏱️  재생 시간: {current_state.audio_file.get('duration', 0)}초")
        
        if hasattr(current_state, 'podcast_script') and current_state.podcast_script:
            print(f"   📝 팟캐스트 제목: {current_state.podcast_script.get('title', 'N/A')}")
            print(f"   ⏱️  예상 재생 시간: {current_state.podcast_script.get('total_estimated_duration', 0)}분")
        
        if hasattr(current_state, 'quality_score') and current_state.quality_score:
            print(f"   🎯 품질 점수: {current_state.quality_score:.2f}")
        
        return current_state
        
    except Exception as e:
        print(f"❌ 단계별 워크플로우 실행 실패: {e}")
        print(f"⏰ 실패 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        raise


def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("사용법: python -m langgraph_mcp.run_workflow <사용자_쿼리>")
        print("예시: python -m langgraph_mcp.run_workflow 'AI 연구 동향에 대한 팟캐스트를 만들어주세요'")
        sys.exit(1)
    
    user_query = sys.argv[1]
    
    try:
        # 기본 워크플로우 실행
        result = asyncio.run(run_workflow(user_query))
        print("\n🎉 워크플로우가 성공적으로 완료되었습니다!")
        
    except KeyboardInterrupt:
        print("\n⏹️  사용자에 의해 워크플로우가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 워크플로우 실행 중 오류가 발생했습니다: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
