#!/usr/bin/env python3
"""
Deterministic Python Print Statement Parser
Focused on complete print statement extraction for migration scripts

This parser extracts ALL print statements (not just emoji ones) and classifies
them by log level based on content analysis and context detection.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class PrintStatement:
    """Represents a print statement found in source code"""

    line_number: int
    full_statement: str
    message_content: str
    is_formatted: bool  # f-string or .format()
    arguments: list[str]
    context: str  # function, class, or global
    suggested_log_level: str  # DEBUG, INFO, WARN, ERROR
    migration_pattern: str


@dataclass
class ParseResult:
    """Complete parsing result for a Python file"""

    file_path: str
    print_statements: list[PrintStatement]
    total_prints: int
    needs_event_import: bool
    needs_logger_init: bool
    suggested_service_name: str


class PythonPrintParser:
    """Deterministic parser for Python print statements"""

    def __init__(self, constraints_path: str = "build/constraints/python.yml"):
        self.constraints = self._load_constraints(constraints_path)
        self._compile_patterns()

    def _load_constraints(self, path: str) -> dict[str, Any]:
        """Load parsing constraints from YAML file"""
        try:
            with open(path) as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            # Fallback to minimal constraints if file not found
            return {
                "log_level_classification": {
                    "error_indicators": ["❌", "error", "failed", "exception"],
                    "warning_indicators": ["⚠️", "warning", "warn", "deprecated"],
                    "info_indicators": ["✅", "🚀", "🎯", "info", "starting"],
                    "debug_indicators": ["🔧", "🔍", "debug", "testing"],
                }
            }

    def _compile_patterns(self):
        """Compile regex patterns for efficient parsing"""
        # Match ALL print statements (not just emoji ones)
        self.print_pattern = re.compile(r"^(\s*)print\s*\(\s*([^)]+)\s*\)", re.MULTILINE)

        # Detect f-strings
        self.fstring_pattern = re.compile(r'f["\'].*?["\']')

        # Context detection patterns
        self.function_pattern = re.compile(r"^(\s*)def\s+(\w+)\s*\(", re.MULTILINE)
        self.class_pattern = re.compile(r"^(\s*)class\s+(\w+)", re.MULTILINE)
        self.except_pattern = re.compile(r"^(\s*)except\b", re.MULTILINE)

        # Import detection
        self.event_import_pattern = re.compile(r"from events import")
        self.logger_init_pattern = re.compile(r"gui_logger\s*=\s*create_gui_logger")

    def parse_file(self, file_path: str) -> ParseResult:
        """Parse a Python file and extract all print statements"""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        print_statements = []

        # Find all print statements
        for match in self.print_pattern.finditer(content):
            line_num = content[: match.start()].count("\n") + 1
            indent = match.group(1)
            args_str = match.group(2)
            full_statement = match.group(0).strip()

            # Parse the print arguments
            message_content, is_formatted, arguments = self._parse_print_args(args_str)

            # Determine context (function, class, global)
            context = self._determine_context(content, match.start())

            # Classify log level based on content and context
            log_level = self._classify_log_level(message_content, context, line_num, lines)

            # Generate migration pattern
            migration_pattern = self._generate_migration_pattern(message_content, is_formatted, log_level)

            print_statements.append(
                PrintStatement(
                    line_number=line_num,
                    full_statement=full_statement,
                    message_content=message_content,
                    is_formatted=is_formatted,
                    arguments=arguments,
                    context=context,
                    suggested_log_level=log_level,
                    migration_pattern=migration_pattern,
                )
            )

        # Check if file needs imports
        needs_event_import = not bool(self.event_import_pattern.search(content))
        needs_logger_init = not bool(self.logger_init_pattern.search(content))

        # Suggest service name based on file path
        suggested_service_name = self._suggest_service_name(file_path)

        return ParseResult(
            file_path=file_path,
            print_statements=print_statements,
            total_prints=len(print_statements),
            needs_event_import=needs_event_import,
            needs_logger_init=needs_logger_init,
            suggested_service_name=suggested_service_name,
        )

    def _parse_print_args(self, args_str: str) -> tuple[str, bool, list[str]]:
        """Parse print statement arguments"""
        # Simple argument parsing (handles most common cases)
        args_str = args_str.strip()

        # Check if it's an f-string
        is_formatted = bool(self.fstring_pattern.search(args_str))

        # Extract main message (first argument)
        if args_str.startswith(('f"', "f'")):
            # F-string
            message_content = args_str
        elif args_str.startswith(('"', "'")):
            # Regular string
            quote_char = args_str[0]
            end_quote = args_str.find(quote_char, 1)
            if end_quote != -1:
                message_content = args_str[: end_quote + 1]
            else:
                message_content = args_str
        else:
            # Variable or complex expression
            message_content = args_str.split(",")[0].strip()

        # Split arguments (simple comma split for now)
        arguments = [arg.strip() for arg in args_str.split(",")]

        return message_content, is_formatted, arguments

    def _determine_context(self, content: str, position: int) -> str:
        """Determine the context (function, class, global) of a print statement"""
        # Find the most recent function or class definition before this position
        content_before = content[:position]

        # Find functions
        function_matches = list(self.function_pattern.finditer(content_before))
        class_matches = list(self.class_pattern.finditer(content_before))

        latest_function = function_matches[-1] if function_matches else None
        latest_class = class_matches[-1] if class_matches else None

        if latest_function and (not latest_class or latest_function.start() > latest_class.start()):
            return f"function:{latest_function.group(2)}"
        elif latest_class:
            return f"class:{latest_class.group(2)}"
        else:
            return "global"

    def _classify_log_level(self, message: str, context: str, line_num: int, lines: list[str]) -> str:
        """Classify the appropriate log level for a print statement"""
        # Ensure message is a string
        if not isinstance(message, str):
            message = str(message)
        message_lower = message.lower()

        # Get classification rules from constraints
        classification = self.constraints.get("log_level_classification", {})

        # Check for error indicators
        error_indicators = classification.get("error_indicators", [])
        for indicator in error_indicators:
            if indicator.lower() in message_lower:
                return "ERROR"

        # Check if in exception context
        if line_num > 0 and line_num <= len(lines):
            # Look at surrounding lines for except blocks
            for i in range(max(0, line_num - 5), min(len(lines), line_num + 2)):
                if "except" in lines[i] and ":" in lines[i]:
                    return "ERROR"

        # Check for warning indicators
        warning_indicators = classification.get("warning_indicators", [])
        for indicator in warning_indicators:
            if indicator.lower() in message_lower:
                return "WARN"

        # Check for debug indicators
        debug_indicators = classification.get("debug_indicators", [])
        for indicator in debug_indicators:
            if indicator.lower() in message_lower:
                return "DEBUG"

        # Check context for debug classification
        if "test" in context.lower() or "debug" in context.lower():
            return "DEBUG"

        # Default to INFO for most cases
        return "INFO"

    def _generate_migration_pattern(self, message: str, is_formatted: bool, log_level: str) -> str:
        """Generate the migration pattern for a print statement"""
        # Ensure inputs are strings
        if not isinstance(message, str):
            message = str(message)
        if not isinstance(log_level, str):
            log_level = str(log_level)

        method_name = log_level.lower()
        if method_name == "warn":
            method_name = "warn"  # Keep as warn, not warning

        if is_formatted:
            return f'gui_logger.{method_name}({message}, {{"event_type": "{log_level.lower()}"}})'
        else:
            return f'gui_logger.{method_name}({message}, {{"event_type": "{log_level.lower()}"}})'

    def _suggest_service_name(self, file_path: str) -> str:
        """Suggest a service name based on file path"""
        path = Path(file_path)

        # Extract meaningful name from path
        if "native_gui" in str(path):
            if path.stem == "launcher":
                return "unhinged-launcher"
            elif "tools" in str(path):
                tool_name = path.parent.name if path.parent.name != "tools" else path.stem
                return f"unhinged-{tool_name.replace('_', '-')}"
            else:
                return f"unhinged-{path.stem.replace('_', '-')}"
        elif "services" in str(path):
            service_name = path.parent.name if path.parent.name != "services" else path.stem
            return f"{service_name.replace('_', '-')}-service"
        else:
            return f"unhinged-{path.stem.replace('_', '-')}"


def extract_all_print_statements(file_path: str) -> list[PrintStatement]:
    """Convenience function to extract all print statements from a file"""
    parser = PythonPrintParser()
    result = parser.parse_file(file_path)
    return result.print_statements


def analyze_print_migration_needs(file_path: str) -> dict[str, Any]:
    """Analyze what's needed to migrate a file's print statements"""
    parser = PythonPrintParser()
    result = parser.parse_file(file_path)

    return {
        "file_path": result.file_path,
        "total_print_statements": result.total_prints,
        "needs_event_import": result.needs_event_import,
        "needs_logger_init": result.needs_logger_init,
        "suggested_service_name": result.suggested_service_name,
        "log_level_breakdown": {
            "ERROR": len([p for p in result.print_statements if p.suggested_log_level == "ERROR"]),
            "WARN": len([p for p in result.print_statements if p.suggested_log_level == "WARN"]),
            "INFO": len([p for p in result.print_statements if p.suggested_log_level == "INFO"]),
            "DEBUG": len([p for p in result.print_statements if p.suggested_log_level == "DEBUG"]),
        },
        "print_statements": result.print_statements,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        analysis = analyze_print_migration_needs(file_path)

        print(f"📊 Analysis for: {analysis['file_path']}")
        print(f"📈 Total print statements: {analysis['total_print_statements']}")
        print(f"📋 Log level breakdown: {analysis['log_level_breakdown']}")
        print(f"🔧 Needs event import: {analysis['needs_event_import']}")
        print(f"🔧 Needs logger init: {analysis['needs_logger_init']}")
        print(f"🏷️ Suggested service name: {analysis['suggested_service_name']}")

        print("\n📝 Print statements found:")
        for stmt in analysis["print_statements"]:
            print(f"  Line {stmt.line_number}: {stmt.suggested_log_level} - {stmt.full_statement[:60]}...")
    else:
        print("Usage: python3 python_parser.py <file_path>")
