#!/usr/bin/env python3
"""
Task Tracker Application
A simple task tracking system to manage tasks with deadlines.
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Task:
    """Represents a single task entry."""
    description: str
    deadline: str  # ISO format datetime string
    completed: bool = False
    completed_at: Optional[str] = None  # ISO format datetime string when task was completed
    archived: bool = False
    id: Optional[int] = None

    def __post_init__(self):
        """Validate task data."""
        if not self.description.strip():
            raise ValueError("Description cannot be empty")
        if not self.deadline:
            raise ValueError("Deadline cannot be empty")
        
        # Validate deadline format
        try:
            datetime.fromisoformat(self.deadline)
        except ValueError:
            raise ValueError("Invalid deadline format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
        
        # Validate completed_at format if provided
        if self.completed_at:
            try:
                datetime.fromisoformat(self.completed_at)
            except ValueError:
                raise ValueError("Invalid completed_at format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")

    def get_deadline_datetime(self) -> datetime:
        """Get deadline as datetime object."""
        return datetime.fromisoformat(self.deadline)
    
    def get_completed_at_datetime(self) -> Optional[datetime]:
        """Get completed_at as datetime object."""
        if self.completed_at:
            return datetime.fromisoformat(self.completed_at)
        return None
    
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        return self.get_deadline_datetime() < datetime.now()
    
    def is_due_soon(self) -> bool:
        """Check if task is due within 24 hours."""
        if self.completed:
            return False
        deadline = self.get_deadline_datetime()
        now = datetime.now()
        time_until_deadline = deadline - now
        return timedelta(0) <= time_until_deadline <= timedelta(hours=24)
    
    def should_be_archived(self) -> bool:
        """Check if task should be archived (completed for 7+ days)."""
        if not self.completed or not self.completed_at:
            return False
        
        completed_datetime = self.get_completed_at_datetime()
        if not completed_datetime:
            return False
        
        days_since_completion = (datetime.now() - completed_datetime).days
        return days_since_completion >= 7


class TaskTracker:
    """Main task tracker class."""
    
    def __init__(self, data_file: str = "tasks.json"):
        """Initialize the task tracker with a data file."""
        self.data_file = Path(data_file)
        self.tasks: List[Task] = []
        self.next_id = 1
        self.load_tasks()
    
    def load_tasks(self):
        """Load tasks from JSON file."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.tasks = [Task(**task) for task in data.get('tasks', [])]
                    self.next_id = data.get('next_id', 1)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Error loading tasks: {e}")
                self.tasks = []
                self.next_id = 1
    
    def save_tasks(self):
        """Save tasks to JSON file."""
        data = {
            'tasks': [asdict(task) for task in self.tasks],
            'next_id': self.next_id
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_task(self, description: str, deadline: str) -> Task:
        """Add a new task."""
        task = Task(
            id=self.next_id,
            description=description.strip(),
            deadline=deadline
        )
        
        self.tasks.append(task)
        self.next_id += 1
        self.save_tasks()
        return task
    
    def get_tasks(self, include_archived: bool = False) -> List[Task]:
        """Get all tasks, sorted with incomplete first, then completed.
        
        Args:
            include_archived: If True, include archived tasks. Default is False.
        """
        # Filter tasks
        if include_archived:
            active_tasks = [t for t in self.tasks if not t.archived]
            archived_tasks = [t for t in self.tasks if t.archived]
        else:
            active_tasks = [t for t in self.tasks if not t.archived]
            archived_tasks = []
        
        # Separate completed and incomplete tasks
        incomplete = [t for t in active_tasks if not t.completed]
        completed = [t for t in active_tasks if t.completed]
        
        # Sort incomplete by deadline (earliest first)
        incomplete.sort(key=lambda x: x.get_deadline_datetime())
        
        # Sort completed by deadline (most recent first, so they appear at bottom)
        completed.sort(key=lambda x: x.get_deadline_datetime(), reverse=True)
        
        # Return incomplete first, then completed, then archived (if included)
        result = incomplete + completed
        if archived_tasks:
            archived_tasks.sort(key=lambda x: x.get_completed_at_datetime() or datetime.min, reverse=True)
            result.extend(archived_tasks)
        
        return result
    
    def get_archived_tasks(self) -> List[Task]:
        """Get all archived tasks."""
        archived = [t for t in self.tasks if t.archived]
        archived.sort(key=lambda x: x.get_completed_at_datetime() or datetime.min, reverse=True)
        return archived
    
    def toggle_task(self, task_id: int) -> bool:
        """Toggle task completion status."""
        for task in self.tasks:
            if task.id == task_id:
                task.completed = not task.completed
                if task.completed:
                    # Set completion timestamp
                    task.completed_at = datetime.now().isoformat()
                    # Unarchive if it was archived
                    task.archived = False
                else:
                    # Clear completion timestamp when uncompleting
                    task.completed_at = None
                self.save_tasks()
                return True
        return False
    
    def archive_old_completed_tasks(self) -> int:
        """Archive tasks that have been completed for 7+ days.
        
        Returns:
            Number of tasks archived.
        """
        archived_count = 0
        for task in self.tasks:
            if task.should_be_archived() and not task.archived:
                task.archived = True
                archived_count += 1
        
        if archived_count > 0:
            self.save_tasks()
        
        return archived_count
    
    def unarchive_task(self, task_id: int) -> bool:
        """Unarchive a task."""
        for task in self.tasks:
            if task.id == task_id and task.archived:
                task.archived = False
                self.save_tasks()
                return True
        return False
    
    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID."""
        original_count = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.id != task_id]
        
        if len(self.tasks) < original_count:
            self.save_tasks()
            return True
        return False
    
    def update_task(self, task_id: int, description: Optional[str] = None, 
                   deadline: Optional[str] = None) -> bool:
        """Update a task's description and/or deadline."""
        for task in self.tasks:
            if task.id == task_id:
                if description is not None:
                    task.description = description.strip()
                if deadline is not None:
                    task.deadline = deadline
                self.save_tasks()
                return True
        return False
