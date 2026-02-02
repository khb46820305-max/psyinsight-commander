"""
이메일 발송 모듈
Gmail SMTP를 사용하여 헤드라인 요약을 이메일로 발송
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
from typing import List, Dict
import json

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_email_config():
    """이메일 설정 가져오기"""
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    receiver = os.getenv("EMAIL_RECEIVER")
    
    # Streamlit Secrets에서도 시도
    try:
        import streamlit as st
        if hasattr(st, 'secrets'):
            if not sender and 'EMAIL_SENDER' in st.secrets:
                sender = st.secrets['EMAIL_SENDER']
            if not password and 'EMAIL_PASSWORD' in st.secrets:
                password = st.secrets['EMAIL_PASSWORD']
            if not receiver and 'EMAIL_RECEIVER' in st.secrets:
                receiver = st.secrets['EMAIL_RECEIVER']
    except:
        pass
    
    if not all([sender, password, receiver]):
        raise ValueError("이메일 설정이 완료되지 않았습니다. .env 파일을 확인하세요.")
    
    return sender, password, receiver


def create_news_email_html(news_list: List[Dict]) -> str:
    """뉴스 헤드라인 이메일 HTML 생성"""
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .news-item {{ border-left: 4px solid #4CAF50; padding: 15px; margin: 15px 0; background-color: #f9f9f9; }}
            .title {{ font-size: 18px; font-weight: bold; color: #333; }}
            .summary {{ color: #666; margin: 10px 0; }}
            .meta {{ color: #999; font-size: 12px; }}
            .link {{ color: #4CAF50; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🧠 PsyInsight Commander</h1>
            <p>오늘의 심리 뉴스 헤드라인 ({datetime.now().strftime('%Y-%m-%d')})</p>
        </div>
        <div class="content">
            <h2>📰 수집된 뉴스: {len(news_list)}개</h2>
    """
    
    # 평점 높은 순으로 정렬
    sorted_news = sorted(news_list, key=lambda x: x.get('validity_score', 3), reverse=True)
    
    for news in sorted_news:
        score = news.get('validity_score', 3)
        stars = '⭐' * score
        html += f"""
            <div class="news-item">
                <div class="title">{stars} {news.get('title', '')}</div>
                <div class="summary">{news.get('content_summary', '')}</div>
                <div class="meta">
                    📅 {news.get('date', '')} | 🌍 {news.get('country', '')} | 
                    <a href="{news.get('url', '')}" class="link">원문 보기</a>
                </div>
            </div>
        """
    
    html += """
        </div>
        <div style="text-align: center; padding: 20px; color: #999;">
            <p>이 이메일은 PsyInsight Commander에서 자동으로 발송되었습니다.</p>
        </div>
    </body>
    </html>
    """
    return html


def send_news_summary(news_list: List[Dict], max_retries: int = 3) -> bool:
    """뉴스 헤드라인 이메일 발송"""
    if not news_list:
        logger.info("발송할 뉴스가 없습니다.")
        return False
    
    try:
        sender, password, receiver = get_email_config()
        
        # 이메일 생성
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"[PsyInsight] 오늘의 심리 뉴스 헤드라인 ({datetime.now().strftime('%Y-%m-%d')})"
        msg['From'] = sender
        msg['To'] = receiver
        
        # HTML 본문
        html_content = create_news_email_html(news_list)
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Gmail SMTP로 발송
        for attempt in range(max_retries):
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender, password)
                server.send_message(msg)
                server.quit()
                
                logger.info(f"이메일 발송 완료: {receiver}")
                return True
            except Exception as e:
                logger.warning(f"이메일 발송 실패 (시도 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2)
        
        return False
        
    except Exception as e:
        logger.error(f"이메일 발송 중 오류: {e}")
        return False
