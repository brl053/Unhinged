#!/usr/bin/env python3
"""
Example: MonacoEditor Integration Research
Demonstrates the complete workflow for your specific use case
"""
from orchestrator import ResearchOrchestrator
from rich.console import Console


def main():
    """Demonstrate MonacoEditor research workflow"""
    
    console = Console()
    orchestrator = ResearchOrchestrator()
    
    console.print("[bold cyan]MonacoEditor Integration Example[/bold cyan]")
    console.print("This demonstrates the exact workflow for your use case:\n")
    
    # Your original request
    request = "Please add MonacoEditor to the project"
    
    console.print(f"[bold]Your Request:[/bold] {request}")
    console.print("\n[dim]The orchestrator will now ask clarifying questions...[/dim]\n")
    
    # This will trigger the interactive workflow
    orchestrator.handle_request(request)


if __name__ == "__main__":
    main()
