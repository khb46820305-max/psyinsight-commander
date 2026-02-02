# PRD: PsyInsight Commander (심리 인사이트 통합 지휘소)

> **⚠️ 이 문서는 이전 버전입니다. 최종 PRD는 `FINAL_PRD.md`를 참조하세요.**

## 📋 문서 정보
- **프로젝트명**: PsyInsight Commander
- **버전**: 1.0 (이전 버전)
- **최종 버전**: 2.0 (FINAL_PRD.md 참조)
- **작성일**: 2026-01-XX
- **작성자**: AI 기획팀 (Planner)
- **프로젝트 타입**: 전문가용 대시보드 웹 애플리케이션 (홈페이지/웹사이트)

---

## 1. 프로젝트 개요

### 1.1 목적
심리학 전문가를 위한 통합 대시보드 웹 애플리케이션으로, 뉴스와 학술 논문을 수집/분석하고 콘텐츠로 재생산하는 원스톱 플랫폼을 제공합니다.

### 1.1.1 프로젝트 형태
- **웹 애플리케이션**: Streamlit 기반 대시보드
- **접근 방식**: 웹 브라우저에서 접속하여 사용 (홈페이지/웹사이트와 유사)
- **실행 환경**: 
  - 로컬 실행: 개인 PC에서 `streamlit run app.py`로 실행
  - 클라우드 배포: Streamlit Cloud에 배포하여 인터넷에서 접속 가능
- **사용자 경험**: 일반 웹사이트처럼 브라우저에서 탭을 클릭하여 각 기능 사용

### 1.2 핵심 가치 제안
- **비용 효율성**: 무료 티어 API(Gemini) 활용으로 운영 비용 최소화
- **완전 자동화**: 앱 접속 없이도 매일 자동 수집 및 이메일 발송
- **통합 관리**: 뉴스와 논문을 한 곳에서 관리
- **콘텐츠 재생산**: 수집된 정보를 다양한 형태의 콘텐츠로 자동 변환
- **이메일 알림**: 수집된 헤드라인을 지정한 이메일로 자동 발송
- **웹 기반 접근**: 브라우저만 있으면 어디서나 접속 가능

### 1.3 타겟 사용자
- 심리학 연구자
- 심리상담 전문가
- 심리학 관련 콘텐츠 크리에이터
- 심리학 교육자

---

## 2. 시스템 아키텍처

### 2.1 기술 스택

#### 프론트엔드
- **Streamlit**: Python 기반 웹 UI 프레임워크
- **장점**: 빠른 프로토타이핑, Python 생태계 활용, 무료

#### 백엔드/로직
- **Python 3.9+**: 메인 개발 언어
- **SQLite**: 경량 데이터베이스 (무료, 서버리스)

#### AI 엔진
- **Google Gemini API**: `google-generativeai` 라이브러리
- **모델**: `gemini-1.5-flash` (속도 우선, 무료 티어)
- **대안**: `gemini-1.5-pro` (정확도 우선, 유료)

#### 데이터 수집
- **뉴스**: RSS Feed, Google News API (무료), NewsAPI (무료 티어)
- **논문**: arXiv API, PubMed API (무료)
- **참고**: 커뮤니티 분석(Tab 2)은 제외 (API 접근 어려움으로 인한 제약)

#### 스케줄링
- **별도 수집 스크립트**: 독립 실행 가능한 Python 스크립트
- **Windows 작업 스케줄러**: 로컬 자동 실행
- **GitHub Actions**: 클라우드 자동 실행 (무료)
- **대안**: APScheduler, cron job

#### 이메일 발송
- **Gmail SMTP**: 무료, 간단한 설정
- **Python smtplib**: 내장 라이브러리 (추가 설치 불필요)
- **이메일 템플릿**: HTML 형식으로 헤드라인 요약 발송

### 2.2 시스템 구조

```
┌─────────────────────────────────────────┐
│         Streamlit Frontend              │
│  (Tab 1~4 UI, 검색, 필터, 페이지네이션)  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         Python Backend Logic           │
│  - 데이터 수집 모듈                     │
│  - AI 분석 모듈 (Gemini)                │
│  - 데이터베이스 관리 모듈                │
│  - 스케줄러                              │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         SQLite Database                 │
│  - articles 테이블                      │
│  - pain_points 테이블                   │
│  - papers 테이블                        │
└─────────────────────────────────────────┘
```

