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

from modules.ai_engine import generate_summary, extract_keywords, get_model
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
    Google News RSS를 통해 한국은행 관련 뉴스 수집
    """
    reports = []
    try:
        # Google News RSS를 통한 한국은행 관련 뉴스 수집
        import urllib.parse
        query = urllib.parse.quote("한국은행 OR BOK OR 한국은행 금리 OR 한국은행 통화정책")
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
        
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            logger.warning(f"한국은행 RSS 피드가 비어있음: {feed.get('bozo_exception', 'Unknown error')}")
            # 대체 방법: 더 간단한 검색어 사용
            rss_url = "https://news.google.com/rss/search?q=한국은행&hl=ko&gl=KR&ceid=KR:ko"
            feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:max_results]:
            title = entry.get("title", "").replace(" - Google 뉴스", "").replace(" - Google News", "").strip()
            url = entry.get("link", "")
            
            if title and url:
                # 날짜 파싱
                try:
                    from dateutil import parser as date_parser
                    pub_date = date_parser.parse(entry.get("published", "")).strftime("%Y-%m-%d")
                except:
                    pub_date = datetime.now().strftime("%Y-%m-%d")
                
                reports.append({
                    "title": title,
                    "url": url,
                    "source": "한국은행 (Google News)",
                    "category": "거시경제",
                    "date": pub_date
                })
        
        logger.info(f"한국은행 관련 뉴스 {len(reports)}개 수집")
        
    except Exception as e:
        logger.error(f"한국은행 뉴스 수집 실패: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    return reports


def fetch_kdi_reports(max_results: int = 10) -> List[Dict]:
    """
    KDI 경제동향 수집
    Google News RSS를 통해 KDI 관련 뉴스 수집
    """
    reports = []
    try:
        # Google News RSS를 통한 KDI 관련 뉴스 수집
        import urllib.parse
        query = urllib.parse.quote("KDI OR 한국개발연구원")
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
        
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            logger.warning(f"KDI RSS 피드가 비어있음")
            rss_url = "https://news.google.com/rss/search?q=KDI&hl=ko&gl=KR&ceid=KR:ko"
            feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:max_results]:
            title = entry.get("title", "").replace(" - Google 뉴스", "").replace(" - Google News", "").strip()
            url = entry.get("link", "")
            
            if title and url:
                try:
                    from dateutil import parser as date_parser
                    pub_date = date_parser.parse(entry.get("published", "")).strftime("%Y-%m-%d")
                except:
                    pub_date = datetime.now().strftime("%Y-%m-%d")
                
                reports.append({
                    "title": title,
                    "url": url,
                    "source": "KDI (Google News)",
                    "category": "거시경제",
                    "date": pub_date
                })
        
        logger.info(f"KDI 관련 뉴스 {len(reports)}개 수집")
        
    except Exception as e:
        logger.error(f"KDI 뉴스 수집 실패: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    return reports


def fetch_hankyung_consensus(max_results: int = 20) -> List[Dict]:
    """
    한경 컨센서스 리포트 수집
    Google News를 통해 한경 관련 뉴스 수집
    """
    reports = []
    try:
        # Google News RSS를 통한 한경 관련 뉴스 수집
        import urllib.parse
        query = urllib.parse.quote("한경 OR 한경컨센서스 OR 한경증권")
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
        
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            logger.warning(f"한경 RSS 피드가 비어있음")
            rss_url = "https://news.google.com/rss/search?q=한경&hl=ko&gl=KR&ceid=KR:ko"
            feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:max_results]:
            title = entry.get("title", "").replace(" - Google 뉴스", "").replace(" - Google News", "").strip()
            url = entry.get("link", "")
            
            if title and url:
                try:
                    from dateutil import parser as date_parser
                    pub_date = date_parser.parse(entry.get("published", "")).strftime("%Y-%m-%d")
                except:
                    pub_date = datetime.now().strftime("%Y-%m-%d")
                
                reports.append({
                    "title": title,
                    "url": url,
                    "source": "한경 컨센서스 (Google News)",
                    "category": "산업분석",
                    "date": pub_date
                })
        
        logger.info(f"한경 컨센서스 {len(reports)}개 수집")
        
    except Exception as e:
        logger.error(f"한경 컨센서스 수집 실패: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    return reports


def fetch_naver_finance(max_results: int = 20) -> List[Dict]:
    """
    네이버 금융 리서치 수집
    Google News RSS를 통해 경제/금융 뉴스 수집
    """
    reports = []
    try:
        # Google News RSS를 통한 경제/금융 뉴스 수집
        import urllib.parse
        query = urllib.parse.quote("경제 OR 금융 OR 증권 OR 시장")
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
        
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            logger.warning(f"네이버 금융 RSS 피드가 비어있음")
            rss_url = "https://news.google.com/rss/search?q=경제&hl=ko&gl=KR&ceid=KR:ko"
            feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:max_results]:
            title = entry.get("title", "").replace(" - Google 뉴스", "").replace(" - Google News", "").strip()
            url = entry.get("link", "")
            
            if title and url:
                try:
                    from dateutil import parser as date_parser
                    pub_date = date_parser.parse(entry.get("published", "")).strftime("%Y-%m-%d")
                except:
                    pub_date = datetime.now().strftime("%Y-%m-%d")
                
                reports.append({
                    "title": title,
                    "url": url,
                    "source": "네이버 금융 (Google News)",
                    "category": "산업분석",
                    "date": pub_date
                })
        
        logger.info(f"네이버 금융 관련 뉴스 {len(reports)}개 수집")
        
    except Exception as e:
        logger.error(f"네이버 금융 수집 실패: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    return reports


def fetch_investing_news(max_results: int = 20) -> List[Dict]:
    """
    Investing.com 뉴스 수집
    Google News RSS를 통해 글로벌 경제 뉴스 수집
    """
    news_list = []
    try:
        # Google News RSS를 통한 글로벌 경제 뉴스 수집
        import urllib.parse
        query = urllib.parse.quote("economy OR fed OR rate OR gdp OR inflation OR market")
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=en&gl=US&ceid=US:en"
        
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            logger.warning(f"글로벌 경제 RSS 피드가 비어있음")
            rss_url = "https://news.google.com/rss/search?q=economy&hl=en&gl=US&ceid=US:en"
            feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:max_results]:
            title = entry.get("title", "").replace(" - Google News", "").strip()
            url = entry.get("link", "")
            
            if title and url:
                try:
                    from dateutil import parser as date_parser
                    pub_date = date_parser.parse(entry.get("published", "")).strftime("%Y-%m-%d")
                except:
                    pub_date = datetime.now().strftime("%Y-%m-%d")
                
                news_list.append({
                    "title": title,
                    "url": url,
                    "source": "Investing.com (Google News)",
                    "category": "글로벌시황",
                    "date": pub_date
                })
        
        logger.info(f"글로벌 경제 뉴스 {len(news_list)}개 수집")
        
    except Exception as e:
        logger.error(f"글로벌 경제 뉴스 수집 실패: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    return news_list


def fetch_daily_economy_news(max_results: int = 30) -> List[Dict]:
    """
    일일 경제 뉴스 수집 (Google News RSS)
    오늘 날짜의 경제 관련 뉴스 수집
    """
    news_list = []
    try:
        # Google News RSS를 통한 일일 경제 뉴스 수집
        import urllib.parse
        keywords = ["경제", "금리", "통화정책"]
        today = datetime.now().strftime("%Y-%m-%d")
        
        for keyword in keywords:
            query = urllib.parse.quote(keyword)
            rss_url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
            
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                logger.warning(f"{keyword} RSS 피드가 비어있음")
                continue
            
            for entry in feed.entries[:max_results//len(keywords)]:
                title = entry.get("title", "").replace(" - Google 뉴스", "").replace(" - Google News", "").strip()
                url = entry.get("link", "")
                
                if title and url and title not in [n.get("title") for n in news_list]:
                    try:
                        from dateutil import parser as date_parser
                        pub_date = date_parser.parse(entry.get("published", "")).strftime("%Y-%m-%d")
                    except:
                        pub_date = today
                    
                    news_list.append({
                        "title": title,
                        "url": url,
                        "source": "일일 경제 뉴스",
                        "category": "거시경제",
                        "date": pub_date
                    })
            
            time.sleep(0.3)  # API 호출 간격
        
        logger.info(f"일일 경제 뉴스 {len(news_list)}개 수집")
        
    except Exception as e:
        logger.error(f"일일 경제 뉴스 수집 실패: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    return news_list


def fetch_kcif_news(max_results: int = 20) -> List[Dict]:
    """
    국제금융센터 일일 브리핑 수집
    Google News RSS를 통해 국제금융센터 관련 뉴스 수집
    """
    news_list = []
    try:
        # Google News RSS를 통한 국제금융센터 관련 뉴스 수집
        import urllib.parse
        query = urllib.parse.quote("국제금융센터 OR KCIF OR 글로벌 금융")
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=ko&gl=KR&ceid=KR:ko"
        
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            logger.warning(f"국제금융센터 RSS 피드가 비어있음")
            rss_url = "https://news.google.com/rss/search?q=글로벌+금융&hl=ko&gl=KR&ceid=KR:ko"
            feed = feedparser.parse(rss_url)
        
        for entry in feed.entries[:max_results]:
            title = entry.get("title", "").replace(" - Google 뉴스", "").replace(" - Google News", "").strip()
            url = entry.get("link", "")
            
            if title and url:
                try:
                    from dateutil import parser as date_parser
                    pub_date = date_parser.parse(entry.get("published", "")).strftime("%Y-%m-%d")
                except:
                    pub_date = datetime.now().strftime("%Y-%m-%d")
                
                news_list.append({
                    "title": title,
                    "url": url,
                    "source": "국제금융센터 (Google News)",
                    "category": "글로벌시황",
                    "date": pub_date
                })
        
        logger.info(f"국제금융센터 관련 뉴스 {len(news_list)}개 수집")
        
    except Exception as e:
        logger.error(f"국제금융센터 뉴스 수집 실패: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
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
    
    bok_reports = fetch_bok_reports(max_results=15)
    all_items.extend(bok_reports)
    time.sleep(0.3)
    
    kdi_reports = fetch_kdi_reports(max_results=15)
    all_items.extend(kdi_reports)
    time.sleep(0.3)
    
    # 2. 산업 및 기업 분석
    logger.info("산업 분석 정보 수집 중...")
    if progress_callback:
        progress_callback(2, 6, "산업 분석 정보 수집 중...")
    
    hankyung_reports = fetch_hankyung_consensus(max_results=20)
    all_items.extend(hankyung_reports)
    time.sleep(0.3)
    
    naver_reports = fetch_naver_finance(max_results=20)
    all_items.extend(naver_reports)
    time.sleep(0.3)
    
    # 3. 글로벌 시황 및 뉴스
    logger.info("글로벌 시황 정보 수집 중...")
    if progress_callback:
        progress_callback(3, 6, "글로벌 시황 정보 수집 중...")
    
    investing_news = fetch_investing_news(max_results=20)
    all_items.extend(investing_news)
    time.sleep(0.3)
    
    kcif_news = fetch_kcif_news(max_results=20)
    all_items.extend(kcif_news)
    time.sleep(0.3)
    
    # 4. 일일 경제 뉴스 추가 수집 (Google News)
    logger.info("일일 경제 뉴스 수집 중...")
    if progress_callback:
        progress_callback(3, 6, "일일 경제 뉴스 수집 중...")
    
    daily_economy_news = fetch_daily_economy_news(max_results=30)
    all_items.extend(daily_economy_news)
    time.sleep(0.3)
    
    # 전체 작업량 계산
    total_work = len(all_items)
    processed_count = 0
    
    logger.info(f"총 {total_work}개 항목 수집 완료. 병렬 처리 시작...")
    
    if total_work == 0:
        logger.warning("수집된 항목이 없습니다. RSS 피드 확인이 필요합니다.")
        if progress_callback:
            progress_callback(6, 6, "수집된 항목이 없습니다.")
        return 0, 0
    
    if progress_callback:
        progress_callback(4, 6, f"항목 분석 준비 중... ({total_work}개 항목)")
    
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


def check_report_exists(date: str) -> bool:
    """
    해당 날짜의 보고서가 이미 생성되었는지 확인
    
    Args:
        date: 확인할 날짜
    
    Returns:
        보고서 존재 여부
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM economy_reports WHERE date = ?", (date,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        logger.error(f"보고서 존재 확인 실패: {e}")
        return False


