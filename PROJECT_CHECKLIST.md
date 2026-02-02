# PsyInsight Commander 세부 작업 체크리스트

## 📋 사용 방법
이 체크리스트는 각 Iteration의 세부 작업을 단계별로 추적하기 위한 것입니다.
작업 완료 시 [ ]를 [x]로 변경하고, todo.md도 함께 업데이트하세요.

---

## Phase 1: MVP 개발

### ✅ Iteration 1: 프로젝트 초기 설정 및 인프라 구축

#### 1.1 프로젝트 구조 생성
- [ ] 루트 디렉토리 생성: `psyinsight-commander/`
- [ ] `app.py` 파일 생성 (메인 Streamlit 앱)
- [ ] `modules/` 폴더 생성
  - [ ] `modules/__init__.py` 생성
  - [ ] `modules/ai_engine.py` (빈 파일)
  - [ ] `modules/news_collector.py` (빈 파일)
  - [ ] `modules/paper_collector.py` (빈 파일)
  - [ ] `modules/database.py` (빈 파일)
  - [ ] `modules/scheduler.py` (빈 파일)
- [ ] `data/` 폴더 생성 (DB 저장소)
- [ ] `config/` 폴더 생성
  - [ ] `config/config.py` (설정 파일)
- [ ] `.env.example` 파일 생성
- [ ] `.gitignore` 파일 생성

#### 1.2 의존성 관리
- [ ] `requirements.txt` 작성
  - [ ] streamlit>=1.28.0
  - [ ] google-generativeai>=0.3.0
  - [ ] feedparser>=6.0.10
  - [ ] requests>=2.31.0
  - [ ] beautifulsoup4>=4.12.0
  - [ ] schedule>=1.2.0
  - [ ] python-dotenv>=1.0.0
  - [ ] wordcloud>=1.9.2 (Tab 2용)
  - [ ] matplotlib>=3.7.0 (워드 클라우드용)
  - [ ] biopython>=1.81 (PubMed용, 선택)

#### 1.3 환경 설정
- [ ] `.env.example` 작성
  - [ ] GEMINI_API_KEY=your_api_key_here
- [ ] `.gitignore` 작성
  - [ ] `.env`
  - [ ] `data/*.db`
  - [ ] `__pycache__/`
  - [ ] `*.pyc`
  - [ ] `.venv/`
  - [ ] `venv/`
- [ ] Streamlit Secrets 가이드 작성 (`README.md`에 추가)

#### 1.4 데이터베이스 초기화
- [ ] `modules/database.py` 구현
  - [ ] `init_database()` 함수: DB 파일 생성
  - [ ] `create_tables()` 함수: 테이블 생성
    - [ ] `articles` 테이블
    - [ ] `papers` 테이블
    - [ ] `pain_points` 테이블 (Tab 2용, 나중에)
  - [ ] `get_connection()` 함수: DB 연결
- [ ] 초기 마이그레이션 스크립트 작성
  - [ ] `scripts/init_db.py` 생성
- [ ] 테스트: DB 생성 및 테이블 확인

---

### ✅ Iteration 2: Gemini AI 엔진 구축

#### 2.1 AI 엔진 모듈 생성
- [ ] `modules/ai_engine.py` 기본 구조 작성
  - [ ] `import` 문 작성
  - [ ] `GeminiClient` 클래스 또는 함수 그룹 정의

#### 2.2 API 클라이언트 설정
- [ ] API 키 로드 함수 구현
  - [ ] 환경 변수에서 로드 (`.env`)
  - [ ] Streamlit Secrets에서 로드 (배포 환경)
  - [ ] 에러 처리 (키가 없을 경우)
- [ ] Gemini API 클라이언트 초기화
  - [ ] `google.generativeai.configure()` 호출
  - [ ] 모델 선택: `gemini-1.5-flash`

#### 2.3 AI 함수 구현
- [ ] `generate_summary(text: str) -> str`
  - [ ] 프롬프트: "다음 뉴스 기사를 3줄로 요약해주세요."
  - [ ] 응답 파싱
  - [ ] 에러 처리
- [ ] `evaluate_article(text: str) -> dict`
  - [ ] 프롬프트: 전문성 평가 기준 포함
  - [ ] 응답에서 점수(1~5) 추출
  - [ ] 평가 근거 추출
- [ ] `extract_keywords(text: str) -> list`
  - [ ] 프롬프트: "핵심 키워드를 5개 추출해주세요."
  - [ ] JSON 형식 응답 파싱
