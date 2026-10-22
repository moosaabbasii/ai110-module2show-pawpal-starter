"""PawPal+ logic layer: Owner, Pet, Task, and Scheduler classes."""

from dataclasses import dataclass, field


@dataclass
class Task:
    description: str
    time: str  # "HH:MM"
    frequency: str = "once"  # "once", "daily", "weekly"
    completed: bool = False

    def mark_complete(self):
        pass


@dataclass
class Pet:
    name: str
    species: str
    tasks: list = field(default_factory=list)

    def add_task(self, task):
        pass


class Owner:
    def __init__(self, name):
        self.name = name
        self.pets = []

    def add_pet(self, pet):
        pass

    def get_all_tasks(self):
        pass


class Scheduler:
    def __init__(self, owner):
        self.owner = owner

    def get_todays_schedule(self):
        pass

    def sort_by_time(self, tasks):
        pass
