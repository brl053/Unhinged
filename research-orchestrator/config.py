"""
Configuration management for Research Orchestrator
"""
import os
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseSettings, Field
import json


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    perplexity_api_key: Optional[str] = Field(None, env="PERPLEXITY_API_KEY")
    perplexity_api_base: str = Field("https://api.perplexity.ai", env="PERPLEXITY_API_BASE")
    
    # Paths
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent.parent)
    templates_dir: Path = Field(default_factory=lambda: Path(__file__).parent / "templates")
    output_dir: Path = Field(default_factory=lambda: Path.home() / ".local/share/unhinged/research")
    cache_dir: Path = Field(default_factory=lambda: Path.home() / ".local/share/unhinged/cache")
    
    # Research Configuration
    default_model: str = "llama-3.1-sonar-large-128k-online"
    max_tokens: int = 4000
    temperature: float = 0.2
    cache_ttl: int = 3600  # 1 hour
    
    # Orchestrator Configuration
    interactive_mode: bool = True
    verbose: bool = False
    auto_generate_artifacts: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class SecureConfig:
    """Secure configuration management for API keys"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".config/unhinged"
        self.secrets_file = self.config_dir / "secrets.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Set secure permissions
        if self.config_dir.exists():
            os.chmod(self.config_dir, 0o700)
    
    def store_secret(self, key: str, value: str, description: str = "") -> bool:
        """Store a secret securely"""
        try:
            secrets = self._load_secrets()
            secrets[key] = {
                "value": value,
                "description": description,
                "created_at": str(Path().stat().st_mtime)
            }
            
            with open(self.secrets_file, 'w') as f:
                json.dump(secrets, f, indent=2)
            
            os.chmod(self.secrets_file, 0o600)
            return True
        except Exception as e:
            print(f"Error storing secret: {e}")
            return False
    
    def get_secret(self, key: str) -> Optional[str]:
        """Retrieve a secret"""
        try:
            secrets = self._load_secrets()
            return secrets.get(key, {}).get("value")
        except Exception:
            return None
    
    def list_secrets(self) -> Dict[str, str]:
        """List all stored secrets (without values)"""
        try:
            secrets = self._load_secrets()
            return {
                key: data.get("description", "No description")
                for key, data in secrets.items()
            }
        except Exception:
            return {}
    
    def _load_secrets(self) -> Dict[str, Any]:
        """Load secrets from file"""
        if not self.secrets_file.exists():
            return {}
        
        try:
            with open(self.secrets_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}


# Global settings instance
settings = Settings()
secure_config = SecureConfig()


def get_api_key() -> Optional[str]:
    """Get Perplexity API key from various sources"""
    # Try environment variable first
    if settings.perplexity_api_key:
        return settings.perplexity_api_key
    
    # Try secure config
    return secure_config.get_secret("PERPLEXITY_API_KEY")


def setup_api_key() -> bool:
    """Interactive API key setup"""
    from rich.console import Console
    from rich.prompt import Prompt
    
    console = Console()
    
    console.print("\n[bold cyan]Perplexity API Key Setup[/bold cyan]")
    console.print("Get your API key from: https://www.perplexity.ai/api-platform")
    
    api_key = Prompt.ask("Enter your Perplexity API key", password=True)
    
    if api_key:
        success = secure_config.store_secret(
            "PERPLEXITY_API_KEY", 
            api_key, 
            "Perplexity AI API key for research orchestrator"
        )
        
        if success:
            console.print("[green]✓ API key stored securely[/green]")
            return True
        else:
            console.print("[red]✗ Failed to store API key[/red]")
            return False
    
    return False


def ensure_directories():
    """Ensure all required directories exist"""
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    settings.cache_dir.mkdir(parents=True, exist_ok=True)
    settings.templates_dir.mkdir(parents=True, exist_ok=True)


# Initialize directories on import
ensure_directories()
