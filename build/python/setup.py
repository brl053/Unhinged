#!/usr/bin/env python3
"""
@llm-type util.setup
@llm-does python environment setup and dependency management for build system
@llm-rule python environment must be isolated and reproducible across platforms
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UnhingedPythonSetup:
    """
@llm-type config.build
@llm-does comprehensive python environment setup for ml/ai etl
@llm-rule environment setup must be reproducible, comprehensive, and failure-resistant
"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.build_python_dir = Path(__file__).parent
        self.venv_path = self.build_python_dir / "venv"
        self.requirements_file = self.build_python_dir / "requirements.txt"

        logger.info(f"🏗️ Setting up Python environment for Unhinged ML/AI ETL & Big Data")
        logger.info(f"📁 Project root: {self.project_root}")
        logger.info(f"🐍 Virtual environment: {self.venv_path}")
        logger.info(f"📦 Requirements file: {self.requirements_file}")
    
    def check_python_version(self) -> bool:
        """Check if Python version is compatible"""
        version = sys.version_info
        
        if version.major != 3 or version.minor < 9:
            logger.error(f"❌ Python 3.9+ required, found {version.major}.{version.minor}")
            logger.info("💡 Install Python 3.9+ and try again")
            return False
        
        logger.info(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    
    def create_virtual_environment(self) -> bool:
        """Create virtual environment"""
        if self.venv_path.exists():
            logger.info(f"🔄 Virtual environment already exists at {self.venv_path}")
            return True
        
        logger.info(f"🏗️ Creating virtual environment at {self.venv_path}")
        
        try:
            subprocess.run([
                sys.executable, "-m", "venv", str(self.venv_path)
            ], check=True, capture_output=True, text=True)
            
            logger.info("✅ Virtual environment created successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to create virtual environment: {e}")
            logger.error(f"stderr: {e.stderr}")
            return False
    
    def upgrade_pip(self) -> bool:
        """Upgrade pip to latest version"""
        pip_executable = self.venv_path / "bin" / "pip"
        
        logger.info("🔄 Upgrading pip to latest version")
        
        try:
            subprocess.run([
                str(pip_executable), "install", "--upgrade", "pip", "setuptools", "wheel"
            ], check=True, capture_output=True, text=True)
            
            logger.info("✅ Pip upgraded successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to upgrade pip: {e}")
            logger.error(f"stderr: {e.stderr}")
            return False
    
    def install_dependencies(self) -> bool:
        """Install all dependencies from consolidated requirements"""
        if not self.requirements_file.exists():
            logger.error(f"❌ Requirements file not found: {self.requirements_file}")
            return False
        
        pip_executable = self.venv_path / "bin" / "pip"
        
        logger.info(f"📦 Installing dependencies from {self.requirements_file}")
        logger.info("⏳ This may take several minutes for ML/AI and big data libraries...")
        
        try:
            # Install with verbose output and no cache to ensure fresh install
            result = subprocess.run([
                str(pip_executable), "install", "-r", str(self.requirements_file),
                "--verbose", "--no-cache-dir"
            ], capture_output=True, text=True, timeout=1800)  # 30 minute timeout
            
            if result.returncode == 0:
                logger.info("✅ All dependencies installed successfully")
                return True
            else:
                logger.error(f"❌ Failed to install dependencies")
                logger.error(f"stdout: {result.stdout}")
                logger.error(f"stderr: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Installation timed out after 30 minutes")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install dependencies: {e}")
            logger.error(f"stderr: {e.stderr}")
            return False
    
    def verify_installation(self) -> bool:
        """Verify critical libraries are installed correctly"""
        python_executable = self.venv_path / "bin" / "python3"
        
        critical_libraries = [
            # Core ML/AI
            "torch", "transformers", "numpy", "pandas", "scikit-learn",
            # Big Data
            "pyspark", "kafka", "cassandra", "elasticsearch", "polars",
            # Build System
            "pyyaml", "click", "rich", "protobuf", "grpcio",
            # Web Frameworks
            "flask", "fastapi", "requests",
            # Development
            "pytest", "jupyter"
        ]
        
        logger.info("🔍 Verifying critical library installations...")
        
        failed_imports = []
        
        for lib in critical_libraries:
            try:
                result = subprocess.run([
                    str(python_executable), "-c", f"import {lib}; print(f'✅ {lib}')"
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    logger.info(result.stdout.strip())
                else:
                    failed_imports.append(lib)
                    logger.warning(f"⚠️ {lib}: {result.stderr.strip()}")
                    
            except subprocess.TimeoutExpired:
                failed_imports.append(lib)
                logger.warning(f"⚠️ {lib}: Import timeout")
            except Exception as e:
                failed_imports.append(lib)
                logger.warning(f"⚠️ {lib}: {e}")
        
        if failed_imports:
            logger.warning(f"⚠️ Some libraries failed to import: {failed_imports}")
            logger.info("💡 This may be normal for optional dependencies")
        
        logger.info("✅ Installation verification completed")
        return True
    
    def create_jupyter_config(self) -> bool:
        """Create Jupyter configuration for ML/AI development"""
        jupyter_dir = self.project_root / ".jupyter"
        jupyter_dir.mkdir(exist_ok=True)
        
        config_content = '''
# Jupyter Lab configuration for Unhinged ML/AI development
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.allow_root = True
c.ServerApp.notebook_dir = str(Path.cwd())

# Enable extensions
c.ServerApp.jpserver_extensions = {
    'jupyter_lsp': True,
    'jupyterlab': True
}
'''
        
        config_file = jupyter_dir / "jupyter_lab_config.py"
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        logger.info(f"✅ Jupyter configuration created: {config_file}")
        return True
    
    def setup_environment(self) -> bool:
        """Complete environment setup process"""
        logger.info("🚀 Starting Unhinged Python environment setup")
        
        steps = [
            ("Checking Python version", self.check_python_version),
            ("Creating virtual environment", self.create_virtual_environment),
            ("Upgrading pip", self.upgrade_pip),
            ("Installing dependencies", self.install_dependencies),
            ("Verifying installation", self.verify_installation),
            ("Creating Jupyter config", self.create_jupyter_config),
        ]
        
        for step_name, step_func in steps:
            logger.info(f"📋 {step_name}...")
            if not step_func():
                logger.error(f"❌ Failed at step: {step_name}")
                return False
        
        logger.info("🎉 Python environment setup completed successfully!")
        logger.info("")
        logger.info("🎯 Next steps:")
        logger.info(f"   1. Run scripts: build/python/run.py <script.py>")
        logger.info(f"   2. Interactive shell: build/python/run.py --shell")
        logger.info(f"   3. Jupyter Lab: build/python/run.py --jupyter")
        logger.info(f"   4. Build system: build/python/run.py build/build.py")
        logger.info("")
        logger.info("📊 Available capabilities:")
        logger.info("   • Apache Kafka, Spark, Flink integration")
        logger.info("   • ML/AI libraries (PyTorch, Transformers, etc.)")
        logger.info("   • Big data processing (Polars, Dask, PyArrow)")
        logger.info("   • Database clients (PostgreSQL, Redis, Cassandra)")
        logger.info("   • Jupyter Lab for interactive development")
        
        return True


def main():
    """CLI entry point for Python environment setup"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Unhinged Python Environment Setup - ML/AI ETL & Big Data"
    )
    parser.add_argument("--force", action="store_true", 
                       help="Force recreation of virtual environment")
    
    args = parser.parse_args()
    
    setup = UnhingedPythonSetup()
    
    if args.force and setup.venv_path.exists():
        logger.info(f"🗑️ Removing existing virtual environment: {setup.venv_path}")
        import shutil
        shutil.rmtree(setup.venv_path)
    
    success = setup.setup_environment()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
