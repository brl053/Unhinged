#!/usr/bin/env python3

"""
@llm-type configuration
@llm-legend Minimal configuration for DAG control plane
@llm-key Simple configuration with sensible defaults and target definitions
@llm-map Configuration module that defines control plane settings and DAG target specifications
@llm-axiom Configuration must be simple, readable, and easily extensible
@llm-contract Provides structured configuration data for control plane components
@llm-token dag-config: Configuration for DAG control plane

DAG Control Plane Configuration

Minimal configuration providing:
- Server settings and ports
- DAG target definitions
- Human approval settings
- Service integration points

Author: Unhinged Team
Version: 1.0.0
Date: 2025-10-19
"""

# Control Plane Configuration
CONTROL_PLANE_CONFIG = {
    "server_port": 9000,
    "static_html_path": "control/static_html",  # Unified control plane
    "auto_open_browser": True,
    "human_approval_timeout": 300,  # 5 minutes
    "max_parallel_jobs": 4,
    "health_check_timeout": 5,
    "execution_timeout": 600  # 10 minutes
}

# Service Integration Configuration
SERVICE_INTEGRATION = {
    "existing_services": {
        "backend": {
            "port": 8080,
            "health_endpoint": "/health",
            "description": "Kotlin backend service"
        },
        "frontend": {
            "port": 3000,
            "health_endpoint": "/",
            "description": "React frontend service"
        },
        "whisper_tts": {
            "port": 8000,
            "health_endpoint": "/health",
            "description": "Whisper TTS service"
        },
        "vision_ai": {
            "port": 8001,
            "health_endpoint": "/health",
            "description": "Vision AI service"
        },
        "ollama": {
            "port": 11434,
            "health_endpoint": "/api/tags",
            "description": "Ollama LLM service"
        }
    }
}

# DAG Target Definitions
DAG_TARGETS = {
    "dev-fast": {
        "description": "Fast development build with intelligent caching",
        "nodes": [
            "proto-gen",
            "backend-compile", 
            "frontend-compile",
            "start-services"
        ],
        "dependencies": {
            "backend-compile": ["proto-gen"],
            "frontend-compile": ["proto-gen"],
            "start-services": ["backend-compile", "frontend-compile"]
        },
        "human_approval_required": False,
        "estimated_duration": 120  # 2 minutes
    },
    
    "dev-full": {
        "description": "Complete development environment with all services",
        "nodes": [
            "proto-gen",
            "backend-build",
            "frontend-build", 
            "start-infrastructure",
            "start-ai-services",
            "health-check"
        ],
        "dependencies": {
            "backend-build": ["proto-gen"],
            "frontend-build": ["proto-gen"],
            "start-infrastructure": [],
            "start-ai-services": ["start-infrastructure"],
            "health-check": ["backend-build", "frontend-build", "start-ai-services"]
        },
        "human_approval_required": False,
        "estimated_duration": 300  # 5 minutes
    },
    
    "test-suite": {
        "description": "Run comprehensive test suite",
        "nodes": [
            "unit-tests-backend",
            "unit-tests-frontend", 
            "integration-tests",
            "e2e-tests"
        ],
        "dependencies": {
            "integration-tests": ["unit-tests-backend", "unit-tests-frontend"],
            "e2e-tests": ["integration-tests"]
        },
        "human_approval_required": False,
        "estimated_duration": 240  # 4 minutes
    },
    
    "production-build": {
        "description": "Production build with optimization and validation",
        "nodes": [
            "proto-gen",
            "backend-build-prod",
            "frontend-build-prod",
            "security-scan",
            "performance-test",
            "package-artifacts"
        ],
        "dependencies": {
            "backend-build-prod": ["proto-gen"],
            "frontend-build-prod": ["proto-gen"],
            "security-scan": ["backend-build-prod", "frontend-build-prod"],
            "performance-test": ["security-scan"],
            "package-artifacts": ["performance-test"]
        },
        "human_approval_required": True,  # Production requires approval
        "estimated_duration": 600  # 10 minutes
    },
    
    "deploy-staging": {
        "description": "Deploy to staging environment",
        "nodes": [
            "build-docker-images",
            "push-to-registry",
            "deploy-to-staging",
            "staging-health-check",
            "staging-smoke-tests"
        ],
        "dependencies": {
            "push-to-registry": ["build-docker-images"],
            "deploy-to-staging": ["push-to-registry"],
            "staging-health-check": ["deploy-to-staging"],
            "staging-smoke-tests": ["staging-health-check"]
        },
        "human_approval_required": True,  # Deployment requires approval
        "estimated_duration": 480  # 8 minutes
    }
}

