# Drills: Word Boundaries and Friends (after Exercise 4)

Run commands from `data/` and check them from the repo root:

```bash
cd ~/regex-practice
./check.sh 4a "grep ... drills/queries.sql"
```

New files: `drills/queries.sql`, `drills/services.txt`, `drills/svc.log`, `drills/deploy.sh`.

**The rule behind it all:** a *word character* is `[A-Za-z0-9_]`. Everything else (space, `-`, `.`, `(`, `:`, `/`) is a non-word character. A word boundary `\b` sits between a word character and a non-word character (or the start or end of the line). `-w` checks for that boundary on **both** sides of the whole match.

That's all `-w` knows. It has no idea what a "service name", an "IP address" or a "command" is. Most drills below test whether you remember that.

---

## Part A: Harden the concept

**4a. Which queries touch `users`?** Count the lines in `drills/queries.sql` that mention the table **`users`** exactly, not `users_archive` or `user_roles`. Output just the number.
> Think: is `_` a boundary? Does `users.id` count as a mention of `users`?

**4b. Exact service name.** In `drills/services.txt`, print the IP (column 2) of every service whose name is **exactly** `shop-api`. Not `shop-api-canary`, `legacy-shop-api`, `shop-api-v2` or `shop-apiserver`.
> Try `grep -w shop-api` first and see what it prints. Why does it fail? What *is* `-` to the regex engine?

**4c. Exact IP.** Print the line for IP address **exactly** `10.0.1.1`, and nothing for `10.0.1.10` or `10.0.141.5`.
> There are **two** separate traps here. `grep '10.0.1.1'` falls into both. Fixing one still leaves you with 2 lines.

---

## Part B: Combine with earlier concepts

**4d. Real log levels (+ position, + case).** From `drills/svc.log`, print the lines whose **level** (the 3rd field) is `WARN` or `ERROR` in **any case**. `WARNING` isn't WARN, `ERRORS` isn't ERROR, and a `WARN` inside the message doesn't count.
> Combines: `-i` (concept 2), alternation (concept 4), word boundary (concept 3), and **context anchoring** from exercises 1 and 2.

**4e. Marker leaderboard (+ counting pipeline).** Across `src/`, count how many times each marker (`TODO`, `FIXME`, `HACK`) appears and print `count marker`, highest first. **Order matters.**
> Combines exercise 4 with exercise 3's pipeline. You need two new flags: one that prints **only the match** and one that **hides file names**. Look them up in `grep --help`.

**4f. Which files? (+ `-l`)** List only the **file names** under `src/` that contain the whole word `TODO`, one per line, with no line content.
> Bonus (unchecked): what does `-L` do? Use it to find `.js` files with **no** `HACK`, using `--include='*.js'`.

**4g. Dangerous SQL (+ anchoring, + `-v`).** In `drills/queries.sql`, find `DELETE` or `UPDATE` statements that have **no `WHERE` clause**, in any case. Ignore the commented line (`-- ...`) and the `INSERT` whose *string value* contains `DELETE FROM users`. Output `line:content` (use `-n`).
> Two greps in a pipeline is fine. Watch out for the indented `  update Orders ...` line.

---

## Part C: Knowing when, and when not, to use `-w`

**4h. Destructive commands in a deploy script.** In `drills/deploy.sh`, find lines that **actually run** one of these:
- `rm -rf`
- `kubectl delete`
- `terraform destroy`
- `git push --force`, but **not** `--force-with-lease`, which is the safe one

Comments, `echo` strings, `kubectl-delete-helper` and `terraform plan -destroy` don't count. Leading indentation is allowed. Output `line:content`.
> Try `grep -w -- '--force'` first and look at line 15. Why does `-w` fail with flags? What should come **after** `--force` instead?

### Judgment questions (no checker, answer to me in your own words)

For each one, choose **`-w`**, **`\b` placed by hand**, **`-F`**, **`^`/`$` anchoring**, or **awk field comparison**, and say **why**:

1. Find the Kubernetes pod named exactly `api` in `kubectl get pods` output, where pods like `api-7d9f-x2k` and `gateway-api` also exist.
2. Find the variable `count` in Python code, but not `count_total`, `account`, `discount` or `self.counter`.
3. Search a log for the literal text `user[admin].role` (a config key containing brackets and dots).
4. Find words that **start** with `auth` (`auth`, `authz`, `authenticate`) but not `oauth`.
5. Count HTTP 404 responses in an nginx log, where `404` can also appear in URLs and byte counts.

---

### Cheat sheet you'll have earned after this
| Need | Tool |
|---|---|
| Whole word, word = letters, digits and `_` | `-w` or `\bword\b` |
| A boundary on **one** side only ("starts with") | `\bword` |
| A name containing `-` or `.` (hostnames, k8s names, flags, IPs) | `-w` is **unreliable**. Use exact field comparison (awk `$1=="x"`) or explicit delimiters |
| Pattern full of `. [ ] * $` that should be literal | `-F` (fixed string), can combine with `-w` |
| Value in a known column | awk `$N == "..."` beats any regex |
| Output only the match / no file names / names only / names without a match | `-o` / `-h` / `-l` / `-L` |
