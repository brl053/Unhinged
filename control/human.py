#!/usr/bin/env python3

"""
@llm-type human-interface
@llm-legend Browser-based human control integration with existing static_html infrastructure
@llm-key Generates HTML interfaces using existing static_html patterns and handles human approval workflows
@llm-map Human interface layer that bridges DAG execution with browser-based control and approval
@llm-axiom Human interface must preserve existing static_html patterns while adding DAG oversight capabilities
@llm-contract Returns approval results and generates browser-compatible HTML interfaces
@llm-token dag-human: Human interface integration for DAG control plane

Human Interface for DAG Control Plane

Browser-based human control integration providing:
- Approval workflow generation
- Browser interface creation
- Human intervention handling
- Integration with existing static_html

Author: Unhinged Team
Version: 1.0.0
Date: 2025-10-19
"""

import os
import time
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .config import CONTROL_PLANE_CONFIG, HUMAN_APPROVAL_CONFIG, BROWSER_INTEGRATION

@dataclass
class ApprovalRequest:
    """Human approval request data"""
    target: str
    node: str
    description: str
    estimated_duration: float
    dependencies: List[str]
    timestamp: float

@dataclass
class ApprovalResult:
    """Result of human approval"""
    approved: bool
    reason: str = ""
    timestamp: float = 0.0
    timeout: bool = False

class HumanInterface:
    """Browser-based human control integration"""
    
    def __init__(self, static_html_path: str = None):
        if static_html_path is None:
            # Use relative path from control package
            static_html_path = Path(__file__).parent / "static_html"
        else:
            static_html_path = Path(static_html_path)

        self.static_html_path = static_html_path
        self.pending_approvals: Dict[str, ApprovalRequest] = {}
        self.approval_results: Dict[str, ApprovalResult] = {}

        # Ensure static_html directory exists
        self.static_html_path.mkdir(exist_ok=True)
    
    def request_approval(self, target: str, node: str, description: str, 
                        estimated_duration: float, dependencies: List[str]) -> ApprovalResult:
        """Generate approval page and wait for human response"""
        
        approval_request = ApprovalRequest(
            target=target,
            node=node,
            description=description,
            estimated_duration=estimated_duration,
            dependencies=dependencies,
            timestamp=time.time()
        )
        
        # Generate unique approval ID
        approval_id = f"{target}_{node}_{int(time.time())}"
        self.pending_approvals[approval_id] = approval_request
        
        # Generate approval page
        approval_html = self.generate_approval_page(approval_request, approval_id)
        
        # Write to static_html directory
        approval_file = self.static_html_path / "dag-approval.html"
        approval_file.write_text(approval_html)
        
        # Open browser if configured
        if BROWSER_INTEGRATION["auto_open_browser"]:
            self.open_browser(approval_file)
        
        # Wait for approval
        return self.wait_for_approval(approval_id)
    
    def generate_approval_page(self, request: ApprovalRequest, approval_id: str) -> str:
        """Generate HTML approval page using existing static_html styling"""
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎛️ DAG Execution Approval - Unhinged AI</title>
    <link rel="stylesheet" href="shared/styles.css">
    <script src="shared/config.js"></script>
    <style>
        .approval-container {{
            max-width: 800px;
            margin: 2rem auto;
            padding: 2rem;
        }}
        
        .approval-header {{
            text-align: center;
            margin-bottom: 2rem;
        }}
        
        .execution-details {{
            background: var(--surface-color);
            border: 2px solid var(--border-color);
            border-radius: var(--border-radius);
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .approval-controls {{
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-top: 2rem;
        }}
        
        .approve-btn {{
            background: var(--success-color);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: var(--border-radius);
            font-size: 1.1rem;
            cursor: pointer;
            transition: var(--transition);
        }}
        
        .approve-btn:hover {{
            background: #059669;
            transform: translateY(-2px);
        }}
        
        .reject-btn {{
            background: #ef4444;
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: var(--border-radius);
            font-size: 1.1rem;
            cursor: pointer;
            transition: var(--transition);
        }}
        
        .reject-btn:hover {{
            background: #dc2626;
            transform: translateY(-2px);
        }}
        
        .timeout-warning {{
            background: rgba(245, 158, 11, 0.1);
            border: 2px solid #f59e0b;
            border-radius: var(--border-radius);
            padding: 1rem;
            margin-bottom: 1rem;
            text-align: center;
        }}
        
        .dependency-list {{
            list-style: none;
            padding: 0;
        }}
        
        .dependency-item {{
            background: rgba(37, 99, 235, 0.1);
            border: 1px solid var(--primary-color);
            border-radius: 4px;
            padding: 0.5rem;
            margin: 0.25rem 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="approval-container">
            <div class="approval-header">
                <h1>🎛️ DAG Execution Approval Required</h1>
                <p>Human oversight needed for the following operation:</p>
            </div>
            
            <div class="timeout-warning">
                ⏰ This approval will timeout in <span id="countdown">{HUMAN_APPROVAL_CONFIG["approval_timeout"]}</span> seconds
            </div>
            
            <div class="execution-details">
                <h2>📋 Execution Details</h2>
                <div class="detail-grid">
                    <div class="detail-item">
                        <strong>🎯 Target:</strong> {request.target}
                    </div>
                    <div class="detail-item">
                        <strong>🔧 Node:</strong> {request.node}
                    </div>
                    <div class="detail-item">
                        <strong>📝 Description:</strong> {request.description}
                    </div>
                    <div class="detail-item">
                        <strong>⏱️ Estimated Duration:</strong> {request.estimated_duration:.1f} seconds
                    </div>
                    <div class="detail-item">
                        <strong>🕐 Requested At:</strong> {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(request.timestamp))}
                    </div>
                </div>
                
                {self._generate_dependencies_html(request.dependencies)}
            </div>
            
            <div class="approval-controls">
                <button class="approve-btn" onclick="approve()">
                    ✅ Approve Execution
                </button>
                <button class="reject-btn" onclick="reject()">
                    ❌ Reject Execution
                </button>
            </div>
            
            <div id="status-message" style="text-align: center; margin-top: 1rem;"></div>
        </div>
    </div>
    
    <script>
        const APPROVAL_ID = '{approval_id}';
        const DAG_SERVICE_URL = 'http://localhost:{CONTROL_PLANE_CONFIG["server_port"]}';
        let timeoutSeconds = {HUMAN_APPROVAL_CONFIG["approval_timeout"]};
        
        // Countdown timer
        function updateCountdown() {{
            const countdownElement = document.getElementById('countdown');
            countdownElement.textContent = timeoutSeconds;
            
            if (timeoutSeconds <= 0) {{
                timeout();
                return;
            }}
            
            timeoutSeconds--;
            setTimeout(updateCountdown, 1000);
        }}
        
        async function approve() {{
            await sendApproval(true, 'Human approved execution');
        }}
        
        async function reject() {{
            const reason = prompt('Please provide a reason for rejection (optional):') || 'Human rejected execution';
            await sendApproval(false, reason);
        }}
        
        async function timeout() {{
            await sendApproval(false, 'Approval timeout exceeded');
            document.getElementById('status-message').innerHTML = 
                '<div style="color: #ef4444;">⏰ Approval timeout - execution cancelled</div>';
        }}
        
        async function sendApproval(approved, reason) {{
            try {{
                const response = await fetch(`${{DAG_SERVICE_URL}}/dag/approve`, {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json'
                    }},
                    body: JSON.stringify({{
                        approval_id: APPROVAL_ID,
                        approved: approved,
                        reason: reason,
                        timestamp: Date.now() / 1000
                    }})
                }});
                
                if (response.ok) {{
                    const result = await response.json();
                    const statusMessage = document.getElementById('status-message');
                    
                    if (approved) {{
                        statusMessage.innerHTML = '<div style="color: #10b981;">✅ Execution approved - proceeding...</div>';
                    }} else {{
                        statusMessage.innerHTML = '<div style="color: #ef4444;">❌ Execution rejected - cancelling...</div>';
                    }}
                    
                    // Disable buttons
                    document.querySelector('.approve-btn').disabled = true;
                    document.querySelector('.reject-btn').disabled = true;
                    
                    // Redirect after delay
                    setTimeout(() => {{
                        window.location.href = 'dag-control.html';
                    }}, 2000);
                    
                }} else {{
                    throw new Error('Failed to send approval');
                }}
                
            }} catch (error) {{
                console.error('Approval error:', error);
                document.getElementById('status-message').innerHTML = 
                    '<div style="color: #ef4444;">❌ Failed to send approval - please try again</div>';
            }}
        }}
        
        // Start countdown when page loads
        document.addEventListener('DOMContentLoaded', () => {{
            updateCountdown();
        }});
        
        // Handle keyboard shortcuts
        document.addEventListener('keydown', (event) => {{
            if (event.key === 'Enter' || event.key === 'y' || event.key === 'Y') {{
                approve();
            }} else if (event.key === 'Escape' || event.key === 'n' || event.key === 'N') {{
                reject();
            }}
        }});
    </script>
