from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A smart pet care planner: track routines, sort and filter tasks, and catch conflicts.")

# Keep the Owner alive across Streamlit reruns
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)


def task_rows(tasks):
    """Convert tasks into table rows for display."""
    return [
        {
            "Date": t.due_date.isoformat(),
            "Time": t.time,
            "Pet": t.pet_name,
            "Task": t.description,
            "Minutes": t.duration_minutes,
            "Priority": t.priority,
            "Repeats": t.frequency,
            "Status": "✅ done" if t.completed else "⏳ to do",
        }
        for t in tasks
    ]


# --- Owner ---
st.subheader("👤 Owner")
owner.name = st.text_input("Owner name", value=owner.name)

# --- Pets ---
st.subheader("🐶 Pets")
with st.form("add_pet", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    pet_name = c1.text_input("Pet name", value="Mochi")
    species = c2.selectbox("Species", ["dog", "cat", "other"])
    age = c3.number_input("Age", min_value=0, max_value=40, value=2)
    if st.form_submit_button("Add pet"):
        if not pet_name.strip():
            st.error("Pet name can't be empty.")
        elif owner.get_pet(pet_name.strip()):
            st.error(f"{pet_name} already exists.")
        else:
            owner.add_pet(Pet(pet_name.strip(), species, int(age)))
            st.success(f"Added {pet_name}!")

if owner.pets:
    st.write(", ".join(f"**{p.name}** ({p.species}, {p.task_count()} tasks)" for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

# --- Tasks ---
st.subheader("📝 Schedule a task")
if owner.pets:
    with st.form("add_task", clear_on_submit=True):
        c1, c2 = st.columns(2)
        target = c1.selectbox("Pet", [p.name for p in owner.pets])
        description = c2.text_input("Task", value="Morning walk")
        c3, c4, c5 = st.columns(3)
        when = c3.time_input("Time")
        duration = c4.number_input("Minutes", min_value=1, max_value=240, value=20)
        priority = c5.selectbox("Priority", ["high", "medium", "low"], index=1)
        c6, c7 = st.columns(2)
        frequency = c6.selectbox("Repeats", ["once", "daily", "weekly"])
        due = c7.date_input("Date", value=date.today())
        if st.form_submit_button("Add task"):
            owner.get_pet(target).add_task(
                Task(description, when.strftime("%H:%M"), int(duration), priority, frequency, due_date=due)
            )
            st.success(f"Scheduled '{description}' for {target} at {when.strftime('%H:%M')}.")
else:
    st.caption("Add a pet first.")

st.divider()

# --- Schedule view ---
st.subheader("📅 Today's schedule")
for warning in scheduler.detect_conflicts(scheduler.get_todays_schedule()):
    st.warning(f"⚠️ {warning}. Consider moving one of these tasks.")

todays = scheduler.get_todays_schedule()
if todays:
    st.table(task_rows(todays))
else:
    st.info("Nothing left to do today. 🎉")

# Mark a task complete
open_tasks = scheduler.sort_by_time(scheduler.filter_tasks(completed=False))
if open_tasks:
    labels = [f"{t.due_date} {t.time} · {t.pet_name} · {t.description}" for t in open_tasks]
    choice = st.selectbox("Mark a task complete", range(len(open_tasks)), format_func=lambda i: labels[i])
    if st.button("Mark complete"):
        task = open_tasks[choice]
        next_task = scheduler.mark_task_complete(task)
        msg = f"Completed '{task.description}'."
        if next_task:
            msg += f" Next {task.frequency} occurrence added for {next_task.due_date}."
        st.success(msg)
        st.rerun()

st.divider()

# --- All tasks with sort / filter ---
st.subheader("🔎 All tasks")
c1, c2, c3 = st.columns(3)
pet_filter = c1.selectbox("Pet", ["All"] + [p.name for p in owner.pets])
status_filter = c2.selectbox("Status", ["All", "To do", "Done"])
sort_mode = c3.selectbox("Sort by", ["Time", "Priority"])

filtered = scheduler.filter_tasks(
    pet_name=None if pet_filter == "All" else pet_filter,
    completed={"All": None, "To do": False, "Done": True}[status_filter],
)
ordered = scheduler.sort_by_time(filtered) if sort_mode == "Time" else scheduler.sort_by_priority(filtered)
if ordered:
    st.table(task_rows(ordered))
else:
    st.info("No tasks match these filters.")
