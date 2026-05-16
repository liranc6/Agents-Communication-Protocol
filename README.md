# Agents Communication Protocol

> The **unambiguous grammar** for coordinating AI agents and human developers.

This repository defines the **rules of engagement**. It specifies **how** agents talk, signal status, and hand off information, without prescribing **where** those files live in your specific project.

---

## 🛠️ How it Works
This protocol acts as a "Cognitive Interface." It reduces token usage and prevents hallucinations by enforcing a strict, shorthand syntax for all interactions.

### The "Op-Urgency" Syntax
All communication must follow the `<ROLE> > <ACTION> | <TARGET> | <STATUS> | <NOTES>` pattern defined in `protocol/format.md`.

---

## 📝 Core Communication Rules
- **No redundancy:** Avoid filler words and articles. (e.g., `ack task` not `I acknowledge the task`).
- **Traceability:** Use `@role` for direct mentions.
- **Signal over Noise:** Use `ACK` for receipt, `Q?` for questions, and `r/o` for read-only updates.
- **Atomic Handoffs:** Clearly state when a role is finished using `DONE`.

## 📁 Repository Structure
- **`protocol/`**: Shorthand, tokens, and the "Op-Urgency" syntax specification.
- **`workflow/`**: Logical handoff steps and role interaction sequences.
- **`glossary/`**: Shared acronyms and terms to minimize context window bloat.

## Examples
- `ORCH > ACK | ALL | WIP | Starting task analysis.`
- `PLAN > scope | ORCH | DONE | Spec ready for review.`
- `QA > note | DEV | WIP | Found edge case in login flow.`
- Avoid filler words and articles.
- Prefer `task: book` not `task: a book`.
- Prefer `need info` not `I need more info`.
- Prefer `confirm` not `please confirm`.
- Prefer `done` not `finished successfully`.
- Prefer `deploy prod` not `deploy to production environment`.
