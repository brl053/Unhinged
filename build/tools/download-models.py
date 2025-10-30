#!/usr/bin/env python3
"""
Model Downloader for Sovereign Image Generation

Downloads Stable Diffusion models for offline use.
Optimized for RTX 5070 Ti with 16GB VRAM.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict

try:
    from huggingface_hub import snapshot_download, hf_hub_download
    import requests
except ImportError:
    print("❌ Required dependencies not installed")
    print("💡 Install with: pip install huggingface-hub requests")
    sys.exit(1)

class ModelDownloader:
    """Downloads and manages Stable Diffusion models."""
    
    def __init__(self, models_dir: Path = Path("/models")):
        self.models_dir = Path(models_dir)
        self.cache_dir = self.models_dir / ".cache"
        
        # Ensure directories exist
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Model configurations optimized for RTX 5070 Ti
        self.models = {
            "sdxl": {
                "repo_id": "stabilityai/stable-diffusion-xl-base-1.0",
                "description": "Stable Diffusion XL - High quality 1024x1024 generation",
                "vram_required": "8GB+",
                "recommended": True
            },
            "sd15": {
                "repo_id": "runwayml/stable-diffusion-v1-5", 
                "description": "Stable Diffusion 1.5 - Fast 512x512 generation",
                "vram_required": "4GB+",
                "recommended": True
            },
            "sdxl_turbo": {
                "repo_id": "stabilityai/sdxl-turbo",
                "description": "SDXL Turbo - Ultra-fast generation (4 steps)",
                "vram_required": "8GB+",
                "recommended": False
            }
        }
    
    def download_model(self, model_key: str) -> bool:
        """Download a specific model."""
        if model_key not in self.models:
            print(f"❌ Unknown model: {model_key}")
            return False
        
        model_info = self.models[model_key]
        repo_id = model_info["repo_id"]
        
        print(f"📥 Downloading {repo_id}...")
        print(f"   Description: {model_info['description']}")
        print(f"   VRAM Required: {model_info['vram_required']}")
        
        try:
            # Download model to local directory
            local_dir = self.models_dir / model_key
            
            snapshot_download(
                repo_id=repo_id,
                cache_dir=str(self.cache_dir),
                local_dir=str(local_dir),
                local_dir_use_symlinks=False,
                ignore_patterns=["*.bin"]  # Prefer safetensors
            )
            
            print(f"✅ Downloaded {repo_id} to {local_dir}")
            
            # Create model info file
            info_file = local_dir / "model_info.txt"
            with open(info_file, 'w') as f:
                f.write(f"Model: {repo_id}\n")
                f.write(f"Description: {model_info['description']}\n")
                f.write(f"VRAM Required: {model_info['vram_required']}\n")
                f.write(f"Downloaded: {self._get_timestamp()}\n")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to download {repo_id}: {e}")
            return False
    
    def download_recommended(self) -> bool:
        """Download all recommended models."""
        print("🚀 Downloading recommended models for RTX 5070 Ti...")
        
        success_count = 0
        total_count = 0
        
        for model_key, model_info in self.models.items():
            if model_info["recommended"]:
                total_count += 1
                if self.download_model(model_key):
                    success_count += 1
        
        print(f"\n📊 Download Summary: {success_count}/{total_count} models downloaded successfully")
        return success_count == total_count
    
    def download_all(self) -> bool:
        """Download all available models."""
        print("🚀 Downloading all available models...")
        
        success_count = 0
        total_count = len(self.models)
        
        for model_key in self.models.keys():
            if self.download_model(model_key):
                success_count += 1
        
        print(f"\n📊 Download Summary: {success_count}/{total_count} models downloaded successfully")
        return success_count == total_count
    
    def list_models(self):
        """List available models."""
        print("📋 Available Models:")
        print()
        
        for model_key, model_info in self.models.items():
            status = "✅ Recommended" if model_info["recommended"] else "⚪ Optional"
            print(f"  {model_key}:")
            print(f"    Repository: {model_info['repo_id']}")
            print(f"    Description: {model_info['description']}")
            print(f"    VRAM Required: {model_info['vram_required']}")
            print(f"    Status: {status}")
            
            # Check if already downloaded
            local_dir = self.models_dir / model_key
            if local_dir.exists():
                print(f"    Local Status: 💾 Downloaded")
            else:
                print(f"    Local Status: ⬇️ Not downloaded")
            print()
    
    def check_disk_space(self) -> bool:
        """Check if there's enough disk space."""
        try:
            import shutil
            total, used, free = shutil.disk_usage(self.models_dir)
            
            # Estimate space needed (rough estimates)
            space_needed_gb = {
                "sdxl": 7,      # ~7GB for SDXL
                "sd15": 4,      # ~4GB for SD 1.5
                "sdxl_turbo": 7 # ~7GB for SDXL Turbo
            }
            
            total_needed = sum(space_needed_gb.values()) * 1024**3  # Convert to bytes
            
            print(f"💾 Disk Space Check:")
            print(f"   Available: {free / 1024**3:.1f} GB")
            print(f"   Estimated needed: {total_needed / 1024**3:.1f} GB")
            
            if free < total_needed:
                print(f"⚠️ Warning: May not have enough disk space")
                return False
            else:
                print(f"✅ Sufficient disk space available")
                return True
                
        except Exception as e:
            print(f"⚠️ Could not check disk space: {e}")
            return True  # Assume it's okay
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Download Stable Diffusion models")
    parser.add_argument("--models-dir", default="/models", help="Directory to store models")
    parser.add_argument("--list", action="store_true", help="List available models")
    parser.add_argument("--recommended", action="store_true", help="Download recommended models only")
    parser.add_argument("--all", action="store_true", help="Download all models")
    parser.add_argument("--model", help="Download specific model by key")
    
    args = parser.parse_args()
    
    downloader = ModelDownloader(Path(args.models_dir))
    
    if args.list:
        downloader.list_models()
        return
    
    # Check disk space
    if not downloader.check_disk_space():
        print("⚠️ Continuing anyway, but monitor disk space...")
    
    if args.recommended:
        success = downloader.download_recommended()
    elif args.all:
        success = downloader.download_all()
    elif args.model:
        success = downloader.download_model(args.model)
    else:
        # Default: download recommended models
        print("No specific action specified, downloading recommended models...")
        success = downloader.download_recommended()
    
    if success:
        print("\n🎉 Model download completed successfully!")
        print("💡 Models are ready for sovereign image generation")
    else:
        print("\n❌ Some downloads failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
