# COP ref (written in COP; machine-dense twin = standalone/COP-rules.md (installed into the host's agent-instructions file); edit both together; this file NOT auto-loaded, /cop reads it)
Origin: github.com/liranc6/Agents-Communication-Protocol
Principle: compression scales w/ shared context; cost unit = tokens. Unlisted case -> does reader share this file+glossary?

## Tiers
- T0 human-read (chat commit PR report user-handoff log review code comments data cfg memory-metadata): normal prose, zero COP codes/symbols. Exception: user explicitly asks radio/terse ("like radio comm", "skip grammar if implied", "use symbols to save tokens") -> chat replies to that user telegraphic + ops/symbols until told otherwise. Still never forward raw peer (T1/T2) shorthand -> rewrite for user.
- T3 agent-only docs (INSIGHTS, specs, runbooks, task/handoff/state files; only agents read and write them): dense COP, not T0 prose. Put a file-local Legend at top. One writer per shared file; others send it entries. If any human reads or maintains the doc, or you are unsure who reads it -> T0.
- T1 own thinking, scratch/tmp, memory body: max dense. Think in COP: in the reasoning, notes and plans you control (visible thinking, scratch, own plans), write fragments from the first token (obs|inf|?, `x -> y`, keep logic words), NOT a full-sentence draft then compress. Hidden or host-fixed reasoning is out of scope. A plan shown to a human is T0. Only human-read output is rewritten as prose.
- T2 any agent<->agent msg (subagent, workflow agent, teammate, other session): dense. Peer starts cold -> state goal+why, constraints, paths, done-criteria, known facts. Hook adds PEER; set N, + only glossary terms used. Never make peer read COP/glossary files; define the terms used inline. Need raw content -> ask explicitly.

## PEER block
- Source hooks/peer.txt (standalone install: ~/.claude/cop/peer.txt); edit wording only there.
- PreToolUse hook peer_hook.py (plugin: hooks/hooks.json; standalone: ~/.claude/settings.json; matcher Agent|Task; fail-open) appends peer.txt to Agent prompts lacking "COP:"; default N=15. State N yourself when different.
- Workflow agent() prompts NOT hooked -> paste peer.txt manually.
- Peer told: telegraphic, keep every step + logic word (NOT if unless only all none because); short tool inputs (relative paths, batched probes); exact numbers/paths/cmds/errors, negation NOT; probe before load, filter at source; no re-read/re-run seen output; no nested subagents unless told; stay in scope; human-read files = prose; blocked/unsure -> stop+report; tag obs|inf|?, list NOT verified; reply <=N lines STATUS/RESULT/EVIDENCE/OPEN.

## Input
- Probe first (grep -n, wc -l, ls, git diff --stat) -> read ranges (offset/limit); whole file only if <=200 lines or truly needed.
- Filter at source (jq head tail grep -c, quiet flags); noisy build/test `| tail -20`.
- No re-read unchanged, no re-run seen.
- Wide sweep (many files/dirs) -> subagent summary, not raw dump.
- Tool inputs = output tokens (expensive): relative paths from cwd, no repeated long abs paths, batch probes in 1 call, no decorative echo separators.

## Process
- T1/T2: cite tool output, don't paraphrase back. To a human, state the finding in prose.
- Decide once: no re-deriving established facts, no re-litigating settled choices, no narrating options not taken.
- Long task -> F1..Fn one-line fact ledger in scratch, cite by id (survives compaction).

## Write (T1/T2)
1. Telegraphic. Drop grammar when meaning inferable: articles, copulas, aux verbs, pronouns, filler connectives; full sentences -> fragments, lists, `x -> y`. Drop hedges, pleasantries, restating. Keep every reasoning step + logic words (NOT if unless only all none because before after): they carry meaning, not grammar.
2. Common words whole (1 token); abbreviate only long ids/multi-word phrases; no ad-hoc slash/unicode shorthand (extra tokens; listed codes and tags are fine).
3. Exact: numbers paths ids cmds quotes errors thresholds. Negation NOT.
4. Pointer>copy (path:line sha run-id url).
5. Delta vs last known state only (reader with prior state; cold reader gets full state).
6. Tag obs|inf|?; inf->obs only after check.
7. Cold reader could parse 2 ways -> spell out.
8. Before irreversible/outward act (delete push send deploy publish) -> state intent in plain full words, then get confirmation unless user already authorised that act.
9. T1/T2 feeding T0 -> rewrite as prose; never forward peer shorthand to user.

## Codes
- Status: ACK; WIP; DONE; BLOCK(reason); Q? question; FYI; NI need info; ND need decision; CFM confirm; PTAL please take a look (review req); ETA; SITREP situation summary; TP/TF test pass/fail; VRF verified; UNV unverified.
- Ops: -> then/input to; => yields; @ at; ! urgent; + add; - remove; ^ update/push; ~ approx; != differs; $ budget/limit.
- Line: STATUS|target|result|evidence|next  ex: DONE|runner.py:120 retry fix|TP 14/14|obs|next PR

## Glossary
- <project root>/.cop/shorthand.md, `T=exp` entries; link it from the project's agent-instructions file (CLAUDE.local.md `@.cop/shorthand.md`, AGENTS.md, ...); create both on first add.
- Add if >=3 uses in session, expansion >=3 tokens, unambiguous in project. Cap 30; prune unused. No ad-hoc abbrev outside COP/glossary.

## Densify existing text
- No separate "extra efficient" mode: this file = the one standing level, every read.
- Find repeats w/ script first, not eyeball: n-gram counter over tokenized words, n=2..6, flag count>=3-4.
- Term specific to one doc/campaign -> file-local Legend at top of that file, NOT global shorthand.md (project-wide, capped 30).
- Never abbrev inside quoted/literal content (scenario/config strings) or fixed defined label (named status value), even if abbrev'd elsewhere in doc.
- Proper nouns/model names/ids stay full always (pointer, not acronym), regardless of repeat count.
- macOS/BSD sed: `\b` fails in default BRE -> use `-E` + explicit `[^a-zA-Z]` boundary classes. After bulk replace check substring collisions (mechanism->mech must not hit "mechanical").

## Measure
`python3 tools/cop_stats.py --main [--split "YYYY-MM-DD HH:MM"]` (run from a clone of the repo; standalone install: ~/.claude/cop/cop_stats.py; UTC). Rule not paying its load -> cut.

## Roles and handoffs (optional)
- Role prefix `ROLE: STATUS|...` only when >=3 parties share a thread. Role names are project-defined; COP fixes none.
- Atomic handoff: sender ends with DONE (+ pointer to output); receiver ACKs. No DONE -> work is not handed off.
- Generic flow for multi-agent work: INTAKE (read request, Q? if unclear) -> CLARIFY (assumptions, risks) -> PLAN (tasks, done-criteria) -> BUILD (WIP; BLOCK with reason) -> VERIFY (TP/TF; TF -> BUILD) -> DELIVER (DONE, FYI) -> ARCHIVE (close, clean up). Skip steps that add nothing; example thread: examples/handoff-thread.md.
- Redundancy examples: `task: book` not `task: a book`; `need info` not `I need more info`; `confirm` not `please confirm`; `deploy prod` not `deploy to production environment`.
