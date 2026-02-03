"""
저명 학술지 필터링 모듈
해적학술지 제외 및 저명 학술지 확인
"""

# 심리학 관련 저명 학술지 목록 (Impact Factor 기준)
REPUTABLE_JOURNALS = {
    # 최상위 저명 학술지
    "Nature", "Science", "Cell", "Lancet", "New England Journal of Medicine",
    
    # 심리학 최상위 저명 학술지
    "Psychological Review", "Annual Review of Psychology", "Psychological Bulletin",
    "Journal of Personality and Social Psychology", "Psychological Science",
    "Journal of Experimental Psychology", "Developmental Psychology",
    "Journal of Abnormal Psychology", "Clinical Psychological Science",
    
    # 임상심리/상담심리 저명 학술지
    "Journal of Consulting and Clinical Psychology", "Clinical Psychology Review",
    "Journal of Counseling Psychology", "Psychotherapy", "Journal of Clinical Psychology",
    "Cognitive Therapy and Research", "Behavior Therapy", "Journal of Behavior Therapy",
    
    # 신경과학/뇌과학 저명 학술지
    "Nature Neuroscience", "Neuron", "Journal of Neuroscience", "Brain",
    "NeuroImage", "Cerebral Cortex", "Trends in Cognitive Sciences",
    
    # 정신건강 저명 학술지
    "American Journal of Psychiatry", "Archives of General Psychiatry",
    "Journal of the American Academy of Child and Adolescent Psychiatry",
    "Depression and Anxiety", "Journal of Affective Disorders",
    
    # 일반 심리학 저명 학술지
    "Personality and Social Psychology Bulletin", "Social Psychological and Personality Science",
    "Journal of Personality", "Personality and Individual Differences",
    "Journal of Research in Personality", "European Journal of Personality",
    
    # 발달심리 저명 학술지
    "Child Development", "Developmental Science", "Journal of Experimental Child Psychology",
    
    # 인지심리 저명 학술지
    "Cognition", "Journal of Memory and Language", "Cognitive Psychology",
    "Memory & Cognition", "Psychonomic Bulletin & Review",
}

# 해적학술지 목록 (일부 주요 해적학술지)
PREDATORY_JOURNALS = {
    "International Journal of",  # 패턴 매칭용
    "Global Journal of",
    "World Journal of",
    "American Journal of Research",
    "Open Access",  # 일부 해적학술지가 사용
}

# 저명 학술지 패턴 (Impact Factor가 높은 학술지)
REPUTABLE_PATTERNS = [
    "Review", "Annual Review", "Nature", "Science", "Cell", "Lancet",
    "Journal of Consulting", "Journal of Clinical", "Clinical Psychology",
    "Psychological Review", "Psychological Bulletin", "Psychological Science",
    "Journal of Experimental Psychology", "Journal of Personality",
    "Journal of Neuroscience", "Neuron", "Brain", "NeuroImage",
    "American Journal of Psychiatry", "Archives of General Psychiatry",
    "Child Development", "Developmental Psychology", "Cognition",
]

# 해적학술지 패턴
PREDATORY_PATTERNS = [
    "International Journal of",  # 일부는 저명하지만 대부분 해적학술지
    "Global Journal of",
    "World Journal of",
    "American Journal of Research",
    "Open Access Journal of",
    "Scientific Research Publishing",
    "OMICS Publishing Group",
    "Hindawi",  # 일부는 괜찮지만 많은 해적학술지 포함
]


def is_reputable_journal(journal_name: str) -> bool:
    """
    저명 학술지 여부 확인
    
    Args:
        journal_name: 학술지 이름
    
    Returns:
        저명 학술지이면 True, 아니면 False
    """
    if not journal_name:
        return False
    
    journal_name_upper = journal_name.upper()
    
    # 1. 정확한 매칭
    if journal_name in REPUTABLE_JOURNALS:
        return True
    
    # 2. 저명 학술지 패턴 매칭
    for pattern in REPUTABLE_PATTERNS:
        if pattern.upper() in journal_name_upper:
            # 해적학술지 패턴이 동시에 있으면 제외
            is_predatory = any(pred_pattern.upper() in journal_name_upper 
                             for pred_pattern in PREDATORY_PATTERNS 
                             if pred_pattern != "International Journal of")
            if not is_predatory:
                return True
    
    # 3. 해적학술지 패턴 체크
    for pattern in PREDATORY_PATTERNS:
        if pattern.upper() in journal_name_upper:
            # 예외: 일부 저명한 "International Journal of" 학술지
            if pattern == "International Journal of":
                # 특정 저명 학술지는 예외 처리
                reputable_exceptions = [
                    "INTERNATIONAL JOURNAL OF PSYCHOLOGY",
                    "INTERNATIONAL JOURNAL OF CLINICAL",
                ]
                if any(exp in journal_name_upper for exp in reputable_exceptions):
                    continue
            return False
    
    # 4. PubMed/arXiv는 기본적으로 신뢰 가능
    if journal_name in ["PubMed", "arXiv", "bioRxiv", "medRxiv"]:
        return True
    
    # 5. Impact Factor가 있는 학술지는 대부분 저명 (간단한 휴리스틱)
    # "Journal of"로 시작하고 해적학술지 패턴이 없으면 허용
    if journal_name_upper.startswith("JOURNAL OF") or journal_name_upper.startswith("AMERICAN JOURNAL OF"):
        is_predatory = any(pred_pattern.upper() in journal_name_upper 
                         for pred_pattern in PREDATORY_PATTERNS)
        if not is_predatory:
            return True
    
    # 기본값: 보수적으로 False 반환 (저명 학술지가 확실하지 않으면 제외)
    return False


def filter_papers_by_journal(papers: list) -> list:
    """
    논문 리스트에서 저명 학술지 논문만 필터링
    
    Args:
        papers: 논문 딕셔너리 리스트
    
    Returns:
        저명 학술지 논문만 포함된 리스트
    """
    filtered_papers = []
    
    for paper in papers:
        journal = paper.get("journal", "")
        if is_reputable_journal(journal):
            filtered_papers.append(paper)
        else:
            # 로깅 (선택사항)
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"저명 학술지가 아닌 논문 제외: {journal} - {paper.get('title', '')[:50]}")
    
    return filtered_papers
