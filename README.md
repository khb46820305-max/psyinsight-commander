# 🧠 PsyInsight Commander

심리학 전문가를 위한 통합 대시보드 웹 애플리케이션

> **💡 새로운 AI 세션 시작 시**: [프로젝트맥락.md](./프로젝트맥락.md) 파일을 먼저 읽으세요!

## 📋 프로젝트 개요

PsyInsight Commander는 심리학 관련 뉴스와 논문을 자동으로 수집, 분석하고, 다양한 형태의 콘텐츠로 재생산하는 플랫폼입니다.

### 핵심 기능
- ✅ **완전 자동화**: 앱 접속 없이도 매일 자동 수집
- ✅ **이메일 알림**: 수집된 헤드라인을 지정 이메일로 자동 발송
- ✅ **AI 기반 분석**: 자동 요약 및 전문성 평가
- ✅ **콘텐츠 재생산**: 블로그, 릴스 대본, 게시글 등으로 변환

## 🚀 빠른 시작 (3단계)

### 1단계: 의존성 설치
```bash
pip install -r requirements.txt
```

### 2단계: 환경 변수 설정
`.env` 파일을 생성하고 다음 내용 입력:
```env
GEMINI_API_KEY=your_api_key
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECEIVER=receiver@example.com
```

**Gemini API 키 발급:** https://makersuite.google.com/app/apikey

### 3단계: 앱 실행
```bash
# 데이터베이스 초기화 (첫 실행 시)
python -m modules.database

# 앱 실행
streamlit run app.py
```

**자세한 사용 방법:** `사용가이드.md` 파일 참조

## 📁 프로젝트 구조

```
psyinsight-commander/
├── app.py                 # 메인 Streamlit 앱
├── requirements.txt       # 의존성 목록
├── .env.example          # 환경 변수 예시
├── .gitignore            # Git 제외 파일
├── modules/               # 모듈 패키지
│   ├── __init__.py
│   ├── ai_engine.py      # AI 엔진 (Gemini)
│   ├── news_collector.py # 뉴스 수집
│   ├── paper_collector.py # 논문 수집
│   ├── database.py        # 데이터베이스 관리
│   └── email_sender.py   # 이메일 발송
├── data/                  # 데이터베이스 저장소
└── config/               # 설정 파일
```

## 🛠️ 개발 상태

### ✅ 완료
- [x] 프로젝트 초기 구조 생성
- [x] 기본 모듈 파일 생성
- [x] 데이터베이스 스키마 설계

### ✅ 완료
- [x] AI 엔진 구축 (Gemini API)
- [x] 뉴스 수집 모듈
- [x] 논문 수집 모듈
- [x] 이메일 발송 모듈
- [x] 완전 자동화 스크립트
- [x] 콘텐츠 팩토리

### 📋 예정 (선택사항)
- [ ] 고급 검색/필터 기능
- [ ] 성능 최적화
- [ ] UI/UX 개선

## 📚 문서

### 🎯 시작하기
- **[프로젝트맥락.md](./프로젝트맥락.md)** ⭐ **새로운 AI 세션 시작 시 필수 읽기**
- [사용가이드.md](./사용가이드.md) - 사용 방법
- [배포가이드.md](./배포가이드.md) - 외부 배포 방법

### 📋 기획 및 설계
- [최종 PRD](./FINAL_PRD.md) - 전체 기능 명세
- [작업계획서](./FINAL_WORK_PLAN.md) - Iteration별 작업
- [핵심 요약](./FINAL_SUMMARY.md) - 기능 요약

### 🔧 기술 문서
- [이메일 설정 가이드](./EMAIL_SETUP_GUIDE.md)
- [자동화 가이드](./AUTOMATION_GUIDE.md)
- [스케줄러 설정](./SCHEDULER_SETUP.md)
- [다른 PC 이동 가이드](./다른PC이동가이드.md)

## 📝 라이선스

이 프로젝트는 교육 목적으로 제작되었습니다.

---

**개발 중인 프로젝트입니다. 기능이 계속 추가됩니다.**
