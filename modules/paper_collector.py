"""
논문 수집 모듈
arXiv, PubMed에서 심리학 관련 논문을 수집
"""

import requests
import logging
from datetime import datetime
from typing import List, Dict, Optional
import time
import json
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed

from modules.ai_engine import summarize_paper, translate_abstract, extract_keywords
from modules.database import get_connection
from modules.journal_filter import is_reputable_journal, filter_papers_by_journal

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_papers_from_arxiv(keywords: List[str], max_results: int = 20) -> List[Dict]:
    """
    arXiv API에서 논문 수집
    
    Args:
        keywords: 검색 키워드 리스트
        max_results: 최대 수집 개수
    
    Returns:
        논문 딕셔너리 리스트
    """
    all_papers = []
    
    for keyword in keywords:
        try:
            # arXiv API URL
            url = f"http://export.arxiv.org/api/query"
            params = {
                "search_query": f"all:{keyword}",
                "start": 0,
                "max_results": max_results,
                "sortBy": "submittedDate",
                "sortOrder": "descending"
            }
            
            logger.info(f"arXiv API 호출 중: {keyword}")
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # XML 파싱
            root = ET.fromstring(response.content)
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            
            entries = root.findall('atom:entry', ns)
            
            for entry in entries:
                title = entry.find('atom:title', ns).text.strip() if entry.find('atom:title', ns) is not None else ""
                summary = entry.find('atom:summary', ns).text.strip() if entry.find('atom:summary', ns) is not None else ""
                link = entry.find('atom:id', ns).text if entry.find('atom:id', ns) is not None else ""
                
                # 저자 추출
                authors = []
                for author in entry.findall('atom:author', ns):
                    name = author.find('atom:name', ns)
                    if name is not None:
                        authors.append(name.text)
                
                # 발행일 추출
                published = entry.find('atom:published', ns)
                published_date = published.text[:10] if published is not None else datetime.now().strftime("%Y-%m-%d")
                
                paper = {
                    "title": title,
                    "abstract": summary,
                    "authors": authors,
                    "url": link,
                    "date": published_date,
                    "journal": "arXiv",
                    "keyword": keyword
                }
                all_papers.append(paper)
            
            time.sleep(0.5)  # Rate limiting (병렬 처리로 인해 감소)
            
        except Exception as e:
            logger.error(f"arXiv API 호출 실패 ({keyword}): {e}")
            continue
    
    logger.info(f"총 {len(all_papers)}개의 논문 수집 완료")
    return all_papers


