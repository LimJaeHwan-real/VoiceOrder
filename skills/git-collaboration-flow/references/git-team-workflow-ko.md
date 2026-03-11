# Git Team Workflow

이 문서는 팀 프로젝트에서 자주 쓰는 Git 협업 흐름의 정확한 명령 예시를 모아 둔 참고 자료다.

## 기본 6단계

### 1. 브랜치 생성

`main`에서 최신 코드를 받은 뒤 새 작업 브랜치를 만든다.

```bash
git checkout main
git pull origin main
git checkout -b feature/cool-feature
```

팀이 `git switch`를 쓰면 다음처럼 바꿔도 된다.

```bash
git switch main
git pull origin main
git switch -c feature/cool-feature
```

### 2. 커밋 작업

작업 브랜치에서 수정한 뒤 필요한 파일만 스테이징하고 커밋한다.

```bash
git add .
git commit -m "Add cool feature"
```

가능하면 커밋은 작은 단위로 유지한다.

### 3. 푸시

작업 브랜치를 원격에 올린다.

```bash
git push -u origin feature/cool-feature
```

### 4. PR 생성

GitHub 웹사이트에서 Pull Request를 만들거나, `gh`가 있으면 CLI로 만든다.

```bash
gh pr create --base main --head feature/cool-feature
```

PR에는 목적, 주요 변경점, 테스트 결과, 리뷰 포인트를 짧게 적는다.

### 5. 머지

리뷰가 끝나고 문제가 없으면 `main`에 머지한다.

스킬은 기본적으로 머지 전까지 준비를 돕고, 실제 머지는 사용자가 명시적으로 요청할 때만 진행한다.

### 6. 정리

머지 후에는 로컬과 원격 브랜치를 정리한다.

```bash
git checkout main
git pull origin main
git branch -d feature/cool-feature
git push origin --delete feature/cool-feature
```

## 자주 있는 상황

### 동료가 브랜치를 삭제했을 때

내 로컬 브랜치 목록에서 없어진 원격 브랜치를 정리한다.

```bash
git fetch --prune
```

### 동료가 `main`에 코드를 합쳤을 때

내 로컬 `main`을 최신 상태로 맞춘다.

```bash
git checkout main
git pull origin main
```

## 작업 전 확인

브랜치 생성, 전환, 삭제 전에 아래를 먼저 확인한다.

```bash
git status
git branch --show-current
git remote -v
```

워킹 트리가 더럽거나 아직 커밋하지 않은 변경이 있으면 먼저 사용자에게 알리고 안전하게 진행한다.

## 적용 팁

- 저장소 기본 브랜치가 `master`면 `main` 대신 `master`를 사용한다.
- 브랜치 prefix는 팀 규칙에 맞춰 `feature/`, `fix/`, `chore/` 등으로 바꾼다.
- 정리 전에 로컬 변경사항이나 미머지 커밋이 없는지 먼저 확인한다.
