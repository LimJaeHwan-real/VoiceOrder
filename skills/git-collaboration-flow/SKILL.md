---
name: git-collaboration-flow
description: Use this skill when the user wants help with a standard team Git or GitHub collaboration workflow built around `main`: create a work branch from `main`, commit on that branch, push to `origin`, prepare or open a pull request, merge, clean up merged branches, prune removed remote branches, or sync local `main` after teammates merge code. Useful for English or Korean requests about 브랜치 생성, 커밋, 푸시, PR 생성, 머지, 브랜치 정리, `git fetch --prune`, and `git pull origin main`.
---

# Git Collaboration Flow

Follow the repository's existing branch naming or review rules if they differ from the default flow below.

## Core Flow

Use this exact order unless the repository uses a different process:

1. Create a branch from `main`.
2. Make changes and commit on that branch.
3. Push the branch to `origin`.
4. Create or prepare a PR targeting `main`.
5. Merge after review.
6. Clean up merged branches and refresh local refs.

Read [references/git-team-workflow-ko.md](references/git-team-workflow-ko.md) when the user wants exact command snippets or Korean guidance.

## Execute Safely

Before running branch or cleanup commands:

- Confirm the directory is a Git repository.
- Check the current branch, working tree status, and configured remotes.
- Preserve uncommitted user changes. Do not switch branches or delete anything blindly when the tree is dirty.
- Prefer `main` as the base branch only when the repository actually uses `main`.

## Run The Standard Steps

### 1. Start from `main`

- Switch to `main`.
- Pull the latest `main` when network access and credentials are available.
- Create a fresh work branch such as `feature/<topic>`.
- Avoid doing feature work directly on `main` unless the user explicitly asks.

### 2. Commit on the work branch

- Stage only the intended changes.
- Make focused commits with clear messages.
- Run the smallest useful verification before or after committing.

### 3. Push the branch

- Push with upstream tracking, typically `git push -u origin <branch>`.
- If push fails because of auth, remote, or network issues, explain the blocker clearly.

### 4. Prepare the PR

- Open or draft a PR from the work branch into `main`.
- If GitHub CLI is available, use it. Otherwise provide the exact manual PR step.
- Summarize purpose, key changes, verification, and review points in a short PR-ready note.

### 5. Merge

- Treat merge as the post-review step.
- Do not merge on behalf of the user unless they explicitly ask and the repository workflow allows it.

### 6. Clean up

- After merge, switch back to `main`.
- Pull the latest `main`.
- Delete the merged local branch with `git branch -d <branch>`.
- Delete the merged remote branch with `git push origin --delete <branch>` when the user wants full cleanup.
- Run `git fetch --prune` when teammates already removed remote branches and the local branch list needs refreshing.

## Special Cases

- When a teammate merged code into `main`, sync with `git checkout main` and `git pull origin main`.
- When a teammate deleted a remote branch, refresh local refs with `git fetch --prune`.
- When the repository uses `git switch`, mirror the same flow with `git switch main` and `git switch -c <branch>`.
- When branch naming differs from `feature/<topic>`, follow the team's convention.

## Guardrails

- Ask before deleting any branch that may still contain unmerged commits or local changes.
- Prefer status checks before cleanup commands.
- If push, pull, or PR creation needs network access or credentials, say so clearly.
- If the directory is not a Git repository, stop early and explain what is missing.

## Common Trigger Examples

- "main에서 새 브랜치 파서 작업 흐름 잡아줘"
- "기능 브랜치에서 커밋하고 PR 올릴 준비까지 해줘"
- "동료가 머지했으니 내 로컬 main 최신화해줘"
- "삭제된 원격 브랜치 정리하고 싶어"
- "팀 프로젝트 Git 협업 순서를 알려줘"
