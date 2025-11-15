#!/usr/bin/env python3
"""
@llm-type misc.virtualization-boundary
@llm-does http proxy server that represents the line-in-the-sand
"""

import sys
import time
from pathlib import Path

import uvicorn
import yaml
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add control system to path
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "deployment"))

from system import SystemController

# Import new control plane modules
try:
    from deploy import UnhingedDeploymentOrchestrator
    from health_checks import UnhingedHealthMonitor

    CONTROL_PLANE_AVAILABLE = True
except ImportError:
    CONTROL_PLANE_AVAILABLE = False

# Initialize event logger
from events import create_service_logger

events = create_service_logger("proxy-server", "1.0.0")

# Initialize FastAPI app
app = FastAPI(
    title="Unhinged Virtualization Boundary",
    description="HTTP proxy server representing the future Unhinged OS system call interface",
    version="0.1.0-alpha",
    docs_url="/control/docs",
    redoc_url="/control/redoc",
)

# Add CORS middleware for HTML interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize system controller
system_controller = SystemController()


# Startup event
@app.on_event("startup")
async def startup_event():
    pass


# Health check endpoint
@app.get("/control/health")
async def health_check():
    """
    Health check endpoint - Future: sys_health_check()

    @llm-future This becomes a fundamental OS health monitoring system call
    """
    return {
        "status": "healthy",
        "service": "unhinged-virtualization-boundary",
        "version": "0.1.0-alpha",
        "uptime": time.time() - system_controller.start_time,
        "future_syscall": "sys_health_check()",
        "virtualization_status": "phase_1_http_shim",
    }


# Future OS System Calls (currently HTTP endpoints)
@app.post("/control/system/tier/{tier}/start")
async def start_service_tier(tier: str, request: Request):
    """
    Start a service tier - Future Unhinged OS system call: sys_start_tier()

    @llm-future This HTTP endpoint will become: int sys_start_tier(tier_id_t tier)
    @llm-kernel-design Service tiers are fundamental OS abstractions in Unhinged
    """
    try:
        result = await system_controller.start_service_tier(tier)

        response_data = {
            "operation": f"start_tier_{tier}",
            "success": result.success,
            "affected_services": result.affected_services,
            "execution_time": result.execution_time,
            "system_state": result.system_state_change,
            "timestamp": result.timestamp.isoformat(),
            # Future OS metadata
            "virtualization_metadata": {
                "future_syscall": f"sys_start_tier({tier})",
                "kernel_operation": "tier_lifecycle_management",
                "security_context": "user_space_request",
                "resource_allocation": "dynamic",
                "audit_trail": True,
            },
        }

        if result.error_message:
            response_data["error_message"] = result.error_message

        return response_data

    except Exception as e:
        # Future: This becomes kernel panic or error code
        events.error("Start tier failed", exception=e, metadata={"tier": tier})
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"System operation failed: {str(e)}",
                "future_syscall": f"sys_start_tier({tier})",
                "kernel_error_code": "ESYSOP",
                "recovery_suggestion": "Check system logs and retry operation",
            },
        )


@app.post("/control/system/tier/{tier}/stop")
async def stop_service_tier(tier: str, request: Request):
    """
    Stop a service tier - Future: sys_stop_tier()

    @llm-future This becomes the foundation for Unhinged process lifecycle management
    """
    try:
        result = await system_controller.stop_service_tier(tier)

        return {
            "operation": f"stop_tier_{tier}",
            "success": result.success,
            "affected_services": result.affected_services,
            "execution_time": result.execution_time,
            "system_state": result.system_state_change,
            "timestamp": result.timestamp.isoformat(),
            "virtualization_metadata": {
                "future_syscall": f"sys_stop_tier({tier})",
                "kernel_operation": "tier_lifecycle_management",
                "graceful_shutdown": True,
            },
        }

    except Exception as e:
        events.error("Stop tier failed", exception=e, metadata={"tier": tier})
        raise HTTPException(status_code=500, detail=f"Stop operation failed: {str(e)}")


