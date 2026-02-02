"""
PsyInsight Commander - 메인 Streamlit 애플리케이션
심리학 전문가를 위한 통합 대시보드
"""

import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="PsyInsight Commander",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 제목
st.title("🧠 PsyInsight Commander")
st.markdown("### 심리 인사이트 통합 지휘소")

# 탭 생성
tab1, tab2, tab3 = st.tabs([
    "📰 Tab 1: 사이콜로지 트랜드 레이더",
    "📚 Tab 2: 아카데믹 아카이브",
    "✨ Tab 3: 콘텐츠 팩토리"
])

# Tab 1: 사이콜로지 트랜드 레이더
with tab1:
    st.header("📰 사이콜로지 트랜드 레이더")
    
    # 뉴스 수집 버튼
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("미국과 한국의 심리 관련 뉴스를 수집하고 AI로 분석합니다.")
    with col2:
        if st.button("🔄 뉴스 수집", type="primary"):
            with st.spinner("뉴스 수집 중... (시간이 걸릴 수 있습니다)"):
                try:
                    from modules.news_collector import collect_and_analyze_news
                    collected, saved = collect_and_analyze_news(
                        keywords=["심리", "마음건강", "뇌과학", "상담"],
                        countries=["KR", "US"],
                        max_per_keyword=5
                    )
                    st.success(f"✅ 수집 완료: {collected}개 수집, {saved}개 저장")
                except Exception as e:
                    st.error(f"❌ 오류 발생: {e}")
    
    # 뉴스 목록 표시
    st.divider()
    
    try:
        from modules.database import get_connection
        import json
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # 페이지네이션
        page_size = 10
        page = st.number_input("페이지", min_value=1, value=1, step=1)
        offset = (page - 1) * page_size
        
        # 뉴스 조회 (최신순)
        cursor.execute("""
            SELECT id, date, title, url, content_summary, keywords, validity_score, country
            FROM articles
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (page_size, offset))
        
        articles = cursor.fetchall()
        conn.close()
        
        if articles:
            st.markdown(f"### 📄 뉴스 목록 (총 {len(articles)}개 표시)")
            
            for article in articles:
                article_id, date, title, url, summary, keywords_json, score, country = article
                
                # 키워드 파싱
                try:
                    keywords = json.loads(keywords_json) if keywords_json else []
                except:
                    keywords = []
                
                # 카드 형태로 표시
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"#### {title}")
                        st.markdown(f"📅 {date} | 🌍 {country} | ⭐ {score}/5")
                        
                        if summary:
                            st.markdown(f"**요약:** {summary}")
                        
                        if keywords:
                            keyword_tags = " ".join([f"`{k}`" for k in keywords[:3]])
                            st.markdown(f"**키워드:** {keyword_tags}")
                        
                        if url:
                            st.markdown(f"[원문 보기 →]({url})")
                    
                    with col2:
                        # 평점 시각화
                        st.markdown(f"### ⭐{score}")
                        st.progress(score / 5)
                    
                    st.divider()
        else:
            st.info("📭 저장된 뉴스가 없습니다. 위의 '뉴스 수집' 버튼을 클릭하여 뉴스를 수집하세요.")
            
    except Exception as e:
        st.error(f"데이터베이스 조회 오류: {e}")
        st.info("데이터베이스가 초기화되지 않았을 수 있습니다. 사이드바에서 '데이터베이스 초기화' 버튼을 클릭하세요.")

# Tab 2: 아카데믹 아카이브
with tab2:
    st.header("📚 아카데믹 아카이브")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("심리학 관련 논문을 수집하고 AI로 요약합니다.")
    with col2:
        if st.button("🔄 논문 수집", type="primary"):
            with st.spinner("논문 수집 중... (시간이 걸릴 수 있습니다)"):
                try:
                    from modules.paper_collector import collect_and_analyze_papers
                    collected, saved = collect_and_analyze_papers(
                        keywords=["psychology", "counseling"],
                        sources=["arxiv"],
                        max_per_keyword=5
                    )
                    st.success(f"✅ 수집 완료: {collected}개 수집, {saved}개 저장")
                except Exception as e:
                    st.error(f"❌ 오류 발생: {e}")
    
    st.divider()
    
    try:
        from modules.database import get_connection
        import json
        
        conn = get_connection()
        cursor = conn.cursor()
        
        page_size = 10
        page = st.number_input("페이지", min_value=1, value=1, step=1, key="paper_page")
        offset = (page - 1) * page_size
        
        cursor.execute("""
            SELECT id, date, title, authors, journal, url, abstract, summary, keywords, category
            FROM papers
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (page_size, offset))
        
        papers = cursor.fetchall()
        conn.close()
        
        if papers:
            st.markdown(f"### 📄 논문 목록 (총 {len(papers)}개 표시)")
            
            for paper in papers:
                paper_id, date, title, authors_json, journal, url, abstract, summary_json, keywords_json, category = paper
                
                try:
                    authors = json.loads(authors_json) if authors_json else []
                    summary = json.loads(summary_json) if summary_json else {}
                    keywords = json.loads(keywords_json) if keywords_json else []
                except:
                    authors = []
                    summary = {}
                    keywords = []
                
                with st.container():
                    st.markdown(f"#### {title}")
                    st.markdown(f"📅 {date} | 📖 {journal} | 🏷️ {category}")
                    
                    if authors:
                        authors_str = ", ".join(authors[:3])
                        if len(authors) > 3:
                            authors_str += f" 외 {len(authors) - 3}명"
                        st.markdown(f"**저자:** {authors_str}")
                    
                    if summary:
                        with st.expander("📋 요약 보기"):
                            if summary.get("purpose"):
                                st.markdown(f"**목적:** {summary['purpose']}")
                            if summary.get("method"):
                                st.markdown(f"**방법:** {summary['method']}")
                            if summary.get("result"):
                                st.markdown(f"**결과:** {summary['result']}")
                            if summary.get("implication"):
                                st.markdown(f"**시사점:** {summary['implication']}")
                    
                    if abstract:
                        with st.expander("📄 초록 보기"):
                            st.markdown(abstract[:500] + "..." if len(abstract) > 500 else abstract)
                    
                    if keywords:
                        keyword_tags = " ".join([f"`{k}`" for k in keywords[:3]])
                        st.markdown(f"**키워드:** {keyword_tags}")
                    
                    if url:
                        st.markdown(f"[원문 보기 →]({url})")
                    
                    st.divider()
        else:
            st.info("📭 저장된 논문이 없습니다. 위의 '논문 수집' 버튼을 클릭하여 논문을 수집하세요.")
            
    except Exception as e:
        st.error(f"데이터베이스 조회 오류: {e}")