- [ ] `extract_pain_points(text: str) -> list`
  - [ ] 프롬프트: "Life Pain Point를 추출해주세요."
  - [ ] JSON 형식 응답 파싱
- [ ] `summarize_paper(abstract: str) -> dict`
  - [ ] 프롬프트: "연구 목적, 방법, 결과, 시사점으로 구조화"
  - [ ] JSON 형식 응답 파싱

#### 2.4 에러 처리 및 로깅
- [ ] API 호출 실패 시 재시도 로직
  - [ ] 최대 3회 재시도
  - [ ] 지수 백오프 (exponential backoff)
- [ ] 타임아웃 설정 (10초)
- [ ] 로깅 기능 추가
  - [ ] `logging` 모듈 사용
  - [ ] API 호출 로그 기록
  - [ ] 에러 로그 기록

#### 2.5 테스트
- [ ] 각 함수 단위 테스트
- [ ] 실제 API 호출 테스트
- [ ] 에러 케이스 테스트

---

### ✅ Iteration 3: Tab 1 - 사이콜로지 트랜드 레이더 (기본 기능)

#### 3.1 뉴스 수집 모듈
- [ ] `modules/news_collector.py` 기본 구조 작성
- [ ] Google News RSS Feed 파싱
  - [ ] `feedparser` 라이브러리 사용
  - [ ] 키워드별 RSS URL 생성
    - [ ] '심리' (psychology)
    - [ ] '마음건강' (mental health)
    - [ ] '뇌과학' (neuroscience)
    - [ ] '상담' (counseling)
  - [ ] 미국/한국 뉴스 분리 수집
- [ ] 뉴스 원문 스크래핑
  - [ ] `requests` + `BeautifulSoup` 사용
  - [ ] 본문 추출 로직
  - [ ] 에러 처리 (접근 불가 시 스킵)
- [ ] 중복 제거 로직
  - [ ] URL 기준 중복 체크
  - [ ] 제목 유사도 체크 (선택)

#### 3.2 AI 분석 및 저장
- [ ] 수집된 뉴스를 AI 엔진으로 분석
  - [ ] `generate_summary()` 호출
  - [ ] `extract_keywords()` 호출
  - [ ] `evaluate_article()` 호출
- [ ] 데이터베이스에 저장
  - [ ] `articles` 테이블에 INSERT
  - [ ] 중복 체크 (URL 기준)
  - [ ] 트랜잭션 처리

#### 3.3 Streamlit UI 구현
- [ ] `app.py`에 Tab 1 추가
  - [ ] `st.tabs()` 사용하여 탭 생성
- [ ] 카드 형태 뉴스 표시
  - [ ] `st.container()` 또는 `st.columns()` 사용
  - [ ] 제목 표시 (`st.header()` 또는 `st.subheader()`)
  - [ ] 요약 표시 (`st.write()`)
  - [ ] 링크 표시 (`st.link_button()` 또는 마크다운)
  - [ ] 평점 표시 (별점 또는 숫자)
  - [ ] 해시태그 표시 (`st.badge()` 또는 `st.tag()`)
- [ ] 기본 페이지네이션
  - [ ] 페이지당 10개 항목
  - [ ] `st.number_input()` 또는 버튼으로 페이지 선택
  - [ ] 최신순 정렬 (SQL ORDER BY)

#### 3.4 테스트
- [ ] 뉴스 수집 테스트 (수동 실행)
- [ ] AI 분석 테스트
- [ ] UI 표시 테스트
- [ ] 페이지네이션 테스트

---

### ✅ Iteration 4: Tab 3 - 아카데믹 아카이브 (기본 기능)

#### 4.1 논문 수집 모듈
- [ ] `modules/paper_collector.py` 기본 구조 작성
- [ ] arXiv API 연동
  - [ ] `arxiv` 라이브러리 또는 직접 API 호출
  - [ ] 심리학 카테고리 필터링
    - [ ] `cat:q-bio.NC` (신경과학)
    - [ ] 키워드 검색: 'psychology', 'counseling'
  - [ ] 최신 논문 수집 (주 1회)
- [ ] 논문 메타데이터 추출
  - [ ] 제목
  - [ ] 저자 (리스트)
  - [ ] 초록 (Abstract)
  - [ ] 링크
