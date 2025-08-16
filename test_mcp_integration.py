"""Test script for MCP integrations."""

import asyncio
import sys
from typing import Dict, Any

from .integrations import MCPManager
from .constants import MCP_SERVER_TYPES, MCP_SERVER_DEFAULTS


async def test_mcp_manager():
    """MCP 매니저를 테스트합니다."""
    print("🧪 MCP 매니저 테스트 시작")
    print("-" * 50)
    
    try:
        # MCP 매니저 초기화
        manager = MCPManager()
        
        # 요약 정보 출력
        summary = manager.get_summary()
        print(f"📊 MCP 매니저 요약:")
        print(f"   총 통합 수: {summary['total_integrations']}")
        print(f"   통합 이름: {', '.join(summary['integration_names'])}")
        print(f"   설정 키: {', '.join(summary['config_keys'])}")
        
        # 연결 상태 확인
        print(f"\n🔌 연결 상태:")
        for name, status in summary['connection_status'].items():
            print(f"   {name}: {status}")
        
        print("✅ MCP 매니저 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ MCP 매니저 테스트 실패: {e}")
        return False


async def test_individual_integrations():
    """개별 MCP 통합들을 테스트합니다."""
    print("\n🧪 개별 MCP 통합 테스트 시작")
    print("-" * 50)
    
    # 테스트 설정
    test_config = {
        "mcpServers": {
            MCP_SERVER_TYPES["SLACK"]: {
                **MCP_SERVER_DEFAULTS[MCP_SERVER_TYPES["SLACK"]],
                "args": ["--token", "test-token"],
                "env": {"SLACK_BOT_TOKEN": "test-token"}
            },
            MCP_SERVER_TYPES["NOTION"]: {
                **MCP_SERVER_DEFAULTS[MCP_SERVER_TYPES["NOTION"]],
                "args": ["--token", "test-token"],
                "env": {"NOTION_INTEGRATION_TOKEN": "test-token"}
            },
            MCP_SERVER_TYPES["GMAIL"]: {
                **MCP_SERVER_DEFAULTS[MCP_SERVER_TYPES["GMAIL"]],
                "args": ["--credentials", "test-credentials.json"],
                "env": {"GMAIL_CREDENTIALS_FILE": "test-credentials.json"}
            }
        }
    }
    
    manager = MCPManager(test_config)
    results = {}
    
    # Slack 통합 테스트
    print("\n📱 Slack 통합 테스트:")
    try:
        slack_info = await manager.get_slack_info()
        print(f"   ✅ 워크스페이스: {slack_info.get('workspace_info', {}).get('workspace_name', 'N/A')}")
        print(f"   ✅ 채널 수: {len(slack_info.get('channels', []))}")
        print(f"   ✅ 연결 상태: {slack_info.get('connection_status', False)}")
        results['slack'] = True
    except Exception as e:
        print(f"   ❌ 실패: {e}")
        results['slack'] = False
    
    # Notion 통합 테스트
    print("\n📚 Notion 통합 테스트:")
    try:
        notion_info = await manager.get_notion_info()
        print(f"   ✅ 워크스페이스: {notion_info.get('workspace_info', {}).get('workspace_name', 'N/A')}")
        print(f"   ✅ 데이터베이스 수: {len(notion_info.get('databases', []))}")
        print(f"   ✅ 연결 상태: {notion_info.get('connection_status', False)}")
        results['notion'] = True
    except Exception as e:
        print(f"   ❌ 실패: {e}")
        results['notion'] = False
    
    # Gmail 통합 테스트
    print("\n📧 Gmail 통합 테스트:")
    try:
        gmail_info = await manager.get_gmail_info()
        print(f"   ✅ 이메일: {gmail_info.get('profile_info', {}).get('email_address', 'N/A')}")
        print(f"   ✅ 라벨 수: {len(gmail_info.get('labels', []))}")
        print(f"   ✅ 연결 상태: {gmail_info.get('connection_status', False)}")
        results['gmail'] = True
    except Exception as e:
        print(f"   ❌ 실패: {e}")
        results['notion'] = False
    
    return results