def fetch_papers_from_pubmed(keywords: List[str], max_results: int = 20) -> List[Dict]:
    """
    PubMed API에서 논문 수집 (간단 버전)
    
    Args:
        keywords: 검색 키워드 리스트
        max_results: 최대 수집 개수
    
    Returns:
        논문 딕셔너리 리스트
    """
    all_papers = []
    
    for keyword in keywords:
        try:
            # PubMed E-utilities API
            search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            search_params = {
                "db": "pubmed",
                "term": keyword,
                "retmax": max_results,
                "sort": "pub_date",
                "retmode": "json"
            }
            
            logger.info(f"PubMed API 호출 중: {keyword}")
            
            response = requests.get(search_url, params=search_params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            pmids = data.get("esearchresult", {}).get("idlist", [])
            
            if not pmids:
                continue
            
            # 상세 정보 가져오기
            fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            fetch_params = {
                "db": "pubmed",
                "id": ",".join(pmids[:max_results]),
                "retmode": "xml"
            }
            
            fetch_response = requests.get(fetch_url, params=fetch_params, timeout=30)
            fetch_response.raise_for_status()
            
            # XML 파싱 (간단 버전)
            root = ET.fromstring(fetch_response.content)
            
            for article in root.findall(".//PubmedArticle"):
                title_elem = article.find(".//ArticleTitle")
                title = title_elem.text if title_elem is not None else ""
                
                abstract_elem = article.find(".//AbstractText")
                abstract = abstract_elem.text if abstract_elem is not None else ""
                
                # 저자 추출
                authors = []
                for author in article.findall(".//Author"):
                    lastname = author.find("LastName")
                    firstname = author.find("FirstName")
                    if lastname is not None:
                        name = lastname.text
                        if firstname is not None:
                            name += f" {firstname.text}"
                        authors.append(name)
                
                # DOI 추출
                doi_elem = article.find(".//ArticleId[@IdType='doi']")
                doi = doi_elem.text if doi_elem is not None else ""
                url = f"https://pubmed.ncbi.nlm.nih.gov/{pmids[0]}" if pmids else ""
                
                # 발행일
                pub_date = article.find(".//PubDate/Year")
                date = pub_date.text if pub_date is not None else datetime.now().strftime("%Y-%m-%d")
                
                # 학술지 이름 추출
                journal_elem = article.find(".//Journal/Title")
                journal_name = journal_elem.text if journal_elem is not None else "PubMed"
                
                paper = {
                    "title": title,
                    "abstract": abstract,
                    "authors": authors,
                    "url": url,
                    "date": date,
                    "journal": journal_name,
                    "keyword": keyword
                }
                all_papers.append(paper)
            
            time.sleep(0.5)  # Rate limiting (병렬 처리로 인해 감소)
            
        except Exception as e:
            logger.error(f"PubMed API 호출 실패 ({keyword}): {e}")
            continue
    
    logger.info(f"총 {len(all_papers)}개의 논문 수집 완료")
    return all_papers


def check_duplicate_paper(url: str) -> bool:
    """논문 URL 중복 체크"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM papers WHERE url = ?", (url,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        logger.error(f"중복 체크 실패: {e}")
        return False


def save_paper_to_db(paper_data: Dict) -> bool:
    """논문을 데이터베이스에 저장"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO papers (
                date, title, authors, journal, url, abstract, summary, keywords, category
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            paper_data.get("date", datetime.now().strftime("%Y-%m-%d")),
            paper_data.get("title", ""),
            json.dumps(paper_data.get("authors", []), ensure_ascii=False),
            paper_data.get("journal", ""),
            paper_data.get("url", ""),
            paper_data.get("abstract", ""),
            json.dumps(paper_data.get("summary", {}), ensure_ascii=False),
            json.dumps(paper_data.get("keywords", []), ensure_ascii=False),
            paper_data.get("category", "psychology")
        ))
        
        conn.commit()
        conn.close()
        logger.info(f"논문 저장 완료: {paper_data.get('title', '')[:50]}")
        return True
        
    except Exception as e:
        logger.error(f"논문 저장 실패: {e}")
        return False


def process_single_paper(paper: Dict) -> Optional[Dict]:
    """
    단일 논문 처리 함수 (병렬 처리용)
    
    Args:
        paper: 논문 딕셔너리
    
    Returns:
        처리된 논문 데이터 (실패 시 None)
    """
    url = paper.get("url", "")
    
    # 중복 체크 (먼저 수행하여 불필요한 처리 방지)
    if check_duplicate_paper(url):
        logger.info(f"중복 논문 스킵: {url}")
        return None
    
    abstract = paper.get("abstract", "")
    title = paper.get("title", "")
    journal = paper.get("journal", "")
    if not abstract:
        return None
    
    # 논문이 외국 논문인지 확인 (arXiv, PubMed, 영문 저널명 등)
    is_foreign = journal.lower() in ["arxiv", "pubmed"] or (abstract and any(char.isascii() and char.isalpha() for char in abstract[:100]))
    
    # AI 분석
    try:
        abstract_translated = ""
        summary = {}  # 한국 논문은 해석 요약 없음
        
        if is_foreign and abstract:
            # 외국 논문: Abstract 한글 번역
            try:
                abstract_translated = translate_abstract(abstract[:3000])
                logger.info(f"Abstract 번역 완료: {len(abstract_translated)}자")
            except Exception as e:
                logger.error(f"Abstract 번역 실패: {e}")
                abstract_translated = abstract  # 번역 실패 시 원문 사용
            # 해석 요약은 제거하고 번역된 Abstract만 사용
            summary = {}  # 빈 딕셔너리로 저장
        else:
            # 한국 논문: 해석 요약 없음, 원문 Abstract만 사용
            abstract_translated = abstract
            summary = {}
        
        # 키워드 추출
        try:
            keywords_list = extract_keywords(abstract[:3000], max_keywords=5)
        except:
            keywords_list = extract_keywords(title[:500], max_keywords=5) if title else []
            
    except Exception as e:
        logger.error(f"AI 분석 실패: {e}")
        import traceback
        logger.error(traceback.format_exc())
        abstract_translated = abstract
        summary = {}
        keywords_list = extract_keywords(title[:500], max_keywords=5) if title else []
    
    # 데이터베이스에 저장
    # Abstract에 번역 병기 (외국 논문인 경우)
    if is_foreign and abstract_translated and abstract_translated != abstract and len(abstract_translated) > 50:
        abstract_display = f"[원문]\n{abstract[:2000]}\n\n[한국어 번역]\n{abstract_translated[:2000]}"
    else:
        abstract_display = abstract
    
    paper_data = {
        "date": paper.get("date", datetime.now().strftime("%Y-%m-%d")),
        "title": paper.get("title", ""),
        "authors": paper.get("authors", []),
        "journal": paper.get("journal", ""),
        "url": url,
        "abstract": abstract_display[:5000],  # 번역 병기된 Abstract
        "summary": summary,  # 빈 딕셔너리 (해석 요약 제거)
        "keywords": keywords_list,
        "category": paper.get("keyword", "psychology")
    }
    
    if save_paper_to_db(paper_data):
        return paper_data
    
    return None