- [ ] PubMed API 연동 (선택)
  - [ ] `biopython` 라이브러리 사용
  - [ ] 키워드 검색
  - [ ] 메타데이터 추출

#### 4.2 AI 요약 및 저장
- [ ] 논문 초록을 AI 엔진으로 요약
  - [ ] `summarize_paper()` 호출
  - [ ] JSON 응답 파싱
- [ ] 데이터베이스에 저장
  - [ ] `papers` 테이블에 INSERT
  - [ ] 중복 체크 (URL 또는 DOI 기준)

#### 4.3 Streamlit UI 구현
- [ ] `app.py`에 Tab 3 추가
- [ ] 카드 형태 논문 표시
  - [ ] 제목 표시
  - [ ] 저자 표시 (쉼표로 구분)
  - [ ] 저널 표시
  - [ ] 요약 미리보기 (접기/펼치기)
  - [ ] 링크 표시
- [ ] 기본 검색 기능
  - [ ] `st.text_input()`으로 검색어 입력
  - [ ] 제목/저자 검색 (SQL LIKE 또는 FTS)

#### 4.4 테스트
- [ ] 논문 수집 테스트
- [ ] AI 요약 테스트
- [ ] UI 표시 테스트
- [ ] 검색 기능 테스트

---

### ✅ Iteration 5: 스케줄러 및 자동화

#### 5.1 스케줄러 모듈
- [ ] `modules/scheduler.py` 기본 구조 작성
- [ ] `schedule` 라이브러리로 작업 스케줄링
  - [ ] Tab 1: 매일 새벽 2시 실행
    - [ ] `schedule.every().day.at("02:00").do(collect_news)`
  - [ ] Tab 3: 매주 월요일 실행
    - [ ] `schedule.every().monday.at("02:00").do(collect_papers)`
- [ ] 백그라운드 실행 설정
  - [ ] 별도 스레드에서 실행
  - [ ] `threading.Thread` 사용
  - [ ] 데몬 스레드로 설정 (선택)

#### 5.2 로깅 기능
- [ ] 스케줄러 실행 로그 기록
- [ ] 수집 결과 로그 기록 (성공/실패, 개수)
- [ ] 에러 로그 기록

#### 5.3 Streamlit 통합
- [ ] `app.py`에서 스케줄러 시작
  - [ ] 앱 실행 시 자동 시작
  - [ ] 수동 실행 버튼 추가 (선택)

#### 5.4 테스트
- [ ] 스케줄러 실행 테스트
- [ ] 로그 확인 테스트

---

## Phase 2: 확장 기능 개발

### ✅ Iteration 6: Tab 1 고급 기능

#### 6.1 검색 기능
- [ ] 검색 입력 필드 추가 (`st.text_input()`)
- [ ] 검색 로직 구현
  - [ ] 제목 검색 (SQL LIKE)
  - [ ] 요약 검색
  - [ ] 키워드 검색 (JSON 배열 검색)
- [ ] 실시간 필터링
  - [ ] 입력 시 즉시 필터링

#### 6.2 카테고리 필터
- [ ] 해시태그 기반 필터링
  - [ ] `st.multiselect()` 사용
  - [ ] 다중 선택 가능
- [ ] 필터 적용 로직
  - [ ] SQL WHERE 절에 조건 추가

#### 6.3 정렬 기능
- [ ] 정렬 옵션 선택 (`st.selectbox()`)
  - [ ] 날짜순 (최신순/오래된순)
  - [ ] 평점순 (높은순/낮은순)
- [ ] 정렬 적용 로직
  - [ ] SQL ORDER BY 절 수정

#### 6.4 테스트
- [ ] 검색 기능 테스트
- [ ] 필터 기능 테스트
- [ ] 정렬 기능 테스트

---

### ✅ Iteration 7: Tab 2 - 소셜 마인드 앤 이모션 리스너

#### 7.1 Reddit 연동
- [ ] `modules/reddit_collector.py` 생성
- [ ] PRAW 라이브러리 설정
  - [ ] Reddit API 인증
  - [ ] 클라이언트 ID/Secret 설정
- [ ] Subreddit 수집
  - [ ] r/mentalhealth
  - [ ] r/depression
  - [ ] r/anxiety
  - [ ] r/relationships
- [ ] 게시글 수집 및 저장
  - [ ] 최신 게시글 수집 (24시간 기준)
  - [ ] 제목, 본문, 링크 저장

