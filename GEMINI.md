# Strata Project Guidelines

## Local & Unrelated Files
All temporary, scratch, debug, exploratory, or non-production files must be saved in the `./.local/` directory (e.g. `./.local/scripts/`, `./.local/scratch/`, `./.local/notes/`). This directory is ignored by git in `.gitignore`. Do not create unrelated or scratch files in the repository root or within packages/services.

## Git Safety & Commit Approval (NO-PASSING GUARD)
This is an absolute, non-negotiable hard block.
Do not stage (`git add`), commit (`git commit`), or push (`git push`) any changes to Git without explicit confirmation and instruction from the user. "Fix this" or "Make it work" does NOT grant implicit permission to commit.

When asking for permission to commit or push:
- Specify exactly which files will be affected (list every staged, modified, or untracked file).
- Summarize the specific changes made in each file.
- Propose the exact commit message.
- For push operations, specify the local branch, remote name, and target repository.
**ABSOLUTE BLOCK:** Always await explicit user consent (e.g. "approved") before executing any git modification commands. Never bypass this to be helpful.
