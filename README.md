# Task Tracker

A clean and simple task tracking application with deadline management.

## Features

- **Task Description**: Add detailed descriptions for your tasks
- **Deadline Management**: Set specific date and time deadlines for each task
- **Completion Tracking**: Mark tasks as completed with a checkbox
- **Smart Sorting**: Completed tasks automatically move to the bottom of the list
- **Auto-Archiving**: Tasks completed for 7+ days are automatically archived
- **Visual Indicators**:
  - 🔴 **Red border**: Tasks that are past their deadline (overdue)
  - 🟡 **Yellow border**: Tasks due within 24 hours
  - ✅ **Grayed out**: Completed tasks
  - 📦 **Gray border**: Archived tasks
- **Clean White UI**: Modern, minimalist interface

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Web UI

Run the Streamlit web interface:
```bash
streamlit run task_tracker_ui.py
```

The application will open in your default web browser.

### Features in the UI

- **Add Tasks**: Use the sidebar to add new tasks with description and deadline
- **Mark Complete**: Click the checkbox next to a task to mark it as completed
- **Delete Tasks**: Click the 🗑️ button to delete a task
- **View Archived**: Check the "📦 Show Archived" checkbox to view archived tasks
- **Unarchive Tasks**: Click the 📤 button on archived tasks to restore them
- **View Statistics**: Check the sidebar for task statistics including archived count
- **Auto-refresh**: Tasks are automatically sorted with incomplete tasks first, then completed tasks
- **Auto-archive**: Tasks completed for 7+ days are automatically archived when you load the app

## Data Storage

Tasks are stored in `tasks.json` in the same directory as the application. The file is automatically created and updated when you add, complete, or delete tasks.

## Requirements

- Python 3.7+
- streamlit >= 1.28.0