#### 7.2 AI 분석
- [ ] 게시글에서 Pain Point 추출
  - [ ] `extract_pain_points()` 호출
- [ ] 빈도 계산
  - [ ] 동일 Pain Point 그룹화
  - [ ] 빈도수 집계
- [ ] `pain_points` 테이블에 저장
  - [ ] INSERT 또는 UPDATE (빈도수 증가)

#### 7.3 UI 구현
- [ ] Streamlit Tab 2 추가
- [ ] 워드 클라우드 시각화
  - [ ] `wordcloud` 라이브러리 사용
  - [ ] `st.pyplot()` 또는 `st.image()`로 표시
- [ ] 리스트 뷰 (빈도순)
  - [ ] `st.dataframe()` 또는 카드 형태
- [ ] 필터 기능
  - [ ] 소스 필터 (Reddit/네이트/블라인드)
  - [ ] 감정 태그 필터

#### 7.4 네이트판/블라인드 연동 (선택, 어려움)
- [ ] 웹 스크래핑 설정
  - [ ] Selenium 또는 BeautifulSoup
  - [ ] 로그인 처리 (필요 시)
- [ ] 게시글 수집
- [ ] 개인정보 마스킹 로직
  - [ ] 이름, 전화번호 등 마스킹

---

### ✅ Iteration 8: Tab 4 - 콘텐츠 팩토리

#### 8.1 콘텐츠 선택 기능
- [ ] Tab 1~3에 체크박스 추가
  - [ ] `st.checkbox()` 사용
- [ ] 선택된 항목 저장
  - [ ] 세션 상태 (`st.session_state`) 사용
  - [ ] 또는 임시 테이블에 저장

#### 8.2 템플릿 설계
- [ ] 블로그 포스트 템플릿
  - [ ] 프롬프트 템플릿 작성
- [ ] 릴스 대본 템플릿
  - [ ] 프롬프트 템플릿 작성
- [ ] 게시글 템플릿
  - [ ] 프롬프트 템플릿 작성
- [ ] 논문 아이디어 템플릿
  - [ ] 프롬프트 템플릿 작성

#### 8.3 AI 콘텐츠 생성
- [ ] Gemini API로 템플릿 기반 생성
  - [ ] 선택한 템플릿에 따라 프롬프트 구성
  - [ ] 선택한 콘텐츠를 컨텍스트로 제공
- [ ] 토큰 제한 처리
  - [ ] 입력이 많을 경우 요약 후 전달
- [ ] 결과 파싱 및 저장

#### 8.4 UI 구현
- [ ] Streamlit Tab 4 추가
- [ ] 템플릿 선택
  - [ ] `st.radio()` 또는 `st.checkbox()` (중복 선택)
- [ ] 생성 버튼
  - [ ] `st.button()` 사용
- [ ] 결과 표시
  - [ ] 미리보기 (`st.text_area()` 또는 `st.markdown()`)
  - [ ] 복사 버튼 (`st.button()` + 클립보드 복사)
  - [ ] 다운로드 버튼 (선택)

#### 8.5 테스트
- [ ] 콘텐츠 선택 테스트
- [ ] 템플릿별 생성 테스트
- [ ] 결과 표시 테스트

---

## Phase 3: 고도화 및 최적화

### ✅ Iteration 9: 성능 최적화
- [ ] 데이터베이스 인덱싱
  - [ ] 검색 컬럼에 인덱스 추가
- [ ] 캐싱 기능
  - [ ] 이미 수집한 데이터 재요청 방지
- [ ] 페이지 로딩 최적화
  - [ ] 지연 로딩 (Lazy Loading)

### ✅ Iteration 10: UI/UX 개선
- [ ] 반응형 디자인 개선
- [ ] 다크 모드 지원 (선택)
- [ ] 애니메이션 및 시각적 피드백
- [ ] 사용자 가이드/도움말 추가

### ✅ Iteration 11: 배포 준비
- [ ] Streamlit Cloud 배포 설정
- [ ] 문서화
- [ ] 테스트

---

## 📝 체크리스트 사용 팁

1. **작업 시작 전**: 해당 Iteration의 모든 항목 확인
2. **작업 중**: 완료한 항목 즉시 체크
3. **작업 완료 후**: todo.md와 함께 업데이트
4. **문제 발생 시**: 해당 항목에 메모 추가

---

**이 체크리스트는 프로젝트 진행에 따라 업데이트됩니다.**
