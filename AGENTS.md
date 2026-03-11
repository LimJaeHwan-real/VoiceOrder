# AGENTS.md

이 문서는 `C:\Users\home\workspace\jungle\codex`에서 작업하는 에이전트를 위한 저장소별 가이드입니다.
설명은 한국어로 유지하고, 에이전트가 직접 따라야 하는 핵심 규칙은 영어로 작성합니다.

## 프로젝트 개요

- 이 저장소는 Python 기반의 키오스크 관련 앱/유틸리티 작업 공간입니다.
- 현재 확인된 주요 파일:
  - `app.py`: 메인 애플리케이션 진입점으로 보이는 파일
  - `init_db.py`: 데이터베이스 초기화 스크립트
  - `kiosk.db`: 로컬 SQLite 데이터베이스 파일
  - `templates/`: 템플릿 리소스
  - `skills/`: 보조 리소스 또는 확장 작업용 디렉터리

## Core Rules

- Read the existing code before making assumptions.
- Prefer minimal, targeted changes.
- Follow the current code style and structure.
- Do not revert user changes unless explicitly asked.
- Validate the affected area after making changes whenever possible.

## 작업 원칙

- 먼저 현재 코드 구조를 읽고, 추측보다 기존 구현을 우선합니다.
- 요청된 작업에 필요한 최소 범위만 수정합니다.
- 새로운 패턴을 도입하기 전에 기존 구현과 스타일을 맞춥니다.
- 관련 파일이 있으면 함께 확인해 변경 영향 범위를 좁힙니다.

## Python Rules

- Keep implementations simple and readable.
- Avoid over-engineering in small scripts.
- Add comments only when the logic is not obvious.
- Prefer small function boundaries when they improve clarity.

## Python 작업 지침

- 작은 스크립트 저장소이므로 과도한 추상화보다 읽기 쉬운 구현을 우선합니다.
- 복잡한 로직에만 짧은 주석을 추가하고, 자명한 코드에는 주석을 남발하지 않습니다.
- 함수 분리는 가독성에 도움이 될 때만 적용합니다.

## Database Rules

- Do not edit `kiosk.db` directly.
- Make schema or seed changes through code.
- Prefer reproducible initialization steps.

## 데이터베이스 주의사항

- `kiosk.db`는 바이너리 산출물이므로 직접 편집하지 않습니다.
- 스키마나 초기 데이터 변경이 필요하면 `init_db.py` 또는 관련 초기화 로직을 수정합니다.
- DB 변경은 가능한 한 재생성 가능한 절차로 관리합니다.

## Template Rules

- Check user-facing text and rendering flow when editing templates.
- Reuse existing patterns before adding new hardcoded values.

## 템플릿 및 리소스

- `templates/` 변경 시 사용자에게 보이는 문자열, 폼 필드, 렌더링 흐름의 영향을 함께 확인합니다.
- 하드코딩된 경로 또는 문구를 추가하기 전에 기존 패턴을 먼저 확인합니다.

## File Rules

- Add new files only when necessary.
- Avoid large refactors unless the user requests them.
- Do not regenerate large binary artifacts without a reason.

## 파일 작업 규칙

- 새 파일은 꼭 필요한 경우에만 추가합니다.
- 대규모 구조 변경은 사용자가 명시적으로 요청한 경우에만 진행합니다.
- 큰 바이너리 파일은 특별한 이유 없이 다시 생성하지 않습니다.

## Validation Rules

- Run the smallest useful verification for the change.
- Report clearly when verification was not performed.
- Check Python syntax when Python files were edited.

## 검증

- 변경 범위에 맞는 최소 검증을 우선 수행합니다.
- Python 파일을 수정했다면 가능한 범위에서 문법 오류를 확인합니다.
- 검증을 하지 못했다면 그 이유를 명확하게 남깁니다.

## Response Rules

- Keep the final explanation short and clear.
- Mention the important file paths you changed.
- Surface risks or follow-up items explicitly.

## 응답 방식

- 결과 설명은 짧고 명확하게 작성합니다.
- 중요한 파일 경로와 검증 여부를 함께 공유합니다.
- 추가 확인이 필요한 위험 요소가 있으면 숨기지 않고 바로 알립니다.
