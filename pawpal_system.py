"""PawPal+ logic layer: Owner, Pet, Task, and Scheduler classes."""

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from typing import Optional

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
RECURRENCE_STEP = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


@dataclass
class Task:
    """A single pet care activity scheduled at a time on a date."""

    description: str
    time: str  # "HH:MM", 24-hour
    duration_minutes: int = 15
    priority: str = "medium"  # "low", "medium", "high"
    frequency: str = "once"  # "once", "daily", "weekly"
    completed: bool = False
    due_date: date = field(default_factory=date.today)
    pet_name: str = ""

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task done and return the next occurrence if it recurs, else None."""
        self.completed = True
        step = RECURRENCE_STEP.get(self.frequency)
        if step is None:
            return None
        return replace(self, completed=False, due_date=self.due_date + step)


@dataclass
class Pet:
    """A pet and the list of care tasks that belong to it."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet and tag it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        self.tasks.remove(task)

    def task_count(self) -> int:
        """Return how many tasks this pet has."""
        return len(self.tasks)


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        """Return the pet with the given name, or None."""
        return next((p for p in self.pets if p.name == name), None)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """The 'brain' that retrieves, organizes, and manages tasks across all pets."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def get_all_tasks(self) -> list[Task]:
        """Fetch all tasks from the owner (across every pet)."""
        return self.owner.get_all_tasks()

    def sort_by_time(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Return tasks sorted chronologically by date, then by HH:MM time."""
        tasks = self.get_all_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda t: (t.due_date, t.time))

    def sort_by_priority(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Return tasks sorted by priority (high first), then by time."""
        tasks = self.get_all_tasks() if tasks is None else tasks
        return sorted(tasks, key=lambda t: (PRIORITY_RANK.get(t.priority, 1), t.due_date, t.time))

    def filter_tasks(
        self,
        tasks: Optional[list[Task]] = None,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> list[Task]:
        """Return tasks matching the given pet name and/or completion status."""
        tasks = self.get_all_tasks() if tasks is None else tasks
        return [
            t
            for t in tasks
            if (pet_name is None or t.pet_name == pet_name)
            and (completed is None or t.completed == completed)
        ]

    def get_todays_schedule(self, day: Optional[date] = None) -> list[Task]:
        """Return incomplete tasks due on the given day (default today), sorted by time."""
        day = day or date.today()
        due = [t for t in self.get_all_tasks() if t.due_date == day]
        return self.sort_by_time(self.filter_tasks(due, completed=False))

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Complete a task and, if it recurs, add its next occurrence to the same pet."""
        next_task = task.mark_complete()
        if next_task is not None:
            pet = self.owner.get_pet(task.pet_name)
            if pet is not None:
                pet.add_task(next_task)
        return next_task

    def detect_conflicts(self, tasks: Optional[list[Task]] = None) -> list[str]:
        """Return warning messages for incomplete tasks that share the same date and start time."""
        tasks = self.get_all_tasks() if tasks is None else tasks
        slots: dict[tuple, list[Task]] = {}
        for t in tasks:
            if not t.completed:
                slots.setdefault((t.due_date, t.time), []).append(t)
        warnings = []
        for (day, time), group in sorted(slots.items()):
            if len(group) > 1:
                names = ", ".join(f"{t.description} ({t.pet_name})" for t in group)
                warnings.append(f"Conflict on {day} at {time}: {names}")
        return warnings
