# Contributing

이 저장소는 `main` 기준 Git 협업 흐름을 사용합니다.

## 기본 흐름

1. `main`을 최신 상태로 동기화합니다.
2. 작업 브랜치를 생성합니다.
3. 필요한 변경만 커밋합니다.
4. 원격 브랜치로 push 합니다.
5. `main` 대상으로 PR을 생성합니다.

예시:

```powershell
git checkout main
git pull origin main
git checkout -b feature/short-topic
git add <changed-files>
git commit -m "Add short topic"
git push -u origin feature/short-topic
```

## 브랜치 규칙

- 기능 추가: `feature/<topic>`
- 버그 수정: `fix/<topic>`
- 문서/정리: `chore/<topic>`

## 커밋 규칙

- 한 커밋에는 한 가지 목적만 담습니다.
- 커밋 메시지는 짧고 동작 중심으로 작성합니다.
- 예시: `Add voice order confirmation summary`

## PR 규칙

- PR 본문에는 목적, 주요 변경점, 검증 결과를 적습니다.
- UI 변경이 있으면 스크린샷 또는 확인 방법을 함께 남깁니다.
- 데이터베이스 변경이 있으면 재현 절차를 함께 적습니다.

## 작업 전 확인

브랜치 전환이나 정리 전에 아래를 먼저 확인합니다.

```powershell
git status
git branch --show-current
git remote -v
```

워킹 트리에 미커밋 변경이 있으면 먼저 커밋하거나 별도 브랜치로 보호한 뒤 진행합니다.