---

## 3. 핵심 기능 명세

### 3.1 Tab 1: 사이콜로지 트랜드 레이더

#### 기능 요약
미국과 한국의 심리 관련 뉴스를 수집, 요약, 평가하여 게시하는 탭

#### 상세 기능

**1.1 뉴스 수집**
- **소스**: 
  - 미국: Google News (심리, 마음건강, 뇌과학, 상담 키워드)
  - 한국: 네이버 뉴스, 다음 뉴스 (동일 키워드)
- **주기**: 하루 1회 (새벽 2시 권장)
- **수집 방식**: RSS Feed 또는 API

**1.2 AI 요약 및 분석**
- **Gemini API 호출**:
  - 입력: 뉴스 원문
  - 출력: 
    - 3줄 요약
    - 핵심 키워드 추출 (해시태그용)
    - 전문성 평가 (1~5점)
- **평가 기준**:
  - 과학적 연구 근거 여부
  - 연구 타당도 (표본 크기, 방법론)
  - 선행 연구 인용 여부
  - 일반상식 vs 근거기반 논리

**1.3 데이터 저장**
- **테이블**: `articles`
- **필드**:
  - `id` (PK)
  - `date` (수집일)
  - `category` (심리/마음건강/뇌과학/상담)
  - `title` (제목)
  - `url` (원문 링크)
  - `content_summary` (3줄 요약)
  - `full_text` (원문 전체)
  - `keywords` (JSON 배열)
  - `validity_score` (1~5점)
  - `country` (US/KR)
  - `created_at` (타임스탬프)

**1.4 UI 기능**
- **페이지네이션**: 
  - 최신순 정렬
  - 페이지당 10개 항목
  - 무한 스크롤 또는 페이지 번호
- **검색**: 
  - 키워드 검색 (제목, 요약, 키워드)
  - 실시간 필터링
- **카테고리 필터**: 
  - 해시태그 기반 필터링
  - 다중 선택 가능
- **정렬**: 
  - 날짜순 (최신/오래된순)
  - 평점순 (높은/낮은순)

#### 기술적 고려사항
- **API 제한**: Google News API는 무료 티어 제한 있음 → RSS Feed 우선 고려
- **스크래핑**: robots.txt 준수, 요청 간격 조절 (rate limiting)
- **에러 처리**: 수집 실패 시 재시도 로직, 로그 기록
- **자동화**: 별도 스크립트(`collect_news.py`)로 독립 실행 가능
- **이메일 발송**: 수집 완료 후 지정한 이메일로 헤드라인 요약 자동 발송

---

### 3.2 Tab 2: 아카데믹 아카이브

#### 기능 요약
심리학 관련 논문을 수집, 요약하여 아카이브로 관리

#### 상세 기능

**2.1 논문 수집**
- **소스**:
  - arXiv (심리학 섹션)
  - PubMed (심리학, 상담학)
  - Google Scholar (스크래핑)
- **키워드**: psychology, counseling, correctional psychology, criminal psychology
- **주기**: 주 1회 (매주 월요일)

**2.2 AI 요약**
- **Gemini API 호출**:
  - 입력: 논문 초록 (Abstract)
  - 출력:
    - 연구 목적
    - 연구 방법
    - 주요 결과
    - 시사점
    - 키워드

**2.3 데이터 저장**
- **테이블**: `papers`
- **필드**:
  - `id` (PK)
  - `date` (수집일)
  - `title` (논문 제목)
  - `authors` (저자, JSON 배열)
  - `journal` (저널명)
  - `url` (원문 링크)
  - `abstract` (초록)
  - `summary` (AI 요약, JSON)
  - `keywords` (키워드, JSON 배열)
  - `category` (심리학/상담/교정심리/범죄심리)

**2.4 UI 기능**
- **카드 뷰**: 
  - 논문 제목, 저자, 저널
  - 요약 미리보기
  - 카테고리 태그
