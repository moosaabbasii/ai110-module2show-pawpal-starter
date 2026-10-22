# 🐾 PawPal+

PawPal+ is a pet care planner that helps a busy owner keep track of feedings, walks, medications, and appointments for multiple pets. The backend logic lives in `pawpal_system.py`, it's verified with a CLI demo (`main.py`) and a pytest suite, and it's wired into a Streamlit UI (`app.py`).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python main.py          # CLI demo
streamlit run app.py    # web app
python -m pytest        # tests
```

## Features

- **Multi-pet owner profile**: an `Owner` holds any number of `Pet`s, and each `Pet` holds its own `Task`s.
- **Sorting by time**: tasks are put in chronological order (date, then `HH:MM`).
- **Priority scheduling**: an optional view sorts high → medium → low priority, then by time.
- **Filtering**: show tasks for one pet, or only done / to-do tasks.
- **Daily and weekly recurrence**: completing a recurring task automatically creates the next one (`+1 day` or `+7 days`).
- **Conflict warnings**: tasks sharing the same date and start time get flagged with a warning instead of crashing the app.
- **Today's schedule**: only the incomplete tasks due today, sorted by time.

## Implementation Summary

| Class | Responsibility |
|-------|----------------|
| `Task` (dataclass) | One care activity: description, time, duration, priority, frequency, completion status, due date, and the pet it belongs to. `mark_complete()` returns the next occurrence for recurring tasks. |
| `Pet` (dataclass) | Pet details plus its list of tasks. `add_task()` tags each task with the pet's name. |
| `Owner` (dataclass) | Manages pets. `get_all_tasks()` returns every pet's tasks in one list. |
| `Scheduler` | The "brain." It always pulls tasks through `Owner.get_all_tasks()`, so it works across all pets, then sorts, filters, completes, and checks for conflicts. |

The Streamlit app keeps one `Owner` in `st.session_state` so data survives reruns, and it builds a `Scheduler` around that owner on every run.

## 🖥️ Sample Output

Output of `python main.py`:

```
=== PawPal+ for Jordan ===

Today's Schedule (sorted by time)
---------------------------------
  07:30  Biscuit Morning walk        30 min  [high  ] daily  todo
  08:00  Biscuit Breakfast           10 min  [high  ] daily  todo
  08:00  Mochi   Breakfast           10 min  [high  ] daily  todo
  09:00  Mochi   Flea medication      5 min  [high  ] weekly todo
  15:00  Mochi   Play session        20 min  [low   ] once   todo
  18:30  Biscuit Evening walk        30 min  [medium] daily  todo

Sorted by priority, then time
-----------------------------
  07:30  Biscuit Morning walk        30 min  [high  ] daily  todo
  08:00  Biscuit Breakfast           10 min  [high  ] daily  todo
  08:00  Mochi   Breakfast           10 min  [high  ] daily  todo
  09:00  Mochi   Flea medication      5 min  [high  ] weekly todo
  18:30  Biscuit Evening walk        30 min  [medium] daily  todo
  15:00  Mochi   Play session        20 min  [low   ] once   todo

Only Mochi's tasks
------------------
  09:00  Mochi   Flea medication      5 min  [high  ] weekly todo
  08:00  Mochi   Breakfast           10 min  [high  ] daily  todo
  15:00  Mochi   Play session        20 min  [low   ] once   todo

Conflict check:
  WARNING: Conflict on 2026-10-21 at 08:00: Breakfast (Biscuit), Breakfast (Mochi)

Completed 'Morning walk' -> next one due 2026-10-22

Completed tasks
---------------
  07:30  Biscuit Morning walk        30 min  [high  ] daily  done

Today's remaining schedule
--------------------------
  08:00  Biscuit Breakfast           10 min  [high  ] daily  todo
  08:00  Mochi   Breakfast           10 min  [high  ] daily  todo
  09:00  Mochi   Flea medication      5 min  [high  ] weekly todo
  15:00  Mochi   Play session        20 min  [low   ] once   todo
  18:30  Biscuit Evening walk        30 min  [medium] daily  todo
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_by_priority()` | `sorted()` with a lambda key of `(due_date, time)`. Zero-padded `HH:MM` strings sort correctly as text. The priority sort uses `(rank, due_date, time)`. |
| Filtering | `Scheduler.filter_tasks(pet_name=..., completed=...)`, `Scheduler.get_todays_schedule()` | Either filter can be left as `None`, meaning "don't filter on this." Today's schedule shows incomplete tasks due today. |
| Conflict handling | `Scheduler.detect_conflicts()` | Groups incomplete tasks by `(due_date, time)` and returns a readable warning string for every slot with more than one task, whether it's the same pet or different pets. |
| Recurring tasks | `Task.mark_complete()`, `Scheduler.mark_task_complete()` | Daily tasks get `due_date + timedelta(days=1)` and weekly tasks get `+ timedelta(weeks=1)`. The scheduler adds the new copy to the same pet. One-time tasks just get marked done. |

## 🧪 Testing PawPal+

```bash
python -m pytest
```

`tests/test_pawpal.py` covers:
- Task completion changes status, and adding a task increases a pet's task count
- `Owner.get_all_tasks()` combines tasks from multiple pets
- Sorting by time is chronological, and priority sorting falls back to time
- Filtering by pet, by status, and by both at once
- Recurrence: daily → next day, weekly → +7 days, one-time → no new task
- Conflict detection flags duplicate times, with no false positives on an empty or conflict-free schedule
- Today's schedule leaves out other days and completed tasks

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-8.4.2, pluggy-1.6.0
rootdir: C:\Users\moosa\OneDrive - University of South Florida\Desktop\School\Professor Borghesi\ai110-module2show-pawpal-starter
plugins: anyio-4.13.0
collected 12 items

tests\test_pawpal.py ............                                        [100%]

============================= 12 passed in 0.03s ==============================
```