# Tab 3: 콘텐츠 팩토리
with tab3:
    st.header("✨ 콘텐츠 팩토리")
    st.markdown("Tab 1~2에서 선택한 콘텐츠를 다양한 형태로 재생산합니다.")
    
    # 선택된 콘텐츠 표시
    if 'selected_items' not in st.session_state:
        st.session_state.selected_items = []
    
    st.divider()
    
    # 콘텐츠 선택 섹션
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📰 뉴스 선택")
        try:
            from modules.database import get_connection
            import json
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, content_summary FROM articles ORDER BY created_at DESC LIMIT 20")
            news_items = cursor.fetchall()
            conn.close()
            
            selected_news = []
            for item in news_items:
                if st.checkbox(f"📰 {item[1][:50]}...", key=f"news_{item[0]}"):
                    selected_news.append({"type": "news", "id": item[0], "title": item[1], "summary": item[2]})
        except Exception as e:
            st.error(f"뉴스 로드 오류: {e}")
            selected_news = []
    
    with col2:
        st.subheader("📚 논문 선택")
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, abstract FROM papers ORDER BY created_at DESC LIMIT 20")
            paper_items = cursor.fetchall()
            conn.close()
            
            selected_papers = []
            for item in paper_items:
                if st.checkbox(f"📚 {item[1][:50]}...", key=f"paper_{item[0]}"):
                    selected_papers.append({"type": "paper", "id": item[0], "title": item[1], "abstract": item[2]})
        except Exception as e:
            st.error(f"논문 로드 오류: {e}")
            selected_papers = []
    
    st.divider()
    
    # 템플릿 선택
    st.subheader("📝 콘텐츠 템플릿 선택")
    template = st.radio(
        "생성할 콘텐츠 유형",
        ["블로그 포스트", "릴스 대본", "게시글", "논문 아이디어"],
        horizontal=True
    )
    
    # 생성 버튼
    if st.button("✨ 콘텐츠 생성", type="primary", disabled=len(selected_news) + len(selected_papers) == 0):
        if len(selected_news) + len(selected_papers) == 0:
            st.warning("콘텐츠를 선택해주세요.")
        else:
            with st.spinner("AI가 콘텐츠를 생성 중입니다..."):
                try:
                    from modules.ai_engine import get_model
                    import google.generativeai as genai
                    
                    # 선택된 콘텐츠 요약
                    selected_content = []
                    for news in selected_news:
                        selected_content.append(f"뉴스: {news['title']}\n{news['summary']}")
                    for paper in selected_papers:
                        selected_content.append(f"논문: {paper['title']}\n{paper['abstract'][:500]}")
                    
                    content_text = "\n\n".join(selected_content)
                    
                    # 템플릿별 프롬프트
                    prompts = {
                        "블로그 포스트": f"""다음 콘텐츠를 바탕으로 전문적인 블로그 포스트를 작성해주세요.
구조: 제목, 서론, 본문(3-4개 섹션), 결론

콘텐츠:
{content_text[:3000]}

블로그 포스트:""",
                        "릴스 대본": f"""다음 콘텐츠를 바탕으로 30초 분량의 릴스 대본을 작성해주세요.
구조: 훅(첫 3초 주목), 본문(핵심 내용), CTA(행동 유도)

콘텐츠:
{content_text[:2000]}

릴스 대본:""",
                        "게시글": f"""다음 콘텐츠를 바탕으로 SNS용 게시글을 작성해주세요.
200자 내외, 해시태그 포함

콘텐츠:
{content_text[:2000]}

게시글:""",
                        "논문 아이디어": f"""다음 논문들을 바탕으로 새로운 연구 아이디어를 제안해주세요.
구조: 연구 주제, 연구 질문, 예상 방법론, 참고 논문

콘텐츠:
{content_text[:3000]}

논문 아이디어:"""
                    }
                    
                    model = get_model()
                    response = model.generate_content(
                        prompts[template],
                        generation_config={"temperature": 0.7, "max_output_tokens": 2000}
                    )
                    
                    generated_content = response.text
                    
                    st.success("✅ 콘텐츠 생성 완료!")
                    st.markdown("### 생성된 콘텐츠")
                    st.text_area("", generated_content, height=400)
                    
                    # 복사 버튼
                    st.code(generated_content, language=None)
                    
                except Exception as e:
                    st.error(f"콘텐츠 생성 실패: {e}")

# 사이드바
with st.sidebar:
    st.header("⚙️ 설정")
    st.info("프로젝트 초기화 완료!")
    
    # 데이터베이스 초기화 버튼
    if st.button("🗄️ 데이터베이스 초기화"):
        try:
            from modules.database import init_database
            init_database()
            st.success("데이터베이스 초기화 완료!")
        except Exception as e:
            st.error(f"오류 발생: {e}")