async def test_health_checks():
    """모든 MCP 통합의 상태를 확인합니다."""
    print("\n🧪 MCP 통합 상태 확인 테스트 시작")
    print("-" * 50)
    
    try:
        manager = MCPManager()
        health_results = await manager.health_check_all()
        
        print("📊 상태 확인 결과:")
        for name, health in health_results.items():
            status = health.get('status', 'unknown')
            message = health.get('message', 'No message')
            print(f"   {name}: {status} - {message}")
        
        print("✅ 상태 확인 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ 상태 확인 테스트 실패: {e}")
        return False


async def test_fallback_mechanisms():
    """폴백 메커니즘을 테스트합니다."""
    print("\n🧪 폴백 메커니즘 테스트 시작")
    print("-" * 50)
    
    try:
        manager = MCPManager()
        
        # 모든 정보 수집 시도 (연결 실패 시 폴백 데이터 사용)
        print("📡 모든 MCP 통합에서 정보 수집 시도...")
        all_info = await manager.get_all_info()
        
        print("📊 수집된 정보 요약:")
        for service, info in all_info.items():
            if service == "overall_status":
                continue
            
            if "error" in info:
                print(f"   {service}: ❌ 오류 - {info['error']}")
            else:
                print(f"   {service}: ✅ 성공 - 데이터 수집 완료")
        
        overall_status = all_info.get("overall_status", {})
        print(f"\n🔌 전체 상태:")
        print(f"   총 통합 수: {overall_status.get('total_integrations', 0)}")
        print(f"   연결된 통합 수: {overall_status.get('connected_count', 0)}")
        
        print("✅ 폴백 메커니즘 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ 폴백 메커니즘 테스트 실패: {e}")
        return False


async def main():
    """메인 테스트 함수"""
    print("🚀 MCP 통합 테스트 시작")
    print("=" * 60)
    
    test_results = {}
    
    # 1. MCP 매니저 테스트
    test_results['manager'] = await test_mcp_manager()
    
    # 2. 개별 통합 테스트
    integration_results = await test_individual_integrations()
    test_results['integrations'] = integration_results
    
    # 3. 상태 확인 테스트
    test_results['health_check'] = await test_health_checks()
    
    # 4. 폴백 메커니즘 테스트
    test_results['fallback'] = await test_fallback_mechanisms()
    
    # 최종 결과 요약
    print("\n" + "=" * 60)
    print("📋 최종 테스트 결과 요약")
    print("=" * 60)
    
    # 매니저 테스트 결과
    print(f"🔧 MCP 매니저: {'✅ 성공' if test_results['manager'] else '❌ 실패'}")
    
    # 개별 통합 테스트 결과
    print(f"🔌 개별 통합:")
    for service, result in test_results['integrations'].items():
        status = "✅ 성공" if result else "❌ 실패"
        print(f"   {service}: {status}")
    
    # 기타 테스트 결과
    print(f"🏥 상태 확인: {'✅ 성공' if test_results['health_check'] else '❌ 실패'}")
    print(f"🔄 폴백 메커니즘: {'✅ 성공' if test_results['fallback'] else '❌ 실패'}")
    
    # 성공률 계산
    total_tests = len(test_results['integrations']) + 3  # integrations + manager + health_check + fallback
    successful_tests = sum(1 for result in test_results['integrations'].values() if result)
    successful_tests += sum(1 for key, result in test_results.items() if key != 'integrations' and result)
    
    success_rate = (successful_tests / total_tests) * 100
    print(f"\n📊 전체 성공률: {success_rate:.1f}% ({successful_tests}/{total_tests})")
    
    if success_rate >= 80:
        print("🎉 테스트가 성공적으로 완료되었습니다!")
    elif success_rate >= 60:
        print("⚠️  테스트가 부분적으로 성공했습니다. 일부 기능에 문제가 있을 수 있습니다.")
    else:
        print("❌ 테스트가 실패했습니다. 시스템을 점검해주세요.")
    
    return success_rate >= 60


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  테스트가 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류가 발생했습니다: {e}")
        sys.exit(1)
