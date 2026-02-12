# GitHub 동기화 가이드 (PC A ↔ PC B)

## 📍 현재 상태
- ✅ Git 초기화 완료
- ✅ GitHub 저장소 연결됨: `https://github.com/khb46820305-max/psyinsight-commander.git`
- ✅ .gitignore 설정 완료 (민감한 정보 자동 제외)

---

## 🖥️ PC A (현재 PC) - 작업 후 업로드

### 작업을 마치고 업로드할 때:

```bash
# 1. 변경된 파일 확인
git status

# 2. 변경된 파일 모두 추가
git add .

# 3. 커밋 (저장 확정)
git commit -m "작업 내용 설명"

# 4. GitHub에 업로드 (Push)
git push origin main
```

**또는 Cursor에서:**
- 좌측 하단의 Git 아이콘 클릭
- 변경된 파일 체크 후 "Commit" 버튼
- "Push" 버튼 클릭

---

## 🖥️ PC B (다른 PC) - 처음 불러오기

### 1단계: GitHub에서 프로젝트 클론 (한 번만)

```bash
# Cursor 터미널에서 (Ctrl+`)
cd 원하는_폴더_경로
git clone https://github.com/khb46820305-max/psyinsight-commander.git
cd psyinsight-commander
```

**또는 Cursor에서:**
- `File` → `Clone Repository`
- 주소 입력: `https://github.com/khb46820305-max/psyinsight-commander.git`
- 저장할 폴더 선택

### 2단계: 필요한 라이브러리 설치

```bash
pip install -r requirements.txt
```

---

## 🔄 PC B - 매일 작업 시작할 때

### PC A에서 작업한 내용을 가져오기 (Pull):

```bash
git pull origin main
```

**또는 Cursor에서:**
- 좌측 하단 Git 아이콘 클릭
- "Pull" 버튼 클릭

---

## 🔄 PC B - 작업 후 업로드

### PC A와 동일하게:

```bash
git add .
git commit -m "작업 내용 설명"
git push origin main
```

---

## ⚠️ 주의사항

### 1. 충돌 방지
- **PC A에서 작업 중이면 PC B에서 작업하지 마세요**
- 작업 전에 항상 `git pull` 먼저 실행
- 같은 파일을 동시에 수정하면 충돌 발생 가능

### 2. 작업 순서 (권장)
```
PC A: 작업 → Commit → Push
PC B: Pull → 작업 → Commit → Push
PC A: Pull → 작업 → Commit → Push
```

### 3. 민감한 정보는 자동 제외됨
- `.env` 파일 (API 키 등)
- `data/*.db` (데이터베이스 파일)
- `__pycache__/` (임시 파일)

이 파일들은 `.gitignore`에 설정되어 있어 자동으로 제외됩니다.

---

## 🆕 새 저장소를 만들고 싶다면

### Step 1: GitHub에서 새 저장소 생성
1. GitHub.com 로그인
2. 우측 상단 `+` → `New repository`
3. Repository name: `MIND_MAGIC` (또는 원하는 이름)
4. **Private** 체크 (중요!)
5. `Create repository` 클릭

### Step 2: 기존 연결 제거 후 새 연결
```bash
# 기존 연결 제거
git remote remove origin

# 새 저장소 연결 (GitHub에서 복사한 주소 사용)
git remote add origin https://github.com/사용자명/MIND_MAGIC.git

# 업로드
git push -u origin main
```

---

## 📝 자주 쓰는 명령어

```bash
# 현재 상태 확인
git status

# 변경된 파일 확인 (간단히)
git diff

# 최근 커밋 내역 보기
git log --oneline -10

# 원격 저장소 확인
git remote -v

# 최신 버전 가져오기
git pull origin main

# 업로드
git push origin main
```

---

## ✅ 체크리스트

### PC A (현재)
- [x] Git 초기화 완료
- [x] GitHub 연결 완료
- [x] 첫 업로드 완료

### PC B (다른 PC)
- [ ] GitHub에서 클론
- [ ] 라이브러리 설치 (`pip install -r requirements.txt`)
- [ ] 테스트 실행 (`streamlit run app.py`)
- [ ] Pull/Push 테스트

---

## 🆘 문제 해결

### "Permission denied" 에러
→ GitHub 인증 필요. Cursor에서 GitHub 로그인하거나 Personal Access Token 사용

### "Already up to date" 메시지
→ 정상입니다. 이미 최신 버전입니다.

### "Merge conflict" 에러
→ 같은 파일을 동시에 수정했을 때 발생. 충돌 해결 필요.

---

**💡 팁:** 매일 작업 시작 전에 `git pull`, 작업 끝날 때 `git push`만 기억하시면 됩니다!
