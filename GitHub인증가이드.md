# GitHub 인증 가이드 (2026년 최신)

## 🔐 Personal Access Token 찾는 방법

### 방법 1: GitHub 웹사이트에서 (가장 쉬움)

1. **GitHub 로그인**
   - https://github.com 접속
   - 로그인

2. **Settings 접속**
   - 우측 상단 프로필 사진 클릭
   - **"Settings"** 클릭

3. **Developer settings**
   - 왼쪽 메뉴 맨 아래 **"Developer settings"** 클릭
   - 또는 직접: https://github.com/settings/developers

4. **Personal access tokens**
   - **"Personal access tokens"** 클릭
   - **"Tokens (classic)"** 클릭
   - 또는 직접: https://github.com/settings/tokens

5. **Generate new token**
   - **"Generate new token"** 클릭
   - **"Generate new token (classic)"** 클릭

6. **토큰 설정**
   - **Note**: `PsyInsight Commander` (설명)
   - **Expiration**: 원하는 기간 선택 (90 days 권장)
   - **권한 선택**:
     - ✅ **repo** (전체 체크)
     - ✅ **workflow** (자동화용)
   - **"Generate token"** 클릭

7. **토큰 복사**
   - ⚠️ **한 번만 보이므로 반드시 복사!**
   - `ghp_xxxxxxxxxxxxxxxxxxxx` 형태

---

## 🚀 더 쉬운 방법: GitHub Desktop 사용

### GitHub Desktop 설치
1. https://desktop.github.com/ 접속
2. "Download for Windows" 클릭
3. 설치 후 실행
4. GitHub 계정 로그인

### 사용 방법
1. GitHub Desktop 실행
2. "File" → "Clone repository"
3. "URL" 탭 선택
4. `https://github.com/khb46820305-max/psyinsight-commander.git` 입력
5. "Clone" 클릭
6. 로컬 폴더 선택
7. 파일 복사 후 커밋/푸시

---

## 💡 푸시 시 인증 방법

### 방법 1: Personal Access Token 사용
```bash
git push -u origin main
# Username: khb46820305-max
# Password: [Personal Access Token 붙여넣기]
```

### 방법 2: Git Credential Manager 사용
- Windows에 자동 설치되어 있음
- 첫 푸시 시 브라우저로 로그인 창 열림
- 한 번 로그인하면 자동 저장

### 방법 3: SSH 키 사용 (고급)
- 더 안전하지만 설정이 복잡함

---

## 🔧 현재 상황

저장소는 생성되었지만 비어있습니다. 코드를 푸시해야 합니다.

**다음 중 하나를 선택하세요:**

1. **Personal Access Token 생성** (위 방법 1 참조)
2. **GitHub Desktop 사용** (위 방법 2 참조)
3. **제가 푸시 시도** (인증 창이 뜨면 토큰 입력)

---

## ⚡ 빠른 진행

**Personal Access Token을 생성하셨으면:**
- 토큰을 복사해두세요
- 제가 푸시할 때 비밀번호 대신 토큰을 입력하시면 됩니다

**또는 GitHub Desktop을 사용하시면:**
- 더 쉽게 푸시할 수 있습니다