**Confidence level: ★★★★☆ (4/5).** Every core behavior and the main edge cases are tested and pass. Conflict detection only catches exact start-time matches, though. It doesn't catch overlapping durations, and the UI is only smoke-tested.

## 📸 Demo Walkthrough

1. **Set the owner.** Run `streamlit run app.py` and enter the owner's name at the top.
2. **Add pets.** Use the *Pets* form to add a pet (name, species, age), e.g. "Mochi" the cat and "Biscuit" the dog. Duplicate or empty names show an error.
3. **Schedule tasks.** In *Schedule a task*, pick a pet and enter a description, time, duration, priority, how often it repeats (once/daily/weekly), and a date. Each task gets a success message.
4. **View today's schedule.** *Today's schedule* shows today's incomplete tasks sorted by time (`Scheduler.get_todays_schedule()`). If two tasks share a time slot, e.g. both pets' breakfast at 08:00, a yellow `st.warning` names both tasks (`Scheduler.detect_conflicts()`).
5. **Complete a task.** Pick a task in *Mark a task complete* and click the button. If it's daily or weekly, a message confirms the next occurrence was created for tomorrow or next week (`Scheduler.mark_task_complete()`).
6. **Explore all tasks.** In *All tasks*, filter by pet and by status (to do / done), and sort by time or by priority (`Scheduler.filter_tasks()`, `sort_by_time()`, `sort_by_priority()`).

CLI version of the same workflow (`python main.py`), showing sorting, priority sort, filtering, a conflict warning, and recurrence:

```
=== PawPal+ for Jordan ===

Today's Schedule (sorted by time)
---------------------------------
  07:30  Biscuit Morning walk        30 min  [high  ] daily  todo
  08:00  Biscuit Breakfast           10 min  [high  ] daily  todo
  08:00  Mochi   Breakfast           10 min  [high  ] daily  todo
  09:00  Mochi   Flea medication      5 min  [high  ] weekly todo
  15:00  Mochi   Play session        20 min  [low   ] once   todo
  18:30  Biscuit Evening walk        30 min  [medium] daily  todo

Sorted by priority, then time
-----------------------------
  07:30  Biscuit Morning walk        30 min  [high  ] daily  todo
  08:00  Biscuit Breakfast           10 min  [high  ] daily  todo
  08:00  Mochi   Breakfast           10 min  [high  ] daily  todo
  09:00  Mochi   Flea medication      5 min  [high  ] weekly todo
  18:30  Biscuit Evening walk        30 min  [medium] daily  todo
  15:00  Mochi   Play session        20 min  [low   ] once   todo

Only Mochi's tasks
------------------
  09:00  Mochi   Flea medication      5 min  [high  ] weekly todo
  08:00  Mochi   Breakfast           10 min  [high  ] daily  todo
  15:00  Mochi   Play session        20 min  [low   ] once   todo

Conflict check:
  WARNING: Conflict on 2026-10-21 at 08:00: Breakfast (Biscuit), Breakfast (Mochi)

Completed 'Morning walk' -> next one due 2026-10-22

Completed tasks
---------------
  07:30  Biscuit Morning walk        30 min  [high  ] daily  done

Today's remaining schedule
--------------------------
  08:00  Biscuit Breakfast           10 min  [high  ] daily  todo
  08:00  Mochi   Breakfast           10 min  [high  ] daily  todo
  09:00  Mochi   Flea medication      5 min  [high  ] weekly todo
  15:00  Mochi   Play session        20 min  [low   ] once   todo
  18:30  Biscuit Evening walk        30 min  [medium] daily  todo
```

## Diagrams

- `diagrams/uml_draft.mmd`: initial Phase 1 design
- `diagrams/uml.mmd` / `diagrams/uml_final.mmd`: final design matching `pawpal_system.py`
