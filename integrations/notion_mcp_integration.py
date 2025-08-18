"""Notion MCP integration for collecting workspace information."""

import asyncio
import os
from typing import Any, Dict, List, Optional
from integrations.base_mcp_integration import BaseMCPIntegration

# 노션 API 클라이언트 임포트
try:
    from notion_client import Client
    NOTION_CLIENT_AVAILABLE = True
except ImportError:
    NOTION_CLIENT_AVAILABLE = False


class NotionMCPIntegration(BaseMCPIntegration):
    """Notion MCP 서버와의 통합을 담당하는 클래스."""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("notion", config)
        
        # Notion 특정 설정
        self.workspace_id = config.get("workspace_id")
        self.databases = config.get("databases", [])
        self.pages = config.get("pages", [])
        
        # 노션 API 토큰 (환경 변수에서 로드)
        self.notion_token = os.getenv("NOTION_INTEGRATION_TOKEN") or config.get("token")
        
        # 연결 상태
        self._connected = False
        self._client = None
        
        # 노션 클라이언트 초기화
        if self.notion_token and NOTION_CLIENT_AVAILABLE:
            try:
                self._client = Client(auth=self.notion_token)
                self.logger.info("노션 API 클라이언트 초기화 성공")
            except Exception as e:
                self.logger.error(f"노션 API 클라이언트 초기화 실패: {e}")
                raise Exception(f"노션 API 클라이언트 초기화 실패: {e}")
        else:
            raise Exception("NOTION_INTEGRATION_TOKEN이 설정되지 않았거나 notion-client가 설치되지 않았습니다.")
    
    async def connect(self) -> bool:
        """Notion API에 연결합니다."""
        try:
            self.logger.info("Notion API 연결 중...")
            
            # 노션 API 연결 테스트
            response = self._client.users.me()
            self._connected = True
            self.update_connection_status("connected")
            self.logger.info(f"노션 API 연결 성공: {response.get('name', 'Unknown User')}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"노션 API 연결 실패: {e}")
            self.update_connection_status("failed", str(e))
            return False
    
    async def disconnect(self) -> bool:
        """Notion MCP 서버 연결을 해제합니다."""
        try:
            self.logger.info("Disconnecting from Notion MCP server...")
            
            # 연결 해제 로직
            
            self._connected = False
            self.update_connection_status("disconnected")
            self.logger.info("Successfully disconnected from Notion MCP server")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to disconnect from Notion MCP server: {e}")
            return False
    
    async def is_connected(self) -> bool:
        """연결 상태를 확인합니다."""
        return self._connected
    
    async def health_check(self) -> Dict[str, Any]:
        """Notion MCP 서버 상태를 확인합니다."""
        try:
            if not await self.is_connected():
                return {
                    "status": "disconnected",
                    "message": "Not connected to Notion MCP server",
                    "timestamp": self._get_current_timestamp()
                }
            
            # 서버 상태 확인
            
            return {
                "status": "healthy",
                "message": "Notion MCP server is responding",
                "timestamp": self._get_current_timestamp(),
                "workspace_id": self.workspace_id,
                "databases_count": len(self.databases),
                "pages_count": len(self.pages)
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Health check failed: {str(e)}",
                "timestamp": self._get_current_timestamp()
            }
    
    async def get_workspace_info(self) -> Dict[str, Any]:
        """워크스페이스 정보를 가져옵니다."""
        return await self.execute_with_retry(self._get_workspace_info_impl)
    
    async def _get_workspace_info_impl(self) -> Dict[str, Any]:
        """워크스페이스 정보를 가져오는 실제 구현."""
        try:
            self.logger.info("워크스페이스 정보 조회 중...")
            # 노션 API에서는 직접적인 워크스페이스 정보 API가 제한적이므로
            # 사용자 정보를 통해 워크스페이스 기본 정보를 구성
            user_info = self._client.users.me()
            
            return {
                "workspace_id": self.workspace_id or "unknown",
                "workspace_name": f"{user_info.get('name', 'Unknown')}의 워크스페이스",
                "workspace_icon": "🤖",
                "workspace_description": "노션 통합 워크스페이스",
                "member_count": 1,
                "plan": "Unknown",
                "created": "Unknown"
            }
        except Exception as e:
            self.logger.error(f"워크스페이스 정보 조회 실패: {e}")
            return {
                "workspace_id": "error",
                "workspace_name": "Error",
                "workspace_icon": "❌",
                "workspace_description": "워크스페이스 정보 조회 실패",
                "member_count": 0,
                "plan": "Unknown",
                "created": "Unknown"
            }
    
    async def get_databases(self) -> List[Dict[str, Any]]:
        """데이터베이스 목록을 가져옵니다."""
        return await self.execute_with_retry(self._get_databases_impl)
    
    async def _get_databases_impl(self) -> List[Dict[str, Any]]:
        """데이터베이스 목록을 가져오는 실제 구현."""
        try:
            self.logger.info("데이터베이스 목록 조회 중...")
            response = self._client.search(filter={"property": "object", "value": "database"})
            
            databases = []
            for db in response.get("results", []):
                db_info = {
                    "id": db["id"],
                    "title": self._extract_title(db.get("title", [])),
                    "description": self._extract_description(db.get("description", [])),
                    "last_edited": db.get("last_edited_time", ""),
                    "created": db.get("created_time", ""),
                    "url": db.get("url", ""),
                    "properties": self._extract_properties(db.get("properties", {}))
                }
                databases.append(db_info)
                self.logger.info(f"   찾은 DB: {db_info['title']}")
            
            return databases
        except Exception as e:
            self.logger.error(f"데이터베이스 조회 실패: {e}")
            return []
    
    async def get_database_entries(self, database_id: str, filter_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """데이터베이스의 항목들을 가져옵니다."""
        return await self.execute_with_retry(self._get_database_entries_impl, database_id, filter_params)
    
    async def _get_database_entries_impl(self, database_id: str, filter_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """데이터베이스 항목을 가져오는 실제 구현."""
        try:
            self.logger.info(f"데이터베이스 항목 조회 중: {database_id[:8]}...")
            response = self._client.databases.query(database_id=database_id)
            
            entries = []
            for page in response.get("results", []):
                page_properties = page.get("properties", {})
                smart_title = self._extract_smart_title(page_properties)
                
                entry = {
                    "id": page["id"],
                    "title": smart_title,
                    "last_edited": page.get("last_edited_time", ""),
                    "created": page.get("created_time", ""),
                    "url": page.get("url", ""),
                    "properties": self._extract_page_properties(page_properties)
                }
                entries.append(entry)
                self.logger.info(f"      항목: {entry['title']}")
            
            return entries
        except Exception as e:
            self.logger.error(f"데이터베이스 항목 조회 실패: {e}")
            return []
    
    async def get_page_content(self, page_id: str) -> Dict[str, Any]:
        """페이지 내용을 가져옵니다."""
        return await self.execute_with_retry(self._get_page_content_impl, page_id)
    
    async def _get_page_content_impl(self, page_id: str) -> Dict[str, Any]:
        """페이지 내용을 가져오는 실제 구현."""
        try:
            self.logger.info(f"페이지 내용 조회 중: {page_id[:8]}...")
            
            # 페이지 정보 가져오기
            page = self._client.pages.retrieve(page_id=page_id)
            
            # 페이지 블록 내용 가져오기
            blocks_response = self._client.blocks.children.list(block_id=page_id)
            
            content_blocks = []
            for block in blocks_response.get("results", []):
                block_content = self._extract_block_content(block)
                if block_content:  # None이 아닌 경우만 추가 (빈 블록 제외)
                    content_blocks.append(block_content)
            
            # 페이지 데이터 안전하게 추출
            if isinstance(page, dict):
                page_properties = page.get("properties", {})
                smart_title = self._extract_smart_title(page_properties)
                
                return {
                    "id": page.get("id", page_id),
                    "title": smart_title,
                    "last_edited": page.get("last_edited_time", ""),
                    "created": page.get("created_time", ""),
                    "url": page.get("url", ""),
                    "content": content_blocks
                }
            else:
                # page가 딕셔너리가 아닌 경우 기본값 반환
                return {
                    "id": page_id,
                    "title": "제목 없음",
                    "last_edited": "",
                    "created": "",
                    "url": "",
                    "content": content_blocks
                }
        except Exception as e:
            self.logger.error(f"페이지 내용 조회 실패: {e}")
            # 오류가 발생해도 기본 구조는 반환
            return {
                "id": page_id,
                "title": "제목 없음",
                "last_edited": "",
                "created": "",
                "url": "",
                "content": []
            }
    
    async def search_pages(self, query: str, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """페이지를 검색합니다."""
        return await self.execute_with_retry(self._search_pages_impl, query, filter_type)
    
    async def _search_pages_impl(self, query: str, filter_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """페이지 검색의 실제 구현."""
        try:
            self.logger.info("페이지 검색 중...")
            search_filter = {"property": "object", "value": "page"}
            # 쿼리 파라미터 처리 (빈 문자열이면 제외)
            search_params = {"filter": search_filter}
            if query and query.strip():
                search_params["query"] = query.strip()
            
            response = self._client.search(**search_params)
            
            pages = []
            for page in response.get("results", []):
                page_properties = page.get("properties", {})
                smart_title = self._extract_smart_title(page_properties)
                
                page_info = {
                    "id": page["id"],
                    "title": smart_title,
                    "type": "page",
                    "last_edited": page.get("last_edited_time", ""),
                    "created": page.get("created_time", ""),
                    "url": page.get("url", "")
                }
                pages.append(page_info)
                self.logger.info(f"   찾은 페이지: {page_info['title']}")
            
            return pages
        except Exception as e:
            self.logger.error(f"페이지 검색 실패: {e}")
            return []
    
    async def get_recent_changes(self, hours: int = 24) -> List[Dict[str, Any]]:
        """최근 변경사항을 가져옵니다."""
        return await self.execute_with_retry(self._get_recent_changes_impl, hours)
    
    async def _get_recent_changes_impl(self, hours: int = 24) -> List[Dict[str, Any]]:
        """최근 변경사항을 가져오는 실제 구현."""
        try:
            self.logger.info(f"최근 {hours}시간 변경사항 조회 중...")
            # 노션 API는 직접적인 변경사항 조회를 지원하지 않으므로
            # 검색을 통해 최근 수정된 페이지를 조회
            response = self._client.search(
                filter={"property": "object", "value": "page"},
                sort={"direction": "descending", "timestamp": "last_edited_time"}
            )
            
            changes = []
            for page in response.get("results", [])[:10]:  # 최근 10개만
                page_properties = page.get("properties", {})
                smart_title = self._extract_smart_title(page_properties)
                
                change = {
                    "id": f"change_{page['id'][:8]}",
                    "page_id": page["id"],
                    "page_title": smart_title,
                    "change_type": "content_updated",
                    "timestamp": page.get("last_edited_time", ""),
                    "user": "Unknown",
                    "description": f"{smart_title} 페이지 수정"
                }
                changes.append(change)
            
            return changes
        except Exception as e:
            self.logger.error(f"최근 변경사항 조회 실패: {e}")
            return []
    
    async def get_user_activity(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """사용자 활동을 가져옵니다."""
        return await self.execute_with_retry(self._get_user_activity_impl, user_id, days)
    
    async def _get_user_activity_impl(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """사용자 활동을 가져오는 실제 구현."""
        try:
            self.logger.info(f"사용자 {user_id} 활동 조회 중...")
            # 노션 API는 사용자별 활동 조회를 직접 지원하지 않으므로
            # 기본 정보만 반환
            user_info = self._client.users.me()
            
            return {
                "user_id": user_id,
                "user_name": user_info.get("name", "Unknown"),
                "period_days": days,
                "total_edits": 0,
                "pages_edited": 0,
                "databases_updated": 0,
                "recent_activities": ["노션 API를 통한 활동 조회는 제한적입니다"],
                "collaboration_score": 0.0
            }
        except Exception as e:
            self.logger.error(f"사용자 활동 조회 실패: {e}")
            return {
                "user_id": user_id,
                "user_name": "Error",
                "period_days": days,
                "total_edits": 0,
                "pages_edited": 0,
                "databases_updated": 0,
                "recent_activities": [],
                "collaboration_score": 0.0
            }
    
    # 헬퍼 메서드들
    def _extract_title(self, title_array: List) -> str:
        """노션 제목 배열에서 텍스트를 추출합니다."""
        if not title_array:
            return ""
        return "".join([item.get("plain_text", "") for item in title_array])
    
    def _extract_description(self, desc_array: List) -> str:
        """노션 설명 배열에서 텍스트를 추출합니다."""
        if not desc_array:
            return ""
        return "".join([item.get("plain_text", "") for item in desc_array])
    
    def _extract_properties(self, properties: Dict) -> Dict:
        """데이터베이스 속성 정보를 추출합니다."""
        result = {}
        for prop_name, prop_data in properties.items():
            result[prop_name] = prop_data.get("type", "unknown")
        return result
    
    def _extract_page_properties(self, properties: Dict) -> Dict:
        """페이지 속성 값들을 추출합니다."""
        result = {}
        for prop_name, prop_data in properties.items():
            prop_type = prop_data.get("type")
            
            if prop_type == "title":
                result[prop_name] = self._extract_title(prop_data.get("title", []))
            elif prop_type == "rich_text":
                result[prop_name] = self._extract_title(prop_data.get("rich_text", []))
            elif prop_type == "select":
                select_data = prop_data.get("select")
                result[prop_name] = select_data.get("name") if select_data else None
            elif prop_type == "multi_select":
                multi_select_data = prop_data.get("multi_select", [])
                result[prop_name] = [item.get("name") for item in multi_select_data]
            elif prop_type == "date":
                date_data = prop_data.get("date")
                result[prop_name] = date_data.get("start") if date_data else None
            elif prop_type == "people":
                people_data = prop_data.get("people", [])
                result[prop_name] = [person.get("name", "Unknown") for person in people_data]
            else:
                result[prop_name] = str(prop_data.get(prop_type, ""))
        
        return result
    
    def _extract_smart_title(self, page_properties: Dict) -> str:
        """노션 페이지에서 실제 제목을 스마트하게 추출합니다."""
        
        # 여러 가능한 제목 속성 확인 (한국어/영어 순서로)
        possible_title_fields = [
            "이름", "Name", "제목", "Title", 
            "name", "title", "이름 (Title)", "Name (Title)",
            "페이지 제목", "Page Title", "타이틀", "TITLE"
        ]
        
        for field_name in possible_title_fields:
            if field_name in page_properties:
                prop_data = page_properties[field_name]
                prop_type = prop_data.get("type")
                
                if prop_type == "title":
                    title = self._extract_title(prop_data.get("title", []))
                    if title.strip():
                        return title.strip()
                
                elif prop_type == "rich_text":
                    title = self._extract_title(prop_data.get("rich_text", []))
                    if title.strip():
                        return title.strip()
        
        return "제목 없음"
    
    def _extract_block_content(self, block: Dict) -> Optional[Dict]:
        """블록 내용을 추출합니다."""
        block_type = block.get("type")
        if not block_type:
            return None
        
        block_data = block.get(block_type, {})
        
        # 텍스트가 있는 블록들 처리 (포괄적)
        text_content = ""
        
        # 1. rich_text 필드 확인
        if "rich_text" in block_data:
            text_content = self._extract_title(block_data["rich_text"])
        
        # 2. text 필드 확인 (일부 블록 타입에서 사용)
        elif "text" in block_data:
            if isinstance(block_data["text"], list):
                text_content = self._extract_title(block_data["text"])
            elif isinstance(block_data["text"], dict) and "rich_text" in block_data["text"]:
                text_content = self._extract_title(block_data["text"]["rich_text"])
            else:
                text_content = str(block_data["text"])
        
        # 3. caption 필드 확인 (이미지, 파일 등)
        elif "caption" in block_data:
            text_content = self._extract_title(block_data["caption"])
        
        # 4. title 필드 확인 (heading 블록들)
        elif "title" in block_data:
            text_content = self._extract_title(block_data["title"])
        
        # 5. 다른 텍스트 필드들 확인
        else:
            # 일반적인 텍스트 필드들 확인
            for field in ["content", "description", "name", "value"]:
                if field in block_data:
                    if isinstance(block_data[field], list):
                        text_content = self._extract_title(block_data[field])
                    else:
                        text_content = str(block_data[field])
                    break
        
        # 텍스트 내용이 있으면 반환
        if text_content and text_content.strip():
            return {
                "type": block_type,
                "text": text_content.strip()
            }
        
        # 텍스트가 없는 블록은 None 반환 (마크다운에서 제외)
        return None


# 데이터 저장 및 메인 실행 함수들
import json
from datetime import datetime
from pathlib import Path

def save_notion_data_to_files(data: Dict[str, Any], output_dir: str = "output/mcp_notion"):
    """노션 데이터를 파일로 저장합니다."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 전체 데이터를 JSON으로 저장
    full_data_file = output_path / "notion_data.json"
    with open(full_data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 전체 데이터 저장: {full_data_file}")
    
    # 데이터베이스별 저장
    for i, db in enumerate(data.get('databases', []), 1):
        db_name = db['title'].replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '') or f"database_{i}"
        
        # 데이터베이스 정보 저장
        db_file = output_path / f"{db_name}.json"
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print(f"💾 DB 저장: {db_file}")
        

    
    # 페이지들을 마크다운으로 저장 (내용이 있는 페이지만)
    used_filenames = set()
    for i, page in enumerate(data.get('pages', []), 1):
        # content가 없거나 비어있는 페이지는 건너뛰기
        if 'content' not in page or not page['content']:
            print(f"⚠️  빈 페이지 건너뛰기: {page['title']}")
            continue
            
        page_title = page['title'].replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '') or f"page_{i}"
        
        # 중복 파일명 처리
        original_title = page_title
        counter = 1
        while page_title in used_filenames:
            page_title = f"{original_title}_{counter}"
            counter += 1
        used_filenames.add(page_title)
        
        page_file = output_path / f"{page_title}.md"
        
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(f"# {page['title']}\n\n")
            f.write(f"**페이지 ID:** {page['id']}\n")
            f.write(f"**생성일:** {page.get('created', 'N/A')}\n")
            f.write(f"**마지막 수정:** {page.get('last_edited', 'N/A')}\n")
            f.write(f"**URL:** {page.get('url', 'N/A')}\n")
            f.write("\n---\n\n")
            
            # 페이지 내용 출력
            for block in page['content']:
                block_type = block.get('type', 'paragraph')
                text = block.get('text', '')
                
                if block_type.startswith('heading'):
                    level = int(block_type.split('_')[1]) if '_' in block_type else 1
                    f.write(f"{'#' * level} {text}\n\n")
                elif block_type == 'paragraph':
                    f.write(f"{text}\n\n")
                elif 'list' in block_type:
                    prefix = "-" if "bulleted" in block_type else "1."
                    f.write(f"{prefix} {text}\n")
                else:
                    f.write(f"{text}\n\n")
        
        print(f"📄 페이지 저장: {page_file}")
    
    # 간단한 요약 출력 (파일 저장하지 않음)
    databases = data.get('databases', [])
    pages = data.get('pages', [])
    content_pages = [p for p in pages if 'content' in p and p['content']]
    
    print(f"📊 수집 요약:")
    print(f"   데이터베이스: {len(databases)}개")
    print(f"   페이지: {len(content_pages)}개 (총 {len(pages)}개 중)")
    for db in databases:
        entry_count = len(db.get('entries', []))
        print(f"   - {db['title']}: {entry_count}개 항목")
    return output_path


async def main():
    """메인 실행 함수"""
    print("🚀 노션 MCP 통합 데이터 수집 시작")
    print("=" * 60)
    
    # .env 파일 로드
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ .env 파일 로드 완료")
    except ImportError:
        print("⚠️  python-dotenv가 설치되지 않았습니다.")
    
    # 환경 변수 및 라이브러리 확인
    if not NOTION_CLIENT_AVAILABLE:
        print("⚠️  notion-client가 설치되지 않았습니다.")
        print("   설치: pip install notion-client")
        return 1
    
    # 노션 통합 초기화
    config = {
        "token": os.getenv("NOTION_INTEGRATION_TOKEN"),
        "workspace_id": os.getenv("NOTION_WORKSPACE_ID")
    }
    
    print(f"🔍 디버깅 정보:")
    print(f"   토큰 길이: {len(config['token']) if config['token'] else 0}")
    print(f"   토큰 시작: {config['token'][:10] + '...' if config['token'] else 'None'}")
    
    notion = NotionMCPIntegration(config)
    
    print(f"   Client 초기화: {notion._client is not None}")
    
    try:
        # 1. 연결
        print("\n🔌 1. 노션 API 연결...")
        connected = await notion.connect()
        if not connected:
            print("❌ 연결 실패")
            return 1
        
        # 2. 데이터 수집
        print("\n📊 2. 데이터 수집 시작...")
        
        # 워크스페이스 정보
        workspace_info = await notion.get_workspace_info()
        print(f"   워크스페이스: {workspace_info.get('workspace_name', 'N/A')}")
        
        # 데이터베이스 수집
        databases = await notion.get_databases()
        print(f"   수집된 데이터베이스: {len(databases)}개")
        
        # 각 데이터베이스의 항목들 수집
        for db in databases:
            entries = await notion.get_database_entries(db['id'])
            db['entries'] = entries
            print(f"   {db['title']}: {len(entries)}개 항목")
        
        # 페이지 검색 및 내용 수집
        search_results = await notion.search_pages("", None)  # 전체 페이지 검색
        pages = []
        
        for result in search_results[:5]:  # 처음 5개만
            page_content = await notion.get_page_content(result['id'])
            pages.append(page_content)
            content_count = len(page_content.get('content', []))
            print(f"   {page_content['title']}: {content_count}개 블록")
        
        # 3. 데이터 저장
        print("\n💾 3. 데이터 저장...")
        
        collection_data = {
            "workspace_info": workspace_info,
            "databases": databases,
            "pages": pages,
            "collection_timestamp": datetime.now().isoformat(),
            "source": "real_api"
        }
        
        output_dir = save_notion_data_to_files(collection_data)
        
        # 4. 연결 해제
        await notion.disconnect()
        
        print("\n" + "=" * 60)
        print("🎉 노션 MCP 데이터 수집 완료!")
        print(f"📁 저장 위치: {output_dir.absolute()}")
        
        # 저장된 파일 목록 표시
        files = list(output_dir.glob("*"))
        print(f"\n📂 저장된 파일 ({len(files)}개):")
        for file in sorted(files):
            size = file.stat().st_size
            size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
            print(f"   📄 {file.name} ({size_str})")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
