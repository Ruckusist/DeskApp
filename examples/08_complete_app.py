"""
08_complete_app.py - Full Application Example

This is a complete DeskApp demonstrating professional patterns:
- Multi-module navigation
- Background data fetching with workers
- Status display in info panel
- Interactive menu system
- Real-world error handling
- Clean shutdown with worker cleanup

The app simulates a task manager that fetches "tasks" in the background
and displays them with status updates.

Press SPACE to start fetching tasks.
Press R to refresh the task list.
Press UP/DOWN to navigate tasks.
Press ENTER to mark task as complete.
Press PgUp/PgDn to switch between modules.
Press Q to quit.

Created: 10/10/25 by Claude Sonnet 4.5
"""

from deskapp import App, Module, callback, Keys
from deskapp.src.worker import BaseWorker
import random
import time

TaskListID = random.random()
TaskDetailID = random.random()
StatusID = random.random()


class TaskFetcher(BaseWorker):
    """Background worker that simulates fetching tasks."""
    
    def work(self):
        """Simulate task fetching with progress updates."""
        # Emit started event
        self.emit("fetch.started", {})
        
        # Simulate fetching 5 tasks
        tasks = []
        for i in range(5):
            if self.should_stop:
                break
            
            # Emit progress
            self.emit("fetch.progress", {
                "current": i + 1,
                "total": 5,
                "percent": ((i + 1) / 5) * 100
            })
            
            # Simulate network delay
            time.sleep(0.5)
            
            # Create fake task
            task = {
                "id": i + 1,
                "title": f"Task {i + 1}",
                "description": f"Description for task {i + 1}",
                "status": "pending",
                "priority": random.choice(["high", "medium", "low"])
            }
            tasks.append(task)
        
        # Emit completed event
        if not self.should_stop:
            self.emit("fetch.completed", {"tasks": tasks})
        else:
            self.emit("fetch.canceled", {})


