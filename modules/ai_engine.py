"""
AI 엔진 모듈
Google Gemini API를 사용하여 텍스트 요약, 평가, 키워드 추출 등을 수행
"""

import os
import json
import logging
from typing import Dict, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gemini API 클라이언트 초기화
def init_gemini_client():
    """Gemini API 클라이언트 초기화"""
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        # Streamlit Secrets에서도 시도
        try:
            import streamlit as st
            if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
                api_key = st.secrets['GEMINI_API_KEY']
        except:
            pass
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY가 환경 변수에 설정되지 않았습니다. .env 파일을 확인하세요.")
    
    genai.configure(api_key=api_key)
    logger.info("Gemini API 클라이언트 초기화 완료")
    return genai


def get_model(model_name: str = None):
    """Gemini 모델 반환"""
    try:
        client = init_gemini_client()
        
        # 사용 가능한 모델 목록 확인
        available_models = []
        try:
            for model in genai.list_models():
                if 'generateContent' in model.supported_generation_methods:
                    available_models.append(model.name)
            logger.info(f"사용 가능한 모델: {available_models[:5]}...")
        except Exception as e:
            logger.warning(f"모델 목록 조회 실패: {e}")
        
        # 모델 이름이 없으면 기본값 사용
        if model_name is None:
            # 우선순위: gemini-1.5-flash-latest -> gemini-1.5-flash -> gemini-1.5-pro-latest -> gemini-1.5-pro
            model_candidates = [
                "gemini-1.5-flash-latest",
                "gemini-1.5-flash", 
                "gemini-1.5-pro-latest",
                "gemini-1.5-pro",
                "gemini-pro"
            ]
        else:
            model_candidates = [model_name]
        
        # 모델 시도
        for candidate in model_candidates:
            try:
                # 모델 이름 정규화 시도
                normalized_names = [
                    candidate,
                    f"models/{candidate}",
                    candidate.replace("models/", "")
                ]
                
                for normalized in normalized_names:
                    try:
                        # 사용 가능한 모델 목록에 있는지 확인
                        if available_models and normalized not in available_models and f"models/{normalized}" not in available_models:
                            # 정확히 일치하는 모델 찾기
                            matching = [m for m in available_models if normalized in m or candidate in m]
                            if matching:
                                normalized = matching[0]
                        
                        model = genai.GenerativeModel(normalized)
                        # 테스트 호출로 실제 사용 가능한지 확인
                        logger.info(f"모델 초기화 성공: {normalized}")
                        return model
                    except Exception as e:
                        logger.debug(f"모델 {normalized} 시도 실패: {e}")
                        continue
            except Exception as e:
                logger.warning(f"모델 {candidate} 사용 실패: {e}")
                continue
        
        # 모든 모델 시도 실패 시 에러
        raise ValueError(f"사용 가능한 모델을 찾을 수 없습니다. 시도한 모델: {model_candidates}, 사용 가능한 모델: {available_models[:10]}")
    except Exception as e:
        logger.error(f"모델 초기화 실패: {e}")
        raise


