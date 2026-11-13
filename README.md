# COP: compressed communication protocol for agents

COP is a small set of rules for any model or agent. It makes agents write tersely where only machines will
read (their own thinking, scratch files, messages between agents, docs that only agents use), and keep normal
prose for anything a human reads (chat replies, commits, PRs, reports). The goal is fewer tokens per session
without hurting what you read.

The rules themselves are plain text and model-agnostic. This repo also ships a Claude Code integration (skill,
hook, installer); other agents use the rules directly, see "Other agents" below. Release history is in
[CHANGELOG.md](CHANGELOG.md).

## Where it works
`install.sh` only changes files in `~/.claude` on your computer. Only agents that read those files see it.

| Where you use Claude | Right after `install.sh` | After the extra setup for that place |
|----------------------|--------------------------|--------------------------------------|
| Claude Code on your computer (terminal, or a local session in the desktop app) | Works: always-on rules, `/cop`, subagent hook, stats. Open a new session first. | Nothing more to do. |
| claude.ai chat, desktop-app chat, cloud or remote sessions | Does NOT work. These run on Anthropic's servers and never read `~/.claude`. | Works for the rules only, through custom instructions or an uploaded skill (see "Chat apps and cloud sessions"). No hook and no stats there. |
| Other agents | Does NOT work. | Works after you add the rules to the agent's instructions (see "Other agents"). |

## Quick start
In a terminal (macOS or Linux; needs bash and python3):

    git clone https://github.com/liranc6/Agents-Communication-Protocol.git
    cd Agents-Communication-Protocol
    ./standalone/install.sh
    ./standalone/check.sh

Then open a new local Claude Code session and type `/cop`. A session that was already open during the install does not list it. If something fails, see "Verify the install".

### Let an agent install it instead
This only works for an agent that runs on your computer and can write to `~/.claude` (for example local Claude Code). Sandboxed agents, including chat and cloud sessions in the Claude desktop app, cannot reach your `~/.claude`; run the commands above yourself. Give your agent this prompt (replace `<REPO_PATH>` with the folder):

```text
Install COP from <REPO_PATH> so you follow it in every future session.
1. Read standalone/COP-rules.md and skills/cop/SKILL.md there.
2. Persist it with the most durable mechanism you have:
   - Claude Code: run standalone/install.sh, then standalone/check.sh.
   - Anything else: copy skills/cop/reference/COP.md and hooks/peer.txt to a permanent folder (not a temp dir), then add COP-rules.md plus one line with those two absolute paths to your global always-on instructions (custom instructions, AGENTS.md, rules file, system prompt). If a size limit stops you, use SKILL.md instead, or install skills/cop as a skill where supported.
   - Cannot write to any of these (for example a chat app): tell me exactly what to paste where.
3. Back up files before editing, do not duplicate if already installed, then tell me what you changed and where, and whether I must restart you.
```

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
changing anything. Needs bash and python3 (macOS or Linux; on Windows use WSL) and the default `~/.claude` config folder (`CLAUDE_CONFIG_DIR` is not supported). Uninstall rewrites `settings.json` as 2-space JSON, so the file may be reformatted even though its content is unchanged. Open a new session afterwards; one that was open during the install will not list `/cop`.

Do not combine A and B: you would get the hook twice.

## Verify the install
    ./standalone/check.sh

For the standalone install (a plugin install has nothing in `~/.claude` to check). It prints PASS or FAIL for each piece: the files in `~/.claude`, the single COP block in `CLAUDE.md`, the single hook entry in `settings.json`, and a live run of the hook. It changes nothing and exits 1 if anything failed.

Then, in a new local Claude Code session:
1. Type `/cop`. If it is unknown, you are probably in a chat or cloud session, or in a session that was open during the install.
2. Ask the agent to start a subagent. The prompt it sends should end with the COP reply block from `hooks/peer.txt`.

## Chat apps and cloud sessions
These sessions cannot read `~/.claude`, so `install.sh` does nothing for them. COP also changes little there, because replies to you stay normal prose either way. If you still want the rules, pick one option. Menu names may change; look for "custom instructions" and "skills" in Settings.

### Option 1: paste the rules (always on)
1. Copy `standalone/COP-rules.md` (on a Mac: `pbcopy < standalone/COP-rules.md`).
2. Paste it into Settings > Your Claude > Instructions and save.
3. Start a new chat. Chats that were already open do not pick up the change.

Why: custom instructions are sent with every chat, so the rules always apply. The cost is about 1.2K tokens in every chat. If the box rejects the text as too long, paste `skills/cop/SKILL.md` without its frontmatter instead.

### Option 2: upload the skill and add one sentence (lighter, less reliable)
1. Build the zip: `./standalone/build-skill-zip.sh` (writes `dist/cop.zip`).
2. Upload it in Settings > Customize > Skills, and make sure it is switched on.
3. Add this sentence to Settings > Your Claude > Instructions and save:

       At the start of every conversation, load the "cop" skill and follow it.

4. Start a new chat. Check that it loads the skill; you should see it in the tool calls.

Why the sentence: a skill is loaded only when Claude judges it relevant to your request, usually from its description. COP is a standing style, not a task, so most requests never trigger it and the skill would sit unused. The sentence tells Claude to load it every time. It costs only a few tokens instead of the full rules, but Claude sometimes skips it, and a session that cannot use skills ignores it.

Neither option adds the subagent hook or stats. Those exist only in local Claude Code.

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
    # run from your clone of this repo (the plugin does not put the script on your PATH)
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
    standalone/                  install.sh, uninstall.sh, check.sh, build-skill-zip.sh, COP-rules.md
    tools/cop_stats.py           token stats
    tests/                       unit and install tests
    .github/workflows/test.yml   CI
    examples/                    verbose vs COP-style, handoff thread, agent-only doc

## Tests
    python3 -m unittest discover tests
    bash tests/test_install.sh
    bash tests/test_install_edge.sh
