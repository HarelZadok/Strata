# Strata Project Guidelines

## Local & Unrelated Files
All temporary, scratch, debug, exploratory, or non-production files must be saved in the `./.local/` directory (e.g. `./.local/scripts/`, `./.local/scratch/`, `./.local/notes/`). This directory is ignored by git in `.gitignore`. Do not create unrelated or scratch files in the repository root or within packages/services.

## Git Safety & Commit Approval
Do not stage (`git add`), commit (`git commit`), or push (`git push`) any changes to Git without explicit confirmation and instruction from the user. Always present the proposed changes, list affected files, and await user consent before executing any git modification commands.