# Node Command Mappings
NODE_COMMANDS = {
    # Protobuf generation
    "proto-gen": "cd proto && ./build.sh",
    
    # Backend builds
    "backend-compile": "cd backend && ./gradlew compileKotlin --build-cache",
    "backend-build": "cd backend && ./gradlew build --parallel",
    "backend-build-prod": "cd backend && ./gradlew build -Pprod --parallel",
    
    # Frontend builds  
    "frontend-compile": "cd frontend && npm run build:dev",
    "frontend-build": "cd frontend && npm run build",
    "frontend-build-prod": "cd frontend && npm run build:prod",
    
    # Service management
    "start-services": "docker compose -f docker-compose.dev.yml up -d backend frontend",
    "start-infrastructure": "docker compose -f docker-compose.dev.yml up -d database kafka zookeeper",
    "start-ai-services": "docker compose -f docker-compose.dev.yml up -d whisper-tts vision-ai",
    
    # Testing
    "unit-tests-backend": "cd backend && ./gradlew test",
    "unit-tests-frontend": "cd frontend && npm run test:unit",
    "integration-tests": "cd backend && ./gradlew integrationTest",
    "e2e-tests": "cd frontend && npm run test:e2e",
    
    # Production tasks
    "security-scan": "make security-scan",
    "performance-test": "make performance-test",
    "package-artifacts": "make package-artifacts",
    
    # Deployment
    "build-docker-images": "docker compose -f docker-compose.prod.yml build",
    "push-to-registry": "make push-images",
    "deploy-to-staging": "make deploy-staging",
    "staging-health-check": "make health-check-staging",
    "staging-smoke-tests": "make test-staging-smoke",
    
    # Health checks
    "health-check": "make status"
}

# Human Approval Configuration
HUMAN_APPROVAL_CONFIG = {
    "approval_timeout": 300,  # 5 minutes
    "auto_approve_dev": True,  # Auto-approve development targets
    "auto_approve_test": True,  # Auto-approve test targets
    "require_approval_prod": True,  # Always require approval for production
    "require_approval_deploy": True,  # Always require approval for deployment
    "approval_page_template": "dag-approval.html",
    "notification_methods": ["browser", "console"]  # Future: email, slack, etc.
}

# Browser Integration Configuration
BROWSER_INTEGRATION = {
    "auto_open_browser": True,
    "browser_command": None,  # None = use system default
    "dashboard_refresh_interval": 2000,  # 2 seconds
    "execution_poll_interval": 1000,  # 1 second
    "health_check_interval": 5000,  # 5 seconds
    "static_html_files": [
        "dag-control.html",
        "dag-approval.html", 
        "dag-monitor.html"
    ]
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_to_file": False,
    "log_file": "control/dag.log",
    "max_log_size": "10MB",
    "backup_count": 3
}

def get_node_command(node_name: str) -> str:
    """Get command for a specific node"""
    return NODE_COMMANDS.get(node_name, f"echo 'No command defined for {node_name}'")

def get_service_port(service_name: str) -> int:
    """Get port for a specific service"""
    service = SERVICE_INTEGRATION["existing_services"].get(service_name)
    return service["port"] if service else None

def requires_human_approval(target_name: str) -> bool:
    """Check if target requires human approval"""
    target = DAG_TARGETS.get(target_name, {})
    return target.get("human_approval_required", False)

def get_estimated_duration(target_name: str) -> int:
    """Get estimated duration for target in seconds"""
    target = DAG_TARGETS.get(target_name, {})
    return target.get("estimated_duration", 60)

# Export main configuration objects
__all__ = [
    'CONTROL_PLANE_CONFIG',
    'SERVICE_INTEGRATION', 
    'DAG_TARGETS',
    'NODE_COMMANDS',
    'HUMAN_APPROVAL_CONFIG',
    'BROWSER_INTEGRATION',
    'LOGGING_CONFIG',
    'get_node_command',
    'get_service_port',
    'requires_human_approval',
    'get_estimated_duration'
]
