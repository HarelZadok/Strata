# Strata Project Guidelines

## Local & Unrelated Files
All temporary, scratch, debug, exploratory, or non-production files must be saved in the `./.local/` directory (e.g. `./.local/scripts/`, `./.local/scratch/`, `./.local/notes/`). This directory is ignored by git in `.gitignore`. Do not create unrelated or scratch files in the repository root or within packages/services.

## Git Safety & Commit Approval
Do not stage (`git add`), commit (`git commit`), or push (`git push`) any changes to Git without explicit confirmation and instruction from the user. 
When asking for permission to commit or push:
- Specify exactly which files will be affected (list every staged, modified, or untracked file).
- Summarize the specific changes made in each file.
- Propose the exact commit message.
- For push operations, specify the local branch, remote name, and target repository.
Always await explicit user consent before executing any git modification commands.
