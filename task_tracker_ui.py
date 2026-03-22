#!/usr/bin/env python3
"""
Task Tracker Web UI
A clean, modern web interface for the task tracker.
"""

import streamlit as st
from datetime import datetime, timedelta
from task_tracker import TaskTracker, Task

# Page configuration
st.set_page_config(
    page_title="Task Tracker",
    page_icon="✓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean white UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        color: #333;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
    }
    .task-item {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        transition: all 0.3s ease;
    }
    .task-item:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .task-overdue {
        border-left: 4px solid #ff4444;
        background-color: #fff5f5;
    }
    .task-due-soon {
        border-left: 4px solid #ffaa00;
        background-color: #fffbf0;
    }
    .task-completed {
        opacity: 0.6;
        background-color: #f9f9f9;
    }
    .task-archived {
        opacity: 0.4;
        background-color: #f5f5f5;
        border-left: 4px solid #999;
    }
    .task-description {
        font-size: 1.1rem;
        color: #333;
        margin-bottom: 0.5rem;
    }
    .task-deadline {
        font-size: 0.9rem;
        color: #666;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 500;
    }
    .stTextInput>div>div>input {
        border-radius: 6px;
    }
    .stTextArea>div>div>textarea {
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'tracker' not in st.session_state:
    st.session_state.tracker = TaskTracker()
    # Auto-archive old completed tasks on first load
    st.session_state.tracker.archive_old_completed_tasks()
if 'refresh' not in st.session_state:
    st.session_state.refresh = False

def refresh_data():
    """Reload tasks from file."""
    st.session_state.tracker.load_tasks()
    # Auto-archive old completed tasks
    archived_count = st.session_state.tracker.archive_old_completed_tasks()
    return archived_count

def get_task_status_class(task: Task) -> str:
    """Get CSS class for task based on status."""
    if task.archived:
        return "task-archived"
    if task.completed:
        return "task-completed"
    elif task.is_overdue():
        return "task-overdue"
    elif task.is_due_soon():
        return "task-due-soon"
    return ""

def format_deadline(task: Task) -> str:
    """Format deadline for display."""
    deadline = task.get_deadline_datetime()
    now = datetime.now()
    
    if task.archived:
        completed_at = task.get_completed_at_datetime()
        if completed_at:
            days_archived = (now - completed_at).days
            return f"📦 Archived {days_archived} day{'s' if days_archived > 1 else ''} ago • Completed: {completed_at.strftime('%Y-%m-%d %H:%M')}"
        return f"📦 Archived • Deadline: {deadline.strftime('%Y-%m-%d %H:%M')}"
    
    if task.completed:
        completed_at = task.get_completed_at_datetime()
        if completed_at:
            days_ago = (now - completed_at).days
            if days_ago >= 7:
                return f"Completed {days_ago} day{'s' if days_ago > 1 else ''} ago • Will be archived soon • {deadline.strftime('%Y-%m-%d %H:%M')}"
            return f"Completed {days_ago} day{'s' if days_ago > 1 else ''} ago • {deadline.strftime('%Y-%m-%d %H:%M')}"
        return f"Completed • Deadline: {deadline.strftime('%Y-%m-%d %H:%M')}"
    
    time_diff = deadline - now
    
    if time_diff.total_seconds() < 0:
        days_overdue = abs(time_diff.days)
        hours_overdue = abs(int(time_diff.total_seconds() // 3600))
        if days_overdue > 0:
            return f"⚠️ Overdue by {days_overdue} day{'s' if days_overdue > 1 else ''} • {deadline.strftime('%Y-%m-%d %H:%M')}"
        else:
            return f"⚠️ Overdue by {hours_overdue} hour{'s' if hours_overdue > 1 else ''} • {deadline.strftime('%Y-%m-%d %H:%M')}"
    elif time_diff.total_seconds() <= 86400:  # 24 hours
        hours_remaining = int(time_diff.total_seconds() // 3600)
        minutes_remaining = int((time_diff.total_seconds() % 3600) // 60)
        return f"⏰ Due in {hours_remaining}h {minutes_remaining}m • {deadline.strftime('%Y-%m-%d %H:%M')}"
    else:
        days_remaining = time_diff.days
        return f"Due in {days_remaining} day{'s' if days_remaining > 1 else ''} • {deadline.strftime('%Y-%m-%d %H:%M')}"

# Header
st.markdown('<h1 class="main-header">✓ Task Tracker</h1>', unsafe_allow_html=True)

# Sidebar for adding tasks
with st.sidebar:
    st.header("➕ Add New Task")
    
    with st.form("add_task_form", clear_on_submit=True):
        description = st.text_area(
            "Task Description",
            placeholder="Enter task description...",
            height=100
        )
        
        # Date and time inputs
        col1, col2 = st.columns(2)
        with col1:
            deadline_date = st.date_input(
                "Deadline Date",
                value=datetime.now().date(),
                min_value=datetime.now().date()
            )
        with col2:
            deadline_time = st.time_input(
                "Deadline Time",
                value=datetime.now().time()
            )
        
        submitted = st.form_submit_button("Add Task", type="primary", use_container_width=True)
        
        if submitted:
            if description.strip():
                try:
                    # Combine date and time into ISO format
                    deadline_datetime = datetime.combine(deadline_date, deadline_time)
                    deadline_str = deadline_datetime.isoformat()
                    
                    task = st.session_state.tracker.add_task(
                        description=description.strip(),
                        deadline=deadline_str
                    )
                    st.success(f"✅ Task added successfully! (ID: {task.id})")
                    st.rerun()
                except ValueError as e:
                    st.error(f"❌ Error: {e}")
            else:
                st.error("❌ Please enter a task description")
    
    st.divider()
    
    # Quick stats in sidebar
    st.header("📊 Statistics")
    sidebar_tasks = st.session_state.tracker.get_tasks(include_archived=False)
    archived_tasks_list = st.session_state.tracker.get_archived_tasks()
    sidebar_total = len(sidebar_tasks)
    sidebar_completed = sum(1 for t in sidebar_tasks if t.completed)
    sidebar_incomplete = sidebar_total - sidebar_completed
    overdue_tasks = sum(1 for t in sidebar_tasks if not t.completed and t.is_overdue())
    due_soon_tasks = sum(1 for t in sidebar_tasks if not t.completed and t.is_due_soon() and not t.is_overdue())
    
    st.metric("Active Tasks", sidebar_total)
    st.metric("Incomplete", sidebar_incomplete)
    st.metric("Completed", sidebar_completed)
    if len(archived_tasks_list) > 0:
        st.metric("📦 Archived", len(archived_tasks_list), delta=None)
    if overdue_tasks > 0:
        st.metric("⚠️ Overdue", overdue_tasks, delta=None, delta_color="inverse")
    if due_soon_tasks > 0:
        st.metric("⏰ Due Soon", due_soon_tasks, delta=None, delta_color="off")

# Auto-archive old tasks (runs silently in background)
st.session_state.tracker.archive_old_completed_tasks()

# Main content area
st.header("Your Tasks")

# Refresh button and view options
col1, col2, col3 = st.columns([1, 7, 2])
with col1:
    if st.button("🔄", help="Refresh tasks"):
        archived = refresh_data()
        st.rerun()
with col3:
    show_archived = st.checkbox("📦 Show Archived", value=False, help="Show archived tasks")

# Get sorted tasks (excluding archived unless checkbox is checked)
tasks = st.session_state.tracker.get_tasks(include_archived=show_archived)
total_tasks = len(tasks)
completed_tasks = sum(1 for t in tasks if t.completed and not t.archived)
incomplete_tasks = sum(1 for t in tasks if not t.completed and not t.archived)
archived_tasks_count = sum(1 for t in tasks if t.archived)

if tasks:
    # Display tasks
    for task in tasks:
        status_class = get_task_status_class(task)
        
        # Create a container for each task
        with st.container():
            # Use columns for layout
            col1, col2, col3 = st.columns([0.05, 0.85, 0.1])
            
            with col1:
                # Checkbox for completion (disabled if archived)
                checked = st.checkbox(
                    "",
                    value=task.completed,
                    key=f"checkbox_{task.id}",
                    label_visibility="collapsed",
                    disabled=task.archived
                )
                
                # Update task if checkbox state changed
                if checked != task.completed and not task.archived:
                    st.session_state.tracker.toggle_task(task.id)
                    st.rerun()
            
            with col2:
                # Task description and deadline
                task_class = "task-completed" if task.completed else ""
                if task.archived:
                    description_style = "text-decoration: line-through; color: #999;"
                elif task.completed:
                    description_style = "text-decoration: line-through; color: #999;"
                else:
                    description_style = "color: #333;"
                
                st.markdown(
                    f'<div class="task-item {status_class} {task_class}">'
                    f'<div class="task-description" style="{description_style}">{task.description}</div>'
                    f'<div class="task-deadline">{format_deadline(task)}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            with col3:
                # Delete button (or unarchive button for archived tasks)
                if task.archived:
                    if st.button("📤", key=f"unarchive_{task.id}", help="Unarchive task"):
                        st.session_state.tracker.unarchive_task(task.id)
                        st.rerun()
                else:
                    if st.button("🗑️", key=f"delete_{task.id}", help="Delete task"):
                        st.session_state.tracker.delete_task(task.id)
                        st.rerun()
    
    # Summary at bottom
    st.divider()
    if show_archived and archived_tasks_count > 0:
        st.info(f"📦 Showing {archived_tasks_count} archived task{'s' if archived_tasks_count > 1 else ''}.")
    
    if incomplete_tasks > 0:
        st.info(f"📋 You have {incomplete_tasks} incomplete task{'s' if incomplete_tasks > 1 else ''}.")
    elif not show_archived or archived_tasks_count == 0:
        st.success("🎉 All active tasks completed! Great job!")
else:
    st.info("📝 No tasks yet. Add your first task using the sidebar!")

# Footer
st.divider()
st.markdown(
    "<div style='text-align: center; color: #999; padding: 1rem; font-size: 0.9rem;'>"
    "✓ Task Tracker | vibe coded with Cursor | By Asher Dmello"
    "</div>",
    unsafe_allow_html=True
)