def collect_and_analyze_papers(keywords: List[str] = None, sources: List[str] = None, max_per_keyword: int = 10, progress_callback=None):
    """
    논문 수집 및 AI 분석 메인 함수 (병렬 처리 최적화)
    
    Args:
        keywords: 검색 키워드 리스트
        sources: 수집 소스 (arxiv, pubmed)
        max_per_keyword: 키워드당 최대 수집 개수
    """
    if keywords is None:
        keywords = ["psychology", "counseling", "correctional psychology", "criminal psychology"]
    
    if sources is None:
        sources = ["arxiv"]  # 기본은 arxiv만 (pubmed는 선택)
    
    logger.info("=== 논문 수집 및 분석 시작 (병렬 처리) ===")
    
    total_collected = 0
    total_saved = 0
    
    all_papers = []
    
    # arXiv 수집
    if "arxiv" in sources:
        arxiv_papers = fetch_papers_from_arxiv(keywords, max_per_keyword)
        all_papers.extend(arxiv_papers)
    
    # PubMed 수집 (선택)
    if "pubmed" in sources:
        pubmed_papers = fetch_papers_from_pubmed(keywords, max_per_keyword)
        all_papers.extend(pubmed_papers)
    
    # 저명 학술지 필터링 및 우선순위 정렬
    logger.info(f"저명 학술지 필터링 전: {len(all_papers)}개 논문")
    
    # 저명 학술지와 일반 학술지 분리
    reputable_papers = []
    other_papers = []
    
    for paper in all_papers:
        journal = paper.get("journal", "")
        if is_reputable_journal(journal):
            reputable_papers.append(paper)
        else:
            other_papers.append(paper)
    
    # 저명 학술지를 먼저, 그 다음 일반 학술지
    all_papers = reputable_papers + other_papers
    
    logger.info(f"저명 학술지: {len(reputable_papers)}개, 일반 학술지: {len(other_papers)}개")
    
    # 전체 작업량 계산
    total_work = len(all_papers)
    processed_count = 0
    
    logger.info(f"총 {total_work}개 논문 수집 완료. 병렬 처리 시작...")
    
    # 병렬 처리 (최대 5개 스레드 동시 실행)
    with ThreadPoolExecutor(max_workers=5) as executor:
        # 모든 논문에 대해 병렬 처리 시작
        future_to_paper = {
            executor.submit(process_single_paper, paper): paper 
            for paper in all_papers
        }
        
        # 완료된 작업부터 처리
        for future in as_completed(future_to_paper):
            processed_count += 1
            paper = future_to_paper[future]
            
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
                logger.error(f"논문 처리 실패: {paper.get('title', '')[:50]} - {e}")
                if progress_callback:
                    progress_callback(processed_count, total_work, 
                                    f"처리 중... ({processed_count}/{total_work})")
    
    logger.info(f"=== 논문 수집 완료: {total_collected}개 수집, {total_saved}개 저장 ===")
    return total_collected, total_saved