@app.get("/control/system/status")
async def get_system_status():
    """
    Get system status - Future: sys_get_system_info()

    @llm-future This endpoint design informs future OS status reporting
    """

    try:
        status = await system_controller.get_system_status()

        return {
            "running_services": status.running_services,
            "failed_services": status.failed_services,
            "resource_usage": status.resource_usage,
            "uptime": status.uptime,
            "last_operation": status.last_operation.to_dict() if status.last_operation else None,
            "virtualization_metadata": {
                "future_syscall": "sys_get_system_info()",
                "kernel_version": "unhinged-0.1.0-alpha",
                "virtualization_layer": "http_proxy_phase_1",
            },
        }

    except Exception as e:
        events.error("System info query failed", exception=e)
        raise HTTPException(status_code=500, detail=f"Status query failed: {str(e)}")


# Virtualization Learning Endpoints
@app.get("/control/virtualization/insights")
async def get_virtualization_insights():
    """
    Endpoint for gathering insights about system operations for future OS design

    @llm-purpose Collect operational patterns that inform Unhinged OS kernel design
    """

    try:
        return {
            "operation_patterns": system_controller.get_operation_patterns(),
            "resource_usage_insights": system_controller.get_resource_insights(),
            "future_os_recommendations": system_controller.get_os_design_insights(),
            "virtualization_roadmap": {
                "current_phase": "1_http_shim",
                "next_phase": "2_direct_container_orchestration",
                "ultimate_goal": "5_full_unhinged_os",
            },
        }
    except Exception as e:
        events.error("Virtualization insights query failed", exception=e)
        raise HTTPException(status_code=500, detail=f"Insights query failed: {str(e)}")


@app.get("/control/virtualization/operation-history")
async def get_operation_history():
    """Get complete operation history for OS development analysis"""
    try:
        history = system_controller.get_operation_history()
        return {
            "operations": [op.to_dict() for op in history],
            "total_operations": len(history),
            "analysis_note": "This data will inform future Unhinged OS kernel design",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History query failed: {str(e)}")


# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    events.error("Unhandled exception", exception=exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "future_note": "In Unhinged OS, this would be a kernel panic with recovery",
        },
    )


# =============================================================================
# NEW CONTROL PLANE ENDPOINTS
# Runtime deployment and health monitoring integration
# =============================================================================


@app.get("/control/deployment/status")
async def get_deployment_status():
    """Get current deployment status across all environments"""
    if not CONTROL_PLANE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Control plane not available")

    try:
        project_root = Path(__file__).parent.parent
        orchestrator = UnhingedDeploymentOrchestrator(project_root, "development")
        status = orchestrator.get_deployment_status()

        return JSONResponse({"status": "success", "data": status, "timestamp": time.time()})
    except Exception as e:
        events.error("Deployment status error", exception=e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/control/health/status")
async def get_health_status():
    """Get current health status of all services"""
    if not CONTROL_PLANE_AVAILABLE:
        raise HTTPException(status_code=503, detail="Control plane not available")

    try:
        project_root = Path(__file__).parent.parent
        monitor = UnhingedHealthMonitor(project_root)

        # Perform health checks
        results = await monitor.check_all_services()

        # Convert results to serializable format
        health_data = {}
        for service_name, result in results.items():
            health_data[service_name] = {
                "status": result.status,
                "response_time": result.response_time,
                "error_message": result.error_message,
                "timestamp": result.timestamp.isoformat(),
            }

        return JSONResponse({"status": "success", "data": health_data, "timestamp": time.time()})
    except Exception as e:
        events.error("Health status error", exception=e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/control/config/services")
async def get_service_registry():
    """Get service registry configuration"""
    try:
        project_root = Path(__file__).parent.parent
        registry_file = project_root / "control" / "config" / "service-registry.yml"

        if registry_file.exists():
            with open(registry_file) as f:
                registry = yaml.safe_load(f)

            return JSONResponse({"status": "success", "data": registry, "timestamp": time.time()})
        else:
            raise HTTPException(status_code=404, detail="Service registry not found")
    except Exception as e:
        events.error("Service registry error", exception=e)
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """Main entry point for the virtualization boundary server"""
    events.info("Starting Unhinged Virtualization Boundary Server")
    events.info("This server represents the future Unhinged OS system call interface")

    uvicorn.run("proxy_server:app", host="0.0.0.0", port=9000, reload=True, log_level="info")


if __name__ == "__main__":
    main()
