#!/usr/bin/env python3
"""
Setup script for Research Orchestrator
"""
import subprocess
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel


def install_dependencies():
    """Install Python dependencies"""
    console = Console()
    
    console.print("[bold cyan]Installing dependencies...[/bold cyan]")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        console.print("[green]✓ Dependencies installed successfully[/green]")
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"[red]✗ Failed to install dependencies: {e}[/red]")
        return False


def create_directories():
    """Create necessary directories"""
    console = Console()
    
    console.print("[bold cyan]Creating directories...[/bold cyan]")
    
    directories = [
        Path.home() / ".local/share/unhinged/research",
        Path.home() / ".local/share/unhinged/cache", 
        Path.home() / ".config/unhinged",
        Path(__file__).parent / "templates"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        console.print(f"  ✓ {directory}")
    
    console.print("[green]✓ Directories created[/green]")


def make_executable():
    """Make orchestrator.py executable"""
    console = Console()
    
    orchestrator_path = Path(__file__).parent / "orchestrator.py"
    
    try:
        orchestrator_path.chmod(0o755)
        console.print("[green]✓ Made orchestrator.py executable[/green]")
    except Exception as e:
        console.print(f"[yellow]⚠ Could not make executable: {e}[/yellow]")


def main():
    """Main setup function"""
    console = Console()
    
    console.print(Panel.fit(
        "[bold cyan]Research Orchestrator Setup[/bold cyan]\n"
        "Setting up AI-powered research and artifact generation",
        border_style="cyan"
    ))
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Make executable
    make_executable()
    
    console.print("\n[bold green]Setup Complete![/bold green]")
    console.print("\nNext steps:")
    console.print("1. Set up your Perplexity API key:")
    console.print("   [cyan]python orchestrator.py setup[/cyan]")
    console.print("\n2. Test the connection:")
    console.print("   [cyan]python orchestrator.py test[/cyan]")
    console.print("\n3. Start researching:")
    console.print("   [cyan]python orchestrator.py research 'Please add MonacoEditor to the project'[/cyan]")


if __name__ == "__main__":
    main()
