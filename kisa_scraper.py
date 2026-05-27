#!/usr/bin/env python3
"""
KISA Security Notice MCP Server
- Author: Kim Wonjin
- Description: KISA(보호나라) 보안공지 게시판을 스크래핑하여 AI 에이전트가 활용할 수 있는 
               MCP(Model Context Protocol) 표준 도구(Tool)로 제공하는 서버입니다.
- Tech Stack: Python 3.10+, FastMCP, HTTPX, BeautifulSoup4
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP

# 1. MCP 서버 초기화 (클라이언트 인식 명칭 설정)
mcp = FastMCP("KISA-Security-Notice-Scraper")

# 설정: KISA 보호나라 보안공지 URL (정식 주소)
KISA_URL = "https://www.boho.or.kr/kr/bbs/list.do?menuNo=205020&bbsId=B0000133"
BASE_VIEW_URL = "https://www.boho.or.kr/kr/bbs/view.do"


async def fetch_kisa_data() -> List[Dict[str, str]]:
    """KISA 보호나라 사이트에서 최신 공지 사항 목록을 비동기로 스크래핑합니다.
    
    Returns:
        List[Dict[str, str]]: 공지사항 날짜, 제목, 상세 링크가 담긴 딕셔너리 리스트
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "Anonymized Security Research Crawler/1.0"
        )
    }
    
    async with httpx.AsyncClient(headers=headers, timeout=10.0) as client:
        response = await client.get(KISA_URL)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        notices = []
        
        # 게시판 테이블의 데이터 행(tr) 셀렉터 추출
        table_rows = soup.select("table.board_list tbody tr")
        
        for row in table_rows:
            cols = row.find_all("td")
            # 유효한 데이터 행이 아니면 건너뜀 (공지사항 구조 검증)
            if len(cols) < 4:
                continue
            
            # 1. 날짜 추출 (4번째 컬럼)
            date_str = cols[3].get_text(strip=True)
            
            # 2. 제목 및 링크 태그 추출 (2번째 컬럼)
            title_tag = cols[1].find("a")
            if not title_tag:
                continue
                
            title = title_tag.get_text(strip=True)
            href = title_tag.get("href", "")
            
            # 3. 상대 경로를 완벽한 절대 경로 URL로 변환 및 파라미터 정제
            if '?' in href:
                query_part = href.split('?', 1)[1]
                full_url = f"{BASE_VIEW_URL}?{query_part}"
            else:
                full_url = f"{BASE_VIEW_URL}?{href}" if not href.startswith("http") else href

            notices.append({
                "date": date_str,
                "title": title,
                "url": full_url
            })
            
        return notices


@mcp.tool()
async def get_security_notices(keyword: Optional[str] = None, days_ago: int = 0) -> str:
    """KISA(보호나라)의 최신 보안 공지를 가져오고 필터링합니다.

    Args:
        keyword (Optional[str]): 특정 키워드가 제목에 포함된 공지만 필터링합니다. (예: '취약점', 'Windows')
        days_ago (int): 최근 며칠 동안의 공지를 조회할지 지정합니다. (0이면 오늘 공지만 조회)

    Returns:
        str: AI 에이전트 및 사용자가 읽기 좋은 마크다운(Markdown) 포맷의 검색 결과 문장
    """
    try:
        # 실시간 데이터 스크래핑 수행
        notices = await fetch_kisa_data()
        
        # 1. 날짜 기준 필터링 로직
        if days_ago > 0:
            target_date = datetime.now().date() - timedelta(days=days_ago)
            filtered_notices = []
            for n in notices:
                try:
                    notice_date = datetime.strptime(n['date'], '%Y-%m-%d').date()
                    if notice_date >= target_date:
                        filtered_notices.append(n)
                except ValueError:
                    # 날짜 형식이 매칭되지 않는 예외적인 행은 무시
                    continue
            notices = filtered_notices
            
        elif days_ago == 0:
            # 오늘 날짜 공지만 매칭
            today_str = datetime.now().strftime('%Y-%m-%d')
            notices = [n for n in notices if n['date'] == today_str]

        # 2. 키워드 기준 필터링 로직
        if keyword:
            notices = [n for n in notices if keyword.lower() in n['title'].lower()]

        # 결과 데이터가 없는 경우 예외 처리
        if not notices:
            return "❌ 지정하신 조건에 부합하는 최신 KISA 보안 공지가 존재하지 않습니다."

        # 3. 응답 데이터 마크다운 포맷팅
        result = [f"### 🛡️ KISA 보안 공지 검색 결과 ({datetime.now().strftime('%Y-%m-%d %H:%M')} 기준)"]
        for n in notices:
            result.append(f"- **[{n['date']}]** {n['title']}  \n  🔗 [상세 공지 바로가기]({n['url']})")
        
        return "\n".join(result)

    except httpx.HTTPStatusError as http_err:
        return f"❌ KISA 서버 연결 실패 (HTTP Error): {http_err.response.status_code}"
    except Exception as e:
        return f"❌ 데이터를 처리하는 도중 예상치 못한 오류가 발생했습니다: {str(e)}"


if __name__ == "__main__":
    # MCP 표준 입출력(Stdio) 모드로 서버 실행
    print("🚀 KISA Security Notice MCP Server가 실행 중입니다...")
    mcp.run()
