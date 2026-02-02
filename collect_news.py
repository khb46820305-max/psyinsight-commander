"""
뉴스 수집 스크립트 (독립 실행)
Windows 작업 스케줄러에서 실행하거나 수동으로 실행 가능
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.news_collector import collect_and_analyze_news
from modules.database import get_connection
from modules.email_sender import send_news_summary
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """메인 실행 함수"""
    logger.info("=== 뉴스 수집 스크립트 시작 ===")
    
    try:
        # 뉴스 수집 및 분석
        collected, saved = collect_and_analyze_news(
            keywords=["심리", "마음건강", "뇌과학", "상담", "psychology", "mental health", "neuroscience", "counseling"],
            countries=["KR", "US"],
            max_per_keyword=10
        )
        
        logger.info(f"수집 완료: {collected}개 수집, {saved}개 저장")
        
        # 오늘 수집된 뉴스 가져오기
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT date, title, url, content_summary, validity_score, country
            FROM articles
            WHERE date = date('now')
            ORDER BY validity_score DESC
            LIMIT 20
        """)
        
        news_list = []
        for row in cursor.fetchall():
            news_list.append({
                "date": row[0],
                "title": row[1],
                "url": row[2],
                "content_summary": row[3],
                "validity_score": row[4],
                "country": row[5]
            })
        
        conn.close()
        
        # 이메일 발송
        if news_list:
            logger.info(f"이메일 발송 시작: {len(news_list)}개 뉴스")
            success = send_news_summary(news_list)
            if success:
                logger.info("이메일 발송 완료")
            else:
                logger.warning("이메일 발송 실패")
        else:
            logger.info("발송할 뉴스가 없습니다.")
        
        logger.info("=== 뉴스 수집 스크립트 완료 ===")
        
    except Exception as e:
        logger.error(f"오류 발생: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
