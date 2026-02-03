"""
뉴스 수집 모듈
미국/한국 심리 관련 뉴스를 수집하고 분석
"""

import feedparser
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from typing import List, Dict, Optional
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from modules.ai_engine import generate_summary, generate_news_summary_korean, translate_title, evaluate_article, extract_keywords
from modules.database import get_connection

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User-Agent 설정 (스크래핑 시 필요)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def fetch_news_from_rss(keywords: List[str], country: str = "KR", max_results: int = 20) -> List[Dict]:
    """
    Google News RSS Feed에서 뉴스 수집
    
    Args:
        keywords: 검색 키워드 리스트
        country: 국가 코드 (KR, US)
        max_results: 최대 수집 개수
    
    Returns:
        뉴스 딕셔너리 리스트
    """
    all_news = []
    
    for keyword in keywords:
        try:
            # 한국 뉴스의 경우 더 구체적인 검색어 조합
            if country == "KR":
                # 심리/상담 관련 키워드만 필터링
                search_query = keyword
                # 제외 키워드 추가 (법률 상담, 디지털 상담 등 제외, 단 IT는 AI/뇌과학 관련이므로 제외하지 않음)
                # 단, 심리학+AI, 뇌과학+AI는 제외하지 않음
                if "상담" in keyword or "심리" in keyword:
                    search_query = f"{keyword} -법률 -법무 -디지털 -건설 -공제회 -IT"
                rss_url = f"https://news.google.com/rss/search?q={search_query}&hl=ko&gl=KR&ceid=KR:ko"
            else:  # US
                rss_url = f"https://news.google.com/rss/search?q={keyword}&hl=en&gl=US&ceid=US:en"
            
            logger.info(f"RSS Feed 파싱 중: {keyword} ({country})")
            
            # RSS Feed 파싱
            feed = feedparser.parse(rss_url)
            
            # 정확히 max_results 개수만 가져오기
            entries = feed.entries[:max_results]
            for entry in entries:
                news_item = {
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "source": entry.get("source", {}).get("title", "") if hasattr(entry, "source") else "",
                    "country": country,
                    "keyword": keyword
                }
                all_news.append(news_item)
            
            # 요청 간격 조절 (Rate limiting) - 병렬 처리로 인해 감소
            time.sleep(0.3)
            
        except Exception as e:
            logger.error(f"RSS Feed 파싱 실패 ({keyword}): {e}")
            continue
    
    logger.info(f"총 {len(all_news)}개의 뉴스 수집 완료")
    return all_news


def scrape_article_content(url: str, max_retries: int = 2) -> Optional[str]:
    """
    뉴스 기사 원문 스크래핑
    
    Args:
        url: 기사 URL
        max_retries: 최대 재시도 횟수
    
    Returns:
        기사 본문 텍스트 (실패 시 None)
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 본문 추출 시도 (다양한 태그 시도)
            content = None
            
            # 일반적인 본문 태그들
            for tag in ['article', 'div[class*="article"]', 'div[class*="content"]', 'main']:
                elements = soup.select(tag)
                if elements:
                    content = ' '.join([elem.get_text(strip=True) for elem in elements])
                    if len(content) > 200:  # 최소 길이 체크
                        break
            
            # 위 방법이 실패하면 모든 p 태그 수집
            if not content or len(content) < 200:
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text(strip=True) for p in paragraphs])
            
            if content and len(content) > 100:
                logger.info(f"기사 본문 추출 성공: {len(content)}자")
                return content[:5000]  # 최대 5000자로 제한
            else:
                logger.warning(f"기사 본문이 너무 짧음: {url}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"기사 스크래핑 실패 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                return None
        except Exception as e:
            logger.error(f"기사 스크래핑 중 오류: {e}")
            return None
    
    return None


def check_duplicate(url: str) -> bool:
    """
    URL 중복 체크
    
    Args:
        url: 체크할 URL
    
    Returns:
        중복이면 True, 아니면 False
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM articles WHERE url = ?", (url,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        logger.error(f"중복 체크 실패: {e}")
        return False


