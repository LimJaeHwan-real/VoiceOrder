# AGENTS.md

이 문서는 `C:\Users\home\workspace\jungle\codex`에서 작업하는 에이전트를 위한 저장소 전용 작업 가이드입니다.
설명과 배경 맥락은 한국어로 정리하고, 에이전트가 직접 따라야 하는 핵심 규칙과 트리거 문장은 영어로 유지합니다.

## 프로젝트 개요

- 이 저장소는 Python 기반 키오스크 앱과 관련 유틸리티를 다루는 작업 공간입니다.
- 현재 기준으로 중요한 파일은 다음과 같습니다.
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

- 먼저 현재 코드 구조와 흐름을 읽고, 추측보다 기존 구현을 우선합니다.
- 요청된 작업에 필요한 최소 범위만 수정합니다.
- 새로운 패턴을 도입하기 전에는 기존 구현과 스타일에 맞추는 것을 우선합니다.
- 관련 파일이 있다면 함께 확인해 변경 영향 범위를 좁힙니다.

## Python Rules

- Keep implementations simple and readable.
- Avoid over-engineering in small scripts.
- Add comments only when the logic is not obvious.
- Prefer small function boundaries when they improve clarity.

## Python 작업 지침

- 작은 스크립트 중심 저장소이므로 과도한 추상화보다 읽기 쉬운 구현을 우선합니다.
- 복잡한 로직에만 짧은 주석을 추가하고, 자명한 코드에는 주석을 남발하지 않습니다.
- 함수 분리는 가독성에 실제로 도움이 될 때만 적용합니다.

## Database Rules

- Do not edit `kiosk.db` directly.
- Make schema or seed changes through code.
- Prefer reproducible initialization steps.

## 데이터베이스 주의사항

- `kiosk.db`는 바이너리 산출물이므로 직접 편집하지 않습니다.
- 스키마나 초기 데이터 변경이 필요하면 `init_db.py` 또는 관련 초기화 로직을 수정합니다.
- DB 변경은 가능한 한 재현 가능한 초기화 절차로 관리합니다.

## Template Rules

- Check user-facing text and rendering flow when editing templates.
- Reuse existing patterns before adding new hardcoded values.

## 템플릿 및 리소스

- `templates/`를 수정할 때는 사용자에게 보이는 문자열, 폼 필드, 렌더링 흐름 영향을 함께 확인합니다.
- 하드코딩된 경로나 문구를 추가하기 전에는 기존 패턴을 먼저 확인합니다.

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
## Skills

아래 섹션은 이 세션에서 사용할 수 있는 스킬과 사용 규칙을 정리한 영역입니다.
설명 문장은 이해를 돕기 위한 안내이고, 실제로 따를 규칙 문장은 영어 원문을 기준으로 해석합니다.