- **검색**: 
  - 제목, 저자, 키워드 검색
- **필터**: 
  - 카테고리별 필터
  - 연도별 필터
- **상세 보기**: 
  - 전체 요약
  - 원문 링크
  - 인용 정보

#### 기술적 고려사항
- **API 제한**: arXiv는 무료, PubMed는 무료, Google Scholar는 스크래핑 필요
- **저작권**: 논문 원문은 저장하지 않고 링크만 저장

---

### 3.3 Tab 3: 콘텐츠 팩토리

#### 기능 요약
Tab 1~2에서 선택한 콘텐츠를 다양한 형태로 재생산

#### 상세 기능

**3.1 콘텐츠 선택**
- Tab 1~2에서 체크박스로 다중 선택
- 선택된 항목을 임시 저장소에 저장

**3.2 콘텐츠 생성 타입**

**3.2.1 블로그 포스트**
- **템플릿**:
  - 제목
  - 서론 (선택한 콘텐츠 소개)
  - 본문 (요약 및 분석)
  - 결론 (시사점)
- **Gemini API**: 선택한 콘텐츠를 바탕으로 블로그 포스트 생성

**3.2.2 AI 생성형 릴스 대본**
- **템플릿**:
  - 훅 (첫 3초 주목)
  - 본문 (핵심 내용, 30초 분량)
  - CTA (Call to Action)
- **Gemini API**: 릴스용 대본 생성 (간결하고 임팩트 있게)

**3.2.3 AI 생성형 게시글**
- **템플릿**: 
  - 짧은 인사이트 (200자 내외)
  - 해시태그
- **Gemini API**: SNS용 게시글 생성

**3.2.4 논문 아이디어 포집**
- **템플릿**:
  - 연구 주제 제안
  - 연구 질문
  - 예상 방법론
  - 참고 논문 리스트
- **Gemini API**: 선택한 논문들을 바탕으로 새로운 연구 아이디어 생성

**3.3 UI 기능**
- **템플릿 선택**: 라디오 버튼 또는 체크박스 (중복 선택 가능)
- **생성 버튼**: 선택한 템플릿에 따라 콘텐츠 생성
- **결과 표시**: 
  - 생성된 콘텐츠 미리보기
  - 복사 버튼
  - 다운로드 버튼 (마크다운, 텍스트)

#### 기술적 고려사항
- **토큰 제한**: Gemini API 토큰 제한 고려 (입력 콘텐츠가 많을 경우 요약 후 전달)
- **품질 관리**: 생성된 콘텐츠의 품질 검증 로직 필요

---

## 4. 데이터베이스 스키마

### 4.1 articles 테이블
```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    category TEXT NOT NULL,  -- 'psychology', 'mental_health', 'neuroscience', 'counseling'
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    content_summary TEXT,  -- 3줄 요약
    full_text TEXT,
    keywords TEXT,  -- JSON 배열
    validity_score INTEGER,  -- 1~5
    country TEXT,  -- 'US', 'KR'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_saved BOOLEAN DEFAULT 0  -- Tab 3에서 선택 여부
);
```

