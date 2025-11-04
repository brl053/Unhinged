#!/usr/bin/env python3
"""
@llm-type build.automation
@llm-does GUI automation layer for autonomous testing and development

Provides structured interface for LLM agents to interact with GTK4 desktop application.
Uses accessibility APIs (AT-SPI2) and xdotool for reliable GUI automation.
"""

import subprocess
import time
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum


class ActionType(Enum):
    """Types of GUI actions"""
    CLICK = "click"
    TYPE = "type"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    FIND_WINDOW = "find_window"
    FOCUS_WINDOW = "focus_window"
    GET_CLIPBOARD = "get_clipboard"
    SET_CLIPBOARD = "set_clipboard"
    EXECUTE_COMMAND = "execute_command"


@dataclass
class GUIAction:
    """Structured GUI action"""
    action_type: ActionType
    target: Optional[str] = None
    value: Optional[str] = None
    timeout: int = 5
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_type": self.action_type.value,
            "target": self.target,
            "value": self.value,
            "timeout": self.timeout
        }


@dataclass
class GUIResult:
    """Result of GUI action"""
    success: bool
    action: Dict[str, Any]
    output: Optional[str] = None
    error: Optional[str] = None
    timestamp: float = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GUIAutomation:
    """
    GUI automation interface for autonomous development loop.
    
    Provides reliable, structured interaction with GTK4 desktop application.
    All actions are logged to /build/tmp/gui_automation.log for debugging.
    """
    
    def __init__(self, app_name: str = "unhinged", log_dir: Optional[Path] = None):
        self.app_name = app_name
        self.log_dir = log_dir or Path.cwd() / "build" / "tmp"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "gui_automation.log"
        self.actions_log: List[GUIResult] = []
    
    def _log_action(self, result: GUIResult) -> None:
        """Log action to file and memory"""
        self.actions_log.append(result)
        with open(self.log_file, "a") as f:
            f.write(json.dumps(result.to_dict()) + "\n")
    
    def click(self, x: int, y: int) -> GUIResult:
        """Click at coordinates"""
        try:
            subprocess.run(["xdotool", "mousemove", str(x), str(y)], check=True)
            subprocess.run(["xdotool", "click", "1"], check=True)
            result = GUIResult(
                success=True,
                action=GUIAction(ActionType.CLICK, value=f"{x},{y}").to_dict(),
                output=f"Clicked at ({x}, {y})"
            )
            self._log_action(result)
            return result
        except Exception as e:
            result = GUIResult(
                success=False,
                action=GUIAction(ActionType.CLICK, value=f"{x},{y}").to_dict(),
                error=str(e)
            )
            self._log_action(result)
            return result
    
    def type_text(self, text: str, delay: float = 0.05) -> GUIResult:
        """Type text with optional delay between characters"""
        try:
            for char in text:
                subprocess.run(["xdotool", "type", char], check=True)
                time.sleep(delay)
            result = GUIResult(
                success=True,
                action=GUIAction(ActionType.TYPE, value=text).to_dict(),
                output=f"Typed: {text}"
            )
            self._log_action(result)
            return result
        except Exception as e:
            result = GUIResult(
                success=False,
                action=GUIAction(ActionType.TYPE, value=text).to_dict(),
                error=str(e)
            )
            self._log_action(result)
            return result
    
    def wait(self, seconds: float) -> GUIResult:
        """Wait for specified duration"""
        try:
            time.sleep(seconds)
            result = GUIResult(
                success=True,
                action=GUIAction(ActionType.WAIT, value=str(seconds)).to_dict(),
                output=f"Waited {seconds} seconds"
            )
            self._log_action(result)
            return result
        except Exception as e:
            result = GUIResult(
                success=False,
                action=GUIAction(ActionType.WAIT, value=str(seconds)).to_dict(),
                error=str(e)
            )
            self._log_action(result)
            return result
    
    def find_window(self, window_name: str) -> GUIResult:
        """Find window by name"""
        try:
            output = subprocess.check_output(
                ["xdotool", "search", "--name", window_name],
                text=True
            ).strip()
            result = GUIResult(
                success=bool(output),
                action=GUIAction(ActionType.FIND_WINDOW, target=window_name).to_dict(),
                output=output
            )
            self._log_action(result)
            return result
        except Exception as e:
            result = GUIResult(
                success=False,
                action=GUIAction(ActionType.FIND_WINDOW, target=window_name).to_dict(),
                error=str(e)
            )
            self._log_action(result)
            return result
    
    def focus_window(self, window_id: str) -> GUIResult:
        """Focus window by ID"""
        try:
            subprocess.run(["xdotool", "windowactivate", window_id], check=True)
            result = GUIResult(
                success=True,
                action=GUIAction(ActionType.FOCUS_WINDOW, target=window_id).to_dict(),
                output=f"Focused window {window_id}"
            )
            self._log_action(result)
            return result
        except Exception as e:
            result = GUIResult(
                success=False,
                action=GUIAction(ActionType.FOCUS_WINDOW, target=window_id).to_dict(),
                error=str(e)
            )
            self._log_action(result)
            return result
    
    def get_logs(self) -> List[Dict[str, Any]]:
        """Get all logged actions"""
        return [r.to_dict() for r in self.actions_log]
    
    def clear_logs(self) -> None:
        """Clear action logs"""
        self.actions_log = []
        self.log_file.write_text("")


if __name__ == "__main__":
    # Example usage
    gui = GUIAutomation()
    print("GUI Automation initialized")
    print(f"Log file: {gui.log_file}")

