# Deskapp Antigravity Directives & Project Rules

## 🚫 Command Execution Rules

### Python Execution
- **NEVER use `python -c` or `python3 -c`**: The user considers `python -c` inline code execution rude and unacceptable.
- **Always write scripts to files**: Whenever Python logic needs to be run, create a dedicated script file (e.g. in scratch or project scripts) and execute it by path (`python script.py`).

---

## 🛠️ Work Request Types

Every user prompt is a work request. Expand the prompt into a full proposal before acting.
There are 4 primary work types:
1. **Add a feature**: Create a TODO or numbered proposal.
2. **Review a proposal**: Review soundness/feasibility, verify file paths and signatures, approve or explicitly deny.
3. **Fix a bug**: Track in a bugfix proposal artifact (`BUGFIX_<NUM>_UNRESOLVED.prop`).
4. **Implement a proposal**: Follow the proposal strictly, checking off items as completed.

---

## 📜 Changelog (.github/changelog.ai)

- Changelog lives at `.github/changelog.ai`.
- Update the changelog upon completion of any work type.
- Credit yourself by model name in every changelog entry.
- The changelog is how agents communicate state across sessions.

---

## 📋 Proposals & TODO Pipeline

### TODO Pipeline
New ideas that are not immediately executed enter as TODO files:
- Filename pattern: `TODO_<Title>_<MMDDYY>.prop`
- Stored in `.github/proposals/`
- Same format as a proposal (originating prompt, interpretation, body)
- NO checkboxes until promoted to a numbered proposal.
- When ready to execute:
  1. Assign the next sequential proposal number.
  2. Rename: `TODO_<Title>_<MMDDYY>.prop` → `PROPOSAL_<NUM>_<Title>_<MMDDYY>.prop`
  3. Add checkboxes (`- [ ]`) to all actionable items.
  4. Begin execution.

### Proposal File Format
```text
<Title>_<MMDDYY>
Last reviewed: <MMDDYY>

Originating Prompt: <exact user prompt>
Interpretation: <expansion of intent and scope>

<full proposal with checkboxes>
```

### Bugfix Tracking
- File: `.github/proposals/BUGFIX_<NUM>_UNRESOLVED.prop`
- On user confirmation of fix, rename to `BUGFIX_<NUM>_RESOLVED.prop`.

---

## 📐 Project Conventions

- **Indentation**: 4 spaces, never tabs.
- **Strings**: Double quotes (`"`), never single quotes (`'`).
- **Naming**: `CamelCase` for all function, method, and variable names. No leading underscores (dunders are fine).
- **Line Length**: 79 characters max.
- **Architecture**:
  - Prefer classes for stateful and domain-modeling work.
  - Keep functions and files small and focused.
  - Think in a UNIX way: one thing, done well, composable.
  - Prefer building our own tools.
  - Always work from a plan.
  - Work in complete sections; do not leave partial implementations.
  - SIMPLE. STREAMLINED. EFFICIENT. MINIMAL.
- **Environment**:
  - Do not touch anything inside `.venv/`.
  - Virtual environment alias is `werk` (`source .venv/bin/activate`).
- **Documentation**: Do not generate unsolicited documentation unless explicitly requested.

---

## 🏷️ Versioning

- Format: `APP_RELEASE.PROPOSAL_NUMBER.BUGFIX_NUMBER`
- `pyproject.toml` is the single source of truth for the version.
- Roll the version on every code change.
  - Example: `0.9.0` (Proposal 9 implementation)
  - Example: `0.9.1` (First bugfix under Proposal 9)
  - Example: `0.10.0` (Proposal 10 implementation)

---

## 📍 Project Metadata

- **Project Focus**: Deskapp
- **Changelog**: `.github/changelog.ai`
- **Proposals Directory**: `.github/proposals/`
- **Build Config**: `pyproject.toml`