def save_report_to_db(date: str, report_text: str, news_count: int, used_news_ids: List[int] = None) -> bool:
    """
    생성된 보고서를 데이터베이스에 저장
    
    Args:
        date: 보고서 날짜
        report_text: 보고서 내용
        news_count: 사용된 뉴스 개수
        used_news_ids: 보고서에 사용된 뉴스 ID 리스트
    
    Returns:
        저장 성공 여부
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 사용된 뉴스 ID를 JSON으로 저장
        used_ids_json = json.dumps(used_news_ids or [], ensure_ascii=False)
        
        # 기존 보고서가 있으면 업데이트, 없으면 삽입
        cursor.execute("""
            INSERT OR REPLACE INTO economy_reports 
            (date, report_text, news_count, used_news_ids, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (date, report_text, news_count, used_ids_json))
        
        conn.commit()
        conn.close()
        logger.info(f"보고서 저장 완료: {date} (뉴스 {news_count}개 사용)")
        return True
    except Exception as e:
        logger.error(f"보고서 저장 실패: {e}")
        return False


def get_report_from_db(date: str) -> Optional[Dict]:
    """
    데이터베이스에서 보고서 조회
    
    Args:
        date: 조회할 날짜
    
    Returns:
        {"report_text": str, "used_news_ids": List[int]} 또는 None
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT report_text, used_news_ids FROM economy_reports WHERE date = ?", (date,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            report_text, used_ids_json = result
            try:
                used_ids = json.loads(used_ids_json) if used_ids_json else []
            except:
                used_ids = []
            return {"report_text": report_text, "used_news_ids": used_ids}
        return None
    except Exception as e:
        logger.error(f"보고서 조회 실패: {e}")
        return None


def get_unused_news_ids(date: str) -> List[int]:
    """
    해당 날짜의 보고서에 사용되지 않은 뉴스 ID 조회
    
    Args:
        date: 조회할 날짜
    
    Returns:
        사용되지 않은 뉴스 ID 리스트
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 해당 날짜의 모든 뉴스 ID 조회
        cursor.execute("SELECT id FROM economy_news WHERE date = ?", (date,))
        all_news_ids = [row[0] for row in cursor.fetchall()]
        
        # 보고서에 사용된 뉴스 ID 조회
        report_data = get_report_from_db(date)
        used_ids = report_data.get("used_news_ids", []) if report_data else []
        
        # 사용되지 않은 뉴스 ID
        unused_ids = [nid for nid in all_news_ids if nid not in used_ids]
        
        conn.close()
        return unused_ids
    except Exception as e:
        logger.error(f"미사용 뉴스 ID 조회 실패: {e}")
        return []