### 4.2 pain_points 테이블 (선택 사항 - Tab 2 제외로 인해 미사용)
```sql
CREATE TABLE pain_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    source TEXT NOT NULL,  -- 'reddit', 'nate', 'blind'
    pain_point TEXT NOT NULL,
    frequency INTEGER DEFAULT 1,
    emotion_tag TEXT,  -- 'negative', 'neutral', 'positive'
    severity_score INTEGER,  -- 1~5
    sample_posts TEXT,  -- JSON 배열
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.3 papers 테이블
```sql
CREATE TABLE papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    title TEXT NOT NULL,
    authors TEXT,  -- JSON 배열
    journal TEXT,
    url TEXT NOT NULL UNIQUE,
    abstract TEXT,
    summary TEXT,  -- JSON (목적, 방법, 결과, 시사점)
    keywords TEXT,  -- JSON 배열
    category TEXT,  -- 'psychology', 'counseling', 'correctional', 'criminal'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_saved BOOLEAN DEFAULT 0
);
```

---

## 4.5 이메일 알림 시스템

### 4.5.1 기능 개요
수집된 뉴스와 논문의 헤드라인을 지정한 이메일로 자동 발송합니다.

### 4.5.2 상세 기능

**이메일 발송 시점**
- Tab 1 (뉴스): 매일 수집 완료 후
- Tab 2 (논문): 매주 수집 완료 후

**이메일 내용**
- **제목**: "[PsyInsight] 오늘의 심리 뉴스 헤드라인 (YYYY-MM-DD)"
- **본문**: 
  - 수집된 뉴스 개수
  - 각 뉴스의 제목, 요약(1줄), 링크
  - 평점이 높은 뉴스 우선 표시
  - HTML 형식으로 깔끔하게 정리

**설정**
- 수신 이메일 주소: 환경 변수 또는 설정 파일에서 관리
- 발신 이메일: Gmail SMTP 사용 (무료)
- 발송 조건: 새로 수집된 항목이 있을 때만 발송

### 4.5.3 기술 스택
- **smtplib**: Python 내장 라이브러리
- **email.mime**: 이메일 형식 생성
- **Gmail SMTP**: smtp.gmail.com, 포트 587 (TLS)

### 4.5.4 보안
- Gmail 앱 비밀번호 사용 (일반 비밀번호 대신)
- 환경 변수로 이메일 계정 정보 관리
- `.gitignore`에 이메일 설정 파일 포함

---

## 5. 비기능 요구사항

### 5.1 성능
- **페이지 로딩**: 3초 이내
- **검색 응답**: 1초 이내
- **AI API 호출**: 10초 이내 (타임아웃 설정)

### 5.2 보안
- **API 키 관리**: `.env` 파일 또는 Streamlit Secrets 사용
- **이메일 계정 정보**: 환경 변수로 관리, Gmail 앱 비밀번호 사용
- **데이터 보호**: 개인정보 보호 (필요 시)
- **입력 검증**: SQL Injection 방지 (파라미터화된 쿼리)

### 5.3 확장성
- **데이터베이스**: SQLite → PostgreSQL 전환 가능하도록 설계
- **모듈화**: 각 Tab을 독립 모듈로 설계

### 5.4 사용성
- **반응형 디자인**: 모바일/태블릿 지원 (Streamlit 기본 지원)
- **직관적 UI**: 명확한 네비게이션, 검색/필터 기능

---

## 6. 우선순위 및 마일스톤

### Phase 1: MVP (최소 기능 제품)
- ✅ Tab 1 기본 기능 (뉴스 수집, 요약, 표시)
- ✅ Tab 2 기본 기능 (논문 수집, 요약)
- ✅ 기본 데이터베이스 구조
- ✅ Gemini API 연동

### Phase 2: 확장 기능
- Tab 3 구현 (콘텐츠 팩토리)
- Tab 1 고급 기능 (검색, 필터, 정렬)
- Tab 2 고급 기능 (검색, 필터)

### Phase 3: 고도화
- 스케줄러 자동화
- 성능 최적화
- UI/UX 개선

---

## 7. 리스크 및 대응 방안

### 7.1 기술적 리스크
- **API 제한**: 무료 티어 제한 → 요청 간격 조절, 캐싱 활용
- **스크래핑 차단**: robots.txt 준수, User-Agent 설정, 프록시 사용
- **Gemini API 오류**: 재시도 로직, 폴백 모델 준비

### 7.2 법적 리스크
- **저작권**: 원문 저장 최소화, 링크만 저장
- **개인정보**: 게시글 개인정보 마스킹

### 7.3 운영 리스크
- **서버 다운**: 로컬 실행 환경 → 클라우드 배포 고려 (Streamlit Cloud 무료)
- **데이터 손실**: 정기 백업 (SQLite 파일 백업)

---

## 8. 성공 지표 (KPI)

- **수집량**: 일일 뉴스 20개 이상, 주간 논문 10개 이상
- **사용성**: 검색 성공률 80% 이상
- **콘텐츠 품질**: 사용자 만족도 4점 이상 (5점 만점)
- **비용**: 월 API 비용 $0 (무료 티어 내)

---

**이 PRD는 프로젝트 진행 중 지속적으로 업데이트됩니다.**