</body>
</html>"""
    
    def _generate_dependencies_html(self, dependencies: List[str]) -> str:
        """Generate HTML for dependency list"""
        if not dependencies:
            return '<div class="detail-item"><strong>📦 Dependencies:</strong> None</div>'
        
        deps_html = '<div class="detail-item"><strong>📦 Dependencies:</strong></div>'
        deps_html += '<ul class="dependency-list">'
        
        for dep in dependencies:
            deps_html += f'<li class="dependency-item">🔗 {dep}</li>'
        
        deps_html += '</ul>'
        return deps_html
    
    def wait_for_approval(self, approval_id: str) -> ApprovalResult:
        """Wait for human approval response"""
        timeout = HUMAN_APPROVAL_CONFIG["approval_timeout"]
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check if approval result is available
            if approval_id in self.approval_results:
                result = self.approval_results.pop(approval_id)
                self.pending_approvals.pop(approval_id, None)
                return result
            
            # Wait a bit before checking again
            time.sleep(1)
        
        # Timeout
        self.pending_approvals.pop(approval_id, None)
        return ApprovalResult(
            approved=False,
            reason="Approval timeout exceeded",
            timestamp=time.time(),
            timeout=True
        )
    
    def handle_approval_response(self, approval_id: str, approved: bool, reason: str = ""):
        """Handle approval response from browser"""
        self.approval_results[approval_id] = ApprovalResult(
            approved=approved,
            reason=reason,
            timestamp=time.time()
        )
    
    def open_browser(self, file_path: Path):
        """Open browser to approval page"""
        try:
            # Convert to file:// URL
            file_url = file_path.as_uri()
            
            # Use configured browser or system default
            browser_command = BROWSER_INTEGRATION.get("browser_command")
            if browser_command:
                os.system(f"{browser_command} {file_url}")
            else:
                webbrowser.open(file_url)
                
            print(f"🌐 Opened approval page in browser: {file_url}")
            
        except Exception as e:
            print(f"⚠️ Failed to open browser: {e}")
            print(f"📄 Please manually open: {file_path}")
    
    def generate_control_dashboard(self, dag_status: Dict[str, Any]) -> str:
        """Generate main control dashboard HTML"""
        # This will be implemented in the next task
        pass
    
    def generate_execution_monitor(self, execution_data: Dict[str, Any]) -> str:
        """Generate real-time execution monitor HTML"""
        # This will be implemented in the next task
        pass
