"""
PsyInsight Commander - 메인 Streamlit 애플리케이션
심리학 전문가를 위한 통합 대시보드
"""

import streamlit as st

# 세션 상태 초기화
if 'scroll_to_top' not in st.session_state:
    st.session_state.scroll_to_top = False
if 'scroll_to_top_tab2' not in st.session_state:
    st.session_state.scroll_to_top_tab2 = False
if 'scroll_to_top_tab3' not in st.session_state:
    st.session_state.scroll_to_top_tab3 = False
if 'scroll_to_top_tab4' not in st.session_state:
    st.session_state.scroll_to_top_tab4 = False
if 'scroll_to_top_tab5' not in st.session_state:
    st.session_state.scroll_to_top_tab5 = False

# 페이지 설정
st.set_page_config(
    page_title="PsyInsight Commander",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 맨 위로 스크롤 JavaScript (전역)
scroll_to_top_js = """
<script>
function scrollToTop() {
    // 모든 가능한 스크롤 방법 시도
    window.scrollTo({top: 0, behavior: 'smooth'});
    document.documentElement.scrollTo({top: 0, behavior: 'smooth'});
    document.body.scrollTo({top: 0, behavior: 'smooth'});
    
    // Streamlit 특정 요소들
    const stApp = document.querySelector('[data-testid="stApp"]');
    if (stApp) stApp.scrollTo({top: 0, behavior: 'smooth'});
    
    const mainContainer = document.querySelector('.main');
    if (mainContainer) mainContainer.scrollTo({top: 0, behavior: 'smooth'});
    
    // 모든 스크롤 가능한 요소
    document.querySelectorAll('*').forEach(el => {
        if (el.scrollTop > 0) {
            el.scrollTo({top: 0, behavior: 'smooth'});
        }
    });
}
</script>
"""
st.markdown(scroll_to_top_js, unsafe_allow_html=True)

# 제목
st.title("🧠 PsyInsight Commander")
st.markdown("### 심리 인사이트 통합 지휘소")

# 사이드바 메뉴 생성
with st.sidebar:
    st.header("📋 메뉴")
    
    menu_options = [
        "🏠 대시보드",
        "📰 트랜드 레이더",
        "📚 아카이브",
        "✨ 팩토리",
        "📈 경제 흐름 파악",
        "💾 내 콘텐츠",
        "🗑️ 수집 내용 관리",
        "🧪 테스트",
        "⚙️ 설정",
        "🗄️ 초기화"
    ]
    
    selected_menu = st.radio("메뉴 선택", menu_options, key="main_menu")
    
    st.divider()
    
    # 데이터베이스 초기화 버튼
    if st.button("🗄️ 데이터베이스 초기화", use_container_width=True):
        try:
            from modules.database import init_database
            init_database()
            st.success("데이터베이스 초기화 완료! (테이블 재생성)")
            st.info("💡 수집된 내용을 삭제하려면 '수집 내용 관리' 메뉴를 사용하세요.")
        except Exception as e:
            st.error(f"오류 발생: {e}")

# 메인 콘텐츠 영역
# 0. 통합 대시보드
if selected_menu == "🏠 대시보드":
    st.header("🏠 통합 대시보드")
    st.markdown("전체 프로젝트의 주요 인사이트를 한눈에 확인합니다.")
    
    try:
        from modules.database import get_connection
        from datetime import datetime, timedelta
        import json
        from collections import Counter
        import pandas as pd
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # 오늘의 주요 이슈 (뉴스 + 논문 통합)
        st.subheader("🔥 오늘의 주요 이슈")
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        # 오늘 수집된 뉴스
        cursor.execute("""
            SELECT title, url, date, keywords FROM articles
            WHERE date = ?
            ORDER BY created_at DESC
            LIMIT 10
        """, (end_date,))
        today_news = cursor.fetchall()
        
        # 오늘 수집된 논문
        cursor.execute("""
            SELECT title, url, date, keywords FROM papers
            WHERE date = ?
            ORDER BY created_at DESC
            LIMIT 10
        """, (end_date,))
        today_papers = cursor.fetchall()
        
        if today_news or today_papers:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📰 오늘의 뉴스**")
                for title, url, date, _ in today_news[:5]:
                    st.markdown(f"- [{title[:50]}{'...' if len(title) > 50 else ''}]({url})")
            
            with col2:
                st.markdown("**📚 오늘의 논문**")
                for title, url, date, _ in today_papers[:5]:
                    st.markdown(f"- [{title[:50]}{'...' if len(title) > 50 else ''}]({url})")
        else:
            st.info("📭 오늘 수집된 내용이 없습니다.")
        
        st.divider()
        
        # 최근 7일 트렌드
        st.subheader("📈 최근 7일 트렌드")
        
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        # 날짜별 뉴스/논문 개수
        cursor.execute("""
            SELECT date, COUNT(*) FROM articles
            WHERE date >= ?
            GROUP BY date
            ORDER BY date
        """, (start_date,))
        news_trend = {date: count for date, count in cursor.fetchall()}
        
        cursor.execute("""
            SELECT date, COUNT(*) FROM papers
            WHERE date >= ?
            GROUP BY date
            ORDER BY date
        """, (start_date,))
        paper_trend = {date: count for date, count in cursor.fetchall()}
        
        # 트렌드 데이터프레임 생성
        trend_dates = []
        news_counts = []
        paper_counts = []
        
        for i in range(7):
            date = (datetime.now() - timedelta(days=6-i)).strftime("%Y-%m-%d")
            trend_dates.append(date)
            news_counts.append(news_trend.get(date, 0))
            paper_counts.append(paper_trend.get(date, 0))
        
        trend_df = pd.DataFrame({
            "날짜": trend_dates,
            "뉴스": news_counts,
            "논문": paper_counts
        })
        
        if not trend_df.empty:
            st.line_chart(trend_df.set_index("날짜"))
        
        st.divider()
        
        # 키워드 클라우드 (상위 키워드)
        st.subheader("🏷️ 주요 키워드")
        
        # 뉴스 키워드
        cursor.execute("""
            SELECT keywords FROM articles
            WHERE date >= ? AND keywords IS NOT NULL
        """, (start_date,))
        
        all_keywords = []
        for row in cursor.fetchall():
            try:
                keywords = json.loads(row[0]) if row[0] else []
                all_keywords.extend(keywords)
            except:
                pass
        
        # 논문 키워드
        cursor.execute("""
            SELECT keywords FROM papers
            WHERE date >= ? AND keywords IS NOT NULL
        """, (start_date,))
        
        for row in cursor.fetchall():
            try:
                keywords = json.loads(row[0]) if row[0] else []
                all_keywords.extend(keywords)
            except:
                pass
        
        keyword_counter = Counter(all_keywords)
        top_keywords = keyword_counter.most_common(10)
        
        if top_keywords:
            keyword_tags = " ".join([f"`{kw} ({count})`" for kw, count in top_keywords])
            st.markdown(keyword_tags)
        else:
            st.info("📭 키워드 데이터가 없습니다.")
        
        conn.close()
        
    except Exception as e:
        st.error(f"❌ 대시보드 로드 실패: {e}")
        import traceback
        st.code(traceback.format_exc())

# 1. 트랜드 레이더
elif selected_menu == "📰 트랜드 레이더":
    st.header("📰 트랜드 레이더")
    
    # 뉴스 수집 버튼
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("미국과 한국의 심리 관련 뉴스를 수집하고 AI로 분석합니다.")
    with col2:
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("🔄 뉴스 수집 (20건)", type="primary", key="news_collect_20"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                try:
                    from modules.news_collector import collect_and_analyze_news
                    
                    def update_progress(current, total, message):
                        progress = current / total if total > 0 else 0
                        progress_bar.progress(progress)
                        status_text.text(f"{message} ({current}/{total}) - {int(progress * 100)}%")
                    
                    # 한국 뉴스 키워드 (개선: 인지행동치료, 정신분석, 집단상담 추가)
                    kr_keywords = ["정신건강", "심리건강", "마음건강", "심리상담", "심리학이론", "심리학", "정신건강증진", 
                                   "우울증", "불안장애", "트라우마", "상담심리", "임상심리", "인지행동치료", "정신분석", "집단상담"]
                    # 미국 뉴스 키워드 (명시적 영어 키워드)
                    us_keywords = ["mental health", "psychology", "counseling psychology", "clinical psychology", 
                                   "depression", "anxiety", "trauma", "psychotherapy", "cognitive behavioral therapy", 
                                   "psychoanalysis", "group therapy", "mental wellness"]
                    
                    collected, saved = collect_and_analyze_news(
                        keywords=kr_keywords + us_keywords,
                        countries=["KR", "US"],
                        max_per_keyword=20,
                        progress_callback=update_progress
                    )
                    progress_bar.progress(1.0)
                    status_text.text(f"✅ 수집 완료: {collected}개 수집, {saved}개 저장")
                    st.success(f"✅ 수집 완료: {collected}개 수집, {saved}개 저장")
                except Exception as e:
                    st.error(f"❌ 오류 발생: {e}")
                    import traceback
                    st.code(traceback.format_exc())
        
        with col_btn2:
            if st.button("➕ 추가 수집 (10건)", type="secondary", key="news_add_10"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                try:
                    from modules.news_collector import collect_and_analyze_news
                    
                    def update_progress(current, total, message):
                        progress = current / total if total > 0 else 0
                        progress_bar.progress(progress)
                        status_text.text(f"{message} ({current}/{total}) - {int(progress * 100)}%")
                    
                    # 한국 뉴스 키워드 (개선: 인지행동치료, 정신분석, 집단상담 추가)
                    kr_keywords = ["정신건강", "심리건강", "마음건강", "심리상담", "심리학이론", "심리학", "정신건강증진", 
                                   "우울증", "불안장애", "트라우마", "상담심리", "임상심리", "인지행동치료", "정신분석", "집단상담"]
                    # 미국 뉴스 키워드 (명시적 영어 키워드)
                    us_keywords = ["mental health", "psychology", "counseling psychology", "clinical psychology", 
                                   "depression", "anxiety", "trauma", "psychotherapy", "cognitive behavioral therapy", 
                                   "psychoanalysis", "group therapy", "mental wellness"]
                    
                    collected, saved = collect_and_analyze_news(
                        keywords=kr_keywords + us_keywords,
                        countries=["KR", "US"],
                        max_per_keyword=10,
                        progress_callback=update_progress
                    )
                    progress_bar.progress(1.0)
                    status_text.text(f"✅ 추가 수집 완료: {collected}개 수집, {saved}개 저장")
                    st.success(f"✅ 추가 수집 완료: {collected}개 수집, {saved}개 저장")
                except Exception as e:
                    st.error(f"❌ 오류 발생: {e}")
                    import traceback
                    st.code(traceback.format_exc())
    
    # 뉴스 목록 표시
    st.divider()
    
    try:
        from modules.database import get_connection
        import json
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # 검색 및 필터 기능
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_query = st.text_input("🔍 검색", placeholder="제목, 요약, 키워드로 검색...", key="news_search")
        
        with col2:
            sort_option = st.selectbox("정렬", ["최신순", "오래된순", "평점 높은순", "평점 낮은순"], key="news_sort")
        
        with col3:
            country_filter = st.selectbox("국가", ["전체", "한국", "미국"], key="news_country")
        
        # 키워드 필터 (해시태그)
        cursor.execute("SELECT DISTINCT keywords FROM articles WHERE keywords IS NOT NULL AND keywords != ''")
        all_keywords = set()
        for row in cursor.fetchall():
            try:
                keywords = json.loads(row[0]) if row[0] else []
                all_keywords.update(keywords)
            except:
                pass
        
        if all_keywords:
            selected_keywords = st.multiselect("🏷️ 키워드 필터", sorted(all_keywords), key="news_keywords")
        else:
            selected_keywords = []
        
        # SQL 쿼리 구성
        where_conditions = []
        params = []
        
        # 검색 조건
        if search_query:
            where_conditions.append("(title LIKE ? OR content_summary LIKE ? OR keywords LIKE ?)")
            search_param = f"%{search_query}%"
            params.extend([search_param, search_param, search_param])
        
        # 국가 필터
        if country_filter != "전체":
            where_conditions.append("country = ?")
            params.append("KR" if country_filter == "한국" else "US")
        
        # 키워드 필터
        if selected_keywords:
            keyword_conditions = []
            for keyword in selected_keywords:
                keyword_conditions.append("keywords LIKE ?")
                params.append(f'%"{keyword}"%')
            where_conditions.append(f"({' OR '.join(keyword_conditions)})")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # 정렬
        if sort_option == "최신순":
            order_by = "created_at DESC"
        elif sort_option == "오래된순":
            order_by = "created_at ASC"
        elif sort_option == "평점 높은순":
            order_by = "validity_score DESC, created_at DESC"
        else:  # 평점 낮은순
            order_by = "validity_score ASC, created_at DESC"
        
        # 페이지네이션
        page_size = 20
        page = st.number_input("페이지", min_value=1, value=1, step=1, key="news_page")
        offset = (page - 1) * page_size
        
        # 뉴스 조회
        query = f"""
            SELECT id, date, title, url, content_summary, keywords, validity_score, country
            FROM articles
            WHERE {where_clause}
            ORDER BY {order_by}
            LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])
        
        cursor.execute(query, params)
        
        articles = cursor.fetchall()
        conn.close()
        
        if articles:
            st.markdown(f"<h4 style='font-size: 16px; margin-bottom: 10px;'>📄 뉴스 목록 (총 {len(articles)}개 표시)</h4>", unsafe_allow_html=True)
            
            for idx, article in enumerate(articles):
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
                        st.markdown(f"<h5 style='font-size: 14px; font-weight: bold; margin-bottom: 5px;'>{title}</h5>", unsafe_allow_html=True)
                        st.markdown(f"<p style='font-size: 11px; color: #666; margin-bottom: 5px;'>📅 {date} | 🌍 {country} | ⭐ {score}/5</p>", unsafe_allow_html=True)
                        
                        if summary:
                            st.markdown(f"<p style='font-size: 12px; margin-bottom: 5px;'><strong>요약:</strong> {summary[:150]}{'...' if len(summary) > 150 else ''}</p>", unsafe_allow_html=True)
                        
                        if keywords:
                            keyword_tags = " ".join([f"`{k}`" for k in keywords[:3]])
                            st.markdown(f"<p style='font-size: 11px; margin-bottom: 5px;'><strong>키워드:</strong> {keyword_tags}</p>", unsafe_allow_html=True)
                        
                        if url:
                            st.markdown(f"<a href='{url}' target='_blank' style='font-size: 11px;'>원문 보기 →</a>", unsafe_allow_html=True)
                    
                    with col2:
                        # 평점 시각화
                        st.markdown(f"<p style='font-size: 16px; margin-bottom: 5px; text-align: center;'>⭐{score}</p>", unsafe_allow_html=True)
                        st.progress(score / 5)
                    
                    if idx < len(articles) - 1:
                        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        else:
            st.info("📭 저장된 뉴스가 없습니다. 위의 '뉴스 수집' 버튼을 클릭하여 뉴스를 수집하세요.")
            
    except Exception as e:
        st.error(f"데이터베이스 조회 오류: {e}")
        st.info("데이터베이스가 초기화되지 않았을 수 있습니다. 사이드바에서 '데이터베이스 초기화' 버튼을 클릭하세요.")
    
    # 맨 위로 버튼
    st.markdown("<div style='text-align: center; margin: 30px 0; padding: 20px;'>", unsafe_allow_html=True)
    if st.button("맨 위로 이동", key="scroll_top_tab1", use_container_width=False):
        st.session_state.scroll_to_top = True
        st.rerun()
    if st.session_state.get("scroll_to_top", False):
        st.markdown("""
        <script>
        window.scrollTo(0, 0);
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
        </script>
        """, unsafe_allow_html=True)
        st.session_state.scroll_to_top = False
    st.markdown("</div>", unsafe_allow_html=True)

# 2. 아카이브
elif selected_menu == "📚 아카이브":
    st.header("📚 아카데믹 아카이브")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("심리학 관련 논문을 수집하고 AI로 요약합니다.")
    with col2:
        col_btn1, col_btn2 = st.columns([1, 1])
        with col_btn1:
            if st.button("🔄 논문 수집 (10건)", type="primary", key="paper_collect_10"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                try:
                    from modules.paper_collector import collect_and_analyze_papers
                    
                    def update_progress(current, total, message):
                        progress = current / total if total > 0 else 0
                        progress_bar.progress(progress)
                        status_text.text(f"{message} ({current}/{total}) - {int(progress * 100)}%")
                    
                    # 논문 키워드 (개선: 하위 분야 추가, 한국어 키워드 추가)
                    paper_keywords = ["psychology", "counseling psychology", "clinical psychology", "mental health",
                                     "cognitive psychology", "developmental psychology", "social psychology",
                                     "심리학", "상담심리", "인지행동", "정신건강"]
                    
                    collected, saved = collect_and_analyze_papers(
                        keywords=paper_keywords,
                        sources=["arxiv"],
                        max_per_keyword=10,
                        progress_callback=update_progress
                    )
                    progress_bar.progress(1.0)
                    if collected > 0:
                        status_text.text(f"✅ 수집 완료: {collected}개 수집, {saved}개 저장")
                        st.success(f"✅ 수집 완료: {collected}개 수집, {saved}개 저장")
                    else:
                        status_text.text("⚠️ 수집된 논문이 없습니다.")
                        st.warning("⚠️ 수집된 논문이 없습니다. 키워드를 확인해주세요.")
                except Exception as e:
                    st.error(f"❌ 오류 발생: {e}")
                    import traceback
                    st.code(traceback.format_exc())
        
        with col_btn2:
            if st.button("➕ 추가 수집 (10건)", type="secondary", key="paper_add_10"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                try:
                    from modules.paper_collector import collect_and_analyze_papers
                    
                    def update_progress(current, total, message):
                        progress = current / total if total > 0 else 0
                        progress_bar.progress(progress)
                        status_text.text(f"{message} ({current}/{total}) - {int(progress * 100)}%")
                    
                    # 논문 키워드 (개선: 하위 분야 추가, 한국어 키워드 추가)
                    paper_keywords = ["psychology", "counseling psychology", "clinical psychology", "mental health",
                                     "cognitive psychology", "developmental psychology", "social psychology",
                                     "심리학", "상담심리", "인지행동", "정신건강"]
                    
                    collected, saved = collect_and_analyze_papers(
                        keywords=paper_keywords,
                        sources=["arxiv"],
                        max_per_keyword=10,
                        progress_callback=update_progress
                    )
                    progress_bar.progress(1.0)
                    if collected > 0:
                        status_text.text(f"✅ 추가 수집 완료: {collected}개 수집, {saved}개 저장")
                        st.success(f"✅ 추가 수집 완료: {collected}개 수집, {saved}개 저장")
                    else:
                        status_text.text("⚠️ 수집된 논문이 없습니다.")
                        st.warning("⚠️ 수집된 논문이 없습니다.")
                except Exception as e:
                    st.error(f"❌ 오류 발생: {e}")
                    import traceback
                    st.code(traceback.format_exc())
    
    # 연구 동향 분석
    st.divider()
    st.subheader("📊 연구 동향 분석")
    
    try:
        from modules.dashboard_utils import get_paper_trend_data
        import pandas as pd
        
        # 키워드별 트렌드 그래프
        trend_data = get_paper_trend_data(days=30)
        
        if trend_data:
            # 상위 5개 키워드만 표시
            top_keywords = sorted(trend_data.items(), key=lambda x: sum(count for _, count in x[1]), reverse=True)[:5]
            
            if top_keywords:
                trend_df = pd.DataFrame({
                    "날짜": [date for date, _ in top_keywords[0][1]] if top_keywords else [],
                    **{keyword: [count for _, count in data] for keyword, data in top_keywords}
                })
                
                if not trend_df.empty:
                    st.line_chart(trend_df.set_index("날짜"))
        else:
            st.info("📭 연구 동향 데이터가 없습니다.")
    except Exception as e:
        st.error(f"❌ 연구 동향 분석 실패: {e}")
    
    st.divider()
    
    try:
        from modules.database import get_connection
        import json
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # 검색 및 필터 기능
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_query = st.text_input("🔍 검색", placeholder="제목, 저자, 키워드로 검색...", key="paper_search")
        
        with col2:
            sort_option = st.selectbox("정렬", ["최신순", "오래된순"], key="paper_sort")
        
        # 키워드 필터
        cursor.execute("SELECT DISTINCT keywords FROM papers WHERE keywords IS NOT NULL AND keywords != ''")
        all_keywords = set()
        for row in cursor.fetchall():
            try:
                keywords = json.loads(row[0]) if row[0] else []
                all_keywords.update(keywords)
            except:
                pass
        
        if all_keywords:
            selected_keywords = st.multiselect("🏷️ 키워드 필터", sorted(all_keywords), key="paper_keywords")
        else:
            selected_keywords = []
        
        # SQL 쿼리 구성
        where_conditions = []
        params = []
        
        # 검색 조건
        if search_query:
            where_conditions.append("(title LIKE ? OR authors LIKE ? OR keywords LIKE ?)")
            search_param = f"%{search_query}%"
            params.extend([search_param, search_param, search_param])
        
        # 키워드 필터
        if selected_keywords:
            keyword_conditions = []
            for keyword in selected_keywords:
                keyword_conditions.append("keywords LIKE ?")
                params.append(f'%"{keyword}"%')
            where_conditions.append(f"({' OR '.join(keyword_conditions)})")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # 정렬
        order_by = "created_at DESC" if sort_option == "최신순" else "created_at ASC"
        
        # 페이지네이션
        page_size = 20
        page = st.number_input("페이지", min_value=1, value=1, step=1, key="paper_page")
        offset = (page - 1) * page_size
        
        # 논문 조회
        query = f"""
            SELECT id, date, title, authors, journal, url, abstract, summary, keywords, category
            FROM papers
            WHERE {where_clause}
            ORDER BY {order_by}
            LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])
        
        cursor.execute(query, params)
        
        papers = cursor.fetchall()
        conn.close()
        
        if papers:
            st.markdown(f"<h4 style='font-size: 16px; margin-bottom: 10px;'>📄 논문 목록 (총 {len(papers)}개 표시)</h4>", unsafe_allow_html=True)
            
            for idx, paper in enumerate(papers):
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
                    # 논문 제목
                    st.markdown(f"<h5 style='font-size: 14px; font-weight: bold; margin-bottom: 8px;'>{title}</h5>", unsafe_allow_html=True)
                    
                    # 메타 정보
                    st.markdown(f"<p style='font-size: 11px; color: #666; margin-bottom: 5px;'>📅 {date} | 📖 {journal} | 🏷️ {category}</p>", unsafe_allow_html=True)
                    
                    # 핵심 키워드 해시태그로 표시
                    if keywords:
                        keyword_tags_html = " ".join([f"<span style='background-color: #e0e0e0; padding: 2px 8px; border-radius: 12px; font-size: 10px; margin-right: 5px; display: inline-block;'>#{k}</span>" for k in keywords[:5]])
                        st.markdown(f"<div style='margin-bottom: 8px;'>{keyword_tags_html}</div>", unsafe_allow_html=True)
                    
                    # 논문 Abstract 펼쳐보기 (제목 아래에 펼쳐지게)
                    if abstract:
                        with st.expander("📄 논문 Abstract 펼쳐보기", expanded=False):
                            # Abstract에 번역이 포함되어 있는지 확인
                            if "[원문]" in abstract and "[한국어 번역]" in abstract:
                                # 외국 논문: 원문과 번역 병기
                                parts = abstract.split("[한국어 번역]")
                                if len(parts) == 2:
                                    original = parts[0].replace("[원문]", "").strip()
                                    translated = parts[1].strip()
                                    st.markdown("**📄 원본 Abstract (영문):**")
                                    st.markdown(f"<p style='font-size: 11px; line-height: 1.6;'>{original}</p>", unsafe_allow_html=True)
                                    st.markdown("---")
                                    st.markdown("**🇰🇷 한국어 번역:**")
                                    st.markdown(f"<p style='font-size: 11px; line-height: 1.6;'>{translated}</p>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<p style='font-size: 11px; line-height: 1.6;'>{abstract}</p>", unsafe_allow_html=True)
                            else:
                                # 한국 논문: 원문만 표시
                                st.markdown("**📄 논문 Abstract:**")
                                st.markdown(f"<p style='font-size: 11px; line-height: 1.6;'>{abstract}</p>", unsafe_allow_html=True)
                    
                    # 저자 정보
                    if authors:
                        authors_str = ", ".join(authors[:3])
                        if len(authors) > 3:
                            authors_str += f" 외 {len(authors) - 3}명"
                        st.markdown(f"<p style='font-size: 11px; margin-bottom: 5px;'><strong>저자:</strong> {authors_str}</p>", unsafe_allow_html=True)
                    
                    # 원문 링크
                    if url:
                        st.markdown(f"<a href='{url}' target='_blank' style='font-size: 11px; color: #0066cc;'>원문 보기 →</a>", unsafe_allow_html=True)
                    
                    if idx < len(papers) - 1:
                        st.markdown("<hr style='margin: 15px 0; border: none; border-top: 1px solid #e0e0e0;'>", unsafe_allow_html=True)
        else:
            st.info("📭 저장된 논문이 없습니다. 위의 '논문 수집' 버튼을 클릭하여 논문을 수집하세요.")
            
    except Exception as e:
        st.error(f"데이터베이스 조회 오류: {e}")
    
    # 맨 위로 버튼
    st.markdown("<div style='text-align: center; margin: 30px 0; padding: 20px;'>", unsafe_allow_html=True)
    if st.button("맨 위로 이동", key="scroll_top_tab2", use_container_width=False):
        st.session_state.scroll_to_top_tab2 = True
        st.rerun()
    if st.session_state.get("scroll_to_top_tab2", False):
        st.markdown("""
        <script>
        window.scrollTo(0, 0);
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
        </script>
        """, unsafe_allow_html=True)
        st.session_state.scroll_to_top_tab2 = False
    st.markdown("</div>", unsafe_allow_html=True)

# 3. 팩토리
elif selected_menu == "✨ 팩토리":
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
        horizontal=True,
        key="content_template_radio"
    )
    
    # 생성 버튼
    if st.button("✨ 콘텐츠 생성", type="primary", disabled=len(selected_news) + len(selected_papers) == 0, key="content_generate_btn"):
        if len(selected_news) + len(selected_papers) == 0:
            st.warning("콘텐츠를 선택해주세요.")
        else:
            try:
                from modules.ai_engine import get_model
                
                # 진행도 표시
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("콘텐츠 준비 중... (10%)")
                progress_bar.progress(0.1)
                
                # 선택된 콘텐츠 수집
                selected_content = []
                for news in selected_news:
                    content = f"뉴스: {news['title']}\n"
                    if news.get('summary'):
                        content += f"요약: {news['summary']}\n"
                    selected_content.append(content)
                
                for paper in selected_papers:
                    content = f"논문: {paper['title']}\n"
                    if paper.get('abstract'):
                        content += f"초록: {paper['abstract'][:500]}\n"
                    selected_content.append(content)
                
                if not selected_content:
                    st.error("선택된 콘텐츠가 없습니다.")
                    st.stop()
                
                content_text = "\n\n".join(selected_content)
                
                status_text.text("프롬프트 준비 중... (20%)")
                progress_bar.progress(0.2)
                
                # 템플릿별 프롬프트
                prompts = {
                    "블로그 포스트": f"""다음 콘텐츠를 바탕으로 전문적인 블로그 포스트를 작성해주세요.
구조: 제목, 서론, 본문(3-4개 섹션), 결론
전문적이고 읽기 쉽게 작성해주세요.

콘텐츠:
{content_text[:3000]}

블로그 포스트:""",
                    "릴스 대본": f"""다음 콘텐츠를 바탕으로 30초 분량의 릴스 대본을 작성해주세요.
구조: 훅(첫 3초 주목), 본문(핵심 내용), CTA(행동 유도)
간결하고 임팩트 있게 작성해주세요.

콘텐츠:
{content_text[:2000]}

릴스 대본:""",
                    "게시글": f"""다음 콘텐츠를 바탕으로 SNS용 게시글을 작성해주세요.
200자 내외, 해시태그 포함
친근하고 공유하기 좋게 작성해주세요.

콘텐츠:
{content_text[:2000]}

게시글:""",
                    "논문 아이디어": f"""다음 논문들을 바탕으로 새로운 연구 아이디어를 제안해주세요.
구조: 연구 주제, 연구 질문, 예상 방법론, 참고 논문
학술적이고 구체적으로 작성해주세요.

콘텐츠:
{content_text[:3000]}

논문 아이디어:"""
                }
                
                status_text.text("AI 모델 초기화 중... (30%)")
                progress_bar.progress(0.3)
                
                # 모델 자동 선택 (404 에러 방지)
                model = get_model()  # 사용 가능한 모델 자동 선택
                
                status_text.text("콘텐츠 생성 중... (60%)")
                progress_bar.progress(0.6)
                
                prompt = prompts.get(template, prompts["블로그 포스트"])
                response = model.generate_content(
                    prompt,
                    generation_config={"temperature": 0.7, "max_output_tokens": 2000}
                )
                
                status_text.text("콘텐츠 생성 완료... (90%)")
                progress_bar.progress(0.9)
                
                generated_content = response.text.strip()
                
                progress_bar.progress(1.0)
                status_text.text("완료! (100%)")
                
                if generated_content:
                    st.success("✅ 콘텐츠 생성 완료!")
                    st.markdown("### 생성된 콘텐츠")
                    st.markdown(f"**템플릿:** {template}")
                    st.text_area("생성된 콘텐츠", generated_content, height=400, key="generated_content")
                    
                    # 콘텐츠 저장 기능
                    col_save1, col_save2 = st.columns([2, 1])
                    with col_save1:
                        content_title = st.text_input("제목 (저장용)", value=f"{template} - {datetime.now().strftime('%Y-%m-%d %H:%M')}", key="content_title_input")
                    with col_save2:
                        if st.button("💾 저장", key="save_content_btn"):
                            try:
                                from modules.database import get_connection
                                import json
                                
                                source_ids = json.dumps([n["id"] for n in selected_news] + [p["id"] for p in selected_papers])
                                
                                conn = get_connection()
                                cursor = conn.cursor()
                                cursor.execute("""
                                    INSERT INTO generated_content (content_type, title, content, source_ids)
                                    VALUES (?, ?, ?, ?)
                                """, (template, content_title, generated_content, source_ids))
                                conn.commit()
                                conn.close()
                                
                                st.success("✅ 콘텐츠가 저장되었습니다!")
                            except Exception as e:
                                st.error(f"❌ 저장 실패: {e}")
                    
                    # 복사용 코드 블록
                    st.markdown("**복사용:**")
                    st.code(generated_content, language=None)
                else:
                    st.error("콘텐츠 생성에 실패했습니다. 다시 시도해주세요.")
                
            except Exception as e:
                st.error(f"콘텐츠 생성 실패: {e}")
                import traceback
                st.code(traceback.format_exc())
    
    # 맨 위로 버튼
    st.markdown("<div style='text-align: center; margin: 30px 0; padding: 20px;'>", unsafe_allow_html=True)
    if st.button("맨 위로 이동", key="scroll_top_tab3", use_container_width=False):
        st.session_state.scroll_to_top_tab3 = True
        st.rerun()
    if st.session_state.get("scroll_to_top_tab3", False):
        st.markdown("""
        <script>
        window.scrollTo(0, 0);
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
        </script>
        """, unsafe_allow_html=True)
        st.session_state.scroll_to_top_tab3 = False
    st.markdown("</div>", unsafe_allow_html=True)

