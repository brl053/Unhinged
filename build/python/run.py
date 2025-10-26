#!/usr/bin/env python3
"""
@llm-type python-runner
@llm-legend Universal Python runner for Unhinged on-premise ML/AI ETL & Big Data pipelines
@llm-key Centralized Python execution with Apache stack integration and ML/AI environment
@llm-map Core Python execution engine supporting Kafka, Spark, Flink, Cassandra, Elasticsearch
@llm-axiom All Python execution must be consistent, reproducible, and ML/AI pipeline ready
@llm-token python-runner: Universal Python execution for on-premise big data and ML workflows

Universal Python Runner for Unhinged System:
- Single virtual environment for all Python execution
- Apache stack integration (Kafka, Spark, Flink, Cassandra)
- ML/AI pipeline support with proper environment setup
- Consistent execution across build system, services, and ETL
- On-premise big data processing capabilities
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import List, Optional, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UnhingedPythonRunner:
    """
    @llm-type python-executor
    @llm-legend Centralized Python execution engine for ML/AI ETL and big data pipelines
    @llm-key Universal Python runner with Apache stack integration and environment management
    @llm-map Core execution engine enabling consistent Python environments across all services
    @llm-axiom Python execution must be reproducible, environment-aware, and big data ready
    @llm-token python-executor: Production Python execution with ML/AI and big data support
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.build_python_dir = self.project_root / "build" / "python"
        self.venv_path = self.build_python_dir / "venv"
        self.python_executable = self.venv_path / "bin" / "python3"
        
        # Ensure venv exists
        if not self.python_executable.exists():
            logger.error(f"❌ Python virtual environment not found at {self.venv_path}")
            logger.info("💡 Run 'build/python/setup.py' to create the environment")
            sys.exit(1)
    
    def setup_environment(self) -> Dict[str, str]:
        """Setup environment variables for ML/AI and big data processing"""
        env = os.environ.copy()
        
        # Python path setup - include event framework
        python_paths = [
            str(self.project_root),
            str(self.project_root / "libs" / "event-framework" / "python" / "src")
        ]
        env["PYTHONPATH"] = os.pathsep.join(python_paths)
        
        # Apache Spark configuration (for our on-premise Spark cluster)
        env["SPARK_HOME"] = "/opt/spark"  # Will be set in containers
        env["PYSPARK_PYTHON"] = str(self.python_executable)
        env["PYSPARK_DRIVER_PYTHON"] = str(self.python_executable)
        
        # Kafka configuration (for our on-premise Kafka cluster)
        env["KAFKA_BOOTSTRAP_SERVERS"] = "localhost:1400"
        
        # Database connections (for our on-premise databases)
        env["DATABASE_URL"] = "postgresql://postgres:password@localhost:1200/unhinged"
        env["REDIS_URL"] = "redis://localhost:1302"
        env["ELASTICSEARCH_URL"] = "http://localhost:1303"
        env["CASSANDRA_HOSTS"] = "localhost:1207"
        
        # Object storage (MinIO S3-compatible)
        env["MINIO_ENDPOINT"] = "localhost:1700"
        env["MINIO_ACCESS_KEY"] = "minioadmin"
        env["MINIO_SECRET_KEY"] = "minioadmin"
        
        # ML/AI model paths
        env["MODELS_DIR"] = str(self.project_root / "models")
        env["DATASETS_DIR"] = str(self.project_root / "datasets")
        
        # Logging configuration
        env["LOG_LEVEL"] = "INFO"
        env["STRUCTURED_LOGGING"] = "true"
        
        # Performance tuning
        env["OMP_NUM_THREADS"] = "4"  # OpenMP threads for NumPy/SciPy
        env["OPENBLAS_NUM_THREADS"] = "4"  # OpenBLAS threads
        env["MKL_NUM_THREADS"] = "4"  # Intel MKL threads
        
        return env
    
    def run_script(self, script_path: str, args: Optional[List[str]] = None, 
                   working_dir: Optional[Path] = None) -> subprocess.CompletedProcess:
        """Run a Python script with proper environment setup"""
        
        # Resolve script path
        if not Path(script_path).is_absolute():
            script_path = str(self.project_root / script_path)
        
        if not Path(script_path).exists():
            logger.error(f"❌ Script not found: {script_path}")
            sys.exit(1)
        
        # Build command
        cmd = [str(self.python_executable), script_path] + (args or [])
        
        # Setup environment
        env = self.setup_environment()
        
        # Set working directory
        cwd = working_dir or self.project_root
        
        logger.info(f"🐍 Running Python script: {script_path}")
        logger.info(f"📁 Working directory: {cwd}")
        logger.info(f"🔧 Python executable: {self.python_executable}")
        
        try:
            result = subprocess.run(
                cmd,
                env=env,
                cwd=cwd,
                capture_output=False,  # Allow real-time output
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Script completed successfully: {script_path}")
            else:
                logger.error(f"❌ Script failed with exit code {result.returncode}: {script_path}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error running script {script_path}: {e}")
            sys.exit(1)
    
    def run_module(self, module_name: str, args: Optional[List[str]] = None) -> subprocess.CompletedProcess:
        """Run a Python module with -m flag"""
        cmd = [str(self.python_executable), "-m", module_name] + (args or [])
        env = self.setup_environment()
        
        logger.info(f"🐍 Running Python module: {module_name}")
        
        try:
            result = subprocess.run(
                cmd,
                env=env,
                cwd=self.project_root,
                capture_output=False,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Module completed successfully: {module_name}")
            else:
                logger.error(f"❌ Module failed with exit code {result.returncode}: {module_name}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error running module {module_name}: {e}")
            sys.exit(1)
    
    def interactive_shell(self) -> None:
        """Start an interactive Python shell with full environment"""
        env = self.setup_environment()
        
        logger.info("🐍 Starting interactive Python shell with ML/AI and big data environment")
        logger.info("📊 Available: Kafka, Spark, Flink, Cassandra, Elasticsearch, ML libraries")
        
        subprocess.run([str(self.python_executable)], env=env, cwd=self.project_root)
    
    def jupyter_lab(self) -> None:
        """Start Jupyter Lab for interactive ML/AI development"""
        env = self.setup_environment()
        
        logger.info("🔬 Starting Jupyter Lab for ML/AI development")
        
        cmd = [str(self.python_executable), "-m", "jupyter", "lab", 
               "--ip=0.0.0.0", "--port=8888", "--no-browser", 
               "--allow-root", "--notebook-dir", str(self.project_root)]
        
        subprocess.run(cmd, env=env, cwd=self.project_root)


def main():
    """CLI entry point for universal Python runner"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Unhinged Universal Python Runner - ML/AI ETL & Big Data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a service
  python run.py services/speech-to-text/main.py
  
  # Run build system
  python run.py build/build.py build service-discovery
  
  # Run ETL pipeline
  python run.py pipelines/kafka_to_spark_etl.py
  
  # Run module
  python run.py -m pytest tests/
  
  # Interactive shell with ML/AI environment
  python run.py --shell
  
  # Jupyter Lab for ML development
  python run.py --jupyter
        """
    )
    
    parser.add_argument("script", nargs="?", help="Python script to run")
    parser.add_argument("args", nargs="*", help="Arguments to pass to the script")
    parser.add_argument("-m", "--module", help="Run Python module with -m flag")
    parser.add_argument("--shell", action="store_true", help="Start interactive Python shell")
    parser.add_argument("--jupyter", action="store_true", help="Start Jupyter Lab")
    parser.add_argument("--working-dir", type=Path, help="Working directory for script execution")
    
    args = parser.parse_args()
    
    runner = UnhingedPythonRunner()
    
    if args.shell:
        runner.interactive_shell()
    elif args.jupyter:
        runner.jupyter_lab()
    elif args.module:
        result = runner.run_module(args.module, args.args)
        sys.exit(result.returncode)
    elif args.script:
        result = runner.run_script(args.script, args.args, args.working_dir)
        sys.exit(result.returncode)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
