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

## Core Rules

1. **Explicit Consent Required**:
   - **Never** run `git add` without the user explicitly asking to stage files.
   - **Never** run `git commit` without the user explicitly approving the commit and reviewing the commit message.
   - **Never** run `git push` without the user explicitly directing a push to remote.

2. **Pre-Action Review Workflow**:
   Before proposing any commit or push:
   - Run and display `git status --short` to inspect what files are modified or untracked.
   - Summarize the exact changes intended to be committed.
   - Propose the commit message to the user.
   - Wait for the user's explicit approval before proceeding.

3. **Avoid Unintended Side Effects**:
   - Never run blanket `git add .` or `git add -A` unless explicitly instructed, as this can accidentally stage untracked scratch files or secrets.
   - Do not perform destructive git actions (such as `git reset --hard` or `git clean -fd`) without explicit user command.
