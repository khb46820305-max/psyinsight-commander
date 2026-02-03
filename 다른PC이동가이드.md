# 다른 PC로 프로젝트 이동 가이드

## 📦 이동 방법

### ✅ 폴더 복사만으로는 부족합니다!

다음 단계를 모두 따라야 합니다.

---

## 🚀 단계별 이동 방법

### 1단계: 현재 PC에서 준비

#### 1.1 필요한 파일 확인
- ✅ 모든 프로젝트 파일 (폴더 전체)
- ✅ `.env` 파일 (중요! API 키 포함)
- ❌ `data/psyinsight.db` (선택사항 - 기존 데이터가 필요하면 복사)

#### 1.2 복사할 폴더
```
C:\EX\ 전체 폴더
```

**복사 방법:**
- USB 드라이브 사용
- 클라우드 저장소 (Google Drive, OneDrive 등)
- 네트워크 공유 폴더

---

### 2단계: 새 PC에서 설정

#### 2.1 Python 설치 확인
```bash
python --version
# Python 3.9 이상이어야 합니다
```

Python이 없으면 설치:
- https://www.python.org/downloads/
- 설치 시 "Add Python to PATH" 체크 필수!

#### 2.2 프로젝트 폴더 이동
- 복사한 `EX` 폴더를 원하는 위치에 붙여넣기
- 예: `C:\EX\` 또는 `D:\Projects\EX\`

#### 2.3 라이브러리 설치
```bash
# 프로젝트 폴더로 이동
cd C:\EX

# 필요한 라이브러리 설치
pip install -r requirements.txt
```

#### 2.4 .env 파일 확인
- `.env` 파일이 있는지 확인
- 없으면 `.env.example`을 복사해서 `.env` 만들고 API 키 입력

#### 2.5 데이터베이스 초기화 (선택)
```bash
# 기존 데이터가 필요 없으면 초기화
python -m modules.database
```

---

## ⚠️ 주의사항

### 1. .env 파일은 반드시 복사해야 함
- API 키와 이메일 정보가 들어있음
- 없으면 앱이 작동하지 않음

### 2. data/psyinsight.db (데이터베이스)
- **복사 안 하면**: 빈 데이터베이스로 시작 (기존 뉴스/논문 없음)
- **복사 하면**: 기존 데이터 유지

### 3. Python 버전
- 새 PC에도 Python 3.9 이상 필요
- 버전이 다르면 문제가 될 수 있음

---

## 📋 체크리스트

### 현재 PC에서
- [ ] 프로젝트 폴더 전체 복사
- [ ] `.env` 파일 포함 확인
- [ ] `data/psyinsight.db` 복사 여부 결정

### 새 PC에서
- [ ] Python 설치 확인
- [ ] 프로젝트 폴더 이동
- [ ] `pip install -r requirements.txt` 실행
- [ ] `.env` 파일 확인
- [ ] `python -m modules.database` 실행 (선택)
- [ ] `streamlit run app.py` 테스트

---

## 🔄 더 간단한 방법: GitHub 사용

### 장점
- 코드만 GitHub에 업로드
- 새 PC에서 `git clone`으로 다운로드
- 버전 관리 가능

### 방법
1. 현재 PC: GitHub에 업로드 (`.env` 제외)
2. 새 PC: `git clone`으로 다운로드
3. 새 PC: `.env` 파일 수동 생성
4. 새 PC: `pip install -r requirements.txt`

---

## 💡 추천 방법

### 방법 1: USB/클라우드 복사 (간단)
1. `C:\EX` 폴더 전체 복사
2. 새 PC에 붙여넣기
3. 라이브러리 재설치
4. 완료!

### 방법 2: GitHub 사용 (권장)
1. GitHub에 업로드
2. 새 PC에서 `git clone`
3. `.env` 파일만 수동 생성
4. 라이브러리 설치
5. 완료!

---

## 🎯 빠른 이동 가이드 (요약)

```bash
# 새 PC에서
1. 프로젝트 폴더 복사
2. cd C:\EX
3. pip install -r requirements.txt
4. .env 파일 확인 (없으면 생성)
5. python -m modules.database
6. streamlit run app.py
```

---

**폴더만 복사하면 안 되고, 라이브러리 재설치가 필수입니다!**
