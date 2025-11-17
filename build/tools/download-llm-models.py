#!/usr/bin/env python3
"""
LLM Model Downloader for Unhinged

Downloads LLM models to local Ollama service.
Optimized for on-premise deployment with mobile device support.

Minimum target: Google Pixel 9XL (4GB RAM)
Default: Mistral 7B (3.5GB quantized)
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List


class OllamaModelManager:
    """Manages LLM models for local Ollama service."""

    def __init__(self):
        self.ollama_host = "http://localhost:1500"
        
        # Models optimized for different device classes
        # All quantized to fit 4GB RAM minimum (Pixel 9XL)
        self.models = {
            "mistral": {
                "name": "mistral:latest",
                "size_gb": 3.5,
                "ram_required": "4GB",
                "description": "Mistral 7B - Fast reasoning, good quality",
                "recommended": True,
                "tier": "mobile",
            },
            "neural-chat": {
                "name": "neural-chat:latest",
                "size_gb": 3.8,
                "ram_required": "4GB",
                "description": "Neural Chat 7B - Conversational, optimized",
                "recommended": False,
                "tier": "mobile",
            },
            "llama2": {
                "name": "llama2:latest",
                "size_gb": 3.8,
                "ram_required": "4GB",
                "description": "Llama 2 7B - General purpose",
                "recommended": False,
                "tier": "mobile",
            },
        }

    def check_ollama_running(self) -> bool:
        """Check if Ollama service is running."""
        try:
            result = subprocess.run(
                ["curl", "-s", f"{self.ollama_host}/api/tags"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

    def pull_model(self, model_key: str) -> bool:
        """Pull a model from Ollama registry."""
        if model_key not in self.models:
            print(f"❌ Unknown model: {model_key}")
            return False

        model_info = self.models[model_key]
        model_name = model_info["name"]

        print(f"📥 Pulling {model_name}...")
        print(f"   Size: {model_info['size_gb']}GB")
        print(f"   RAM Required: {model_info['ram_required']}")

        try:
            # Try docker exec first (container deployment)
            result = subprocess.run(
                ["docker", "exec", "ollama-service", "ollama", "pull", model_name],
                capture_output=False,
            )
            if result.returncode == 0:
                print(f"✅ Successfully pulled {model_name}")
                return True

            # Fallback to local ollama command
            result = subprocess.run(
                ["ollama", "pull", model_name],
                capture_output=False,
            )
            if result.returncode == 0:
                print(f"✅ Successfully pulled {model_name}")
                return True

            print(f"❌ Failed to pull {model_name}")
            return False

        except Exception as e:
            print(f"❌ Error pulling {model_name}: {e}")
            return False

    def list_models(self) -> None:
        """List available models."""
        print("📋 Available LLM Models (Mobile-Optimized):\n")
        for key, info in self.models.items():
            status = "⭐ RECOMMENDED" if info["recommended"] else "  Optional"
            print(f"  {key}:")
            print(f"    Name: {info['name']}")
            print(f"    Size: {info['size_gb']}GB")
            print(f"    RAM: {info['ram_required']}")
            print(f"    Description: {info['description']}")
            print(f"    Status: {status}\n")

    def pull_recommended(self) -> bool:
        """Pull recommended models for mobile deployment."""
        print("🚀 Pulling recommended models for mobile deployment...\n")
        
        if not self.check_ollama_running():
            print("❌ Ollama service not running at localhost:1500")
            print("   Start with: docker-compose up llm")
            return False

        success = True
        for key, info in self.models.items():
            if info["recommended"]:
                if not self.pull_model(key):
                    success = False

        return success


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Download LLM models for Unhinged (on-premise)"
    )
    parser.add_argument(
        "--list", action="store_true", help="List available models"
    )
    parser.add_argument(
        "--model", help="Download specific model by key"
    )
    parser.add_argument(
        "--recommended", action="store_true", help="Download recommended models"
    )

    args = parser.parse_args()
    manager = OllamaModelManager()

    if args.list:
        manager.list_models()
        return 0

    if args.recommended or (not args.model):
        success = manager.pull_recommended()
        return 0 if success else 1

    if args.model:
        success = manager.pull_model(args.model)
        return 0 if success else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