def save_article_to_db(article_data: Dict) -> bool:
    """
    뉴스 기사를 데이터베이스에 저장
    
    Args:
        article_data: 기사 데이터 딕셔너리
    
    Returns:
        저장 성공 여부
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 날짜 파싱
        date_str = article_data.get("date", datetime.now().strftime("%Y-%m-%d"))
        
        cursor.execute("""
            INSERT INTO articles (
                date, category, title, url, content_summary, 
                full_text, keywords, validity_score, country
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            date_str,
            article_data.get("category", "psychology"),
            article_data.get("title", ""),
            article_data.get("url", ""),
            article_data.get("content_summary", ""),
            article_data.get("full_text", ""),
            json.dumps(article_data.get("keywords", []), ensure_ascii=False),
            article_data.get("validity_score", 3),
            article_data.get("country", "KR")
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"기사 저장 완료: {article_data.get('title', '')[:50]}")
        return True
        
    except Exception as e:
        logger.error(f"기사 저장 실패: {e}")
        return False


def process_single_news(news: Dict, country: str) -> Optional[Dict]:
    """
    단일 뉴스 처리 함수 (병렬 처리용)
    
    Args:
        news: 뉴스 딕셔너리
        country: 국가 코드
    
    Returns:
        처리된 기사 데이터 (실패 시 None)
    """
    url = news.get("url", "")
    
    # 중복 체크 (먼저 수행하여 불필요한 처리 방지)
    if check_duplicate(url):
        logger.info(f"중복 기사 스킵: {url}")
        return None
    
    # 제목 기반 관련성 필터링 (스크래핑 전에 먼저 체크)
    # 하지만 너무 엄격하게 필터링하지 않도록 키워드 확대
    title_lower = news.get("title", "").lower()
    relevant_keywords = [
        "심리", "정신", "마음", "우울", "불안", "트라우마", "상담", "치료", "인지", "행동",
        "psychology", "mental", "counseling", "therapy", "depression", "anxiety", "trauma",
        "cognitive", "behavior", "brain", "neuroscience", "psychiatry", "wellness", "health"
    ]
    is_relevant = any(kw in title_lower for kw in relevant_keywords)
    
    # 관련성 체크는 경고만 하고 스킵하지 않음 (본문에서 확인 가능하도록)
    if not is_relevant:
        logger.info(f"관련성 낮은 뉴스 (제목만): {news.get('title', '')[:50]}")
        # 스킵하지 않고 계속 진행 (본문에서 관련성 확인 가능)
    
    # 기사 본문 스크래핑
    full_text = scrape_article_content(url)
    if not full_text:
        logger.warning(f"본문 추출 실패, 제목만 저장: {url}")
        full_text = news.get("title", "")
    
    # AI 분석
    try:
        title_original = news.get("title", "")
        title_translated = ""
        summary = ""
        
        if country == "US":  # 외국 뉴스
            # 제목 번역
            try:
                title_translated = translate_title(title_original)
                logger.info(f"제목 번역 완료: {title_translated[:50]}")
            except Exception as e:
                logger.error(f"제목 번역 실패: {e}")
                title_translated = title_original
            
            # 100자 수준 한국어 요약
            try:
                summary = generate_news_summary_korean(full_text[:2000])
                if not summary or len(summary) > 150:
                    summary = summary[:100] + "..." if summary and len(summary) > 100 else (title_translated[:100] + "...")
                logger.info(f"요약 생성 완료: {summary[:50]}")
            except Exception as e:
                logger.error(f"요약 생성 실패: {e}")
                summary = title_translated[:100] + "..." if len(title_translated) > 100 else title_translated
            
            # 제목에 번역 병기
            if title_translated != title_original:
                title_display = f"{title_original} ({title_translated})"
            else:
                title_display = title_original
        else:  # 국내 뉴스는 요약 없음
            title_display = title_original
            summary = ""
        
        # 전문성 평가
        evaluation = evaluate_article(full_text[:2000])
        validity_score = evaluation.get("score", 3)
        
        # 키워드 추출
        keywords_list = extract_keywords(full_text[:2000], max_keywords=5)
        
    except Exception as e:
        logger.error(f"AI 분석 실패: {e}")
        title_display = news.get("title", "")
        if country == "US":
            summary = news.get('title', '')[:100] + "..." if news.get('title') else ""
        else:
            summary = ""
        validity_score = 3
        keywords_list = []
    
    # 데이터베이스에 저장
    article_data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "category": news.get("keyword", "psychology"),
        "title": title_display,  # 번역 병기된 제목 저장
        "url": url,
        "content_summary": summary,
        "full_text": full_text[:5000],
        "keywords": keywords_list,
        "validity_score": validity_score,
        "country": country
    }
    
    if save_article_to_db(article_data):
        return article_data
    
    return None


