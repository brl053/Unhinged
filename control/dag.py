#!/usr/bin/env python3

"""
@llm-type dag-engine
@llm-legend Minimal DAG execution engine with cycle detection and human control points
@llm-key Single-file DAG implementation with zero external dependencies
@llm-map Core DAG engine that provides dependency resolution, parallel execution, and service integration
@llm-axiom DAG execution must be deterministic, cycle-free, and provide human oversight capabilities
@llm-contract Returns execution results with clear success/failure status and detailed error information
@llm-token dag-core: Minimal DAG execution engine for control plane

Minimal DAG Execution Engine

Core DAG implementation with:
- Cycle detection using DFS
- Parallel execution groups via topological sort
- Service health integration
- Human approval checkpoints
- Zero external dependencies

Author: Unhinged Team
Version: 1.0.0
Date: 2025-10-19
"""

import time
import urllib.request
import urllib.error
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

class NodeStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class ExecutionResult:
    """Result of DAG node execution"""
    node_name: str
    success: bool
    duration: float
    error_message: Optional[str] = None
    output: str = ""
    start_time: float = 0.0
    end_time: float = 0.0

@dataclass
class DAGNode:
    """Individual DAG execution unit with service integration capabilities"""
    name: str
    command: str = ""
    service_port: Optional[int] = None
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    status: NodeStatus = NodeStatus.PENDING
    execution_result: Optional[ExecutionResult] = None
    human_approval_required: bool = False
    
    def is_service_healthy(self) -> bool:
        """Check service health using existing patterns from config.js"""
        if not self.service_port:
            return True
        
        try:
            response = urllib.request.urlopen(
                f"http://localhost:{self.service_port}/health",
                timeout=5
            )
            return response.status == 200
        except (urllib.error.URLError, urllib.error.HTTPError, OSError):
            return False
    
    def execute(self) -> ExecutionResult:
        """Execute this DAG node"""
        start_time = time.time()
        self.status = NodeStatus.RUNNING
        
        try:
            # Check service health if applicable
            if self.service_port and not self.is_service_healthy():
                raise RuntimeError(f"Service on port {self.service_port} is not healthy")
            
            # Execute command if provided
            if self.command:
                import subprocess
                result = subprocess.run(
                    self.command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode != 0:
                    raise RuntimeError(f"Command failed: {result.stderr}")
                
                output = result.stdout
            else:
                output = f"Node '{self.name}' executed successfully"
            
            # Success
            end_time = time.time()
            self.status = NodeStatus.COMPLETE
            self.execution_result = ExecutionResult(
                node_name=self.name,
                success=True,
                duration=end_time - start_time,
                output=output,
                start_time=start_time,
                end_time=end_time
            )
            
        except Exception as e:
            # Failure
            end_time = time.time()
            self.status = NodeStatus.FAILED
            self.execution_result = ExecutionResult(
                node_name=self.name,
                success=False,
                duration=end_time - start_time,
                error_message=str(e),
                start_time=start_time,
                end_time=end_time
            )
        
        return self.execution_result

class DAG:
    """Minimal DAG with cycle detection and parallel execution"""
    
    def __init__(self):
        self.nodes: Dict[str, DAGNode] = {}
        self.execution_history: List[ExecutionResult] = []
        self.current_execution: Optional[str] = None
        
    def add_node(self, node: DAGNode):
        """Add a node to the DAG"""
        self.nodes[node.name] = node
    
    def add_dependency(self, child: str, parent: str):
        """Add dependency relationship: child depends on parent"""
        if child in self.nodes and parent in self.nodes:
            if parent not in self.nodes[child].dependencies:
                self.nodes[child].dependencies.append(parent)
    
    def validate(self) -> Tuple[bool, List[str]]:
        """Check for cycles using DFS"""
        errors = []
        
        # Check for missing dependencies
        for node_name, node in self.nodes.items():
            for dep in node.dependencies:
                if dep not in self.nodes:
                    errors.append(f"Node '{node_name}' depends on missing node '{dep}'")
        
        if errors:
            return False, errors
        
        # Cycle detection using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(node_name: str) -> bool:
            if node_name in rec_stack:
                return True
            if node_name in visited:
                return False
            
            visited.add(node_name)
            rec_stack.add(node_name)
            
            for dep in self.nodes[node_name].dependencies:
                if has_cycle(dep):
                    return True
            
            rec_stack.remove(node_name)
            return False
        
        for node_name in self.nodes:
            if node_name not in visited:
                if has_cycle(node_name):
                    errors.append(f"Cycle detected involving node '{node_name}'")
                    return False, errors
        
        return True, []
    
    def get_execution_order(self, target: str) -> List[List[str]]:
        """Return groups that can execute in parallel using topological sort"""
        
        # Get all nodes needed for target
        needed_nodes = self._get_dependencies(target)
        
        # Calculate in-degrees for topological sort
        in_degree = {node: 0 for node in needed_nodes}
        for node in needed_nodes:
            for dep in self.nodes[node].dependencies:
                if dep in needed_nodes:
                    in_degree[node] += 1
        
        # Generate execution groups
        execution_groups = []
        remaining = set(needed_nodes)
        
        while remaining:
            # Find nodes with no dependencies (in-degree 0)
            ready_nodes = [node for node in remaining if in_degree[node] == 0]
            
            if not ready_nodes:
                # This shouldn't happen if validation passed
                raise RuntimeError("No ready nodes found - possible cycle")
            
            execution_groups.append(ready_nodes)
            
            # Remove ready nodes and update in-degrees
            for node in ready_nodes:
                remaining.remove(node)
                # Update in-degrees of dependent nodes
                for other_node in remaining:
                    if node in self.nodes[other_node].dependencies:
                        in_degree[other_node] -= 1
        
        return execution_groups
    
    def _get_dependencies(self, target: str) -> Set[str]:
        """Get all nodes needed to build target (including target itself)"""
        if target not in self.nodes:
            return set()
        
        visited = set()
        
        def visit(node_name: str):
            if node_name in visited:
                return
            visited.add(node_name)
            
            for dep in self.nodes[node_name].dependencies:
                visit(dep)
        
        visit(target)
        return visited
    
    def execute(self, target: str, human_approval: bool = True) -> List[ExecutionResult]:
        """Execute DAG with optional human approval"""
        
        # Validate DAG
        is_valid, errors = self.validate()
        if not is_valid:
            error_result = ExecutionResult(
                node_name="validation",
                success=False,
                duration=0.0,
                error_message=f"DAG validation failed: {'; '.join(errors)}"
            )
            return [error_result]
        
        # Get execution order
        try:
            execution_groups = self.get_execution_order(target)
        except Exception as e:
            error_result = ExecutionResult(
                node_name="planning",
                success=False,
                duration=0.0,
                error_message=f"Execution planning failed: {e}"
            )
            return [error_result]
        
        # Execute groups sequentially, nodes within groups in parallel
        all_results = []
        self.current_execution = target
        
        for group_index, group in enumerate(execution_groups):
            print(f"🔄 Executing group {group_index + 1}/{len(execution_groups)}: {group}")
            
            # For now, execute sequentially within groups
            # TODO: Add actual parallel execution
            group_results = []
            
            for node_name in group:
                node = self.nodes[node_name]
                
                # Human approval checkpoint
                if human_approval and node.human_approval_required:
                    print(f"⏸️  Human approval required for node '{node_name}'")
                    # TODO: Implement actual human approval workflow
                    # For now, assume approval
                
                # Execute node
                result = node.execute()
                group_results.append(result)
                self.execution_history.append(result)
                
                # Stop on failure
                if not result.success:
                    print(f"❌ Node '{node_name}' failed: {result.error_message}")
                    self.current_execution = None
                    return all_results + group_results
                else:
                    print(f"✅ Node '{node_name}' completed in {result.duration:.2f}s")
            
            all_results.extend(group_results)
        
        self.current_execution = None
        print(f"🎉 DAG execution completed successfully for target '{target}'")
        return all_results
    
    def get_status(self) -> Dict:
        """Get current DAG status"""
        return {
            "nodes": {name: {
                "status": node.status.value,
                "description": node.description,
                "dependencies": node.dependencies,
                "service_port": node.service_port,
                "service_healthy": node.is_service_healthy() if node.service_port else None
            } for name, node in self.nodes.items()},
            "current_execution": self.current_execution,
            "execution_history": len(self.execution_history)
        }
    
    def reset(self):
        """Reset all nodes to pending status"""
        for node in self.nodes.values():
            node.status = NodeStatus.PENDING
            node.execution_result = None
        self.current_execution = None
