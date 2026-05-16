# Agents Communication Protocol

> The **unambiguous grammar** for coordinating AI agents and human developers.

This repository is **Protocol-as-Code**. It provides a structured language and workflow system that reduces AI hallucinations, saves tokens, and ensures 100% traceability in multi-agent environments.

---

## 🛠️ How a Developer Uses This

### 1. As a "System Prompt"
You don't "run" this code. You **inject** these rules into your AI agents.
**Prompt Shortcut:**
> "Follow the protocol rules in `protocol/` and `workflow/` to coordinate all tasks. Use the `Op-Urgency` syntax for all internal messages."

### 2. As a Submodule
Add this repo to your project workspace to ensure your AI agents have a local reference to their "Operating Instructions."

---

## 📁 Repository Structure

- **`protocol/`**: The language specification (shorthand, tokens, and format).
- **`workflow/`**: The handoff rules. How a task moves from "Intake" to "Archive."
- **`glossary/`**: Synonyms and shorthand to keep context windows small.
- **`msg-thread-template.md`**: The boilerplate for starting new team discussions.

## 📝 Core Rules Summary
- **No redundancy:** Avoid filler words. Use compact style.
- **Traceability:** Use `@role` and `ACK` for every handoff.
- **Compactness:** If a doc grows, link it. Don't bloat the chat.

## Notes
- Use `[[format]]`, `[[acronyms]]`, `[[common-phrases]]`., `[[../msgs/README]]`, `[[../glossary/README]]`, `[[../init/README]]`.
- Keep lines short.
- Use `Q?` for questions, `ACK` for receipt.
- If a doc grows beyond 2 lines, link it, do not expand chat.
- Team communication supports Obsidian-like folder structure and sub-threads.
- Use `@role` or `@name` when you need direct attention.
- If one agent is acting as multiple roles, keep internal messages in `msgs/` and use role-prefixed syntax.
- Before any execution/edit step, open or update the matching `msgs/YYYYMMDD-<topic>/README.md` thread.
- Use `ORCH > ACK`, `XAA > r/o`, `XPM > decision`, `PLAN > scope`, `SPDP > WIP/DONE`, `XQA > note` in that thread before implementation starts.
- If the thread is missing, create it first; do not begin code changes before the internal coordination exists.

## No redundancy
- Avoid filler words and articles.
- Prefer `task: book` not `task: a book`.
- Prefer `need info` not `I need more info`.
- Prefer `confirm` not `please confirm`.
- Prefer `done` not `finished successfully`.
- Prefer `deploy prod` not `deploy to production environment`.