def generate_daily_economy_report(date: str = None, force_regenerate: bool = False) -> Optional[str]:
    """
    일일 경제 종합 보고서 생성
    수집된 모든 경제 뉴스를 종합하여 하나의 보고서로 작성
    새로운 뉴스가 추가되면 기존 보고서를 업데이트
    
    Args:
        date: 보고서 날짜 (None이면 오늘 날짜)
        force_regenerate: 기존 보고서가 있어도 재생성할지 여부
    
    Returns:
        종합 보고서 텍스트 (실패 시 None)
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 해당 날짜의 모든 경제 뉴스 조회 (ID 포함)
        cursor.execute("""
            SELECT id, title, content_summary, category, source, keywords
            FROM economy_news
            WHERE date = ?
            ORDER BY created_at DESC
        """, (date,))
        
        all_news = cursor.fetchall()
        conn.close()
        
        if not all_news:
            logger.warning(f"{date} 날짜의 경제 뉴스가 없습니다.")
            return None
        
        # 기존 보고서 확인
        existing_report_data = get_report_from_db(date)
        used_news_ids = existing_report_data.get("used_news_ids", []) if existing_report_data else []
        
        # 사용되지 않은 새로운 뉴스가 있는지 확인
        all_news_ids = [news[0] for news in all_news]
        unused_news_ids = [nid for nid in all_news_ids if nid not in used_news_ids]
        
        # 재생성 강제가 아니고, 기존 보고서가 있고, 새로운 뉴스가 없으면 기존 보고서 반환
        if not force_regenerate and existing_report_data and not unused_news_ids:
            logger.info(f"{date} 날짜의 보고서가 이미 존재하고 새로운 뉴스가 없습니다.")
            return existing_report_data["report_text"]
        
        # 새로운 뉴스가 있거나 재생성 강제인 경우 보고서 생성/업데이트
        if unused_news_ids:
            logger.info(f"{date} 날짜에 새로운 뉴스 {len(unused_news_ids)}개가 추가되었습니다. 보고서를 업데이트합니다.")
        elif force_regenerate:
            logger.info(f"{date} 날짜의 보고서를 강제로 재생성합니다.")
        
        logger.info(f"{date} 날짜의 경제 뉴스 {len(all_news)}개를 종합하여 보고서 생성 중...")
        
        # 뉴스 데이터를 카테고리별로 분류 (ID 포함)
        macro_economy = []  # 거시경제
        industry_analysis = []  # 산업분석
        global_market = []  # 글로벌시황
        all_used_ids = []  # 보고서에 사용된 모든 뉴스 ID
        
        for news in all_news:
            news_id, title, summary, category, source, keywords_json = news
            all_used_ids.append(news_id)  # 모든 뉴스를 사용
            
            try:
                keywords = json.loads(keywords_json) if keywords_json else []
            except:
                keywords = []
            
            news_item = {
                "id": news_id,
                "title": title,
                "summary": summary or title,
                "source": source,
                "keywords": keywords
            }
            
            if category == "거시경제":
                macro_economy.append(news_item)
            elif category == "산업분석":
                industry_analysis.append(news_item)
            elif category == "글로벌시황":
                global_market.append(news_item)
        
        # AI를 사용하여 종합 보고서 생성
        report_prompt = f"""다음은 {date} 날짜에 수집된 경제 뉴스 정보입니다. 이를 종합하여 일일 경제 종합 보고서를 작성해주세요.

