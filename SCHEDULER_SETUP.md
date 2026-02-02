# 자동화 스케줄러 설정 가이드

## Windows 작업 스케줄러 설정

### 1. 뉴스 수집 자동화 (매일 새벽 2시)

1. Windows 작업 스케줄러 열기
   - `Win + R` → `taskschd.msc` 입력

2. 기본 작업 만들기
   - 오른쪽 "기본 작업 만들기" 클릭
   - 이름: "PsyInsight 뉴스 수집"
   - 트리거: 매일, 새벽 2시
   - 작업: 프로그램 시작
   - 프로그램: `python`
   - 인수 추가: `C:\EX\collect_news.py`
   - 시작 위치: `C:\EX`

3. 고급 설정
   - "가장 높은 수준의 권한으로 실행" 체크
   - "사용자가 로그온할 때만 실행" 선택

### 2. 논문 수집 자동화 (매주 월요일 새벽 2시)

1. 기본 작업 만들기
   - 이름: "PsyInsight 논문 수집"
   - 트리거: 매주, 월요일, 새벽 2시
   - 프로그램: `python`
   - 인수: `C:\EX\collect_papers.py`
   - 시작 위치: `C:\EX`

## GitHub Actions 설정 (선택)

`.github/workflows/collect_news.yml` 파일 생성:

```yaml
name: Collect News Daily

on:
  schedule:
    - cron: '0 17 * * *'  # 매일 UTC 17시 (한국시간 새벽 2시)
  workflow_dispatch:  # 수동 실행 가능

jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python collect_news.py
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          EMAIL_SENDER: ${{ secrets.EMAIL_SENDER }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
          EMAIL_RECEIVER: ${{ secrets.EMAIL_RECEIVER }}
```

## 환경 변수 확인

스크립트 실행 전 `.env` 파일이 올바르게 설정되었는지 확인:

```env
GEMINI_API_KEY=your_key
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=app_password
EMAIL_RECEIVER=receiver@example.com
```

## 테스트

수동으로 스크립트 실행하여 테스트:

```bash
python collect_news.py
python collect_papers.py
```
