---
description: Verify that the current block is really done, from evidence rather than my word
allowed-tools: Bash(./scripts/pane.sh:*)
---
1. Work out which block I'm on from our conversation and the day file.
2. Gather evidence yourself: read my pane with ./scripts/pane.sh, and run read-only checks in the VM, for example `incus exec laptop:lab-ubuntu -- systemctl show ...`, `cat /proc/...`, `df`, `ss`. Don't change anything.
3. Compare the evidence with the block's "Done when" line.
4. Ask me one or two "why" questions about what I just did. I may answer by voice.
5. Give the verdict: done, or not yet with exactly what's missing. If it's done, add the evidence (date and what I showed) to the matching row in progress/skills-ledger.md.
