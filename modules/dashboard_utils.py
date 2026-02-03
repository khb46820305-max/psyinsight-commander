"""
대시보드 유틸리티 모듈
트렌드 분석, 통계 계산 등 대시보드에 필요한 함수들
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import Counter
from modules.database import get_connection


def get_category_summary(category: str, days: int = 7) -> Dict:
    """
    카테고리별 요약 정보 계산
    
    Args:
        category: 카테고리명
        days: 조회할 일수
    
    Returns:
        {"count": int, "keywords": List[str], "trend": str}
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        # 해당 카테고리 뉴스 개수
        cursor.execute("""
            SELECT COUNT(*) FROM economy_news
            WHERE category = ? AND date BETWEEN ? AND ?
        """, (category, start_date, end_date))
        count = cursor.fetchone()[0]
        
        # 전일 대비 비교 (최근 3일)
        three_days_ago = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
        cursor.execute("""
            SELECT COUNT(*) FROM economy_news
            WHERE category = ? AND date BETWEEN ? AND ?
        """, (category, three_days_ago, end_date))
        recent_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM economy_news
            WHERE category = ? AND date < ?
        """, (category, three_days_ago))
        old_count = cursor.fetchone()[0]
        
        # 트렌드 계산
        if old_count > 0:
            trend_diff = recent_count - old_count
            if trend_diff > 0:
                trend = f"📈 +{trend_diff}건"
            elif trend_diff < 0:
                trend = f"📉 {trend_diff}건"
            else:
                trend = "➡️ 동일"
        else:
            trend = "📊 신규"
        
        # 주요 키워드 추출
        cursor.execute("""
            SELECT keywords FROM economy_news
            WHERE category = ? AND date BETWEEN ? AND ? AND keywords IS NOT NULL
        """, (category, start_date, end_date))
        
        all_keywords = []
        for row in cursor.fetchall():
            try:
                keywords = json.loads(row[0]) if row[0] else []
                all_keywords.extend(keywords)
            except:
                pass
        
        # 키워드 빈도수 계산
        keyword_counter = Counter(all_keywords)
        top_keywords = [kw for kw, _ in keyword_counter.most_common(3)]
        
        conn.close()
        
        return {
            "count": count,
            "keywords": top_keywords,
            "trend": trend
        }
    except Exception as e:
        return {"count": 0, "keywords": [], "trend": "❌ 오류"}


def get_trend_data(category: str, days: int = 7) -> List[Tuple[str, int]]:
    """
    날짜별 트렌드 데이터 계산
    
    Args:
        category: 카테고리명
        days: 조회할 일수
    
    Returns:
        [(날짜, 개수), ...] 리스트
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        end_date = datetime.now()
        trend_data = []
        
        for i in range(days):
            date = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
            cursor.execute("""
                SELECT COUNT(*) FROM economy_news
                WHERE category = ? AND date = ?
            """, (category, date))
            count = cursor.fetchone()[0]
            trend_data.append((date, count))
        
        conn.close()
        return list(reversed(trend_data))  # 오래된 날짜부터
    except Exception as e:
        return []


def get_top_issues(category: str = None, limit: int = 5) -> List[Dict]:
    """
    주요 이슈 하이라이트 (키워드 빈도수 기반)
    
    Args:
        category: 카테고리 필터 (None이면 전체)
        limit: 최대 개수
    
    Returns:
        [{"title": str, "url": str, "date": str, "keyword_count": int}, ...]
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        if category:
            cursor.execute("""
                SELECT title, url, date, keywords FROM economy_news
                WHERE category = ? AND date BETWEEN ? AND ?
                ORDER BY created_at DESC
            """, (category, start_date, end_date))
        else:
            cursor.execute("""
                SELECT title, url, date, keywords FROM economy_news
                WHERE date BETWEEN ? AND ?
                ORDER BY created_at DESC
            """, (start_date, end_date))
        
        all_news = cursor.fetchall()
        
        # 키워드 빈도수 기반으로 중요도 계산
        scored_news = []
        for title, url, date, keywords_json in all_news:
            try:
                keywords = json.loads(keywords_json) if keywords_json else []
                # 제목에 포함된 키워드 수로 중요도 계산
                keyword_count = len(keywords)
                # 제목 길이도 고려 (너무 짧거나 길면 감점)
                title_score = 1.0 if 20 <= len(title) <= 100 else 0.8
                score = keyword_count * title_score
                
                scored_news.append({
                    "title": title,
                    "url": url,
                    "date": date,
                    "keyword_count": keyword_count,
                    "score": score
                })
            except:
                pass
        
        # 점수 순으로 정렬
        scored_news.sort(key=lambda x: x["score"], reverse=True)
        
        conn.close()
        return scored_news[:limit]
    except Exception as e:
        return []


def get_news_trend_data(days: int = 7) -> Dict[str, List[Tuple[str, int]]]:
    """
    뉴스 트렌드 데이터 (키워드별)
    
    Args:
        days: 조회할 일수
    
    Returns:
        {"키워드": [(날짜, 개수), ...], ...}
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        end_date = datetime.now()
        start_date = (end_date - timedelta(days=days)).strftime("%Y-%m-%d")
        
        # 모든 키워드 수집
        cursor.execute("""
            SELECT keywords, date FROM articles
            WHERE date >= ? AND keywords IS NOT NULL
        """, (start_date,))
        
        keyword_dates = {}
        for keywords_json, date in cursor.fetchall():
            try:
                keywords = json.loads(keywords_json) if keywords_json else []
                for keyword in keywords:
                    if keyword not in keyword_dates:
                        keyword_dates[keyword] = []
                    keyword_dates[keyword].append(date)
            except:
                pass
        
        # 날짜별로 그룹화
        trend_data = {}
        for keyword, dates in keyword_dates.items():
            date_counter = Counter(dates)
            trend_list = []
            for i in range(days):
                check_date = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
                count = date_counter.get(check_date, 0)
                trend_list.append((check_date, count))
            trend_data[keyword] = list(reversed(trend_list))
        
        conn.close()
        return trend_data
    except Exception as e:
        return {}


def get_paper_trend_data(days: int = 30) -> Dict[str, List[Tuple[str, int]]]:
    """
    논문 트렌드 데이터 (키워드별)
    
    Args:
        days: 조회할 일수
    
    Returns:
        {"키워드": [(날짜, 개수), ...], ...}
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        end_date = datetime.now()
        start_date = (end_date - timedelta(days=days)).strftime("%Y-%m-%d")
        
        # 모든 키워드 수집
        cursor.execute("""
            SELECT keywords, date FROM papers
            WHERE date >= ? AND keywords IS NOT NULL
        """, (start_date,))
        
        keyword_dates = {}
        for keywords_json, date in cursor.fetchall():
            try:
                keywords = json.loads(keywords_json) if keywords_json else []
                for keyword in keywords:
                    if keyword not in keyword_dates:
                        keyword_dates[keyword] = []
                    keyword_dates[keyword].append(date)
            except:
                pass
        
        # 날짜별로 그룹화
        trend_data = {}
        for keyword, dates in keyword_dates.items():
            date_counter = Counter(dates)
            trend_list = []
            for i in range(days):
                check_date = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
                count = date_counter.get(check_date, 0)
                trend_list.append((check_date, count))
            trend_data[keyword] = list(reversed(trend_list))
        
        conn.close()
        return trend_data
    except Exception as e:
        return {}