# 4. 내 콘텐츠
elif selected_menu == "💾 내 콘텐츠":
    st.header("💾 내 콘텐츠")
    st.markdown("생성된 콘텐츠와 북마크를 관리합니다.")
    
    tab1, tab2 = st.tabs(["생성된 콘텐츠", "북마크"])
    
    with tab1:
        st.subheader("생성된 콘텐츠")
        try:
            from modules.database import get_connection
            from datetime import datetime
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, content_type, title, content, created_at
                FROM generated_content
                ORDER BY created_at DESC
            """)
            
            contents = cursor.fetchall()
            conn.close()
            
            if contents:
                for content_id, content_type, title, content, created_at in contents:
                    with st.expander(f"📝 {title} ({content_type}) - {created_at[:10]}"):
                        st.markdown(f"**생성일:** {created_at}")
                        st.text_area("내용", content, height=200, key=f"content_{content_id}")
                        
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            st.download_button(
                                "📥 다운로드",
                                content,
                                file_name=f"{title}_{created_at[:10]}.txt",
                                mime="text/plain",
                                key=f"download_{content_id}"
                            )
                        with col2:
                            if st.button("🗑️ 삭제", key=f"delete_{content_id}"):
                                try:
                                    conn = get_connection()
                                    cursor = conn.cursor()
                                    cursor.execute("DELETE FROM generated_content WHERE id = ?", (content_id,))
                                    conn.commit()
                                    conn.close()
                                    st.success("✅ 삭제되었습니다!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ 삭제 실패: {e}")
            else:
                st.info("📭 저장된 콘텐츠가 없습니다.")
        except Exception as e:
            st.error(f"❌ 콘텐츠 로드 실패: {e}")
    
    with tab2:
        st.subheader("북마크")
        st.info("📌 북마크 기능은 곧 추가될 예정입니다.")

# 5. 수집 내용 관리
elif selected_menu == "🗑️ 수집 내용 관리":
    st.header("🗑️ 수집 내용 관리")
    st.markdown("수집된 뉴스와 논문을 선택하여 삭제할 수 있습니다.")
    
    st.divider()
    
    # 뉴스 삭제 섹션
    st.subheader("📰 뉴스 삭제")
    try:
        from modules.database import get_connection
        import json
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # 뉴스 목록 조회
        cursor.execute("""
            SELECT id, date, title, url, country, validity_score
            FROM articles
            ORDER BY created_at DESC
        """)
        news_items = cursor.fetchall()
        conn.close()
        
        if news_items:
            st.markdown(f"**총 {len(news_items)}개의 뉴스가 있습니다.**")
            
            # 체크박스로 선택
            selected_news_ids = []
            for item in news_items:
                news_id, date, title, url, country, score = item
                checkbox_key = f"news_delete_{news_id}"
                if st.checkbox(
                    f"📰 [{country}] {title[:60]}{'...' if len(title) > 60 else ''} | ⭐{score}/5 | {date}",
                    key=checkbox_key
                ):
                    selected_news_ids.append(news_id)
            
            # 삭제 버튼
            if selected_news_ids:
                st.warning(f"⚠️ {len(selected_news_ids)}개의 뉴스를 삭제하시겠습니까?")
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("✅ 선택한 뉴스 삭제", type="primary", key="delete_news_btn"):
                        try:
                            conn = get_connection()
                            cursor = conn.cursor()
                            placeholders = ",".join(["?" for _ in selected_news_ids])
                            cursor.execute(f"DELETE FROM articles WHERE id IN ({placeholders})", selected_news_ids)
                            conn.commit()
                            conn.close()
                            st.success(f"✅ {len(selected_news_ids)}개의 뉴스가 삭제되었습니다.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 삭제 중 오류 발생: {e}")
                with col2:
                    if st.button("❌ 취소", key="cancel_news_btn"):
                        st.rerun()
        else:
            st.info("📭 삭제할 뉴스가 없습니다.")
            
    except Exception as e:
        st.error(f"뉴스 조회 오류: {e}")
    
    st.divider()
    
    # 논문 삭제 섹션
    st.subheader("📚 논문 삭제")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 논문 목록 조회
        cursor.execute("""
            SELECT id, date, title, journal, category
            FROM papers
            ORDER BY created_at DESC
        """)
        paper_items = cursor.fetchall()
        conn.close()
        
        if paper_items:
            st.markdown(f"**총 {len(paper_items)}개의 논문이 있습니다.**")
            
            # 체크박스로 선택
            selected_paper_ids = []
            for item in paper_items:
                paper_id, date, title, journal, category = item
                checkbox_key = f"paper_delete_{paper_id}"
                if st.checkbox(
                    f"📚 [{journal}] {title[:60]}{'...' if len(title) > 60 else ''} | {date}",
                    key=checkbox_key
                ):
                    selected_paper_ids.append(paper_id)
            
            # 삭제 버튼
            if selected_paper_ids:
                st.warning(f"⚠️ {len(selected_paper_ids)}개의 논문을 삭제하시겠습니까?")
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("✅ 선택한 논문 삭제", type="primary", key="delete_paper_btn"):
                        try:
                            conn = get_connection()
                            cursor = conn.cursor()
                            placeholders = ",".join(["?" for _ in selected_paper_ids])
                            cursor.execute(f"DELETE FROM papers WHERE id IN ({placeholders})", selected_paper_ids)
                            conn.commit()
                            conn.close()
                            st.success(f"✅ {len(selected_paper_ids)}개의 논문이 삭제되었습니다.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ 삭제 중 오류 발생: {e}")
                with col2:
                    if st.button("❌ 취소", key="cancel_paper_btn"):
                        st.rerun()
        else:
            st.info("📭 삭제할 논문이 없습니다.")
            
    except Exception as e:
        st.error(f"논문 조회 오류: {e}")
    
    # 맨 위로 버튼
    st.markdown("<div style='text-align: center; margin: 30px 0; padding: 20px;'>", unsafe_allow_html=True)
    if st.button("맨 위로 이동", key="scroll_top_tab4", use_container_width=False):
        st.session_state.scroll_to_top_tab4 = True
        st.rerun()
    if st.session_state.get("scroll_to_top_tab4", False):
        st.markdown("""
        <script>
        window.scrollTo(0, 0);
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
        </script>
        """, unsafe_allow_html=True)
        st.session_state.scroll_to_top_tab4 = False
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    # 전체 삭제 섹션
    st.subheader("⚠️ 전체 삭제")
    st.warning("⚠️ 모든 뉴스와 논문을 삭제합니다. 이 작업은 되돌릴 수 없습니다!")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🗑️ 모든 뉴스 삭제", type="secondary", key="delete_all_news_btn"):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM articles")
                conn.commit()
                conn.close()
                st.success("✅ 모든 뉴스가 삭제되었습니다.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 삭제 중 오류 발생: {e}")
    
    with col2:
        if st.button("🗑️ 모든 논문 삭제", type="secondary", key="delete_all_paper_btn"):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM papers")
                conn.commit()
                conn.close()
                st.success("✅ 모든 논문이 삭제되었습니다.")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 삭제 중 오류 발생: {e}")

# 6. 경제 흐름 파악
elif selected_menu == "📈 경제 흐름 파악":
    st.header("📈 경제 흐름 파악")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("거시경제, 산업 분석, 글로벌 시황 정보를 수집하고 분석합니다.")
    with col2:
        if st.button("🔄 경제 흐름 파악하기", type="primary", key="economy_collect_btn"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                try:
                    from modules.economy_collector import collect_economy_news
                    
                    def update_progress(current, total, message):
                        progress = current / total if total > 0 else 0
                        progress_bar.progress(progress)
                        status_text.text(f"{message} ({current}/{total}) - {int(progress * 100)}%")
                    
                    collected, saved = collect_economy_news(progress_callback=update_progress)
                    progress_bar.progress(0.9)
                    status_text.text(f"✅ 수집 완료: {collected}개 수집, {saved}개 저장")
                    
                    
                    progress_bar.progress(1.0)
                except Exception as e:
                    st.error(f"❌ 오류 발생: {e}")
                    import traceback
                    st.code(traceback.format_exc())
        
    
    # 경제 흐름 대시보드
    st.divider()
    st.subheader("📊 경제 흐름 대시보드")
    
    try:
        from modules.dashboard_utils import get_category_summary, get_trend_data, get_top_issues
        import pandas as pd
        
        # 카테고리별 요약 카드
        col1, col2, col3 = st.columns(3)
        
        with col1:
            macro_summary = get_category_summary("거시경제", days=7)
            st.markdown(f"""
            <div style='padding: 15px; background-color: #f0f7ff; border-radius: 10px; border-left: 4px solid #4CAF50;'>
                <h4 style='margin: 0 0 10px 0;'>📊 거시경제</h4>
                <p style='font-size: 24px; font-weight: bold; margin: 5px 0;'>{macro_summary['count']}건</p>
                <p style='font-size: 12px; margin: 5px 0;'><strong>주요 키워드:</strong> {', '.join(macro_summary['keywords'][:3]) if macro_summary['keywords'] else '없음'}</p>
                <p style='font-size: 12px; margin: 5px 0;'>{macro_summary['trend']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            industry_summary = get_category_summary("산업분석", days=7)
            st.markdown(f"""
            <div style='padding: 15px; background-color: #fff7f0; border-radius: 10px; border-left: 4px solid #FF9800;'>
                <h4 style='margin: 0 0 10px 0;'>🏭 산업분석</h4>
                <p style='font-size: 24px; font-weight: bold; margin: 5px 0;'>{industry_summary['count']}건</p>
                <p style='font-size: 12px; margin: 5px 0;'><strong>주요 키워드:</strong> {', '.join(industry_summary['keywords'][:3]) if industry_summary['keywords'] else '없음'}</p>
                <p style='font-size: 12px; margin: 5px 0;'>{industry_summary['trend']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            global_summary = get_category_summary("글로벌시황", days=7)
            st.markdown(f"""
            <div style='padding: 15px; background-color: #f0fff0; border-radius: 10px; border-left: 4px solid #2196F3;'>
                <h4 style='margin: 0 0 10px 0;'>🌍 글로벌시황</h4>
                <p style='font-size: 24px; font-weight: bold; margin: 5px 0;'>{global_summary['count']}건</p>
                <p style='font-size: 12px; margin: 5px 0;'><strong>주요 키워드:</strong> {', '.join(global_summary['keywords'][:3]) if global_summary['keywords'] else '없음'}</p>
                <p style='font-size: 12px; margin: 5px 0;'>{global_summary['trend']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 주요 이슈 하이라이트
        st.subheader("🔥 오늘의 주요 이슈")
        top_issues = get_top_issues(limit=5)
        
        if top_issues:
            for idx, issue in enumerate(top_issues, 1):
                st.markdown(f"""
                <div style='padding: 12px; margin: 8px 0; background-color: #fff9e6; border-left: 4px solid #FFC107; border-radius: 5px;'>
                    <p style='margin: 0; font-weight: bold;'>{idx}. {issue['title'][:80]}{'...' if len(issue['title']) > 80 else ''}</p>
                    <p style='margin: 5px 0 0 0; font-size: 11px; color: #666;'>📅 {issue['date']} | 🏷️ 키워드 {issue['keyword_count']}개</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📭 주요 이슈가 없습니다.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 날짜별 트렌드 그래프
        st.subheader("📈 최근 7일간 트렌드")
        
        macro_trend = get_trend_data("거시경제", days=7)
        industry_trend = get_trend_data("산업분석", days=7)
        global_trend = get_trend_data("글로벌시황", days=7)
        
        if macro_trend or industry_trend or global_trend:
            trend_df = pd.DataFrame({
                "날짜": [date for date, _ in macro_trend] if macro_trend else [],
                "거시경제": [count for _, count in macro_trend] if macro_trend else [],
                "산업분석": [count for _, count in industry_trend] if industry_trend else [],
                "글로벌시황": [count for _, count in global_trend] if global_trend else []
            })
            
            if not trend_df.empty:
                st.line_chart(trend_df.set_index("날짜"))
        else:
            st.info("📭 트렌드 데이터가 없습니다.")
        
    except Exception as e:
        st.error(f"❌ 대시보드 로드 실패: {e}")
        import traceback
        st.code(traceback.format_exc())
    
    st.divider()
    st.subheader("📋 경제 뉴스 헤드라인")
    
    # 헤드라인 표 스타일
    st.markdown("""
    <style>
    .economy-headline-table {
        font-size: 10pt !important;
        line-height: 1.2 !important;
    }
    .economy-headline-table th {
        font-size: 10pt !important;
        padding: 4px 8px !important;
        background-color: #f0f0f0;
    }
    .economy-headline-table td {
        font-size: 10pt !important;
        padding: 3px 8px !important;
        line-height: 1.2 !important;
    }
    .economy-headline-table tr {
        border-bottom: 1px solid #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    try:
        from modules.database import get_connection
        from datetime import datetime, timedelta
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # 최근 7일간의 경제 뉴스 조회
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        cursor.execute("""
            SELECT date, title, category, source, url
            FROM economy_news
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC, created_at DESC
            LIMIT 200
        """, (start_date, end_date))
        
        news_list = cursor.fetchall()
        conn.close()
        
        if news_list:
            # 표 데이터 준비
            table_data = []
            for news in news_list:
                date, title, category, source, url = news
                table_data.append({
                    "날짜": date,
                    "제목": title[:80] + "..." if len(title) > 80 else title,
                    "카테고리": category,
                    "소스": source,
                    "링크": url
                })
            
            # DataFrame으로 변환하여 표시
            import pandas as pd
            df = pd.DataFrame(table_data)
            
            # 표 스타일 적용하여 표시
            st.markdown('<div class="economy-headline-table">', unsafe_allow_html=True)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "날짜": st.column_config.TextColumn("날짜", width="small"),
                    "제목": st.column_config.TextColumn("제목", width="large"),
                    "카테고리": st.column_config.TextColumn("카테고리", width="small"),
                    "소스": st.column_config.TextColumn("소스", width="small"),
                    "링크": st.column_config.LinkColumn("링크", width="medium")
                }
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.caption(f"총 {len(news_list)}개의 경제 뉴스가 표시됩니다.")
        else:
            st.info("📭 표시할 경제 뉴스가 없습니다. 먼저 경제 뉴스를 수집해주세요.")
    except Exception as e:
        st.error(f"❌ 뉴스 헤드라인 표시 중 오류 발생: {e}")
        import traceback
        st.code(traceback.format_exc())
    
    st.divider()
    
    try:
        from modules.database import get_connection
        import json
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # 검색 및 필터 기능
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_query = st.text_input("🔍 검색", placeholder="제목, 요약, 키워드로 검색...", key="economy_search")
        
        with col2:
            sort_option = st.selectbox("정렬", ["최신순", "오래된순"], key="economy_sort")
        
        with col3:
            category_filter = st.selectbox("카테고리", ["전체", "거시경제", "산업분석", "글로벌시황"], key="economy_category")
        
        # 소스 필터
        cursor.execute("SELECT DISTINCT source FROM economy_news WHERE source IS NOT NULL")
        all_sources = [row[0] for row in cursor.fetchall() if row[0]]
        
        if all_sources:
            selected_sources = st.multiselect("📊 소스 필터", sorted(all_sources), key="economy_sources")
        else:
            selected_sources = []
        
        # SQL 쿼리 구성
        where_conditions = []
        params = []
        
        # 검색 조건
        if search_query:
            where_conditions.append("(title LIKE ? OR content_summary LIKE ? OR keywords LIKE ?)")
            search_param = f"%{search_query}%"
            params.extend([search_param, search_param, search_param])
        
        # 카테고리 필터
        if category_filter != "전체":
            where_conditions.append("category = ?")
            params.append(category_filter)
        
        # 소스 필터
        if selected_sources:
            source_conditions = []
            for source in selected_sources:
                source_conditions.append("source = ?")
                params.append(source)
            where_conditions.append(f"({' OR '.join(source_conditions)})")
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # 정렬
        order_by = "created_at DESC" if sort_option == "최신순" else "created_at ASC"
        
        # 페이지네이션
        page_size = 20
        page = st.number_input("페이지", min_value=1, value=1, step=1, key="economy_page")
        offset = (page - 1) * page_size
        
        # 경제 뉴스 조회
        query = f"""
            SELECT id, date, title, url, content_summary, keywords, source, category
            FROM economy_news
            WHERE {where_clause}
            ORDER BY {order_by}
            LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])
        
        cursor.execute(query, params)
        
        economy_items = cursor.fetchall()
        conn.close()
        
        if economy_items:
            st.markdown(f"<h4 style='font-size: 16px; margin-bottom: 10px;'>📄 경제 정보 목록 (총 {len(economy_items)}개 표시)</h4>", unsafe_allow_html=True)
            
            for idx, item in enumerate(economy_items):
                item_id, date, title, url, summary, keywords_json, source, category = item
                
                # 키워드 파싱
                try:
                    keywords = json.loads(keywords_json) if keywords_json else []
                except:
                    keywords = []
                
                # 카드 형태로 표시
                with st.container():
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"<h5 style='font-size: 14px; font-weight: bold; margin-bottom: 5px;'>{title}</h5>", unsafe_allow_html=True)
                        st.markdown(f"<p style='font-size: 11px; color: #666; margin-bottom: 5px;'>📅 {date} | 📊 {source} | 🏷️ {category}</p>", unsafe_allow_html=True)
                        
                        if summary:
                            st.markdown(f"<p style='font-size: 12px; margin-bottom: 5px;'><strong>요약:</strong> {summary[:150]}{'...' if len(summary) > 150 else ''}</p>", unsafe_allow_html=True)
                        
                        if keywords:
                            keyword_tags = " ".join([f"`{k}`" for k in keywords[:3]])
                            st.markdown(f"<p style='font-size: 11px; margin-bottom: 5px;'><strong>키워드:</strong> {keyword_tags}</p>", unsafe_allow_html=True)
                        
                        if url:
                            st.markdown(f"<a href='{url}' target='_blank' style='font-size: 11px;'>원문 보기 →</a>", unsafe_allow_html=True)
                    
                    with col2:
                        # 카테고리 배지
                        category_colors = {
                            "거시경제": "#4CAF50",
                            "산업분석": "#2196F3",
                            "글로벌시황": "#FF9800"
                        }
                        color = category_colors.get(category, "#666")
                        st.markdown(f"<div style='background-color: {color}; color: white; padding: 5px 10px; border-radius: 12px; font-size: 10px; text-align: center;'>{category}</div>", unsafe_allow_html=True)
                    
                    if idx < len(economy_items) - 1:
                        st.markdown("<hr style='margin: 10px 0;'>", unsafe_allow_html=True)
        else:
            st.info("📭 저장된 경제 정보가 없습니다. 위의 '경제 흐름 파악하기' 버튼을 클릭하여 정보를 수집하세요.")
            
    except Exception as e:
        st.error(f"데이터베이스 조회 오류: {e}")
        st.info("데이터베이스가 초기화되지 않았을 수 있습니다. 사이드바에서 '데이터베이스 초기화' 버튼을 클릭하세요.")
    
    # 맨 위로 버튼
    st.markdown("<div style='text-align: center; margin: 30px 0; padding: 20px;'>", unsafe_allow_html=True)
    if st.button("맨 위로 이동", key="scroll_top_tab5", use_container_width=False):
        st.session_state.scroll_to_top_tab5 = True
        st.rerun()
    if st.session_state.get("scroll_to_top_tab5", False):
        st.markdown("""
        <script>
        window.scrollTo(0, 0);
        document.documentElement.scrollTop = 0;
        document.body.scrollTop = 0;
        </script>
        """, unsafe_allow_html=True)
        st.session_state.scroll_to_top_tab5 = False
    st.markdown("</div>", unsafe_allow_html=True)

# 6. 테스트
elif selected_menu == "🧪 테스트":
    st.header("🧪 테스트 수집")
    st.markdown("### 빠른 테스트를 위한 수집 기능")
    st.info("한국 뉴스 1개, 외국 뉴스 1개, 논문 2개를 수집하여 테스트합니다.")
    
    # 테스트 수집 버튼
    if st.button("🧪 테스트 수집 시작 (뉴스2개 + 논문2개)", type="primary", key="test_collect_btn_main"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        test_results = {"kr_news": [], "us_news": [], "papers": []}
        
        try:
            from modules.news_collector import collect_and_analyze_news
            from modules.paper_collector import collect_and_analyze_papers
            from modules.database import get_connection
            
            def update_progress(current, total, message):
                progress = current / total if total > 0 else 0
                progress_bar.progress(progress)
                status_text.text(f"{message} ({current}/{total}) - {int(progress * 100)}%")
            
            # 1. 한국 뉴스 1개 수집
            status_text.text("한국 뉴스 수집 중... (1/4)")
            progress_bar.progress(0.1)
            collected_kr, saved_kr = collect_and_analyze_news(
                keywords=["심리건강", "심리상담", "정신건강", "마음건강"],
                countries=["KR"],
                max_per_keyword=5,  # 더 많이 가져와서 필터링 후 저장
                progress_callback=update_progress
            )
            
            # 최근 수집된 한국 뉴스 가져오기
            if saved_kr > 0:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, title, date, country, url, content_summary, keywords, validity_score
                    FROM articles
                    WHERE country = 'KR'
                    ORDER BY created_at DESC
                    LIMIT 1
                """)
                test_results["kr_news"] = cursor.fetchall()
                conn.close()
            
            # 2. 외국 뉴스 1개 수집
            status_text.text("외국 뉴스 수집 중... (2/4)")
            progress_bar.progress(0.3)
            collected_us, saved_us = collect_and_analyze_news(
                keywords=["mental health", "psychology", "counseling"],
                countries=["US"],
                max_per_keyword=5,  # 더 많이 가져와서 필터링 후 저장
                progress_callback=update_progress
            )
            
            # 최근 수집된 외국 뉴스 가져오기
            if saved_us > 0:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, title, date, country, url, content_summary, keywords, validity_score
                    FROM articles
                    WHERE country = 'US'
                    ORDER BY created_at DESC
                    LIMIT 1
                """)
                test_results["us_news"] = cursor.fetchall()
                conn.close()
            
            # 3. 논문 수집
            status_text.text("논문 수집 중... (3/4)")
            progress_bar.progress(0.6)
            collected_papers, saved_papers = collect_and_analyze_papers(
                keywords=["psychology"],
                sources=["arxiv"],
                max_per_keyword=2,
                progress_callback=update_progress
            )
            
            # 최근 수집된 논문 가져오기
            if saved_papers > 0:
                conn = get_connection()
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        SELECT id, title, date, journal, url, abstract, keywords
                        FROM papers
                        WHERE (journal LIKE '%arXiv%' OR journal LIKE '%arxiv%' OR url LIKE '%arxiv%')
                        ORDER BY created_at DESC
                        LIMIT 2
                    """)
                    test_results["papers"] = cursor.fetchall()
                except Exception as e:
                    # 에러 발생 시 더 간단한 쿼리로 재시도
                    logger.error(f"논문 조회 실패: {e}")
                    cursor.execute("""
                        SELECT id, title, date, journal, url, abstract, keywords
                        FROM papers
                        ORDER BY created_at DESC
                        LIMIT 2
                    """)
                    test_results["papers"] = cursor.fetchall()
                finally:
                    conn.close()
            
            progress_bar.progress(1.0)
            status_text.text("✅ 테스트 수집 완료!")
            
            # 결과 표시
            st.success(f"✅ 테스트 수집 완료!\n- 한국 뉴스: {saved_kr}개 저장\n- 외국 뉴스: {saved_us}개 저장\n- 논문: {saved_papers}개 저장")
            
            # 수집된 내용 표시
            st.divider()
            st.subheader("📋 수집된 내용")
            
            # 한국 뉴스 표시
            if test_results["kr_news"]:
                st.markdown("#### 🇰🇷 한국 뉴스")
                for news in test_results["kr_news"]:
                    news_id, title, date, country, url, summary, keywords, rating = news
                    st.markdown(f"**{title}**")
                    st.markdown(f"📅 {date} | 🌍 {country} | ⭐ {rating}/5")
                    if summary:
                        st.markdown(f"요약: {summary[:150]}...")
                    if url:
                        st.markdown(f"[원문 보기 →]({url})")
                    st.markdown("---")
            
            # 외국 뉴스 표시
            if test_results["us_news"]:
                st.markdown("#### 🌍 외국 뉴스")
                for news in test_results["us_news"]:
                    news_id, title, date, country, url, summary, keywords, rating = news
                    # 제목이 "원제 (번역)" 형식인지 확인
                    if " (" in title and title.endswith(")"):
                        parts = title.rsplit(" (", 1)
                        if len(parts) == 2:
                            original_title = parts[0]
                            translated_title = parts[1].rstrip(")")
                            st.markdown(f"**{translated_title}**")
                            st.markdown(f"<p style='font-size: 11px; color: #666;'>(원제: {original_title})</p>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"**{title}**")
                    else:
                        st.markdown(f"**{title}**")
                    st.markdown(f"📅 {date} | 🌍 {country} | ⭐ {rating}/5")
                    if summary:
                        # 요약 전체 표시 (150자 제한 제거)
                        st.markdown(f"**요약:** {summary}")
                    if url:
                        st.markdown(f"[원문 보기 →]({url})")
                    st.markdown("---")
            
            # 논문 표시
            if test_results["papers"]:
                st.markdown("#### 📚 논문")
                for paper in test_results["papers"]:
                    paper_id, title, date, journal, url, abstract, keywords = paper
                    st.markdown(f"**{title}**")
                    st.markdown(f"📅 {date} | 📖 {journal}")
                    if abstract:
                        with st.expander("📄 Abstract", expanded=True):
                            # Abstract에 번역이 포함되어 있는지 확인
                            if "[원문]" in abstract and "[한국어 번역]" in abstract:
                                # 외국 논문: 원문과 번역 분리 표시
                                parts = abstract.split("[한국어 번역]")
                                if len(parts) == 2:
                                    original = parts[0].replace("[원문]", "").strip()
                                    translated = parts[1].strip()
                                    
                                    # 한국어 번역 먼저 표시 (가독성 향상)
                                    st.markdown("**🇰🇷 한국어 번역:**")
                                    st.markdown(f"<p style='font-size: 13px; line-height: 1.8; color: #333; margin-bottom: 15px;'>{translated}</p>", unsafe_allow_html=True)
                                    st.markdown("---")
                                    st.markdown("**📄 원본 Abstract (영문):**")
                                    st.markdown(f"<p style='font-size: 12px; line-height: 1.6; color: #666;'>{original}</p>", unsafe_allow_html=True)
                                else:
                                    st.markdown("**📄 논문 Abstract:**")
                                    st.markdown(f"<p style='font-size: 12px; line-height: 1.6;'>{abstract}</p>", unsafe_allow_html=True)
                            else:
                                # 한국 논문 또는 번역 실패: 원문만 표시
                                st.markdown("**📄 논문 Abstract:**")
                                st.markdown(f"<p style='font-size: 12px; line-height: 1.6;'>{abstract}</p>", unsafe_allow_html=True)
                                if journal and ("arxiv" in journal.lower() or "pubmed" in journal.lower()):
                                    st.info("💡 외국 논문이지만 번역이 아직 생성되지 않았습니다. 잠시 후 다시 확인해주세요.")
                    if url:
                        st.markdown(f"[원문 보기 →]({url})")
                    st.markdown("---")
            
            if not test_results["kr_news"] and not test_results["us_news"] and not test_results["papers"]:
                st.info("수집된 내용이 없습니다. 이미 수집된 내용이거나 중복된 항목일 수 있습니다.")
                
        except Exception as e:
            st.error(f"❌ 테스트 수집 실패: {e}")
            import traceback
            st.code(traceback.format_exc())
    
    # 이전 테스트 결과가 있으면 표시
    else:
        st.info("위의 '테스트 수집 시작' 버튼을 클릭하여 테스트를 진행하세요.")

# 7. 설정
elif selected_menu == "⚙️ 설정":
    st.header("⚙️ 설정")
    st.info("프로젝트 초기화 완료!")
    st.markdown("""
    ### 주요 기능
    - 📰 **트랜드 레이더**: 심리 관련 뉴스 수집 및 분석
    - 📚 **아카이브**: 학술 논문 수집 및 분석
    - ✨ **팩토리**: 수집된 콘텐츠로 다양한 형태의 콘텐츠 생성
    - 📈 **경제 흐름 파악**: 경제 정보 수집 및 분석
    - 🗑️ **수집 내용 관리**: 수집된 뉴스 및 논문 관리
    """)

# 8. 초기화
elif selected_menu == "🗄️ 초기화":
    st.header("🗄️ 데이터베이스 초기화")
    st.warning("⚠️ 이 작업은 데이터베이스 테이블을 재생성합니다. 수집된 내용은 삭제되지 않습니다.")
    st.info("💡 수집된 내용을 삭제하려면 '수집 내용 관리' 메뉴를 사용하세요.")
    
    if st.button("🗄️ 데이터베이스 초기화", type="primary"):
        try:
            from modules.database import init_database
            init_database()
            st.success("데이터베이스 초기화 완료! (테이블 재생성)")
        except Exception as e:
            st.error(f"오류 발생: {e}")

# 기본값 (트랜드 레이더)
else:
    st.header("📰 트랜드 레이더")
    st.info("좌측 사이드바에서 메뉴를 선택하세요.")
