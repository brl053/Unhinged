# Autonomous Development Loop - LLM Agent Framework

> **Purpose**: Enable LLM agents (like Augment) to autonomously develop, test, and iterate on the Unhinged system through a structured, feedback-driven development loop.

## Overview

The autonomous development loop shifts development from manual VS Code interactions to a **structured task-based system** where:

1. **User** describes what they want: "Make the `/image` command work"
2. **LLM Agent** (Augment) executes tasks autonomously through the development loop
3. **System** provides structured feedback via logs in `/build/tmp/`
4. **LLM Agent** iterates based on feedback until task is complete

## Architecture

### Three Core Components

#### 1. **Development Loop Orchestrator** (`build/development_loop.py`)
- Manages task lifecycle (create → start → complete/fail)
- Executes shell commands with full logging
- Provides structured feedback to LLM agents
- All tasks logged to `/build/tmp/development_loop.log`

#### 2. **GUI Automation Layer** (`build/gui_automation.py`)
- Interacts with GTK4 desktop application
- Uses xdotool + AT-SPI2 for reliable automation
- Supports: click, type, wait, find_window, focus_window
- All actions logged to `/build/tmp/gui_automation.log`

#### 3. **Task Protocol** (JSON-based)
- Structured format for defining development tasks
- Supports: code_change, test, gui_test, verification
- Each task has: id, name, description, instructions, status, result

## Task Types

- **code_change**: Modify source files
- **test**: Run unit/integration tests
- **gui_test**: Test through GUI automation
- **verification**: Verify system state

## Logging & Feedback

### Development Loop Log
**Location**: `/build/tmp/development_loop.log`

Each line is a JSON object with task state and timestamps.

### GUI Automation Log
**Location**: `/build/tmp/gui_automation.log`

Each line is a JSON object with action result.

## Usage Example

```python
from build.development_loop import DevelopmentLoop

loop = DevelopmentLoop()

# Create task
task = loop.create_task(
    task_id="test_001",
    name="Test image generation",
    description="Verify /image command works",
    task_type="test",
    instructions={"command": "python3 test_image_command.py"}
)

# Execute
loop.start_task(task)
result = loop.execute_shell_command("python3 test_image_command.py")
loop.complete_task(task, result)
```

## Best Practices for LLM Agents

1. **Always check logs first** - Read `/build/tmp/development_loop.log` before creating new tasks
2. **Use structured tasks** - Don't execute arbitrary commands, use the task protocol
3. **Log everything** - All actions should be logged for debugging
4. **Fail fast** - If a task fails, analyze the error and create a fix task
5. **Iterate systematically** - Don't make multiple changes at once
6. **Verify after changes** - Always create a verification task after code changes

## Files

- `build/development_loop.py` - Task orchestrator
- `build/gui_automation.py` - GUI automation layer
- `build/test_autonomous_loop.py` - Example test
- `docs/AUTONOMOUS_LOOP_GUIDE.md` - This file