## 수집된 뉴스 정보

### 1. 거시경제 ({len(macro_economy)}건)
"""
        
        for idx, news in enumerate(macro_economy[:10], 1):  # 최대 10개만 사용
            report_prompt += f"""
{idx}. [{news['source']}] {news['title']}
   요약: {news['summary'][:200]}
"""
        
        report_prompt += f"""
### 2. 산업분석 ({len(industry_analysis)}건)
"""
        
        for idx, news in enumerate(industry_analysis[:10], 1):
            report_prompt += f"""
{idx}. [{news['source']}] {news['title']}
   요약: {news['summary'][:200]}
"""
        
        report_prompt += f"""
### 3. 글로벌시황 ({len(global_market)}건)
"""
        
        for idx, news in enumerate(global_market[:10], 1):
            report_prompt += f"""
{idx}. [{news['source']}] {news['title']}
   요약: {news['summary'][:200]}
"""
        
        report_prompt += """
## 보고서 작성 지침

위 정보를 바탕으로 다음 형식으로 일일 경제 종합 보고서를 작성해주세요:

1. **보고서 제목**: 날짜와 함께 명확한 제목
2. **요약**: 전체 경제 동향을 한눈에 파악할 수 있는 3-4줄 요약
3. **주요 이슈**: 가장 중요한 경제 이슈 3-5개를 선별하여 설명
4. **카테고리별 분석**:
   - 거시경제: 금리, 통화정책, GDP, 인플레이션 등
   - 산업분석: 주요 산업 동향, 기업 분석 등
   - 글로벌시황: 해외 경제 동향, 환율, 국제 금융 등
5. **시사점**: 오늘의 경제 뉴스가 시사하는 바와 향후 전망

중복되는 내용은 제거하고, 관련된 내용은 연합시켜 일목요연하게 정리해주세요.
"""
        
        # AI 모델을 사용하여 보고서 생성
        try:
            model = get_model()
            response = model.generate_content(
                report_prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 3000,
                }
            )
            
            report = response.text.strip()
            logger.info(f"일일 경제 종합 보고서 생성 완료: {len(report)}자 (뉴스 {len(all_news)}개 사용)")
            
            # 보고서를 데이터베이스에 저장 (사용된 뉴스 ID 포함)
            save_report_to_db(date, report, len(all_news), all_used_ids)
            
            return report
            
        except Exception as e:
            logger.error(f"보고서 생성 실패: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None
            
    except Exception as e:
        logger.error(f"보고서 생성 중 오류 발생: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None
