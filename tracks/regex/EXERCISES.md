# Regex Practice: Real-World grep / sed / awk

All commands run **from inside `data/`**. Check yourself with:

```bash
cd ~/regex-practice
./check.sh 7 "grep -nE '...' docs/README.md"
```

The checker ignores leading and trailing whitespace and `./` path prefixes. It also ignores line order, except where an exercise says **order matters**.
Every dataset has **deliberate traps**. If your first attempt passes, ask yourself why the obvious version would have failed.

Send me your answers (one command per exercise is fine). I'll check each one, point out edge cases it misses, and show more idiomatic, faster or more robust versions.

Files: `logs/access.log` (nginx), `logs/auth.log` (sshd), `logs/app.log` (app + Python tracebacks), `users.csv`, `ips.txt`, `deps.txt`, `passwords.txt`, `pods.txt` (`kubectl get pods -A`), `config/` (`.env`, k8s YAML), `src/` (JS/Python), `docs/README.md`.

---

## Level 1: Intermediate

**1. Count server errors.** How many requests in `logs/access.log` returned a **5xx** status? Output only the number.
*Concepts: anchoring to field context, `-c`.*

**2. Who is POSTing?** Print the unique client IPs that made **POST** requests, one per line.
*Concepts: matching inside a quoted field, `-o`, `sort -u`.*

**3. Credential-stuffing usernames.** From `logs/auth.log`, take only the sshd lines of the form `Invalid user <name> from ...`, *not* the `Failed password for invalid user ...` lines. Print the **top 3** usernames as `count name`, highest first. **Order matters.**
*Concepts: case sensitivity, extraction with `\K` or `sed`, the `sort | uniq -c | sort -rn` idiom.*

**4. Tech-debt markers.** Recursively list every `TODO`, `FIXME` or `HACK` marker in `src/`, in grep's `file:line:content` format, with paths starting `src/`. Markers are **uppercase, standalone words**. `TODOS`, `FIXMEs`, `todoList` and lowercase `todo` don't count.
*Concepts: `-r`, `-n`, word boundaries.*

**5. Real errors only.** Print the lines from `logs/app.log` whose **log level** is `ERROR` or `FATAL`, excluding the `[healthcheck]` component. A message that merely *contains* the word ERROR doesn't count.
*Concepts: position-aware matching, piping `-v`, `-F` for literal brackets.*

**6. Empty config values.** Under `config/`, but only in `*.env` files, find variables assigned an **empty** value: nothing, only whitespace, `""` or `''`. Commented lines don't count. Output `file:line:content`.
*Concepts: `--include`, `^…$` anchoring, POSIX classes, shell quoting of quotes.*

**7. Doubled words.** Find lines in `docs/README.md` containing an accidentally repeated word (case-insensitive, e.g. "The the"). Output `line:content`. Watch out for `the theme` and `test testall`.
*Concepts: backreferences, `\b` on both sides.*

---

## Level 2: Advanced

**8. Valid IPv4 only.** Print the lines of `ips.txt` that are **exactly** a valid IPv4 address: 4 octets, each 0–255, **no leading zeros**, nothing else on the line.
*Concepts: numeric ranges in regex, alternation, quantified groups.*

**9. Brute-force sources.** From `logs/auth.log`, print the IPs with **3 or more** `Failed password` events, including ones for invalid users. IPs only, one per line.
*Concepts: optional groups, `\K` / lookbehind, aggregation.*

**10. Strict email validation.** Print the `email` column of `users.csv` for rows whose email is valid under these rules:
- local part: letters, digits, `_ % + -` and dots, but **no leading dot and no `..`**
- exactly one `@`
- domain: one or more dot-separated labels plus a TLD of 2+ letters

The whole field must be valid, so a valid *substring* inside a bad email doesn't count.
*Concepts: anchoring a regex to a CSV field, repeated groups.*

