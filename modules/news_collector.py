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

from modules.ai_engine import generate_summary, evaluate_article, extract_keywords
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
                if "상담" in keyword or "심리" in keyword:
                    search_query = f"{keyword} -법률 -법무 -디지털 -건설 -공제회"
                rss_url = f"https://news.google.com/rss/search?q={search_query}&hl=ko&gl=KR&ceid=KR:ko"
            else:  # US
                rss_url = f"https://news.google.com/rss/search?q={keyword}&hl=en&gl=US&ceid=US:en"
            
            logger.info(f"RSS Feed 파싱 중: {keyword} ({country})")
            
            # RSS Feed 파싱
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:max_results]:
                news_item = {
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "source": entry.get("source", {}).get("title", "") if hasattr(entry, "source") else "",
                    "country": country,
                    "keyword": keyword
                }
                all_news.append(news_item)
            
            # 요청 간격 조절 (Rate limiting)
            time.sleep(1)
            
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
                time.sleep(2)
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


def collect_and_analyze_news(keywords: List[str] = None, countries: List[str] = None, max_per_keyword: int = 10):
    """
    뉴스 수집 및 AI 분석을 수행하는 메인 함수
    
    Args:
        keywords: 검색 키워드 리스트 (기본값: 심리 관련 키워드)
        countries: 국가 코드 리스트 (기본값: ["KR", "US"])
        max_per_keyword: 키워드당 최대 수집 개수
    """
    if keywords is None:
        keywords = ["정신건강", "심리건강", "마음건강", "심리상담", "심리학이론", "심리학", "정신건강증진", "우울증", "불안장애", "트라우마", "상담심리", "임상심리", "psychology", "mental health", "counseling psychology", "clinical psychology", "depression", "anxiety", "trauma"]
    
    if countries is None:
        countries = ["KR", "US"]
    
    logger.info("=== 뉴스 수집 및 분석 시작 ===")
    
    total_collected = 0
    total_saved = 0
    
    for country in countries:
        # 국가별 키워드 필터링
        if country == "KR":
            country_keywords = [k for k in keywords if not k.isascii()]  # 한글 키워드
        else:  # US
            country_keywords = [k for k in keywords if k.isascii()]  # 영문 키워드
        
        if not country_keywords:
            continue
        
        # RSS Feed에서 뉴스 수집
        news_list = fetch_news_from_rss(country_keywords, country, max_per_keyword)
        
        for news in news_list:
            url = news.get("url", "")
            
            # 중복 체크
            if check_duplicate(url):
                logger.info(f"중복 기사 스킵: {url}")
                continue
            
            total_collected += 1
            
            # 기사 본문 스크래핑
            full_text = scrape_article_content(url)
            if not full_text:
                logger.warning(f"본문 추출 실패, 제목만 저장: {url}")
                full_text = news.get("title", "")
            
            # 제목 기반 관련성 필터링 (심리/정신건강 관련 키워드 체크)
            title_lower = news.get("title", "").lower()
            relevant_keywords = ["심리", "정신", "마음", "우울", "불안", "트라우마", "상담", "치료", "psychology", "mental", "counseling", "therapy", "depression", "anxiety", "trauma"]
            is_relevant = any(kw in title_lower for kw in relevant_keywords)
            
            # 관련 없는 뉴스는 스킵 (제목에 관련 키워드가 없으면)
            if not is_relevant:
                logger.info(f"관련 없는 뉴스 스킵: {news.get('title', '')[:50]}")
                continue
            
            # AI 분석
            try:
                # 요약 생성
                summary = generate_summary(full_text[:2000])  # 최대 2000자만 전달
                if not summary or summary == "요약 생성에 실패했습니다.":
                    # 제목을 기반으로 간단한 요약 생성
                    summary = f"{news.get('title', '')[:100]}..."
                
                # 전문성 평가
                evaluation = evaluate_article(full_text[:2000])
                validity_score = evaluation.get("score", 3)
                
                # 키워드 추출
                keywords_list = extract_keywords(full_text[:2000], max_keywords=5)
                
            except Exception as e:
                logger.error(f"AI 분석 실패: {e}")
                # 기본값 설정
                summary = f"{news.get('title', '')[:100]}..." if news.get('title') else "요약을 생성할 수 없습니다."
                validity_score = 3
                keywords_list = []
            
            # 데이터베이스에 저장
            article_data = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "category": news.get("keyword", "psychology"),
                "title": news.get("title", ""),
                "url": url,
                "content_summary": summary,
                "full_text": full_text[:5000],  # 최대 5000자
                "keywords": keywords_list,
                "validity_score": validity_score,
                "country": country
            }
            
            if save_article_to_db(article_data):
                total_saved += 1
            
            # 요청 간격 조절
            time.sleep(2)
    
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
