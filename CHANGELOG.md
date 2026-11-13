# Changelog

## 2.0.0

COP replaces v1's role-based "Op-Urgency" syntax. v1 is not kept in the tree; use git history (tag or commit `b4d75bd`) if you need it.

### Why v1 was replaced
- One style for every message, with no notion of who reads it. v2 sorts text into tiers, so humans keep prose.
- Role codes (ORCH, PLAN, SPDP, XPM, ...) and medical/military vocabulary were project-specific. v2 fixes no roles.
- Its workflow and glossary referred to folders that did not exist.

### Carried over from v1
- Status codes ACK, WIP, DONE, BLOCK, Q?, FYI, NI, ND, TP/TF, and CFM, PTAL, ETA, SITREP.
- Operators `->` `=>` `@` `!` `^` `+` `-` and `$` (budget/limit). New: `~` and `!=`.
- Atomic handoff (DONE ends a handoff), the intake-to-archive flow, the message-thread template, and the "no redundancy" examples. These now live in `skills/cop/reference/COP.md` and `examples/`.
- Dropped: `r/o`, the role codes, `hx`, `p/w`, `v`, project-structure rules.

### New
- Tiers: T0 human, T1 own notes, T2 agent to agent, T3 agent-only docs.
- Line format `STATUS|target|result|evidence|next` replaces `ROLE > ACTION | TARGET | STATUS | NOTES`.
- Evidence tags `obs | inf | ?`, input and process discipline, per-project glossary at `.cop/shorthand.md`.
- Model-agnostic rules (`standalone/COP-rules.md`, `skills/cop/reference/COP.md`, `hooks/peer.txt`).
- Claude Code integration: plugin layout, `/cop` skill, subagent hook (fail-open, opt-outs via `cop:off` and `COP_SKIP_SUBAGENTS`), `standalone/install.sh` and `uninstall.sh` (preflight checks, ownership markers, timestamped backups), `tools/cop_stats.py` (tolerates malformed transcripts).
- Irreversible or outward actions require confirmation unless already authorised; the same rule is injected into subagent prompts.
- When unsure who reads a document, treat it as human-read (T0).
- Tests, CI and examples.

### Removed
- The self-referencing `.gitmodules`, the v1 docs, and the project-structure rules.
