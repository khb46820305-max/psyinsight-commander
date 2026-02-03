# Streamlit Cloud 배포 가이드

## ✅ 1단계 완료: GitHub 푸시

GitHub에 코드가 성공적으로 업로드되었습니다!
- 저장소: https://github.com/khb46820305-max/psyinsight-commander

---

## 🚀 2단계: Streamlit Cloud 배포

### 1. Streamlit Cloud 접속
1. **https://streamlit.io/cloud** 접속
2. **"Sign up"** 또는 **"Log in"** 클릭
3. **"Continue with GitHub"** 클릭
4. GitHub 계정으로 로그인 (khb46820305-max)

### 2. 앱 배포
1. **"New app"** 클릭
2. **Repository**: `khb46820305-max/psyinsight-commander` 선택
3. **Branch**: `main` (기본값)
4. **Main file path**: `app.py` (기본값)
5. **App URL**: 자동 생성됨 (예: `psyinsight-commander.streamlit.app`)
6. **"Deploy!"** 클릭

### 3. Secrets 설정 (환경 변수) - 중요!

배포가 시작되면:
1. 앱 페이지에서 **"⚙️ Settings"** 클릭
2. 왼쪽 메뉴에서 **"Secrets"** 클릭
3. 다음 내용 입력:

```toml
GEMINI_API_KEY = "AIzaSyDvgTdju4cNj-x4MNXV_8Hv2xRRrS8rZ-o"
EMAIL_SENDER = "khb46820305@gmail.com"
EMAIL_PASSWORD = "*apel*0305"
EMAIL_RECEIVER = "khb4682@naver.com"
```

4. **"Save"** 클릭

### 4. 배포 완료 대기
- 배포는 1-2분 정도 걸립니다
- 완료되면 **"View app"** 버튼이 나타납니다
- 클릭하면 웹사이트가 열립니다!

---

## 🌐 배포 완료 후

### 접속 URL
- 예: `https://psyinsight-commander.streamlit.app`
- 또는 Streamlit Cloud에서 제공하는 URL

### 자동 업데이트
- GitHub에 푸시하면 자동으로 재배포됩니다
- 수동 작업 불필요!

---

## ✅ 체크리스트

- [x] GitHub 푸시 완료
- [ ] Streamlit Cloud 로그인
- [ ] 앱 배포
- [ ] Secrets 설정
- [ ] 배포 완료 확인

---

## 🎯 다음 단계

1. Streamlit Cloud에 배포하시면
2. 인터넷 어디서나 접속 가능한 웹사이트가 됩니다!
3. PC 꺼져도 작동합니다 (클라우드에서 실행)

**배포하시면 알려주세요!**