**11. Slow endpoints report.** Using `logs/access.log`, print every request with `rt` **≥ 1 second** as `<rt> <METHOD> <path>`, sorted slowest first, e.g. `5.000 POST /api/payments`. **Order matters.** Do the reformatting with a regex (sed/perl/awk), and compare numbers with regex rather than arithmetic.
*Concepts: capture groups, `sed -nE 's/…/…/p'`.*

**12. Date normalization.** Output the whole of `users.csv` with every `MM/DD/YYYY` date (two-digit month 01–12, two-digit day 01–31) rewritten as `YYYY-MM-DD`. Leave anything else, such as `1/5/2025` or `13/01/2025`, untouched. **Order matters** (it's the full file).
*Concepts: backreference reordering, range validation.*

**13. Secret scanner.** Scan `config/` and `src/` for leaked secrets, printing `file:line:match` (only the matched secret):
- AWS access key: `AKIA` + **exactly** 16 uppercase letters or digits
- GitHub token: `ghp_` + **exactly** 36 alphanumerics
- AcmePay live key (a made-up provider): `ak_live_` + 24 or more alphanumerics
- PEM private key header: `-----BEGIN <optional type> PRIVATE KEY-----` (not PUBLIC)

*Concepts: `-o` with multiple alternatives, exact lengths, false-positive control.*

**14. Semantic versions.** Print the lines of `deps.txt` whose version is valid **SemVer 2.0**: `MAJOR.MINOR.PATCH` with no leading zeros, an optional `-prerelease` (dot-separated non-empty identifiers) and an optional `+build`. No `v` prefix.
*Concepts: nested optional groups, precise repetition.*

---

## Level 3: Expert

**15. Multi-condition, any order.** From `logs/app.log`, print just the `request_id` value of lines that have **`status=500` exactly** *and* **`latency_ms` ≥ 1000**. The key=value pairs may appear in **any order**, and `status=5000` is not 500.
*Concepts: PCRE lookaheads, `\K`, numeric thresholds by digit count.*

**16. Live debug statements.** Find `console.log(` calls in `src/**/*.js` that are **not commented out**: ignore lines starting with `//` or `/*`, but a trailing comment after real code is fine. Output `file:line:content`.
*Concepts: negative lookahead at line start.*

**17. Password policy in one regex.** Print the lines of `passwords.txt` that meet **all** of these, using a **single** regex:
12+ chars · ≥1 uppercase · ≥1 lowercase · ≥1 digit · ≥1 non-alphanumeric · **no character repeated 3+ times in a row**.
*Concepts: stacked lookaheads, negative lookahead with a backreference.*

**18. Traceback attribution.** Every Python traceback in `logs/app.log` ends with an exception line such as `KeyError: 'uid'`. For each one, print `<id> <ExceptionType>`, where `<id>` is the `request_id` *or* `job_id` value from the most recent log line before the traceback. Example: `f004 KeyError`.
*Concepts: stateful matching across lines (awk `match()`/`RSTART`, or perl/`grep -z`).*

**19. PII redaction.** Output the whole of `users.csv` with the email column (column 3) masked as `<first char>***@<everything after the LAST @>`, e.g. `alice.khan@example.com` → `a***@example.com` and `gus@@example.com` → `g***@example.com`. Other columns stay untouched. **Order matters.**
*Concepts: greedy vs. negated classes, field-bounded matching in sed.*

**20. Unhealthy pods.** From `pods.txt`, print `namespace/name` for every pod that is unhealthy:
- STATUS is anything other than `Running` or `Completed`, **or**
- RESTARTS ≥ 10, **or**
- STATUS is `Running` but not all containers are ready (READY `x/y` with x ≠ y)

*Concepts: awk field regex (`~`), splitting `x/y`, coercing `14 (2h ago)`.*

---

### Stretch goals (no checker, discuss with me)
- Re-do #3, #9 and #13 with `rg` (ripgrep) and compare speed and syntax on a large file (`for i in $(seq 5000); do cat logs/access.log; done > /tmp/big.log`).
- Solve #15 **without** PCRE (ERE + two greps, or awk). Which is more readable?
- Solve #18 with `grep -Pzo` (whole-file mode) instead of awk.
