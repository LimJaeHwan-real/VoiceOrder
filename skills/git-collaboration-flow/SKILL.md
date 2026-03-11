---
name: git-collaboration-flow
description: Use this skill when the user wants help with a team Git or GitHub collaboration workflow: creating a feature branch from main, working and committing on that branch, pushing to origin, preparing or opening a pull request, merging, deleting merged branches, pruning removed remote branches, or syncing local main after teammates merge code. Useful for English or Korean requests about 브랜치, 커밋, 푸시, PR, 머지, 정리, and main sync.
---

# Git Collaboration Flow

## Overview

Use this skill to guide or execute a standard team workflow built around a shared `main` branch and short-lived work branches.

Default assumptions:

- `main` is the integration branch.
- Work should happen on a separate branch.
- Safety and clean handoff matter more than clever Git history edits.

If the repository has a different convention, adapt to the repository instead of forcing new naming or branch rules.

## Workflow

### 1. Inspect before acting

- Confirm the current directory is a Git repository.
- Check the current branch, working tree, and remote setup before creating, switching, or deleting branches.
- If the tree is dirty, preserve the user's changes and explain any risk before switching branches or cleaning up.

### 2. Start work from `main`

- Move to `main` and sync it when that is safe.
- Create a fresh work branch from `main`.
- Prefer the repository's naming convention. If none is visible, use a clear prefix such as `feature/<topic>` or `fix/<topic>`.
- Never do feature work directly on `main` unless the user explicitly asks.

### 3. Implement and verify

- Make the requested changes on the work branch.
- Run relevant tests, lint, or build steps when they exist.
- Summarize what changed, what was verified, and any remaining risk.

### 4. Prepare the handoff

- Commit focused changes with a clear message.
- Push the branch with upstream tracking.
- If GitHub tooling is available, help create or draft the PR. Otherwise provide the exact manual next step.
- Include a short PR-ready summary covering purpose, key changes, verification, and open questions.

### 5. Clean up after merge

- After the branch is merged, switch back to `main`.
- Pull the latest `main`.
- Delete the merged local branch and remote branch when the user wants cleanup or when the workflow clearly includes it.
- Run `git fetch --prune` when teammates deleted remote branches and the local branch list should be refreshed.

## Safety Rules

- Ask before deleting any branch that may still contain unmerged commits or local changes.
- Prefer status checks before cleanup commands.
- If push, pull, or PR creation needs network access or credentials, say so clearly.
- If the directory is not a Git repository, stop early and explain what is missing.

## Communication

Keep the user updated with:

- current branch
- whether `main` is synced
- commands you ran or recommend
- blockers such as dirty state, missing remote, auth, or merge conflicts

When the user wants exact command snippets or Korean phrasing, read [references/git-team-workflow-ko.md](references/git-team-workflow-ko.md).

## Common Trigger Examples

- "main에서 새 브랜치 파서 작업 흐름 잡아줘"
- "기능 브랜치에서 커밋하고 PR 올릴 준비까지 해줘"
- "동료가 머지했으니 내 로컬 main 최신화해줘"
- "삭제된 원격 브랜치 정리하고 싶어"
- "팀 프로젝트 Git 협업 순서를 알려줘"

