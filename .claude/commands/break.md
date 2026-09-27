---
description: Plant a hidden fault in lab-ubuntu for me to diagnose, like a live troubleshooting round
argument-hint: [topic, e.g. disk, dns, systemd, memory, network, permissions, tls]
---
1. Snapshot first: `incus snapshot create laptop:lab-ubuntu pre-break-<timestamp>`.
2. Pick a realistic fault for $ARGUMENTS (or today's calendar topic if empty), at my current level. Prefer faults that test items in progress/misses.md.
3. Plant it as root without spoiling it: write the fault script, base64-encode it, and run `echo <base64> | base64 -d | incus exec laptop:lab-ubuntu -- bash -s`. Never show the fault in plain text in the chat.
4. Save the fault, the root cause and how to verify the fix in progress/.faults/<timestamp>.md. Don't read it out.
5. Tell me only what a user would report (for example "the site returns 502 since this morning"), give me 25 minutes, and say "Go".
6. When I say I'm done, verify the fix with your saved check. Debrief: the root cause, the first signal I should have noticed, and the fastest command to find it. Score it: solved or not, time taken, hints used. Log it in progress/log.md, add any gap to progress/misses.md, and offer to restore the snapshot.
