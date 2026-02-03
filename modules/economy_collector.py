"""
경제 흐름 수집 모듈
거시경제, 산업 분석, 글로벌 시황 정보 수집
"""

import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from typing import List, Dict, Optional
import time
import json
import feedparser
from concurrent.futures import ThreadPoolExecutor, as_completed

from modules.ai_engine import generate_summary, extract_keywords
from modules.database import get_connection

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User-Agent 설정
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def fetch_bok_reports(max_results: int = 10) -> List[Dict]:
    """
    한국은행 이슈노트 및 경제전망 수집
    
    Returns:
        보고서 딕셔너리 리스트
    """
    reports = []
    try:
        # 한국은행 RSS Feed 또는 웹사이트 스크래핑
        # 실제 구현 시 한국은행 웹사이트 구조에 맞게 수정 필요
        rss_url = "https://www.bok.or.kr/portal/bbs/B0000245/list.do?menuNo=200761"
        
        # RSS Feed가 없으면 웹 스크래핑
        response = requests.get(rss_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 보고서 링크 및 제목 추출 (실제 구조에 맞게 수정 필요)
        items = soup.select('a[href*="view.do"]')[:max_results]
        
        for item in items:
            title = item.get_text(strip=True)
            url = "https://www.bok.or.kr" + item.get('href', '')
            
            if title and '경제' in title or '금리' in title or '통화' in title:
                reports.append({
                    "title": title,
                    "url": url,
                    "source": "한국은행",
                    "category": "거시경제",
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
        
        logger.info(f"한국은행 보고서 {len(reports)}개 수집")
        
    except Exception as e:
        logger.error(f"한국은행 보고서 수집 실패: {e}")
    
    return reports


def fetch_kdi_reports(max_results: int = 10) -> List[Dict]:
    """
    KDI 경제동향 수집
    
    Returns:
        보고서 딕셔너리 리스트
    """
    reports = []
    try:
        # KDI 웹사이트 스크래핑
        url = "https://www.kdi.re.kr/kdi_etc/issue/issue_list.jsp"
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 경제동향 관련 링크 추출 (실제 구조에 맞게 수정 필요)
        items = soup.select('a[href*="issue_view"]')[:max_results]
        
        for item in items:
            title = item.get_text(strip=True)
            url = "https://www.kdi.re.kr" + item.get('href', '')
            
            if title:
                reports.append({
                    "title": title,
                    "url": url,
                    "source": "KDI",
                    "category": "거시경제",
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
        
        logger.info(f"KDI 보고서 {len(reports)}개 수집")
        
    except Exception as e:
        logger.error(f"KDI 보고서 수집 실패: {e}")
    
    return reports


def fetch_hankyung_consensus(max_results: int = 20) -> List[Dict]:
    """
    한경 컨센서스 리포트 수집
    
    Returns:
        리포트 딕셔너리 리스트
    """
    reports = []
    try:
        # 한경 컨센서스 RSS Feed
        rss_url = "https://consensus.hankyung.com/rss"
        
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:max_results]:
            reports.append({
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "source": "한경 컨센서스",
                "category": "산업분석",
                "date": entry.get("published", datetime.now().strftime("%Y-%m-%d"))
            })
        
        logger.info(f"한경 컨센서스 {len(reports)}개 수집")
        
    except Exception as e:
        logger.error(f"한경 컨센서스 수집 실패: {e}")
    
    return reports


def fetch_naver_finance(max_results: int = 20) -> List[Dict]:
    """
    네이버 금융 리서치 수집
    
    Returns:
        리포트 딕셔너리 리스트
    """
    reports = []
    try:
        # 네이버 금융 RSS Feed
        rss_url = "https://finance.naver.com/news/rss/news_list.naver?mode=LSS2D&section_id=101&section_id2=258"
        
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:max_results]:
            reports.append({
                "title": entry.get("title", ""),
                "url": entry.get("link", ""),
                "source": "네이버 금융",
                "category": "산업분석",
                "date": entry.get("published", datetime.now().strftime("%Y-%m-%d"))
            })
        
        logger.info(f"네이버 금융 {len(reports)}개 수집")
        
    except Exception as e:
        logger.error(f"네이버 금융 수집 실패: {e}")
    
    return reports


def fetch_investing_news(max_results: int = 20) -> List[Dict]:
    """
    Investing.com 뉴스 수집
    
    Returns:
        뉴스 딕셔너리 리스트
    """
    news_list = []
    try:
        # Investing.com RSS Feed
        rss_url = "https://www.investing.com/rss/news.rss"
        
        feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:max_results]:
            # 경제 관련 키워드 필터링
            title = entry.get("title", "").lower()
            if any(kw in title for kw in ["economy", "fed", "rate", "gdp", "inflation", "market"]):
                news_list.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "source": "Investing.com",
                    "category": "글로벌시황",
                    "date": entry.get("published", datetime.now().strftime("%Y-%m-%d"))
                })
        
        logger.info(f"Investing.com {len(news_list)}개 수집")
        
    except Exception as e:
        logger.error(f"Investing.com 수집 실패: {e}")
    
    return news_list


