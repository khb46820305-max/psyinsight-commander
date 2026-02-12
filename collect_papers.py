"""
논문 수집 스크립트 (독립 실행)
Windows 작업 스케줄러에서 실행하거나 수동으로 실행 가능
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from modules.paper_collector import collect_and_analyze_papers
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """메인 실행 함수"""
    logger.info("=== 논문 수집 스크립트 시작 ===")
    
    try:
        # 논문 수집 및 분석
        collected, saved = collect_and_analyze_papers(
            keywords=["psychology", "counseling", "correctional psychology", "criminal psychology"],
            sources=["arxiv"],
            max_per_keyword=10
        )
        
        logger.info(f"수집 완료: {collected}개 수집, {saved}개 저장")
        logger.info("=== 논문 수집 스크립트 완료 ===")
        
    except Exception as e:
        logger.error(f"오류 발생: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