def collect_and_analyze_news(keywords: List[str] = None, countries: List[str] = None, max_per_keyword: int = 10, progress_callback=None):
    """
    뉴스 수집 및 AI 분석을 수행하는 메인 함수 (병렬 처리 최적화)
    
    Args:
        keywords: 검색 키워드 리스트 (기본값: 심리 관련 키워드)
        countries: 국가 코드 리스트 (기본값: ["KR", "US"])
        max_per_keyword: 키워드당 최대 수집 개수
    """
    if keywords is None:
        keywords = ["정신건강", "심리건강", "마음건강", "심리상담", "심리학이론", "심리학", "정신건강증진", "우울증", "불안장애", "트라우마", "상담심리", "임상심리", "psychology", "mental health", "counseling psychology", "clinical psychology", "depression", "anxiety", "trauma"]
    
    if countries is None:
        countries = ["KR", "US"]
    
    logger.info("=== 뉴스 수집 및 분석 시작 (병렬 처리) ===")
    
    total_collected = 0
    total_saved = 0
    
    all_news_list = []  # 모든 수집된 뉴스
    
    for country in countries:
        # 국가별 키워드 매핑 (같은 주제로 양쪽 모두 검색)
        if country == "KR":
            # 한국 뉴스: 한글 키워드 사용
            country_keywords = [k for k in keywords if not k.isascii()]
            # 한글 키워드가 없으면 영문 키워드를 한글로 변환하여 검색
            if not country_keywords:
                # 영문 키워드를 한글로 매핑
                keyword_mapping = {
                    "psychology": "심리학",
                    "mental health": "정신건강",
                    "counseling psychology": "상담심리",
                    "clinical psychology": "임상심리",
                    "depression": "우울증",
                    "anxiety": "불안장애",
                    "trauma": "트라우마"
                }
                country_keywords = [keyword_mapping.get(k, k) for k in keywords if k.isascii()]
        else:  # US
            # 미국 뉴스: 영문 키워드 사용
            country_keywords = [k for k in keywords if k.isascii()]
            # 영문 키워드가 없으면 한글 키워드를 영문으로 변환하여 검색
            if not country_keywords:
                # 한글 키워드를 영문으로 매핑
                keyword_mapping = {
                    "정신건강": "mental health",
                    "심리건강": "mental health",
                    "마음건강": "mental health",
                    "심리상담": "counseling",
                    "심리학이론": "psychology theory",
                    "심리학": "psychology",
                    "정신건강증진": "mental health promotion",
                    "우울증": "depression",
                    "불안장애": "anxiety disorder",
                    "트라우마": "trauma",
                    "상담심리": "counseling psychology",
                    "임상심리": "clinical psychology"
                }
                country_keywords = [keyword_mapping.get(k, "psychology") for k in keywords if not k.isascii()]
        
        if not country_keywords:
            continue
        
        # RSS Feed에서 뉴스 수집
        news_list = fetch_news_from_rss(country_keywords, country, max_per_keyword)
        # 국가 정보 추가
        for news in news_list:
            news["country"] = country
        all_news_list.extend(news_list)
    
    # 전체 작업량 계산
    total_work = len(all_news_list)
    processed_count = 0
    
    logger.info(f"총 {total_work}개 뉴스 수집 완료. 병렬 처리 시작...")
    
    # 병렬 처리 (최대 5개 스레드 동시 실행)
    with ThreadPoolExecutor(max_workers=5) as executor:
        # 모든 뉴스에 대해 병렬 처리 시작
        future_to_news = {
            executor.submit(process_single_news, news, news.get("country", "KR")): news 
            for news in all_news_list
        }
        
        # 완료된 작업부터 처리
        for future in as_completed(future_to_news):
            processed_count += 1
            news = future_to_news[future]
            
            try:
                result = future.result()
                if result:
                    total_collected += 1
                    total_saved += 1
                    
                    # 진행도 업데이트
                    if progress_callback:
                        progress_callback(processed_count, total_work, 
                                        f"처리 중... ({processed_count}/{total_work}) - {total_saved}개 저장됨")
            except Exception as e:
                logger.error(f"뉴스 처리 실패: {news.get('title', '')[:50]} - {e}")
                if progress_callback:
                    progress_callback(processed_count, total_work, 
                                    f"처리 중... ({processed_count}/{total_work})")
    
    logger.info(f"=== 뉴스 수집 완료: {total_collected}개 수집, {total_saved}개 저장 ===")
    return total_collected, total_saved


# 테스트 코드
if __name__ == "__main__":
    # 간단한 테스트 (한국 뉴스만, 키워드 1개만)
    print("=== 뉴스 수집 테스트 ===")
    collect_and_analyze_news(
        keywords=["심리"],
        countries=["KR"],
        max_per_keyword=3
    )
