---
name: cop
description: Load the COP (compressed communication protocol) rules for terse machine-to-machine text. Use when the user types /cop, asks about COP or token-efficient agent communication, or when writing prompts for subagents, scratch notes, or agent-to-agent messages.
---

# COP

Write tersely where only machines or agents read the text. Write normal prose for anything a human reads.

## Tiers
- T0, human reads (chat, commits, PRs, reports, code comments, config): normal prose, no COP codes or symbols. Exception: the user explicitly asks for terse or radio-style replies.
- T1, own thinking, scratch files, memory body: maximum density. Think in COP: in the reasoning, notes and plans you control, write fragments from the first token, not full sentences you compress afterwards. A plan shown to a human is T0.
- T3, agent-only docs (specs, runbooks, task/handoff/state files, insights logs) that no human reads or maintains: dense COP with a file-local legend at the top. If a human reads it, or you are unsure who reads it, it is T0.
- T2, agent to agent (subagents, teammates, other sessions): dense. State goal and why, constraints, paths, done-criteria and known facts, because the peer starts cold.
- Text going from T1 or T2 to a human is rewritten as prose. Never forward peer shorthand to the user.

## Core rules
- Drop grammar the reader can infer (articles, copulas, filler). Keep every reasoning step and logic word (NOT, if, unless, only, all, none, because).
- Exact numbers, paths, ids, commands, errors. Negation is spelled NOT.
- Pointer over copy (path:line, sha, run-id, url). Send only the delta since the last known state.
- Tag claims obs (seen in tool output), inf (inferred), or ? (unknown).
- Before any irreversible or outward action (delete, push, send, deploy, publish), state the intent in plain full words and get confirmation unless the user already authorised that action.
- Probe before loading (wc -l, grep -n), then read a range. Filter at the source. Never re-read or re-run what was already seen.

## Codes
ACK, WIP, DONE, BLOCK(reason), Q? question, FYI, NI need info, ND need decision, CFM confirm, PTAL review request, TP/TF test pass/fail, VRF verified, UNV unverified.
Line format: `STATUS|target|result|evidence|next`

## Full reference
Read `reference/COP.md` in this skill's directory for the complete rules (peer block, glossary, densifying existing text, measuring) and follow it for the rest of the session.