A skill is a set of local instructions to follow that is stored in a `SKILL.md` file. Below is the list of skills that can be used. Each entry includes a name, description, and file path so you can open the source for full instructions when using a specific skill.
### Available skills
- `git-collaboration-flow`: Use this skill when the user wants help with a standard team Git or GitHub collaboration workflow built around `main`: create a work branch from `main`, commit on that branch, push to `origin`, prepare or open a pull request, merge, clean up merged branches, prune removed remote branches, or sync local `main` after teammates merge code. Useful for English or Korean team requests about branch creation, commits, pushes, PR creation, merges, branch cleanup, `git fetch --prune`, and `git pull origin main`. (file: `C:/Users/home/.codex/skills/git-collaboration-flow/SKILL.md`)
- `vercel-deploy`: Deploy applications and websites to Vercel. Use when the user requests deployment actions like "deploy my app", "deploy and give me the link", "push this live", or "create a preview deployment". (file: `C:/Users/home/.codex/skills/vercel-deploy/SKILL.md`)
- `skill-creator`: Guide for creating effective skills. This skill should be used when users want to create a new skill (or update an existing skill) that extends Codex's capabilities with specialized knowledge, workflows, or tool integrations. (file: `C:/Users/home/.codex/skills/.system/skill-creator/SKILL.md`)
- `skill-installer`: Install Codex skills into `$CODEX_HOME/skills` from a curated list or a GitHub repo path. Use when a user asks to list installable skills, install a curated skill, or install a skill from another repo (including private repos). (file: `C:/Users/home/.codex/skills/.system/skill-installer/SKILL.md`)
- `slides`: Build, edit, render, import, and export presentation decks with the preloaded `@oai/artifact-tool` JavaScript surface through the artifacts tool. (file: `C:/Users/home/.codex/skills/.system/slides/SKILL.md`)
- `spreadsheets`: Build, edit, recalculate, import, and export spreadsheet workbooks with the preloaded `@oai/artifact-tool` JavaScript surface through the artifacts tool. (file: `C:/Users/home/.codex/skills/.system/spreadsheets/SKILL.md`)
### How to use skills
- Discovery: The list above is the skills available in this session (name + description + file path). Skill bodies live on disk at the listed paths.
- Trigger rules: If the user names a skill (with `$SkillName` or plain text) OR the task clearly matches a skill's description shown above, you must use that skill for that turn. Treat requests such as "깃허브에 올려줘" or "GitHub에 올려줘" as matching `git-collaboration-flow` with the default expectation of branch push -> PR creation -> PR merge -> main-branch reflection when repository permissions and workflow allow it. Treat requests such as "브랜치 파서 PR까지 해줘", "PR 준비해줘", "main에 반영되게 진행해줘", or "push 해줘" as matching `git-collaboration-flow` as well unless the user explicitly asks for a different workflow. Automatic deployment after a push to `main` is handled by the GitHub Actions workflow at `.github/workflows/vercel-production.yml`, not by chaining `vercel-deploy` automatically. Treat requests about manual deployment, preview deployment, production deployment outside the workflow, or deployment URL retrieval as matching `vercel-deploy`. Multiple mentions mean use them all. Do not carry skills across turns unless re-mentioned.
- GitHub collaboration default: Even if `git-collaboration-flow` is unavailable, follow this repository default directly from `AGENTS.md`: branch push -> PR creation -> PR merge -> main-branch reflection. When the user says "깃허브에 올려줘" or equivalent, treat the request as aiming for that full path unless repository permissions, branch protection, required reviews, or missing credentials block a later step.
- GitHub collaboration execution rules:
  1) Check the current branch, working tree, and remotes before branch switching, merging, or cleanup.
  2) Preserve user changes. If the tree is dirty, stash or otherwise isolate only what is necessary before changing branches.
  3) Push the intended work branch to `origin`.
  4) Create or prepare a PR targeting `main`.
  5) Merge the PR into `main` when the repository workflow and user intent allow it.
  6) Sync local `main` or the dedicated main worktree after merge when needed.
  7) Let `.github/workflows/vercel-production.yml` handle automatic deployment after `main` changes land.
- GitHub collaboration fallback: If PR creation or merge cannot be completed automatically because GitHub CLI is unavailable, branch protection blocks merge, or remote permissions are missing, still finish the highest safe step and clearly report the exact next manual step.
- Missing/blocked: If a named skill isn't in the list or the path can't be read, say so briefly and continue with the best fallback.
- How to use a skill (progressive disclosure):
  1) After deciding to use a skill, open its `SKILL.md`. Read only enough to follow the workflow.
  2) When `SKILL.md` references relative paths (e.g., `scripts/foo.py`), resolve them relative to the skill directory listed above first, and only consider other paths if needed.
  3) If `SKILL.md` points to extra folders such as `references/`, load only the specific files needed for the request; don't bulk-load everything.
  4) If `scripts/` exist, prefer running or patching them instead of retyping large code blocks.
  5) If `assets/` or templates exist, reuse them instead of recreating from scratch.
- Coordination and sequencing:
  - If multiple skills apply, choose the minimal set that covers the request and state the order you'll use them.
  - Announce which skill(s) you're using and why (one short line). If you skip an obvious skill, say why.
- Context hygiene:
  - Keep context small: summarize long sections instead of pasting them; only load extra files when needed.
  - Avoid deep reference-chasing: prefer opening only files directly linked from `SKILL.md` unless you're blocked.
  - When variants exist (frameworks, providers, domains), pick only the relevant reference file(s) and note that choice.
- Safety and fallback: If a skill can't be applied cleanly (missing files, unclear instructions), state the issue, pick the next-best approach, and continue.
