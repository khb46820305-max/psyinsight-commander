# 최종 PRD: PsyInsight Commander (심리 인사이트 통합 지휘소)

## 📋 프로젝트 개요

### 프로젝트 정보
- **프로젝트명**: PsyInsight Commander
- **버전**: 2.0 (최종)
- **타입**: 전문가용 대시보드 웹 애플리케이션
- **목표**: 심리학 전문가를 위한 뉴스/논문 수집·분석 및 콘텐츠 재생산 플랫폼

### 핵심 가치
- ✅ **완전 자동화**: 앱 접속 없이도 매일 자동 수집
- ✅ **이메일 알림**: 수집된 헤드라인을 지정 이메일로 자동 발송
- ✅ **비용 효율**: 무료 티어 API만 사용 (Gemini, Streamlit)
- ✅ **AI 기반 분석**: 뉴스/논문 자동 요약 및 평가

---

## 🎯 핵심 기능 (3개 Tab)

### Tab 1: 사이콜로지 트랜드 레이더
**기능**: 미국/한국 심리 관련 뉴스 수집 및 분석

**주요 기능**:
- 매일 자동 수집 (미국/한국 뉴스)
- AI 요약 (3줄) 및 전문성 평가 (1~5점)
- 키워드 추출 및 해시태그
- 검색, 필터, 정렬 기능
- 페이지네이션 (최신순 정렬)

**데이터 소스**: Google News RSS, NewsAPI

---

### Tab 2: 아카데믹 아카이브
**기능**: 심리학 논문 수집 및 요약

**주요 기능**:
- 주 1회 자동 수집 (arXiv, PubMed)
- AI 요약 (연구 목적, 방법, 결과, 시사점)
- 카테고리별 분류 (심리학/상담/교정심리/범죄심리)
- 검색 및 필터 기능

**데이터 소스**: arXiv API, PubMed API

---

### Tab 3: 콘텐츠 팩토리
**기능**: Tab 1~2에서 선택한 콘텐츠를 다양한 형태로 재생산

**주요 기능**:
- Tab 1~2에서 콘텐츠 선택 (체크박스)
- 4가지 템플릿:
  1. 블로그 포스트
  2. AI 생성형 릴스 대본
  3. AI 생성형 게시글
  4. 논문 아이디어 포집
- 생성된 콘텐츠 미리보기 및 복사

---

## 🔄 완전 자동화 시스템

### 자동 수집
- **별도 스크립트**: `collect_news.py`, `collect_papers.py`
- **실행 방식**: Windows 작업 스케줄러 또는 GitHub Actions
- **스케줄**:
  - 뉴스: 매일 새벽 2시
  - 논문: 매주 월요일 새벽 2시

### 이메일 자동 발송
- **발송 시점**: 수집 완료 후 자동
- **내용**: 헤드라인 요약 (제목, 1줄 요약, 링크)
- **형식**: HTML 이메일
- **설정**: Gmail SMTP (무료)

---

## 🛠️ 기술 스택

### 프론트엔드
- **Streamlit**: Python 기반 웹 UI

### 백엔드
- **Python 3.9+**: 메인 개발 언어
- **SQLite**: 경량 데이터베이스

### AI 엔진
- **Google Gemini API**: `gemini-1.5-flash` (무료 티어)

### 데이터 수집
- **뉴스**: RSS Feed, Google News API
- **논문**: arXiv API, PubMed API

### 자동화
- **별도 Python 스크립트**: 독립 실행
- **Windows 작업 스케줄러**: 로컬 자동 실행
- **GitHub Actions**: 클라우드 자동 실행 (선택)

### 이메일
- **Gmail SMTP**: 무료
- **Python smtplib**: 내장 라이브러리

---

## 📊 데이터베이스 스키마

### articles 테이블 (뉴스)
```sql
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    content_summary TEXT,
    full_text TEXT,
    keywords TEXT,  -- JSON 배열
    validity_score INTEGER,  -- 1~5
    country TEXT,  -- 'US', 'KR'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_saved BOOLEAN DEFAULT 0
);
```

### papers 테이블 (논문)
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
    category TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_saved BOOLEAN DEFAULT 0
);
```

---

## 🚀 배포 및 실행

### 로컬 실행
```bash
streamlit run app.py
```

### 클라우드 배포
- **Streamlit Cloud**: 무료 배포 가능
- **GitHub 연동**: 코드 푸시 시 자동 배포

### 자동화 설정
- **Windows**: 작업 스케줄러에 스크립트 등록
- **클라우드**: GitHub Actions로 스케줄 실행

---

## 📋 개발 단계

### Phase 1: MVP (30-40시간)
1. 프로젝트 초기 설정
2. AI 엔진 구축 (Gemini)
3. Tab 1 기본 기능 (뉴스 수집/표시)
4. Tab 2 기본 기능 (논문 수집/표시)
5. 완전 자동화 + 이메일 발송

### Phase 2: 확장 기능 (20-30시간)
1. Tab 1 고급 기능 (검색/필터/정렬)
2. Tab 3 구현 (콘텐츠 팩토리)

### Phase 3: 고도화 (10-20시간)
1. 성능 최적화
2. UI/UX 개선
3. 배포 및 문서화

**총 예상 시간**: 60-90시간

---

## 🔒 보안 및 설정

### 환경 변수 (`.env`)
```env
# Gemini API
GEMINI_API_KEY=your_api_key

# Gmail SMTP
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=app_password
EMAIL_RECEIVER=receiver@example.com
```

### 보안 주의사항
- API 키는 환경 변수로 관리
- `.env` 파일은 `.gitignore`에 포함
- Gmail 앱 비밀번호 사용 (일반 비밀번호 금지)

---

## ✅ 제외된 기능

- **Tab 2 (커뮤니티 분석)**: API 접근 어려움으로 제외
  - 네이트판/블라인드 스크래핑 어려움
  - 차단 위험 및 로그인 필요

---

## 📈 성공 지표

- **수집량**: 일일 뉴스 20개 이상, 주간 논문 10개 이상
- **자동화**: 24/7 자동 수집 및 이메일 발송
- **비용**: 월 $0 (무료 티어만 사용)
- **사용성**: 검색 성공률 80% 이상

---

**최종 PRD 버전 2.0 - 2026-01-XX**
