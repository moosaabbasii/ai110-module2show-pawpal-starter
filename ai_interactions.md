# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Build PawPal+ end to end: fork and clone the starter, draft the UML, generate dataclass skeletons, implement Owner/Pet/Task/Scheduler (sorting, filtering, recurrence, conflict detection, priority sort), write `main.py` and the pytest suite, wire `app.py` to the logic layer, and update the docs.

**What did the agent do?**

- Ran `gh repo fork --clone` and read the starter files
- Created `diagrams/uml_draft.mmd` and a skeleton in `pawpal_system.py`, then committed
- Implemented `pawpal_system.py` and `main.py`, then ran `python main.py` to check the output
- Wrote `tests/test_pawpal.py` and ran `python -m pytest` (12 passed)
- Rewrote `app.py` to use `st.session_state` and the Scheduler, then smoke-tested it with Streamlit's `AppTest`
- Wrote `diagrams/uml.mmd` / `uml_final.mmd`, `README.md`, and `reflection.md`, then committed each phase and pushed

**What did you have to verify or fix manually?**

The first AppTest run timed out on Streamlit's cold start. Rerunning with a longer timeout passed. I reviewed the design choices (adding `due_date` and `pet_name` to Task, and sorting by `(due_date, time)` instead of time alone) and the reflection text to make sure they matched how I wanted the system to work.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
