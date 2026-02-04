"""
데이터베이스 관리 모듈
SQLite 데이터베이스 초기화 및 관리
"""

import sqlite3
import os
from pathlib import Path

# 데이터베이스 파일 경로
DB_DIR = Path("data")
DB_FILE = DB_DIR / "psyinsight.db"


def init_database():
    """데이터베이스 디렉토리 및 파일 초기화"""
    # data 디렉토리 생성
    DB_DIR.mkdir(exist_ok=True)
    
    # 데이터베이스 연결 및 테이블 생성
    conn = get_connection()
    create_tables(conn)
    conn.close()
    print(f"데이터베이스 초기화 완료: {DB_FILE}")


def get_connection():
    """데이터베이스 연결 반환 (디렉토리 및 테이블 자동 생성)"""
    # 디렉토리가 없으면 생성
    DB_DIR.mkdir(exist_ok=True)
    
    # 데이터베이스 연결
    conn = sqlite3.connect(DB_FILE)
    
    # 테이블이 없으면 생성 (최초 실행 시)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='articles'")
        if cursor.fetchone() is None:
            # 테이블이 없으면 생성
            create_tables(conn)
    except:
        # 오류 발생 시에도 테이블 생성 시도
        create_tables(conn)
    
    return conn


def create_tables(conn):
    """필요한 테이블 생성"""
    cursor = conn.cursor()
    
    # articles 테이블 (뉴스)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            content_summary TEXT,
            full_text TEXT,
            keywords TEXT,
            validity_score INTEGER,
            country TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_saved BOOLEAN DEFAULT 0
        )
    """)
    
    # papers 테이블 (논문)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            title TEXT NOT NULL,
            authors TEXT,
            journal TEXT,
            url TEXT NOT NULL UNIQUE,
            abstract TEXT,
            summary TEXT,
            keywords TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_saved BOOLEAN DEFAULT 0
        )
    """)
    
    # economy_news 테이블 (경제 뉴스)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS economy_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            content_summary TEXT,
            full_text TEXT,
            keywords TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_saved BOOLEAN DEFAULT 0
        )
    """)
    
    # economy_reports 테이블 (경제 종합 보고서)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS economy_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL UNIQUE,
            report_text TEXT NOT NULL,
            news_count INTEGER,
            used_news_ids TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # generated_content 테이블 (생성된 콘텐츠 저장)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generated_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            source_ids TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # bookmarks 테이블 (북마크)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            tags TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(item_type, item_id)
        )
    """)
    
    conn.commit()
    print("테이블 생성 완료")


if __name__ == "__main__":
    # 직접 실행 시 데이터베이스 초기화
    init_database()
