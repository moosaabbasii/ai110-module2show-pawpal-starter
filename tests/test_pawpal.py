"""Tests for the PawPal+ logic layer."""

import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pawpal_system import Owner, Pet, Scheduler, Task


def make_scheduler():
    owner = Owner("Jordan")
    dog = Pet("Biscuit", "dog")
    cat = Pet("Mochi", "cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    return owner, dog, cat, Scheduler(owner)


def test_mark_complete_changes_status():
    task = Task("Walk", "07:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Biscuit", "dog")
    assert pet.task_count() == 0
    pet.add_task(Task("Walk", "07:00"))
    assert pet.task_count() == 1
    assert pet.tasks[0].pet_name == "Biscuit"


def test_owner_get_all_tasks_spans_pets():
    owner, dog, cat, scheduler = make_scheduler()
    dog.add_task(Task("Walk", "07:00"))
    cat.add_task(Task("Feed", "08:00"))
    assert len(scheduler.get_all_tasks()) == 2


def test_sort_by_time_is_chronological():
    owner, dog, cat, scheduler = make_scheduler()
    dog.add_task(Task("Evening walk", "18:30"))
    cat.add_task(Task("Breakfast", "08:00"))
    dog.add_task(Task("Morning walk", "07:15"))
    times = [t.time for t in scheduler.sort_by_time()]
    assert times == ["07:15", "08:00", "18:30"]


def test_sort_by_priority_then_time():
    owner, dog, cat, scheduler = make_scheduler()
    dog.add_task(Task("Play", "07:00", priority="low"))
    dog.add_task(Task("Meds", "09:00", priority="high"))
    dog.add_task(Task("Brush", "08:00", priority="high"))
    order = [t.description for t in scheduler.sort_by_priority()]
    assert order == ["Brush", "Meds", "Play"]


def test_filter_by_pet_and_status():
    owner, dog, cat, scheduler = make_scheduler()
    walk = Task("Walk", "07:00")
    dog.add_task(walk)
    cat.add_task(Task("Feed", "08:00"))
    walk.mark_complete()
    assert [t.description for t in scheduler.filter_tasks(pet_name="Mochi")] == ["Feed"]
    assert scheduler.filter_tasks(completed=True) == [walk]
    assert scheduler.filter_tasks(pet_name="Biscuit", completed=False) == []


def test_daily_task_recurs_next_day():
    owner, dog, cat, scheduler = make_scheduler()
    today = date(2026, 10, 21)
    walk = Task("Walk", "07:00", frequency="daily", due_date=today)
    dog.add_task(walk)
    next_walk = scheduler.mark_task_complete(walk)
    assert walk.completed is True
    assert next_walk.due_date == today + timedelta(days=1)
    assert next_walk.completed is False
    assert next_walk in dog.tasks


def test_weekly_task_recurs_next_week():
    task = Task("Flea meds", "09:00", frequency="weekly", due_date=date(2026, 10, 21))
    assert task.mark_complete().due_date == date(2026, 10, 28)


def test_one_time_task_does_not_recur():
    owner, dog, cat, scheduler = make_scheduler()
    vet = Task("Vet visit", "10:00")
    dog.add_task(vet)
    assert scheduler.mark_task_complete(vet) is None
    assert dog.task_count() == 1


def test_conflict_detection_flags_same_time():
    owner, dog, cat, scheduler = make_scheduler()
    dog.add_task(Task("Breakfast", "08:00"))
    cat.add_task(Task("Breakfast", "08:00"))
    dog.add_task(Task("Walk", "09:00"))
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "08:00" in warnings[0] and "Biscuit" in warnings[0] and "Mochi" in warnings[0]


def test_no_conflicts_and_empty_pet():
    owner, dog, cat, scheduler = make_scheduler()
    assert scheduler.detect_conflicts() == []
    assert scheduler.get_todays_schedule() == []
    dog.add_task(Task("Walk", "07:00"))
    assert scheduler.detect_conflicts() == []


def test_todays_schedule_excludes_other_days_and_completed():
    owner, dog, cat, scheduler = make_scheduler()
    today = date(2026, 10, 21)
    dog.add_task(Task("Walk", "07:00", due_date=today))
    dog.add_task(Task("Tomorrow walk", "07:00", due_date=today + timedelta(days=1)))
    done = Task("Feed", "06:00", due_date=today)
    dog.add_task(done)
    done.mark_complete()
    assert [t.description for t in scheduler.get_todays_schedule(today)] == ["Walk"]