def fetch_kcif_news(max_results: int = 20) -> List[Dict]:
    """
    국제금융센터 일일 브리핑 수집
    
    Returns:
        뉴스 딕셔너리 리스트
    """
    news_list = []
    try:
        # 국제금융센터 웹사이트 스크래핑
        url = "https://www.kcif.or.kr/main.do"
        
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 일일 브리핑 링크 추출 (실제 구조에 맞게 수정 필요)
        items = soup.select('a[href*="daily"]')[:max_results]
        
        for item in items:
            title = item.get_text(strip=True)
            url = "https://www.kcif.or.kr" + item.get('href', '')
            
            if title:
                news_list.append({
                    "title": title,
                    "url": url,
                    "source": "국제금융센터",
                    "category": "글로벌시황",
                    "date": datetime.now().strftime("%Y-%m-%d")
                })
        
        logger.info(f"국제금융센터 {len(news_list)}개 수집")
        
    except Exception as e:
        logger.error(f"국제금융센터 수집 실패: {e}")
    
    return news_list


def scrape_content(url: str, max_retries: int = 2) -> Optional[str]:
    """
    웹페이지 본문 스크래핑
    
    Args:
        url: 웹페이지 URL
        max_retries: 최대 재시도 횟수
    
    Returns:
        본문 텍스트 (실패 시 None)
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 본문 추출 시도
            content = None
            for tag in ['article', 'div[class*="article"]', 'div[class*="content"]', 'main']:
                elements = soup.select(tag)
                if elements:
                    content = ' '.join([elem.get_text(strip=True) for elem in elements])
                    if len(content) > 200:
                        break
            
            if not content or len(content) < 200:
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs])
            
            if content and len(content) > 100:
                return content[:5000]  # 최대 5000자
            else:
                return None
                
        except Exception as e:
            logger.warning(f"본문 스크래핑 실패 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                return None
    
    return None


def check_duplicate(url: str) -> bool:
    """URL 중복 체크"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM economy_news WHERE url = ?", (url,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        logger.error(f"중복 체크 실패: {e}")
        return False


def save_economy_news_to_db(news_data: Dict) -> bool:
    """경제 뉴스를 데이터베이스에 저장"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        date_str = news_data.get("date", datetime.now().strftime("%Y-%m-%d"))
        
        cursor.execute("""
            INSERT INTO economy_news (
                date, category, title, url, content_summary, 
                full_text, keywords, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date_str,
            news_data.get("category", "경제"),
            news_data.get("title", ""),
            news_data.get("url", ""),
            news_data.get("content_summary", ""),
            news_data.get("full_text", ""),
            json.dumps(news_data.get("keywords", []), ensure_ascii=False),
            news_data.get("source", "")
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"경제 뉴스 저장 완료: {news_data.get('title', '')[:50]}")
        return True
        
    except Exception as e:
        logger.error(f"경제 뉴스 저장 실패: {e}")
        return False


def process_single_economy_item(item: Dict) -> Optional[Dict]:
    """
    단일 경제 뉴스 처리 함수 (병렬 처리용)
    
    Args:
        item: 경제 뉴스 딕셔너리
    
    Returns:
        처리된 뉴스 데이터 (실패 시 None)
    """
    url = item.get("url", "")
    
    # 중복 체크 (먼저 수행하여 불필요한 처리 방지)
    if check_duplicate(url):
        logger.info(f"중복 항목 스킵: {url}")
        return None
    
    # 본문 스크래핑
    full_text = scrape_content(url)
    if not full_text:
        full_text = item.get("title", "")
    
    # AI 분석
    try:
        # 요약 생성 (3줄)
        summary = generate_summary(full_text[:2000])
        if not summary or len(summary) > 200:
            summary = summary[:200] + "..." if summary and len(summary) > 200 else (item.get('title', '')[:100] + "...")
        
        # 키워드 추출
        keywords_list = extract_keywords(full_text[:2000], max_keywords=5)
        
    except Exception as e:
        logger.error(f"AI 분석 실패: {e}")
        summary = item.get('title', '')[:100] + "..."
        keywords_list = []
    
    # 데이터베이스에 저장
    news_data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "category": item.get("category", "경제"),
        "title": item.get("title", ""),
        "url": url,
        "content_summary": summary,
        "full_text": full_text[:5000],
        "keywords": keywords_list,
        "source": item.get("source", "")
    }
    
    if save_economy_news_to_db(news_data):
        return news_data
    
    return None


