#!/usr/bin/env python3
"""
Research Orchestrator - Interactive AI-powered research and artifact generation
"""
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from config import settings, setup_api_key, get_api_key
from perplexity_client import PerplexityClient, ResearchQuery
from artifact_generator import ArtifactGenerator


class ResearchOrchestrator:
    """Main orchestrator for interactive research and artifact generation"""
    
    def __init__(self):
        self.console = Console()
        self.client = None
        self.artifact_generator = ArtifactGenerator()
        
        # Initialize client if API key is available
        try:
            if get_api_key():
                self.client = PerplexityClient()
        except ValueError:
            pass  # Will prompt for setup when needed
    
    def greet(self):
        """Display welcome message"""
        self.console.print(Panel.fit(
            "[bold cyan]Research Orchestrator[/bold cyan]\n"
            "AI-powered research and artifact generation for Unhinged Platform\n\n"
            "[dim]Tell me what you'd like to add to the project, and I'll help you research and implement it.[/dim]",
            border_style="cyan"
        ))
    
    def handle_request(self, request: str) -> None:
        """Handle a research request with interactive questioning"""
        
        self.console.print(f"\n[bold]Request:[/bold] {request}")
        
        # Parse the request to understand what's being asked
        context = self._analyze_request(request)
        
        # Ask clarifying questions
        refined_context = self._ask_clarifying_questions(context)
        
        # Confirm the research plan
        if not self._confirm_research_plan(refined_context):
            self.console.print("[yellow]Research cancelled.[/yellow]")
            return
        
        # Ensure we have API access
        if not self._ensure_api_access():
            return
        
        # Conduct research
        research_response = self._conduct_research(refined_context)
        
        # Generate artifacts
        artifacts = self._generate_artifacts(research_response, refined_context)
        
        # Present results
        self._present_results(research_response, artifacts, refined_context)
    
    def _analyze_request(self, request: str) -> Dict[str, Any]:
        """Analyze the request to understand intent and extract key information"""
        
        request_lower = request.lower()
        
        # Detect technology/library
        technology = None
        for tech in ["monacoeditor", "monaco", "react", "typescript", "graphql", "api"]:
            if tech in request_lower:
                technology = tech
                break
        
        # Detect intent
        intent = "integration"  # default
        if any(word in request_lower for word in ["add", "integrate", "implement"]):
            intent = "integration"
        elif any(word in request_lower for word in ["compare", "vs", "versus"]):
            intent = "comparison"
        elif any(word in request_lower for word in ["research", "learn", "understand"]):
            intent = "research"
        
        # Detect platform context
        platform_context = "unhinged" if "unhinged" in request_lower else "general"
        
        return {
            "original_request": request,
            "technology": technology,
            "intent": intent,
            "platform_context": platform_context,
            "complexity": "unknown"
        }
    
    def _ask_clarifying_questions(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Ask interactive clarifying questions based on the context"""
        
        self.console.print("\n[bold cyan]Let me ask a few questions to better understand your needs:[/bold cyan]\n")
        
        # Question 1: Integration type
        if context["intent"] == "integration":
            integration_types = [
                "React component wrapper",
                "Standalone JavaScript integration", 
                "API client/wrapper",
                "Backend service integration",
                "Full-stack implementation"
            ]
            
            context["integration_type"] = Prompt.ask(
                "What type of integration do you need?",
                choices=[str(i) for i in range(1, len(integration_types) + 1)],
                show_choices=False
            )
            
            # Display choices
            table = Table(show_header=False)
            for i, choice in enumerate(integration_types, 1):
                table.add_row(f"{i}.", choice)
            self.console.print(table)
            
            context["integration_type"] = integration_types[int(context["integration_type"]) - 1]
        
        # Question 2: Use case
        context["use_case"] = Prompt.ask(
            "\nWhat's your primary use case?",
            default="General purpose implementation"
        )
        
        # Question 3: Experience level target
        experience_levels = ["Quick setup", "Balanced approach", "Full customization", "Enterprise-grade"]
        
        table = Table(show_header=False)
        for i, level in enumerate(experience_levels, 1):
            table.add_row(f"{i}.", level)
        self.console.print(table)
        
        level_choice = Prompt.ask(
            "What level of implementation depth do you need?",
            choices=[str(i) for i in range(1, len(experience_levels) + 1)],
            default="3"
        )
        context["depth"] = experience_levels[int(level_choice) - 1]
        
        # Question 4: Platform-specific requirements
        if context["platform_context"] == "unhinged":
            platform_features = []
            
            if Confirm.ask("Do you need Unhinged Platform theme integration?"):
                platform_features.append("theming")
            
            if Confirm.ask("Do you need authentication integration?"):
                platform_features.append("auth")
            
            if Confirm.ask("Do you need real-time collaboration features?"):
                platform_features.append("realtime")
            
            context["platform_features"] = platform_features
        
        # Question 5: Additional requirements
        context["additional_requirements"] = Prompt.ask(
            "\nAny additional requirements or constraints?",
            default=""
        )
        
        return context
    
    def _confirm_research_plan(self, context: Dict[str, Any]) -> bool:
        """Confirm the research plan with the user"""
        
        self.console.print("\n[bold green]Research Plan:[/bold green]")
        
        plan_table = Table(show_header=False, box=None)
        plan_table.add_row("[bold]Technology:[/bold]", context.get("technology", "Unknown"))
        plan_table.add_row("[bold]Integration Type:[/bold]", context.get("integration_type", "N/A"))
        plan_table.add_row("[bold]Use Case:[/bold]", context["use_case"])
        plan_table.add_row("[bold]Depth:[/bold]", context["depth"])
        plan_table.add_row("[bold]Platform Features:[/bold]", ", ".join(context.get("platform_features", [])))
        
        self.console.print(plan_table)
        
        return Confirm.ask("\nProceed with this research plan?", default=True)
    
    def _ensure_api_access(self) -> bool:
        """Ensure we have API access"""
        if self.client:
            return True
        
        self.console.print("\n[yellow]Perplexity API key required for research.[/yellow]")
        
        if Confirm.ask("Would you like to set up your API key now?"):
            if setup_api_key():
                try:
                    self.client = PerplexityClient()
                    return True
                except ValueError:
                    self.console.print("[red]Failed to initialize client with new API key.[/red]")
                    return False
            else:
                return False
        else:
            self.console.print("[yellow]Cannot proceed without API key.[/yellow]")
            return False
    
    def _conduct_research(self, context: Dict[str, Any]) -> Any:
        """Conduct the actual research"""
        
        # Map context to research query
        focus_mapping = {
            "React component wrapper": "react-wrapper",
            "API client/wrapper": "api-integration",
            "Backend service integration": "backend-integration",
            "Full-stack implementation": "fullstack"
        }
        
        depth_mapping = {
            "Quick setup": "implementation",
            "Balanced approach": "senior-ic", 
            "Full customization": "senior-ic",
            "Enterprise-grade": "architect"
        }
        
        query = ResearchQuery(
            topic=context.get("technology", "Unknown Technology"),
            focus=focus_mapping.get(context.get("integration_type", ""), "implementation"),
            depth=depth_mapping.get(context["depth"], "senior-ic"),
            context=context,
            custom_instructions=self._build_custom_instructions(context)
        )
        
        self.console.print(f"\n[bold]Researching {query.topic}...[/bold]")
        
        return self.client.research(query)
    
    def _build_custom_instructions(self, context: Dict[str, Any]) -> str:
        """Build custom instructions based on context"""
        
        instructions = []
        
        if context.get("platform_features"):
            instructions.append(f"Include integration with Unhinged Platform features: {', '.join(context['platform_features'])}")
        
        if context.get("additional_requirements"):
            instructions.append(f"Additional requirements: {context['additional_requirements']}")
        
        if context.get("use_case"):
            instructions.append(f"Optimize for use case: {context['use_case']}")
        
        return "\n".join(instructions)
    
    def _generate_artifacts(self, research_response: Any, context: Dict[str, Any]) -> List[Path]:
        """Generate code artifacts based on research"""
        
        self.console.print("\n[bold]Generating artifacts...[/bold]")
        
        return self.artifact_generator.generate_from_research(research_response, context)
    
    def _present_results(self, research_response: Any, artifacts: List[Path], context: Dict[str, Any]) -> None:
        """Present the research results and artifacts to the user"""
        
        self.console.print("\n" + "="*80)
        self.console.print("[bold green]Research Complete![/bold green]")
        self.console.print("="*80)
        
        # Show research summary
        self.console.print(f"\n[bold]Research Summary for {context.get('technology', 'Unknown')}:[/bold]")
        
        # Display main content (truncated)
        content_preview = research_response.content[:500] + "..." if len(research_response.content) > 500 else research_response.content
        self.console.print(Panel(content_preview, title="Research Content Preview", border_style="blue"))
        
        # Show citations
        if research_response.citations:
            self.console.print(f"\n[bold]Sources ({len(research_response.citations)}):[/bold]")
            for i, citation in enumerate(research_response.citations[:5], 1):
                self.console.print(f"  {i}. {citation}")
        
        # Show generated artifacts
        if artifacts:
            self.console.print(f"\n[bold]Generated Artifacts ({len(artifacts)}):[/bold]")
            for artifact in artifacts:
                self.console.print(f"  📄 {artifact}")
        
        # Show related questions
        if research_response.related_questions:
            self.console.print(f"\n[bold]Related Questions for Further Research:[/bold]")
            for question in research_response.related_questions[:3]:
                self.console.print(f"  • {question}")
        
        # Save full research report
        report_path = self._save_research_report(research_response, context)
        self.console.print(f"\n[bold]Full research report saved to:[/bold] {report_path}")
        
        self.console.print(f"\n[dim]All artifacts are ready for integration into your Unhinged Platform project![/dim]")
    
    def _save_research_report(self, research_response: Any, context: Dict[str, Any]) -> Path:
        """Save the complete research report"""
        
        timestamp = int(research_response.metadata["timestamp"])
        safe_topic = "".join(c for c in context.get("technology", "research") if c.isalnum() or c in "-_")
        
        report_path = settings.output_dir / f"{safe_topic}_research_report_{timestamp}.md"
        
        with open(report_path, 'w') as f:
            f.write(f"# Research Report: {context.get('technology', 'Unknown')}\n\n")
            f.write(f"**Generated:** {research_response.metadata.get('timestamp')}\n")
            f.write(f"**Integration Type:** {context.get('integration_type', 'N/A')}\n")
            f.write(f"**Use Case:** {context['use_case']}\n")
            f.write(f"**Depth:** {context['depth']}\n\n")
            f.write("---\n\n")
            f.write(research_response.content)
            f.write("\n\n---\n\n")
            
            if research_response.citations:
                f.write("## Sources\n\n")
                for citation in research_response.citations:
                    f.write(f"- {citation}\n")
                f.write("\n")
            
            if research_response.related_questions:
                f.write("## Related Questions\n\n")
                for question in research_response.related_questions:
                    f.write(f"- {question}\n")
        
        return report_path


@click.group()
def cli():
    """Research Orchestrator - AI-powered research and artifact generation"""
    pass


@cli.command()
@click.argument('request', required=False)
@click.option('--interactive', '-i', is_flag=True, help='Force interactive mode')
def research(request: Optional[str], interactive: bool):
    """Conduct interactive research based on a request"""
    
    orchestrator = ResearchOrchestrator()
    orchestrator.greet()
    
    if not request:
        request = Prompt.ask("\n[bold]What would you like to add to the project?[/bold]")
    
    orchestrator.handle_request(request)


@cli.command()
def setup():
    """Set up API keys and configuration"""
    console = Console()
    console.print("[bold cyan]Research Orchestrator Setup[/bold cyan]\n")
    
    if setup_api_key():
        console.print("[green]Setup complete![/green]")
    else:
        console.print("[red]Setup failed.[/red]")


@cli.command()
def test():
    """Test API connection"""
    console = Console()
    
    try:
        client = PerplexityClient()
        if client.test_connection():
            console.print("[green]✓ API connection successful[/green]")
        else:
            console.print("[red]✗ API connection failed[/red]")
    except ValueError as e:
        console.print(f"[red]✗ {e}[/red]")


if __name__ == "__main__":
    cli()
