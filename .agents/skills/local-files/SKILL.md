---
name: local-files
description: >-
  Directs all unrelated, temporary, scratch, experimental, or user-specific files to be saved
  within the project's ./.local/ directory. Use whenever creating scratch scripts, temporary test
  utilities, local debug notes, benchmark experiments, or non-production artifacts that should not pollute
  the repository.
---

# Local Files & Scratch Workspace Skill

## Purpose

The `Strata` repository maintains a clean, production-oriented monorepo layout. All non-core, exploratory, scratch, or temporary files generated during development, debugging, or experimentation must reside in `./.local/` at the repository root.

The `./.local/` folder is registered in [`.gitignore`](../../.gitignore) and is never committed or pushed to remote repositories.

---

## Directory Conventions

When generating local or unrelated files, place them in standard subfolders inside `./.local/`:

- **`./.local/scripts/`**: One-off diagnostic scripts, ad-hoc automation runs, exploratory tools.
- **`./.local/scratch/`**: Temporary test snippets, throwaway code, prototypes.
- **`./.local/notes/`**: Task logs, scratchpads, planning documents, manual test notes.
- **`./.local/dumps/`**: Screen capture dumps, OCR raw outputs, test audio/video recordings.
- **`./.local/data/`**: Local test databases, mock payloads, experimental inputs/outputs.

---

## Guidelines for the Agent

1. **Check or Create `./.local/` Subdirectory**:
   Before creating any non-production or scratch file, ensure the target path resides within `./.local/` (e.g. `f:/Strata/.local/...`). Create the directory if it does not already exist.

2. **Never Place Scratch Files in Root or Source Directories**:
   Do not create ad-hoc test scripts or logs directly in `services/`, `packages/`, or the repository root.

3. **Running Local Scripts**:
   Execute local scripts within the project context using `uv run`:
   ```powershell
   uv run python ./.local/scripts/my_test.py
   ```

4. **Verify Ignored Status**:
   Confirm that any new files inside `./.local/` are not tracked by Git.
