---
description: Load a calendar day, show the plan, and start the first unfinished block
argument-hint: [day number]
allowed-tools: Bash(date:*), Bash(./scripts/pane.sh:*)
---
Today's date: !`date +%F`

1. Work out the day. If a number was given ($ARGUMENTS), use it. Otherwise compute it from the Day 1 date and any plan shifts at the top of progress/log.md. Confirm it with me in one line.
2. Read docs/plan/calendar/day-NN.md (two digits, so day-04.md). Read the last entry in progress/log.md to see what was left unfinished.
3. From progress/misses.md, pick up to two items whose "Covered on" is this day or whose re-test is due. Ask them during the warm-up.
4. Show me the day in under 15 lines: the title, why it matters, the blocks with their minutes, and the minimum version for a low-energy day.
5. Start the first unfinished block: tell me exactly the first thing to do, then wait for me.

While I work, go one step at a time through the block's steps. Before moving to the next part, check the previous one yourself (read my pane with ./scripts/pane.sh and run read-only checks in the VM). Ask me the block's "Prove it" questions out loud, and grade them honestly.
