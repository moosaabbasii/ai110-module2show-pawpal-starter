"""CLI demo for PawPal+: builds an owner with pets and prints today's schedule."""

from pawpal_system import Owner, Pet, Scheduler, Task


def print_tasks(title, tasks):
    """Print a list of tasks as a readable table."""
    print(f"\n{title}")
    print("-" * len(title))
    if not tasks:
        print("  (none)")
    for t in tasks:
        status = "done" if t.completed else "todo"
        print(
            f"  {t.time}  {t.pet_name:<7} {t.description:<18} "
            f"{t.duration_minutes:>3} min  [{t.priority:<6}] {t.frequency:<6} {status}"
        )


def main():
    owner = Owner("Jordan")
    biscuit = Pet("Biscuit", "dog", age=4)
    mochi = Pet("Mochi", "cat", age=2)
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # Added out of order on purpose to show sorting
    biscuit.add_task(Task("Evening walk", "18:30", 30, "medium", "daily"))
    biscuit.add_task(Task("Morning walk", "07:30", 30, "high", "daily"))
    mochi.add_task(Task("Flea medication", "09:00", 5, "high", "weekly"))
    mochi.add_task(Task("Breakfast", "08:00", 10, "high", "daily"))
    biscuit.add_task(Task("Breakfast", "08:00", 10, "high", "daily"))  # same time as Mochi
    mochi.add_task(Task("Play session", "15:00", 20, "low"))

    scheduler = Scheduler(owner)

    print(f"=== PawPal+ for {owner.name} ===")
    print_tasks("Today's Schedule (sorted by time)", scheduler.get_todays_schedule())
    print_tasks("Sorted by priority, then time", scheduler.sort_by_priority())
    print_tasks("Only Mochi's tasks", scheduler.filter_tasks(pet_name="Mochi"))

    print("\nConflict check:")
    for warning in scheduler.detect_conflicts():
        print(f"  WARNING: {warning}")

    morning_walk = biscuit.tasks[1]
    next_walk = scheduler.mark_task_complete(morning_walk)
    print(f"\nCompleted '{morning_walk.description}' -> next one due {next_walk.due_date}")
    print_tasks("Completed tasks", scheduler.filter_tasks(completed=True))
    print_tasks("Today's remaining schedule", scheduler.get_todays_schedule())


if __name__ == "__main__":
    main()
