#!/usr/bin/env python3
"""
@llm-type build.orchestration
@llm-does Autonomous development loop orchestrator

Provides structured task execution framework for LLM agents.
Tasks are defined in JSON format and executed with full logging and feedback.
"""

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

# Import subprocess utilities
try:
    from subprocess_utils import SubprocessRunner
except ImportError:
    # Fallback if subprocess_utils not available
    SubprocessRunner = None


class TaskStatus(Enum):
    """Task execution status"""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class Task:
    """Structured development task"""

    id: str
    name: str
    description: str
    task_type: str  # "code_change", "test", "gui_test", "verification"
    instructions: dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    result: dict[str, Any] | None = None
    error: str | None = None
    started_at: str | None = None
    completed_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "task_type": self.task_type,
            "instructions": self.instructions,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }


class DevelopmentLoop:
    """
    Autonomous development loop orchestrator.

    Manages task execution, logging, and feedback for LLM agents.
    All tasks and results logged to /build/tmp/development_loop.log
    """

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()
        self.log_dir = self.project_root / "build" / "tmp"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "development_loop.log"
        self.tasks: list[Task] = []
        self.current_task: Task | None = None

    def create_task(
        self, task_id: str, name: str, description: str, task_type: str, instructions: dict[str, Any]
    ) -> Task:
        """Create a new task"""
        task = Task(id=task_id, name=name, description=description, task_type=task_type, instructions=instructions)
        self.tasks.append(task)
        self._log_task(task)
        return task

    def start_task(self, task: Task) -> None:
        """Start task execution"""
        self.current_task = task
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now().isoformat()
        self._log_task(task)

    def complete_task(self, task: Task, result: dict[str, Any]) -> None:
        """Mark task as complete"""
        task.status = TaskStatus.SUCCESS
        task.result = result
        task.completed_at = datetime.now().isoformat()
        self._log_task(task)

    def fail_task(self, task: Task, error: str) -> None:
        """Mark task as failed"""
        task.status = TaskStatus.FAILED
        task.error = error
        task.completed_at = datetime.now().isoformat()
        self._log_task(task)

    def _log_task(self, task: Task) -> None:
        """Log task to file"""
        with open(self.log_file, "a") as f:
            f.write(json.dumps(task.to_dict()) + "\n")

    def get_task_summary(self) -> dict[str, Any]:
        """Get summary of all tasks"""
        return {
            "total": len(self.tasks),
            "pending": sum(1 for t in self.tasks if t.status == TaskStatus.PENDING),
            "running": sum(1 for t in self.tasks if t.status == TaskStatus.RUNNING),
            "success": sum(1 for t in self.tasks if t.status == TaskStatus.SUCCESS),
            "failed": sum(1 for t in self.tasks if t.status == TaskStatus.FAILED),
            "tasks": [t.to_dict() for t in self.tasks],
        }

    def execute_shell_command(self, command: str, cwd: Path | None = None) -> dict[str, Any]:
        """Execute shell command and return result"""
        runner = SubprocessRunner(timeout=300)
        result = runner.run_shell(command, cwd=cwd or self.project_root)
        return {
            "success": result["success"],
            "stdout": result["output"],
            "stderr": result["error"],
            "returncode": result["returncode"],
        }


if __name__ == "__main__":
    loop = DevelopmentLoop()
    print("Development loop initialized")
    print(f"Log file: {loop.log_file}")
