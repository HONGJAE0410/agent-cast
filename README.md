# 🎙️ Agent-Cast | 에이전트 기반 AI 트렌드 팟캐스트 자동화

AI 연구 동향을 자동으로 분석하고 팟캐스트를 생성하는 멀티 에이전트 시스템입니다.

## 🚀 빠른 시작

```bash
# 1. 저장소 클론
git clone <repository-url>
cd agent-cast

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 변수 설정
cp env_example.txt .env
# .env 파일에 API 키 입력 (아래 섹션 참조)

# 4. 워크플로우 실행
python -m agent-cast.run_workflow "AI 연구 동향에 대한 팟캐스트를 만들어주세요"
```

## 🏗️ 시스템 구조

### 📁 프로젝트 구조
```
agent-cast/
├── __init__.py                    - 메인 패키지 초기화
├── state.py                       - 상태 관리 시스템
├── orchestrator_graph.py          - LangGraph 워크플로우 정의
├── run_workflow.py                - 워크플로우 실행 엔진
├── mcp_config.yaml                - MCP 서버 설정
├── test_mcp_integration.py        - MCP 통합 테스트
├── README_WORKFLOW.md             - 이 파일
├── agents/                        - 🤖 에이전트 클래스들
│   ├── base_agent.py             - 기본 에이전트 클래스
│   ├── orchestrator_agent.py     - 워크플로우 조율자
│   ├── personalize_agent.py      - 사용자 맞춤화
│   ├── query_writer_agent.py     - 검색 쿼리 생성
│   ├── searcher_agent.py         - 웹 크롤링
│   ├── db_constructor_agent.py   - 벡터 DB 구축
│   ├── researcher_agent.py       - RAG 검색 및 분석
│   ├── critic_agent.py           - 품질 검토
│   ├── script_writer_agent.py    - 팟캐스트 스크립트 작성
│   └── tts_agent.py              - 음성 변환
├── constants/                     - ⚙️ 시스템 상수
│   ├── agents.py                 - 에이전트 설정
│   ├── mcp.py                    - MCP 관련 상수
│   ├── workflow.py               - 워크플로우 설정
│   ├── ai_models.py              - AI 모델 설정
│   ├── prompts.py                - AI 프롬프트
│   └── configuration.py          - 시스템 설정
└── mcp/                           - 🔌 MCP 서비스 연결
    ├── base_mcp.py               - 기본 MCP 클래스
    ├── mcp_manager.py            - MCP 서비스 관리자
    ├── slack_mcp.py              - Slack 연결
    ├── notion_mcp.py             - Notion 연결
    └── gmail_mcp.py              - Gmail 연결
```

### 🔄 워크플로우 흐름
```
사용자 쿼리 → Orchestrator → Personalize → Searcher → QueryWriter → 
DBConstructor → Researcher → Critic → ScriptWriter → TTS → 🎵 오디오
```

## 🤖 에이전트 설명

| 에이전트 | 역할 | 주요 기능 |
|---------|------|-----------|
| **Orchestrator** | 🎭 워크플로우 조율 | 전체 프로세스 관리 및 단계별 진행 |
| **Personalize** | 👤 사용자 맞춤화 | Slack/Notion/Gmail에서 개인 정보 수집 |
| **Searcher** | 🌐 웹 크롤링 | TechCrunch, AI Times, arXiv 등에서 정보 수집 |
| **QueryWriter** | 🔍 쿼리 생성 | RAG 검색을 위한 최적화된 쿼리 생성 |
| **DBConstructor** | 🗄️ 벡터 DB 구축 | 수집된 데이터를 벡터화하여 저장 |
| **Researcher** | 📚 RAG 검색 | 벡터 DB에서 관련 정보 검색 및 분석 |
| **Critic** | ✅ 품질 검토 | 연구 결과의 정확성 및 신뢰성 평가 |
| **ScriptWriter** | 📝 스크립트 작성 | 연구 결과를 팟캐스트 대본으로 변환 |
| **TTS** | 🎵 음성 변환 | 텍스트를 자연스러운 음성으로 변환 |

## ⚙️ 설정

### 환경 변수 (`.env`)
```env
# OpenAI API Key (for Critic Agent)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API Key (for Script Writer Agent)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google API Key (for Narrator Agent)
GOOGLE_API_KEY=your_google_api_key_here

# Perplexity API Key (for Searcher Agent)
PERPLEXITY_API_KEY=your_perplexity_api_key_here

# Database Configuration (if needed)
DATABASE_URL=your_database_url_here

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=agent-cast.log

# Output Configuration
OUTPUT_BASE_PATH=agent-cast/output
```

