# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

1. Add a pet (name, species, age) to the owner's profile.
2. Schedule a care task for a pet (walk, feeding, meds) at a time, with a priority and a repeat setting (once, daily, or weekly).
3. See today's schedule in time order, get warned about conflicts, and mark tasks complete.

**a. Initial design**

My first UML (`diagrams/uml_draft.mmd`) had four classes:

- **Task**: a single activity with a description, `HH:MM` time, frequency, and completion flag. Method: `mark_complete()`.
- **Pet**: name, species, and a list of tasks. Method: `add_task()`.
- **Owner**: name and a list of pets. Methods: `add_pet()` and `get_all_tasks()`, which returns every pet's tasks together.
- **Scheduler**: holds a reference to an `Owner` and is responsible for organizing tasks (`get_todays_schedule()`, `sort_by_time()`).

The relationships were Owner *has many* Pets, Pet *has many* Tasks, and Scheduler *reads from* Owner. I used dataclasses for `Task` and `Pet` because they're mostly data containers.

**b. Design changes**

- **Added `due_date` to `Task`.** Recurring tasks need to know *which day* they're for. Without a date, a "daily" task that recreated itself would just look like a duplicate. With `due_date`, the next occurrence is `due_date + timedelta(days=1)`, and "today's schedule" becomes a simple filter.
- **Added `pet_name` to `Task`, set by `Pet.add_task()`.** After the review, the Scheduler couldn't tell which pet a task belonged to once it pulled the combined list from `Owner.get_all_tasks()`. I needed that for filtering by pet, for conflict messages, and for adding the next occurrence to the right pet. I chose a name string over a full back-reference to the `Pet` object to avoid circular references and keep the dataclasses easy to print and compare.
- **Added `duration_minutes` and `priority`**, because the README scenario asks for them, and added `Owner.get_pet()` so the UI and Scheduler can look pets up by name.
- **Made `mark_complete()` return the next `Task`** instead of having `Task` reach into its pet. The `Scheduler.mark_task_complete()` method attaches the new task to the pet. That keeps `Task` unaware of the rest of the system.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers **date** (only tasks due today show up in today's schedule), **time** (chronological order), **completion status** (finished tasks are hidden from the plan), and **priority** (high → low, as an alternate sort). I decided time mattered most, because a pet owner's day is driven by the clock: meds and feeding happen at fixed times. Priority is a secondary view for deciding what to drop on a busy day.

**b. Tradeoffs**

Conflict detection only checks for **exact start-time matches** (same date and same `HH:MM`). It doesn't check whether durations overlap. For example, a 30-minute walk at 07:30 and a feeding at 07:45 aren't flagged. That's reasonable here because most pet care tasks are short and scheduled on round times, and the check stays simple, fast (one pass grouping tasks into a dict), and easy to explain. Interval-overlap detection would be the next improvement.

A second tradeoff: times are stored as zero-padded `"HH:MM"` strings and sorted as text rather than parsed into `datetime.time`. This only works because the format is fixed. The UI enforces it with `st.time_input(...).strftime("%H:%M")`.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code in agent mode for most of the build. It forked and cloned the repo, drafted the UML in Mermaid, generated the dataclass skeleton, implemented the four classes, and wrote `main.py`, the pytest suite, and the Streamlit wiring. The most useful prompts were specific and tied to files, for example "the Scheduler must read tasks from `Owner.get_all_tasks()`, not from one pet," or "use `timedelta` so a daily task's next occurrence is due_date + 1 day." Asking it to run `python main.py` and `python -m pytest` after each change and show me the output helped me verify it instead of trusting it.

**b. Judgment and verification**

- A simple "sort by time" sorts only on the `HH:MM` string. Once recurring tasks exist, that would put tomorrow's 07:30 walk ahead of today's 08:00 breakfast. I kept the sort key as `(due_date, time)` so multi-day lists stay correct.
- A more "Pythonic" option for conflict detection was a one-liner using `itertools.groupby`. I kept the explicit dict-based loop because `groupby` requires pre-sorting and is harder to read at a glance.

I verified behavior three ways: the CLI demo output (tasks added out of order come out sorted, the 08:00 breakfast conflict is flagged, the completed daily walk reappears for tomorrow), the 12 pytest tests, and a Streamlit `AppTest` smoke test that adds a pet, adds a task, and marks it complete without exceptions.

**c. Separate chat sessions**

Keeping design, implementation, algorithms, and testing as separate phases (and separate commits) kept each AI conversation focused on one concern. Test generation wasn't influenced by implementation details I might have wanted to change, and each commit maps to one phase of the project.

---

## 4. Testing and Verification

**a. What you tested**

Task completion; adding a task increases a pet's count; `Owner.get_all_tasks()` spans pets; chronological sorting; priority-then-time sorting; filtering by pet, by status, and by both; daily, weekly, and one-time recurrence; conflict detection for same-time tasks across pets; no false conflicts on empty or clean schedules; and today's schedule excluding other days and completed tasks. These matter because sorting, recurrence, and conflicts are the "smart" parts of the app, and they're the easiest to break silently.

**b. Confidence**

4/5. All 12 tests pass and cover the main edge cases. Next I'd test overlapping durations, invalid time strings (e.g., `"7:5"`), tasks for a pet that was removed, two pets with the same name, and completing the same recurring task twice.

---

## 5. Reflection

**a. What went well**

The separation between `pawpal_system.py` and `app.py`. Because the logic was verified in the CLI and with tests first, wiring the UI was mostly calling existing methods, and the UI needed no scheduling logic of its own.

**b. What you would improve**

I'd add duration-overlap conflict detection, JSON persistence (`save_to_json` / `load_from_json`), and the ability to edit or delete tasks from the UI. I'd also store `time` as a real `datetime.time` instead of a string.

**c. Key takeaway**

Being the "lead architect" means owning the design decisions even when AI writes the code. The AI produced working code quickly, but choices like adding `due_date`, where the recurrence logic lives, and what counts as a conflict were the ones that decided whether the system was actually correct. Running the code and tests myself was how I checked those choices.