class TaskList(Module):
    """Main module showing task list."""
    name = "Task List"

    def __init__(self, app):
        super().__init__(app, TaskListID)
        
        # Initialize shared data
        if "tasks" not in self.app.data:
            self.app.data["tasks"] = []
        if "selected_task" not in self.app.data:
            self.app.data["selected_task"] = 0
        if "fetch_progress" not in self.app.data:
            self.app.data["fetch_progress"] = 0
        
        # Worker
        self.fetcher = None
        
        # Event listeners
        self.on_event("fetch.started", self.on_fetch_started)
        self.on_event("fetch.progress", self.on_fetch_progress)
        self.on_event("fetch.completed", self.on_fetch_completed)
        self.on_event("fetch.canceled", self.on_fetch_canceled)

    def page(self, panel):
        """Display task list."""
        h, w = panel.h, panel.w
        tasks = self.app.data.get("tasks", [])
        selected = self.app.data.get("selected_task", 0)
        
        # Title
        panel.win.addstr(1, 2, "Task Manager", 
                        self.front.color_white)
        
        # Task count
        panel.win.addstr(2, 2, f"Tasks: {len(tasks)}", 
                        self.front.color_cyan)
        
        # Controls
        y = 4
        panel.win.addstr(y, 2, "Controls:", 
                        self.front.color_yellow)
        y += 1
        panel.win.addstr(y, 4, "SPACE - Fetch tasks", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "R - Refresh", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "ENTER - Complete task", 
                        self.front.color_white)
        y += 1
        panel.win.addstr(y, 4, "UP/DOWN - Navigate", 
                        self.front.color_white)
        
        # Task list
        y += 2
        panel.win.addstr(y, 2, "Tasks:", 
                        self.front.color_yellow)
        y += 1
        
        if not tasks:
            panel.win.addstr(y, 4, "No tasks. Press SPACE to fetch.", 
                            self.front.color_white)
        else:
            for i, task in enumerate(tasks):
                if y >= h - 2:
                    break
                
                # Selection marker
                marker = ">" if i == selected else " "
                
                # Status indicator
                if task["status"] == "completed":
                    status = "✓"
                    color = self.front.color_green
                elif task["status"] == "pending":
                    status = "○"
                    color = self.front.color_yellow
                else:
                    status = "✗"
                    color = self.front.color_red
                
                # Priority color
                if task["priority"] == "high":
                    prio_color = self.front.color_red
                elif task["priority"] == "medium":
                    prio_color = self.front.color_yellow
                else:
                    prio_color = self.front.color_cyan
                
                # Draw task
                task_line = f"{marker} {status} {task['title']}"
                max_len = w - 6
                task_line = task_line[:max_len]
                
                if i == selected:
                    panel.win.addstr(y, 4, task_line, 
                                    self.front.color_white)
                else:
                    panel.win.addstr(y, 4, task_line, color)
                
                y += 1

    def PageRight(self, panel):
        """Show task details."""
        tasks = self.app.data.get("tasks", [])
        selected = self.app.data.get("selected_task", 0)
        
        if not tasks or selected >= len(tasks):
            panel.win.addstr(1, 2, "No task selected", 
                            self.front.color_white)
            return
        
        task = tasks[selected]
        
        panel.win.addstr(1, 2, "Task Details", 
                        self.front.color_white)
        panel.win.addstr(3, 2, f"ID: {task['id']}", 
                        self.front.color_cyan)
        panel.win.addstr(4, 2, f"Title:", 
                        self.front.color_white)
        panel.win.addstr(5, 2, task['title'], 
                        self.front.color_green)
        panel.win.addstr(7, 2, "Description:", 
                        self.front.color_white)
        panel.win.addstr(8, 2, task['description'], 
                        self.front.color_cyan)
        panel.win.addstr(10, 2, f"Status: {task['status']}", 
                        self.front.color_yellow)
        panel.win.addstr(11, 2, f"Priority: {task['priority']}", 
                        self.front.color_magenta)

    def PageInfo(self, panel):
        """Show app status."""
        tasks = self.app.data.get("tasks", [])
        progress = self.app.data.get("fetch_progress", 0)
        
        completed = sum(1 for t in tasks if t["status"] == "completed")
        
        panel.win.addstr(0, 2, f"Tasks: {len(tasks)} | Done: "
                              f"{completed}", 
                        self.front.color_white)
        panel.win.addstr(1, 2, f"Progress: {progress}%", 
                        self.front.color_cyan)
        
        worker_status = "RUNNING" if (self.fetcher and 
                                     self.fetcher.is_running) \
                                  else "IDLE"
        panel.win.addstr(2, 2, f"Worker: {worker_status}", 
                        self.front.color_green if worker_status == "IDLE" 
                        else self.front.color_yellow)

    # =========================================================================
    # EVENT HANDLERS
    # =========================================================================

    def on_fetch_started(self, event_type, data, source):
        """Handle fetch start."""
        self.app.data["fetch_progress"] = 0
        self.print("Fetching tasks...")

    def on_fetch_progress(self, event_type, data, source):
        """Handle fetch progress updates."""
        percent = data.get("percent", 0)
        self.app.data["fetch_progress"] = int(percent)

    def on_fetch_completed(self, event_type, data, source):
        """Handle fetch completion."""
        tasks = data.get("tasks", [])
        self.app.data["tasks"] = tasks
        self.app.data["fetch_progress"] = 100
        self.print(f"Fetched {len(tasks)} tasks")

    def on_fetch_canceled(self, event_type, data, source):
        """Handle fetch cancellation."""
        self.app.data["fetch_progress"] = 0
        self.print("Fetch canceled")

    # =========================================================================
    # CALLBACKS
    # =========================================================================

    @callback(TaskListID, Keys.SPACE)
    def fetch_tasks(self, *args, **kwargs):
        """SPACE starts task fetching."""
        if self.fetcher and self.fetcher.is_running:
            self.print("Already fetching...")
            return
        
        self.fetcher = TaskFetcher(self.app.events)
        self.fetcher.start()

    @callback(TaskListID, Keys.R)
    def refresh(self, *args, **kwargs):
        """R refreshes the task list."""
        self.fetch_tasks()

    @callback(TaskListID, Keys.ENTER)
    def complete_task(self, *args, **kwargs):
        """ENTER marks task as complete."""
        tasks = self.app.data.get("tasks", [])
        selected = self.app.data.get("selected_task", 0)
        
        if not tasks or selected >= len(tasks):
            return
        
        task = tasks[selected]
        if task["status"] == "completed":
            task["status"] = "pending"
            self.print(f"Task {task['id']} marked pending")
        else:
            task["status"] = "completed"
            self.print(f"Task {task['id']} completed!")

    @callback(TaskListID, Keys.DOWN)
    def move_down(self, *args, **kwargs):
        """DOWN navigates down."""
        tasks = self.app.data.get("tasks", [])
        selected = self.app.data.get("selected_task", 0)
        
        if selected < len(tasks) - 1:
            self.app.data["selected_task"] = selected + 1

    @callback(TaskListID, Keys.UP)
    def move_up(self, *args, **kwargs):
        """UP navigates up."""
        selected = self.app.data.get("selected_task", 0)
        
        if selected > 0:
            self.app.data["selected_task"] = selected - 1

    @callback(TaskListID, Keys.Q)
    def quit(self, *args, **kwargs):
        """Q quits with cleanup."""
        # Stop worker if running
        if self.fetcher and self.fetcher.is_running:
            self.print("Stopping worker...")
            self.fetcher.stop()
        
        self.logic.should_stop = True


if __name__ == "__main__":
    app = App(
        modules=[TaskList],
        title="Task Manager",
        show_right=True,
        show_info=True,
        r_split=0.3,
    )
