# GitHub 푸시 방법 (쉬운 방법)

## 🎯 가장 쉬운 방법: GitHub Desktop 사용

### 1단계: GitHub Desktop 설치
1. **https://desktop.github.com/** 접속
2. **"Download for Windows"** 클릭
3. 설치 후 실행

### 2단계: GitHub 계정 로그인
1. GitHub Desktop 실행
2. **"Sign in to GitHub.com"** 클릭
3. **"Sign in with your browser"** 클릭
4. 브라우저에서 GitHub 로그인
5. 권한 승인

### 3단계: 저장소 클론
1. GitHub Desktop에서
2. **"File"** → **"Clone repository"**
3. **"URL"** 탭 선택
4. URL 입력: `https://github.com/khb46820305-max/psyinsight-commander.git`
5. **"Local path"**: `C:\EX` (또는 다른 폴더)
6. **"Clone"** 클릭

### 4단계: 파일 복사 및 푸시
1. `C:\EX` 폴더의 모든 파일을 클론된 폴더로 복사
2. GitHub Desktop에서 변경사항 확인
3. **"Commit to main"** 클릭
4. 메시지 입력: `Initial commit`
5. **"Push origin"** 클릭
6. 완료!

---

## 🔐 Personal Access Token 찾는 방법 (상세)

### GitHub 웹사이트에서

1. **https://github.com** 접속 및 로그인

2. **우측 상단 프로필 사진 클릭** → **"Settings"**

3. **왼쪽 메뉴 맨 아래로 스크롤**
   - **"Developer settings"** 클릭
   - 또는 직접: **https://github.com/settings/developers**

4. **"Personal access tokens"** 클릭
   - **"Tokens (classic)"** 클릭
   - 또는 직접: **https://github.com/settings/tokens**

5. **"Generate new token"** 클릭
   - **"Generate new token (classic)"** 클릭

6. **설정**
   - **Note**: `PsyInsight Commander`
   - **Expiration**: `90 days` (또는 원하는 기간)
   - **권한**: 
     - ✅ **repo** (전체 체크)
   - **"Generate token"** 클릭

7. **토큰 복사**
   - ⚠️ **한 번만 보이므로 반드시 복사!**
   - `ghp_xxxxxxxxxxxxxxxxxxxx` 형태

---

## 💻 명령어로 푸시 (토큰 사용)

### 1. Git credential 초기화
```bash
git credential-manager-core erase
```

### 2. 푸시 시도
```bash
git push -u origin main
```

### 3. 인증 정보 입력
- **Username**: `khb46820305-max`
- **Password**: [Personal Access Token 붙여넣기]

---

## 🚀 추천: GitHub Desktop 사용

**가장 쉽고 안전한 방법:**
- ✅ 브라우저로 자동 로그인
- ✅ 토큰 불필요
- ✅ 시각적으로 확인 가능
- ✅ 충돌 해결 쉬움

---

## 📝 현재 상황

저장소는 생성되었지만 비어있습니다.
코드를 푸시해야 Streamlit Cloud에 배포할 수 있습니다.

**다음 중 선택:**
1. **GitHub Desktop 사용** (가장 쉬움) ⭐ 추천
2. **Personal Access Token 생성** (위 방법 참조)
3. **제가 다시 푸시 시도** (인증 정보 필요)
