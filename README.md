# Voice Kiosk

Flask와 SQLite로 만든 음성 주문 키오스크 데모입니다. 브라우저의 Web Speech API로 음성을 텍스트로 받아 주문 후보를 만들고, 결제 버튼으로 주문 내역을 저장합니다.

## 구성 파일

- `app.py`: Flask 서버와 API
- `init_db.py`: SQLite 테이블 생성 및 샘플 메뉴 시드
- `templates/index.html`: 맥도날드 스타일 키오스크 UI
- `kiosk.db`: 로컬 SQLite 데이터베이스 파일
- `requirements.txt`: Python 의존성

## 요구 사항

- Python 3.10 이상
- Chrome 또는 Edge 같은 Web Speech API 지원 브라우저
- 마이크 사용 가능 환경

## 실행 방법

1. 가상환경 생성

```powershell
python -m venv .venv
```

2. 가상환경 활성화

```powershell
.\.venv\Scripts\Activate.ps1
```

3. 패키지 설치

```powershell
pip install -r requirements.txt
```

4. 데이터베이스 초기화

```powershell
python init_db.py
```

5. 서버 실행

```powershell
python app.py
```

6. 브라우저 접속

```text
http://localhost:5000
```

## 사용 방법

1. 메뉴를 직접 담거나 `음성으로 주문하기` 버튼을 누릅니다.
2. 처음 실행 시 브라우저에서 마이크 권한을 `허용`합니다.
3. 예시 문장처럼 메뉴명과 수량을 말합니다.
4. 장바구니가 업데이트되면 `결제하기`를 눌러 주문을 저장합니다.

## 마이크 권한 팁

- `http://localhost:5000` 또는 `http://127.0.0.1:5000` 에서 여는 것을 권장합니다.
- 주소창 왼쪽 자물쇠 아이콘에서 `마이크`를 `허용`으로 바꿔야 합니다.
- 이미 `차단`을 눌렀다면 설정을 바꾼 뒤 새로고침해야 합니다.

## API 요약

- `GET /api/menus`: 메뉴 목록 조회
- `POST /api/order/voice`: 음성 텍스트를 주문 후보로 변환
- `POST /api/order/confirm`: 주문 저장

## 참고

현재 음성 주문 파싱은 단순 문자열 매칭 방식입니다. 이후에는 메뉴 별 별칭 확장, 숫자 표현 개선, 주문 내역 조회 API, 관리자 화면 등을 추가하기 좋습니다.

## Git 협업 흐름

이 저장소는 `main` 기준 브랜치 협업을 권장합니다.

- 작업 가이드: `CONTRIBUTING.md`
- PR 템플릿: `.github/PULL_REQUEST_TEMPLATE.md`

## 배포 자동화

`main` 브랜치에 푸시되면 GitHub Actions가 Vercel `production` 배포를 실행합니다.

동작 파일:

- `.github/workflows/vercel-production.yml`

필수 GitHub Actions secret:

- `VERCEL_TOKEN`: Vercel 개인 또는 팀 토큰

이 저장소는 이미 Vercel 프로젝트에 연결되어 있어 워크플로 안에 `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`가 고정되어 있습니다.
