# COP: compressed communication protocol for agents

COP is a small set of rules for any model or agent. It makes agents write tersely where only machines will
read (their own thinking, scratch files, messages between agents, docs that only agents use), and keep normal
prose for anything a human reads (chat replies, commits, PRs, reports). The goal is fewer tokens per session
without hurting what you read.

The rules themselves are plain text and model-agnostic. This repo also ships a Claude Code integration (skill,
hook, installer); other agents use the rules directly, see "Other agents" below. Release history is in
[CHANGELOG.md](CHANGELOG.md).

## Quick start: let your agent install it
Download or clone this repo, then give your agent this prompt (replace `<REPO_PATH>` with the folder):

```text
Install COP from <REPO_PATH> so you follow it in every future session.
1. Read standalone/COP-rules.md and skills/cop/SKILL.md there.
2. Persist it with the most durable mechanism you have:
   - Claude Code: run standalone/install.sh.
   - Anything else: copy skills/cop/reference/COP.md and hooks/peer.txt to a permanent folder (not a temp dir), then add COP-rules.md plus one line with those two absolute paths to your global always-on instructions (custom instructions, AGENTS.md, rules file, system prompt). If a size limit stops you, use SKILL.md instead, or install skills/cop as a skill where supported.
   - Cannot write to any of these (for example a chat app): tell me exactly what to paste where.
3. Back up files before editing, do not duplicate if already installed, then tell me what you changed and where, and whether I must restart you.
```

The agent needs to read local files. In a chat app without file access, paste `standalone/COP-rules.md` into your
custom instructions yourself (for Claude.ai: Settings > General > Profile). Chat replies are for humans, so COP
changes little in a plain chat app; it matters most for agents that use tools, subagents and files.

## What you get
- `skills/cop/reference/COP.md`: the full rules, usable by any agent.
- `/cop` skill (Claude Code): loads the full rules into a session.
- Subagent hook (Claude Code): a PreToolUse hook that appends a terse-reply block to every subagent prompt.
- Always-on rules: a dense snippet for the agent's global instructions (`~/.claude/CLAUDE.md` for Claude Code).
- `tools/cop_stats.py` (Claude Code): per-session token stats from your transcripts, to check whether COP pays off.

## Install

### Option A: plugin (try it)
    git clone https://github.com/liranc6/Agents-Communication-Protocol.git
    claude --plugin-dir ./Agents-Communication-Protocol

The plugin provides the `/cop` skill and the subagent hook. It cannot edit your `CLAUDE.md`, so the always-on
rules are not active. Either run `/cop` per session, or append `standalone/COP-rules.md` to
`~/.claude/CLAUDE.md` yourself, followed by a line with the absolute paths of `COP.md` and `peer.txt`.

### Option B: standalone
    ./standalone/install.sh

Copies the skill, hook and stats script into `~/.claude`, appends the always-on rules to `~/.claude/CLAUDE.md`
between `<!-- COP:begin -->` and `<!-- COP:end -->` markers, and registers the hook in `~/.claude/settings.json`.
It is safe to re-run. Each change to `CLAUDE.md` or `settings.json` gets a timestamped `*.bak-cop-*` backup. It refuses to run
if `~/.claude/cop` or `~/.claude/skills/cop` exists and was not installed by COP, and it validates `settings.json` before
changing anything. Needs bash and python3 (macOS or Linux; on Windows use WSL) and the default `~/.claude` config folder (`CLAUDE_CONFIG_DIR` is not supported). Uninstall rewrites `settings.json` as 2-space JSON, so the file may be reformatted even though its content is unchanged. Restart your agent afterwards.

Do not combine A and B: you would get the hook twice.

### Subagent hook opt-out
The hook appends a reply-format block to subagent prompts. Subagents that must return a fixed format (for example
JSON) can opt out: put `cop:off` in the prompt, start a line with `COP:` to supply your own block, or list the
subagent type in the `COP_SKIP_SUBAGENTS` environment variable (comma separated). The hook never blocks a call: on any
error it passes the prompt through unchanged, and the registered command does nothing if the script is missing.
It returns `permissionDecision: "allow"` together with the rewritten prompt, which is how a hook replaces a tool input. That skips the permission prompt for that call; your deny and ask rules are still evaluated.

## Tiers at a glance
| Tier | Who reads it | Style |
|------|--------------|-------|
| T0 | a human: chat, commits, PRs, reports, code comments, config | normal prose, no COP codes or symbols |
| T1 | the agent itself: thinking, scratch files, memory body | maximum density; the agent reasons in COP, not in full sentences |
| T2 | another agent: subagents, teammates, other sessions | dense; state goal, constraints, paths, done-criteria, known facts |
| T3 | docs only agents read and write: specs, runbooks, task/handoff/state files, insights logs | dense, with a file-local legend at the top; if a human reads the doc it is T0 |

Anything moving from T1 or T2 to a human is rewritten as prose. Status line format: `STATUS|target|result|evidence|next`.
Full rules: [skills/cop/reference/COP.md](skills/cop/reference/COP.md). Worked examples: [examples/](examples/).

## Other agents
COP is text, so any agent can use it:
1. Add `standalone/COP-rules.md` to the agent's instructions file (AGENTS.md, a system prompt, and so on). Replace the placeholders with real paths, or delete them.
2. Give subagents the block in `hooks/peer.txt`. Where the host has no prompt hook, paste it into each peer prompt yourself.
3. Keep `skills/cop/reference/COP.md` where the agent can read it.

## Measure (Claude Code only)
    python3 tools/cop_stats.py --main
    python3 tools/cop_stats.py --main --split "2026-11-01 00:00"   # before/after averages, UTC

The savings are not guaranteed: the always-on rules cost tokens every session. Compare your own sessions before
and after, and cut any rule that does not pay for its load.

## Uninstall
Standalone: `./standalone/uninstall.sh` removes the COP block from `CLAUDE.md`, the hook entry from
`settings.json`, and the files it installed (only those marked as COP's). Plugin: remove the `--plugin-dir` flag.

## Layout
    .claude-plugin/plugin.json   plugin manifest
    skills/cop/                  SKILL.md and reference/COP.md
    hooks/                       hooks.json, peer_hook.py, peer.txt
    standalone/                  install.sh, uninstall.sh, COP-rules.md
    tools/cop_stats.py           token stats
    tests/                       unit and install tests
    .github/workflows/test.yml   CI
    examples/                    verbose vs COP-style, handoff thread, agent-only doc

## Tests
    python3 -m unittest discover tests
    bash tests/test_install.sh
    bash tests/test_install_edge.sh
