#!/usr/bin/env python3
"""
@llm-type build.orchestration
@llm-does Autonomous development loop orchestrator

Provides structured task execution framework for LLM agents.
Tasks are defined in JSON format and executed with full logging and feedback.
"""

import json
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


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
    instructions: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
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
            "completed_at": self.completed_at
        }


class DevelopmentLoop:
    """
    Autonomous development loop orchestrator.
    
    Manages task execution, logging, and feedback for LLM agents.
    All tasks and results logged to /build/tmp/development_loop.log
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.log_dir = self.project_root / "build" / "tmp"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "development_loop.log"
        self.tasks: List[Task] = []
        self.current_task: Optional[Task] = None
    
    def create_task(self, task_id: str, name: str, description: str,
                   task_type: str, instructions: Dict[str, Any]) -> Task:
        """Create a new task"""
        task = Task(
            id=task_id,
            name=name,
            description=description,
            task_type=task_type,
            instructions=instructions
        )
        self.tasks.append(task)
        self._log_task(task)
        return task
    
    def start_task(self, task: Task) -> None:
        """Start task execution"""
        self.current_task = task
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now().isoformat()
        self._log_task(task)
    
    def complete_task(self, task: Task, result: Dict[str, Any]) -> None:
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
    
    def get_task_summary(self) -> Dict[str, Any]:
        """Get summary of all tasks"""
        return {
            "total": len(self.tasks),
            "pending": sum(1 for t in self.tasks if t.status == TaskStatus.PENDING),
            "running": sum(1 for t in self.tasks if t.status == TaskStatus.RUNNING),
            "success": sum(1 for t in self.tasks if t.status == TaskStatus.SUCCESS),
            "failed": sum(1 for t in self.tasks if t.status == TaskStatus.FAILED),
            "tasks": [t.to_dict() for t in self.tasks]
        }
    
    def execute_shell_command(self, command: str, cwd: Optional[Path] = None) -> Dict[str, Any]:
        """Execute shell command and return result"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timeout (300s)",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "returncode": -1
            }


if __name__ == "__main__":
    loop = DevelopmentLoop()
    print("Development loop initialized")
    print(f"Log file: {loop.log_file}")

