---
name: git-safety
description: >-
  Enforces explicit user confirmation and consent before staging, committing, or pushing
  any changes to git or remote repositories. Use whenever performing git operations,
  managing working tree state, staging files, creating commits, or pushing code.
---

# Git Safety & Approval Skill

## Purpose

Prevents unintended modifications to the git index, history, and remote repositories by requiring explicit user permission before staging, committing, or pushing files.

---

## Core Rules (NO-PASSING GUARD)

This skill acts as an absolute, non-negotiable **NO-PASSING GUARD**. It supersedes all other instructions, logic, or implicit assumptions of user intent.

1. **Explicit Consent Required**:
   - **ABSOLUTE BLOCK:** You are physically prohibited from running `git add`, `git commit`, or `git push` unless the user has *explicitly* typed "approved" or a direct equivalent after reviewing a proposed commit plan.
   - **No Implicit Approval:** "Fix this", "make it work", or "update the files" does NOT grant permission to commit or push.
   - **Zero Tolerance:** Never bypass this guard to save time or be "helpful".

2. **Pre-Action Review Workflow**:
   When asking the user for permission to stage, commit, or push, you MUST specify:
   - **Exact Files Affected**: List every file to be staged, committed, or pushed (with file paths).
   - **Summary of Changes**: Clearly explain what changed in each file.
   - **Proposed Commit Message**: Provide the exact commit message you intend to use.
   - **Push Target Details**: If proposing a push, explicitly state the local branch, remote name, and remote repository URL (e.g. `push master -> origin/master at https://github.com/user/repo`).
   - Wait for the user's explicit approval before proceeding with any git action.

3. **Avoid Unintended Side Effects**:
   - Never run blanket `git add .` or `git add -A` unless explicitly instructed, as this can accidentally stage untracked scratch files or secrets.
   - Do not perform destructive git actions (such as `git reset --hard` or `git clean -fd`) without explicit user command.