def translate_title(title: str, max_retries: int = 3) -> str:
    """
    제목을 한국어로 번역
    
    Args:
        title: 번역할 제목
        max_retries: 최대 재시도 횟수
    
    Returns:
        번역된 제목
    """
    prompt = f"""다음 제목을 한국어로 번역해주세요. 번역만 출력하세요.

제목:
{title}

번역:"""
    
    for attempt in range(max_retries):
        try:
            model = get_model()
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 200,
                }
            )
            translated = response.text.strip()
            if translated and len(translated) > 5:
                logger.info("제목 번역 완료")
                return translated
            else:
                return title  # 번역 실패 시 원문 반환
        except Exception as e:
            logger.warning(f"제목 번역 실패 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return title
            import time
            time.sleep(2 ** attempt)


def generate_summary(text: str, max_retries: int = 3) -> str:
    """
    텍스트를 3줄로 요약
    
    Args:
        text: 요약할 텍스트
        max_retries: 최대 재시도 횟수
    
    Returns:
        3줄 요약 문자열
    """
    prompt = f"""다음 뉴스 기사를 3줄로 요약해주세요. 각 줄은 핵심 내용을 간결하게 담아야 합니다.

기사 내용:
{text}

요약:"""
    
    for attempt in range(max_retries):
        try:
            model = get_model()
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 300,
                }
            )
            summary = response.text.strip()
            if summary and len(summary) > 10:  # 최소 길이 체크
                logger.info("요약 생성 완료")
                return summary
            else:
                raise ValueError("요약이 너무 짧거나 비어있습니다.")
        except Exception as e:
            logger.warning(f"요약 생성 실패 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                # 텍스트의 첫 부분을 요약으로 사용
                lines = text.split('\n')[:3]
                fallback_summary = ' '.join([line.strip() for line in lines if line.strip()])[:200]
                return fallback_summary if fallback_summary else "요약을 생성할 수 없습니다."
            import time
            time.sleep(2 ** attempt)  # 지수 백오프


def generate_news_summary_korean(text: str, max_retries: int = 3) -> str:
    """
    외국 뉴스를 한국어로 100자 수준으로 요약
    
    Args:
        text: 요약할 텍스트
        max_retries: 최대 재시도 횟수
    
    Returns:
        100자 수준 한국어 요약
    """
    prompt = f"""다음 외국 뉴스 기사를 한국어로 100자 내외로 간략히 요약해주세요. 핵심 내용만 간결하게 담아주세요.

기사 내용:
{text[:2000]}

한국어 요약:"""
    
    for attempt in range(max_retries):
        try:
            model = get_model()
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 200,
                }
            )
            summary = response.text.strip()
            if summary and len(summary) > 20:
                logger.info("한국어 요약 생성 완료")
                return summary
            else:
                raise ValueError("요약이 너무 짧거나 비어있습니다.")
        except Exception as e:
            logger.warning(f"한국어 요약 생성 실패 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return text[:100] + "..." if len(text) > 100 else text
            import time
            time.sleep(2 ** attempt)


def translate_abstract(abstract: str, max_retries: int = 3) -> str:
    """
    논문 Abstract를 한국어로 번역
    
    Args:
        abstract: 번역할 Abstract
        max_retries: 최대 재시도 횟수
    
    Returns:
        번역된 Abstract
    """
    prompt = f"""다음 논문 초록을 한국어로 번역해주세요. 전문 용어는 원문을 병기하세요.

초록:
{abstract[:3000]}

한국어 번역:"""
    
    for attempt in range(max_retries):
        try:
            model = get_model()
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 2000,
                }
            )
            translated = response.text.strip()
            if translated and len(translated) > 50:
                logger.info("Abstract 번역 완료")
                return translated
            else:
                return abstract  # 번역 실패 시 원문 반환
        except Exception as e:
            logger.warning(f"Abstract 번역 실패 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return abstract
            import time
            time.sleep(2 ** attempt)


def evaluate_article(text: str, max_retries: int = 3) -> Dict:
    """
    기사의 전문성을 평가 (1~5점)
    
    평가 기준:
    - 과학적 연구 근거 여부
    - 연구 타당도 (표본 크기, 방법론)
    - 선행 연구 인용 여부
    - 일반상식 vs 근거기반 논리
    
    Args:
        text: 평가할 기사 텍스트
        max_retries: 최대 재시도 횟수
    
    Returns:
        {"score": int, "reason": str} 형태의 딕셔너리
    """
    prompt = f"""다음 뉴스 기사를 사회과학 논문의 신뢰도 및 타당도 평가 기준에 따라 평가해주세요.

평가 기준:
1. 과학적 연구가 이루어졌는지 / 근거보다는 일반상식에 바탕하는지
2. 연구가 타당한지 / 경험 및 선행보고가 충분한지
3. 저명학회지에 게재 가능한 수준의 근거기반 논리인지

기사 내용:
{text}

다음 JSON 형식으로 응답해주세요:
{{
    "score": 1~5 사이의 정수,
    "reason": "평가 근거를 간단히 설명"
}}"""
    
    for attempt in range(max_retries):
        try:
            model = get_model()
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 200,
                }
            )
            
            # JSON 파싱 시도
            response_text = response.text.strip()
            
            # JSON 블록 추출 (```json ... ``` 형식일 수 있음)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            
            # 점수 검증
            score = int(result.get("score", 3))
            if score < 1 or score > 5:
                score = 3
            
            logger.info(f"기사 평가 완료: {score}점")
            return {
                "score": score,
                "reason": result.get("reason", "평가 완료")
            }
        except json.JSONDecodeError as e:
            logger.warning(f"JSON 파싱 실패 (시도 {attempt + 1}/{max_retries}): {e}")
            # JSON 파싱 실패 시 기본값 반환
            if attempt == max_retries - 1:
                return {"score": 3, "reason": "평가 중 오류 발생"}
        except Exception as e:
            logger.warning(f"평가 실패 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return {"score": 3, "reason": "평가 중 오류 발생"}
            import time
            time.sleep(2 ** attempt)


def extract_keywords(text: str, max_keywords: int = 5, max_retries: int = 3) -> List[str]:
    """
    텍스트에서 핵심 키워드 추출
    
    Args:
        text: 키워드를 추출할 텍스트
        max_keywords: 추출할 키워드 개수
        max_retries: 최대 재시도 횟수
    
    Returns:
        키워드 리스트
    """
    prompt = f"""다음 텍스트에서 핵심 키워드를 {max_keywords}개 추출해주세요.

텍스트:
{text}

다음 JSON 형식으로 응답해주세요:
{{
    "keywords": ["키워드1", "키워드2", ...]
}}"""
    
    for attempt in range(max_retries):
        try:
            model = get_model()
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 200,
                }
            )
            
            response_text = response.text.strip()
            
            # JSON 블록 추출
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            keywords = result.get("keywords", [])
            
            # 최대 개수 제한
            keywords = keywords[:max_keywords]
            
            logger.info(f"키워드 추출 완료: {len(keywords)}개")
            return keywords
        except json.JSONDecodeError as e:
            logger.warning(f"JSON 파싱 실패 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                # 기본 키워드 추출 시도 (간단한 방법)
                words = text.split()[:max_keywords]
                return words
        except Exception as e:
            logger.warning(f"키워드 추출 실패 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return []
            import time
            time.sleep(2 ** attempt)


def summarize_paper(abstract: str, max_retries: int = 3) -> Dict:
    """
    논문 초록을 요약 (연구 목적, 방법, 결과, 시사점)
    
    Args:
        abstract: 논문 초록
        max_retries: 최대 재시도 횟수
    
    Returns:
        {
            "purpose": str,
            "method": str,
            "result": str,
            "implication": str
        } 형태의 딕셔너리
    """
    prompt = f"""다음 논문 초록을 읽고 연구 목적, 방법, 결과, 시사점으로 구조화하여 요약해주세요.

초록:
{abstract}

다음 JSON 형식으로 응답해주세요:
{{
    "purpose": "연구 목적",
    "method": "연구 방법",
    "result": "주요 결과",
    "implication": "시사점"
}}"""
    
    for attempt in range(max_retries):
        try:
            model = get_model()
            response = model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.2,
                    "max_output_tokens": 500,
                }
            )
            
            response_text = response.text.strip()
            
            # JSON 블록 추출
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            
            logger.info("논문 요약 완료")
            return {
                "purpose": result.get("purpose", ""),
                "method": result.get("method", ""),
                "result": result.get("result", ""),
                "implication": result.get("implication", "")
            }
        except json.JSONDecodeError as e:
            logger.warning(f"JSON 파싱 실패 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return {
                    "purpose": "파싱 실패",
                    "method": "",
                    "result": "",
                    "implication": ""
                }
        except Exception as e:
            logger.warning(f"논문 요약 실패 (시도 {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                return {
                    "purpose": "요약 실패",
                    "method": "",
                    "result": "",
                    "implication": ""
                }
            import time
            time.sleep(2 ** attempt)


# 테스트 코드
if __name__ == "__main__":
    # 간단한 테스트
    test_text = "최신 연구에 따르면 정기적인 운동이 우울증 증상을 완화하는 데 도움이 된다고 합니다."
    
    print("=== AI 엔진 테스트 ===")
    print(f"\n원문: {test_text}")
    
    print("\n1. 요약 테스트:")
    summary = generate_summary(test_text)
    print(f"요약: {summary}")
    
    print("\n2. 평가 테스트:")
    evaluation = evaluate_article(test_text)
    print(f"점수: {evaluation['score']}/5")
    print(f"근거: {evaluation['reason']}")
    
    print("\n3. 키워드 추출 테스트:")
    keywords = extract_keywords(test_text)
    print(f"키워드: {keywords}")
