"""
@llm-type util.validator
@llm-does resource allocation validation for memory, disk, and cpu limits
@llm-rule resource allocation must be validated at build time to prevent runtime failures
"""

import logging
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import psutil
import yaml


@dataclass
class ResourceIssue:
    """Represents a resource issue detected at build time"""

    resource_type: str  # memory, cpu, disk, network
    service: str
    issue_type: str  # insufficient, missing, invalid
    description: str
    resolution_suggestions: list[str]
    severity: str = "error"


class ResourceValidator:
    """
    Build-time resource validator

    Analyzes resource requirements and validates against available system resources.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logging.getLogger(__name__)

    def validate_resources(self) -> list[ResourceIssue]:
        """
        Validate all resource requirements in the project

        @llm-future This becomes part of Unhinged OS resource allocation compiler
        """
        issues = []

        # Get system resources
        system_resources = self._get_system_resources()

        # Analyze resource requirements from compose files
        service_requirements = self._analyze_service_requirements()

        # Validate memory requirements
        issues.extend(self._validate_memory_requirements(service_requirements, system_resources))

        # Validate disk space requirements
        issues.extend(self._validate_disk_requirements(service_requirements, system_resources))

        # Validate required tools/binaries
        issues.extend(self._validate_required_tools())

        return issues

    def _get_system_resources(self) -> dict[str, float]:
        """Get current system resource availability"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "memory_total_gb": memory.total / (1024**3),
                "memory_available_gb": memory.available / (1024**3),
                "disk_total_gb": disk.total / (1024**3),
                "disk_free_gb": disk.free / (1024**3),
                "cpu_count": psutil.cpu_count(),
            }
        except Exception as e:
            self.logger.error(f"Failed to get system resources: {e}")
            return {}

    def _analyze_service_requirements(self) -> dict[str, dict[str, float]]:
        """Analyze resource requirements from docker-compose files"""
        requirements = {}

        compose_files = ["docker-compose.yml", "docker-compose.simple.yml", "docker-compose.observability.yml"]

        for compose_file in compose_files:
            file_path = self.project_root / compose_file
            if file_path.exists():
                self._parse_resource_requirements(file_path, requirements)

        return requirements

    def _parse_resource_requirements(self, file_path: Path, requirements: dict[str, dict[str, float]]):
        """Parse resource requirements from a docker-compose file"""
        try:
            with open(file_path) as f:
                compose_data = yaml.safe_load(f)

            services = compose_data.get("services", {})

            for service_name, service_config in services.items():
                service_reqs = {}

                # Parse deploy.resources if present
                deploy = service_config.get("deploy", {})
                resources = deploy.get("resources", {})

                # Parse limits
                limits = resources.get("limits", {})
                if "memory" in limits:
                    memory_str = limits["memory"]
                    service_reqs["memory_gb"] = self._parse_memory_string(memory_str)

                # Parse reservations
                reservations = resources.get("reservations", {})
                if "memory" in reservations:
                    memory_str = reservations["memory"]
                    service_reqs["memory_reserved_gb"] = self._parse_memory_string(memory_str)

                # Estimate requirements for known services
                service_reqs.update(self._estimate_service_requirements(service_name, service_config))

                if service_reqs:
                    requirements[service_name] = service_reqs

        except Exception as e:
            self.logger.error(f"Failed to parse resource requirements from {file_path}: {e}")

    def _parse_memory_string(self, memory_str: str) -> float:
        """Parse memory string like '512m', '2g' to GB"""
        memory_str = memory_str.lower().strip()

        if memory_str.endswith("g"):
            return float(memory_str[:-1])
        elif memory_str.endswith("m"):
            return float(memory_str[:-1]) / 1024
        elif memory_str.endswith("k"):
            return float(memory_str[:-1]) / (1024 * 1024)
        else:
            # Assume bytes
            return float(memory_str) / (1024**3)

    def _estimate_service_requirements(self, service_name: str, service_config: dict) -> dict[str, float]:
        """Estimate resource requirements for known service types"""
        estimates = {}

        # Database services
        if any(db in service_name.lower() for db in ["postgres", "mysql", "cockroach", "mongo", "redis"]):
            estimates["memory_gb"] = 1.0  # Minimum for databases
            estimates["disk_gb"] = 5.0  # Minimum disk space

        # AI/ML services
        if any(ai in service_name.lower() for ai in ["llm", "ollama", "whisper", "vision"]):
            estimates["memory_gb"] = 4.0  # AI services need more memory
            estimates["disk_gb"] = 10.0  # Model storage

        # Observability services
        if any(obs in service_name.lower() for obs in ["grafana", "prometheus", "elasticsearch"]):
            estimates["memory_gb"] = 2.0
            estimates["disk_gb"] = 5.0

        # Application services
        if any(app in service_name.lower() for app in ["backend", "frontend", "api"]):
            estimates["memory_gb"] = 0.5
            estimates["disk_gb"] = 1.0

        return estimates

    def _validate_memory_requirements(
        self, requirements: dict[str, dict[str, float]], system_resources: dict[str, float]
    ) -> list[ResourceIssue]:
        """Validate memory requirements against available memory"""
        issues = []

        if "memory_available_gb" not in system_resources:
            return issues

        available_memory = system_resources["memory_available_gb"]
        total_required = 0

        for service, reqs in requirements.items():
            service_memory = reqs.get("memory_gb", 0)
            total_required += service_memory

            if service_memory > available_memory:
                issues.append(
                    ResourceIssue(
                        resource_type="memory",
                        service=service,
                        issue_type="insufficient",
                        description=f"Service '{service}' requires {service_memory:.1f}GB but only {available_memory:.1f}GB available",
                        resolution_suggestions=[
                            f"Reduce memory allocation for {service}",
                            "Add more RAM to the system",
                            "Run fewer services simultaneously",
                        ],
                    )
                )

        if total_required > available_memory:
            issues.append(
                ResourceIssue(
                    resource_type="memory",
                    service="all_services",
                    issue_type="insufficient",
                    description=f"Total memory required ({total_required:.1f}GB) exceeds available ({available_memory:.1f}GB)",
                    resolution_suggestions=[
                        "Reduce memory allocations for services",
                        "Add more RAM to the system",
                        "Use service tiers to run services in stages",
                    ],
                    severity="warning",
                )
            )

        return issues

    def _validate_disk_requirements(
        self, requirements: dict[str, dict[str, float]], system_resources: dict[str, float]
    ) -> list[ResourceIssue]:
        """Validate disk space requirements"""
        issues = []

        if "disk_free_gb" not in system_resources:
            return issues

        available_disk = system_resources["disk_free_gb"]
        total_required = 0

        for service, reqs in requirements.items():
            service_disk = reqs.get("disk_gb", 0)
            total_required += service_disk

        # Add Docker image space estimates
        total_required += 10  # Estimate for Docker images

        if total_required > available_disk:
            issues.append(
                ResourceIssue(
                    resource_type="disk",
                    service="all_services",
                    issue_type="insufficient",
                    description=f"Total disk required (~{total_required:.1f}GB) may exceed available ({available_disk:.1f}GB)",
                    resolution_suggestions=[
                        "Free up disk space",
                        "Use external volumes for data storage",
                        "Clean up unused Docker images and containers",
                    ],
                    severity="warning",
                )
            )

        return issues

    def _validate_required_tools(self) -> list[ResourceIssue]:
        """Validate that required tools are available"""
        issues = []

        required_tools = {
            "docker": "Docker is required for container orchestration",
            "python3": "Python 3 is required for build scripts",
            "git": "Git is required for version control",
        }

        # Check for Docker Compose (v2 or v1)
        docker_compose_available = False
        try:
            # Try modern docker compose (v2)
            result = subprocess.run(["docker", "compose", "version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                docker_compose_available = True
        except:
            try:
                # Try legacy docker-compose (v1)
                result = subprocess.run(["docker-compose", "--version"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    docker_compose_available = True
            except:
                pass

        if not docker_compose_available:
            issues.append(
                ResourceIssue(
                    resource_type="tool",
                    description="Docker Compose is required for multi-container applications",
                    severity="error",
                    current_value="not found",
                    recommended_value="docker compose v2 or docker-compose v1",
                )
            )

        for tool, description in required_tools.items():
            if not shutil.which(tool):
                issues.append(
                    ResourceIssue(
                        resource_type="tools",
                        service="build_system",
                        issue_type="missing",
                        description=f"Required tool '{tool}' not found: {description}",
                        resolution_suggestions=[
                            f"Install {tool}",
                            f"Add {tool} to PATH",
                            "Check installation documentation",
                        ],
                    )
                )

        return issues