### 🔑 API 키 설정 가이드

1. **OpenAI API Key**
   - [OpenAI Platform](https://platform.openai.com/api-keys)에서 발급
   - Critic Agent에서 사용

2. **Anthropic API Key**
   - [Anthropic Console](https://console.anthropic.com/)에서 발급
   - Script Writer Agent에서 사용

3. **Google API Key**
   - [Google AI Studio](https://makersuite.google.com/app/apikey)에서 발급
   - Narrator Agent에서 사용

4. **Perplexity API Key**
   - [Perplexity Settings](https://www.perplexity.ai/settings/api)에서 발급
   - Searcher Agent에서 사용

⚠️ **보안 주의사항**
- `.env` 파일은 절대 Git에 커밋하지 마세요
- API 키를 안전하게 보관하고 정기적으로 갱신하세요
- 프로덕션 환경에서는 환경 변수를 사용하세요

### MCP 설정 (`mcp_config.yaml`)
```yaml
mcpServers:
  slack:
    command: slack-mcp-server
    args: ["--token", "YOUR_SLACK_BOT_TOKEN"]
  notion:
    command: notion-mcp-server
    args: ["--token", "YOUR_NOTION_TOKEN"]
  gmail:
    command: gmail-mcp-server
    args: ["--credentials", "path/to/credentials.json"]
```

## 📖 사용법

### 기본 실행
```python
from agent-cast.run_workflow import run_workflow

# 전체 워크플로우 실행
result = await run_workflow("AI 연구 동향에 대한 팟캐스트를 만들어주세요")
```

### 단계별 실행
```python
from agent-cast.run_workflow import run_step_by_step

# 특정 단계까지 실행
result = await run_step_by_step("AI 연구 동향에 대한 팟캐스트를 만들어주세요", steps=["personalize", "searcher"])
```

### MCP 통합 테스트
```bash
python -m agent-cast.test_mcp_integration
```

## 🔧 개발

### 새로운 에이전트 추가
```python
# 1. agents/ 디렉토리에 새 에이전트 클래스 생성
from .base_agent import BaseAgent

class NewAgent(BaseAgent):
    async def process(self, state: WorkflowState) -> WorkflowState:
        # 에이전트 로직 구현
        pass

# 2. orchestrator_graph.py에 노드 추가
workflow.add_node("NEW_AGENT", new_agent.process)

# 3. 엣지 연결
workflow.add_edge("PREVIOUS_AGENT", "NEW_AGENT")
```

### 새로운 MCP 서버 추가
```python
# 1. mcp/ 디렉토리에 새 MCP 클래스 생성
from .base_mcp import BaseMCP

class NewMCP(BaseMCP):
    async def connect(self) -> bool:
        # 연결 로직 구현
        pass

# 2. mcp_manager.py에 서비스 추가
self.integrations["new_service"] = NewMCP(config)
```

## 🧪 테스트

```bash
# 전체 테스트
python -m pytest

# MCP 통합 테스트
python -m agent-cast.test_mcp_integration

# 워크플로우 테스트
python -m agent-cast.run_workflow "테스트 쿼리"
```

## 🚨 문제 해결

### 일반적인 문제
- **MCP 연결 실패**: 서버 상태 및 인증 정보 확인
- **에이전트 실행 오류**: 의존성 및 설정 파일 확인
- **메모리 부족**: 벡터 DB 설정 및 청킹 크기 조정

### 로그 확인
```bash
# 디버그 모드로 실행
export LOG_LEVEL=DEBUG
python -m agent-cast.run_workflow "쿼리"
```

## 📈 성능 최적화

- **병렬 처리**: MCP 통합 및 에이전트 병렬 실행
- **캐싱**: MCP 응답 및 임베딩 결과 캐싱
- **리소스 관리**: 연결 풀 및 메모리 사용량 최적화

## 🔮 향후 계획

- [ ] 실제 MCP 서버 연동
- [ ] OpenAI API 연동
- [ ] 벡터 DB 연동
- [ ] 웹 크롤링 도구 구현
- [ ] 다국어 지원
- [ ] 실시간 모니터링

## 📄 라이선스

MIT License

## 🤝 기여하기

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**참고**: 이 시스템은 현재 개발 중이며, 일부 기능은 시뮬레이션 모드로 동작합니다.