def collect_economy_news(progress_callback=None):
    """
    경제 흐름 정보 수집 메인 함수 (병렬 처리 최적화)
    
    Args:
        progress_callback: 진행도 콜백 함수
    """
    logger.info("=== 경제 흐름 정보 수집 시작 (병렬 처리) ===")
    
    total_collected = 0
    total_saved = 0
    
    all_items = []
    
    # 1. 거시경제 및 정책
    logger.info("거시경제 정보 수집 중...")
    if progress_callback:
        progress_callback(1, 6, "거시경제 정보 수집 중...")
    
    bok_reports = fetch_bok_reports(max_results=5)
    all_items.extend(bok_reports)
    time.sleep(0.3)
    
    kdi_reports = fetch_kdi_reports(max_results=5)
    all_items.extend(kdi_reports)
    time.sleep(0.3)
    
    # 2. 산업 및 기업 분석
    logger.info("산업 분석 정보 수집 중...")
    if progress_callback:
        progress_callback(2, 6, "산업 분석 정보 수집 중...")
    
    hankyung_reports = fetch_hankyung_consensus(max_results=10)
    all_items.extend(hankyung_reports)
    time.sleep(0.3)
    
    naver_reports = fetch_naver_finance(max_results=10)
    all_items.extend(naver_reports)
    time.sleep(0.3)
    
    # 3. 글로벌 시황 및 뉴스
    logger.info("글로벌 시황 정보 수집 중...")
    if progress_callback:
        progress_callback(3, 6, "글로벌 시황 정보 수집 중...")
    
    investing_news = fetch_investing_news(max_results=10)
    all_items.extend(investing_news)
    time.sleep(0.3)
    
    kcif_news = fetch_kcif_news(max_results=10)
    all_items.extend(kcif_news)
    time.sleep(0.3)
    
    # 전체 작업량 계산
    total_work = len(all_items)
    processed_count = 0
    
    logger.info(f"총 {total_work}개 항목 수집 완료. 병렬 처리 시작...")
    if progress_callback:
        progress_callback(4, 6, f"항목 분석 준비 중...")
    
    # 병렬 처리 (최대 5개 스레드 동시 실행)
    with ThreadPoolExecutor(max_workers=5) as executor:
        # 모든 항목에 대해 병렬 처리 시작
        future_to_item = {
            executor.submit(process_single_economy_item, item): item 
            for item in all_items
        }
        
        # 완료된 작업부터 처리
        for future in as_completed(future_to_item):
            processed_count += 1
            item = future_to_item[future]
            
            try:
                result = future.result()
                if result:
                    total_collected += 1
                    total_saved += 1
                    
                    # 진행도 업데이트
                    if progress_callback:
                        progress = 4 + (processed_count / total_work * 2) if total_work > 0 else 4
                        progress_callback(min(progress, 6), 6, 
                                        f"처리 중... ({processed_count}/{total_work}) - {total_saved}개 저장됨")
            except Exception as e:
                logger.error(f"경제 뉴스 처리 실패: {item.get('title', '')[:50]} - {e}")
                if progress_callback:
                    progress = 4 + (processed_count / total_work * 2) if total_work > 0 else 4
                    progress_callback(min(progress, 6), 6, 
                                    f"처리 중... ({processed_count}/{total_work})")
    
    logger.info(f"=== 경제 흐름 정보 수집 완료: {total_collected}개 수집, {total_saved}개 저장 ===")
    return total_collected, total_saved
