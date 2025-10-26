#!/usr/bin/env python3

"""
Enhanced Error Guidance System

Provides clear, actionable error messages and troubleshooting steps
for common build and system issues.
"""

import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ErrorGuidance:
    """Provides contextual error guidance and troubleshooting steps"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.error_patterns = self._build_error_patterns()
    
    def analyze_error(self, error_message: str, context: str = "") -> Dict:
        """Analyze error and provide guidance"""
        guidance = {
            'error_type': 'unknown',
            'description': 'An error occurred during the build process',
            'likely_cause': 'Unknown cause',
            'fix_commands': [],
            'additional_info': [],
            'severity': 'medium'
        }
        
        # Match against known error patterns
        for pattern, handler in self.error_patterns.items():
            if re.search(pattern, error_message, re.IGNORECASE):
                guidance.update(handler(error_message, context))
                break
        
        return guidance
    
    def _build_error_patterns(self) -> Dict:
        """Build dictionary of error patterns and their handlers"""
        return {
            r'cmake.*not found|cmake.*command not found': self._handle_cmake_missing,
            r'gcc.*not found|clang.*not found|compiler.*not found': self._handle_compiler_missing,
            r'drm\.h.*no such file|libdrm.*not found': self._handle_drm_missing,
            r'cffi.*not found|import cffi.*failed': self._handle_cffi_missing,
            r'python3.*not found': self._handle_python_missing,
            r'docker.*not found|docker.*permission denied': self._handle_docker_issues,
            r'port.*already in use|address already in use': self._handle_port_conflicts,
            r'no space left on device': self._handle_disk_space,
            r'permission denied': self._handle_permissions,
            r'timeout|timed out': self._handle_timeouts,
            r'network.*unreachable|connection.*refused': self._handle_network_issues,
        }
    
    def _handle_cmake_missing(self, error: str, context: str) -> Dict:
        return {
            'error_type': 'missing_dependency',
            'description': 'CMake build system is not installed',
            'likely_cause': 'CMake is required for building C/C++ components but is not available in PATH',
            'fix_commands': [
                '# Install CMake using the project dependency manager',
                'python3 build/dependencies/package_manager.py install cmake',
                '',
                '# Alternative: Install manually',
                'sudo apt-get update && sudo apt-get install -y cmake',
                '',
                '# Verify installation',
                'cmake --version'
            ],
            'additional_info': [
                'CMake is required for building the native C graphics library',
                'The graphics library provides hardware-accelerated rendering capabilities',
                'Without CMake, the system cannot build native components'
            ],
            'severity': 'high'
        }
    
    def _handle_compiler_missing(self, error: str, context: str) -> Dict:
        return {
            'error_type': 'missing_dependency',
            'description': 'C/C++ compiler is not installed',
            'likely_cause': 'GCC or Clang compiler is required for building native C components',
            'fix_commands': [
                '# Install build tools using project dependency manager',
                'python3 build/dependencies/package_manager.py install build-essential',
                '',
                '# Alternative: Install manually',
                'sudo apt-get update && sudo apt-get install -y build-essential',
                '',
                '# Verify installation',
                'gcc --version',
                'g++ --version'
            ],
            'additional_info': [
                'build-essential includes GCC, G++, and other essential build tools',
                'These are required for compiling the native C graphics library',
                'The graphics library provides direct hardware access for rendering'
            ],
            'severity': 'high'
        }
    
    def _handle_drm_missing(self, error: str, context: str) -> Dict:
        return {
            'error_type': 'missing_dependency',
            'description': 'DRM (Direct Rendering Manager) headers are missing',
            'likely_cause': 'libdrm development headers are required for native graphics rendering',
            'fix_commands': [
                '# Install DRM development headers',
                'sudo apt-get update && sudo apt-get install -y libdrm-dev',
                '',
                '# Verify DRM headers are available',
                'ls -la /usr/include/xf86drm.h',
                'ls -la /usr/include/libdrm/',
                '',
                '# Test DRM compilation',
                'echo \'#include <xf86drm.h>\nint main(){return 0;}\' | gcc -I/usr/include/libdrm -x c - -ldrm'
            ],
            'additional_info': [
                'DRM provides direct access to graphics hardware',
                'Required for native rendering without external browser dependencies',
                'Essential for the voice-first, independent system architecture'
            ],
            'severity': 'high'
        }
    
    def _handle_cffi_missing(self, error: str, context: str) -> Dict:
        return {
            'error_type': 'missing_dependency',
            'description': 'CFFI (C Foreign Function Interface) is not available',
            'likely_cause': 'CFFI is required for Python-C integration in the graphics system',
            'fix_commands': [
                '# Install CFFI in the centralized Python environment',
                'build/python/venv/bin/pip install cffi',
                '',
                '# Alternative: Install system-wide',
                'pip3 install cffi --break-system-packages',
                '',
                '# Verify CFFI installation',
                'build/python/venv/bin/python -c "import cffi; print(\'CFFI version:\', cffi.__version__)"'
            ],
            'additional_info': [
                'CFFI enables Python to call C functions directly',
                'Required for integrating the C graphics library with Python services',
                'Essential for the build system to generate Python bindings'
            ],
            'severity': 'medium'
        }
    
    def _handle_python_missing(self, error: str, context: str) -> Dict:
        return {
            'error_type': 'missing_dependency',
            'description': 'Python 3 is not available in PATH',
            'likely_cause': 'Python 3 is required for the build system and service management',
            'fix_commands': [
                '# Install Python 3',
                'sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv',
                '',
                '# Verify installation',
                'python3 --version',
                'pip3 --version'
            ],
            'additional_info': [
                'Python 3 is the foundation of the Unhinged build system',
                'Required for service orchestration and build management',
                'The centralized Python environment depends on system Python 3'
            ],
            'severity': 'critical'
        }
    
    def _handle_docker_issues(self, error: str, context: str) -> Dict:
        if 'permission denied' in error.lower():
            return {
                'error_type': 'permission_issue',
                'description': 'Docker permission denied',
                'likely_cause': 'User is not in the docker group or Docker daemon is not running',
                'fix_commands': [
                    '# Add user to docker group',
                    'sudo usermod -aG docker $USER',
                    '',
                    '# Start Docker daemon',
                    'sudo systemctl start docker',
                    'sudo systemctl enable docker',
                    '',
                    '# Apply group changes (requires logout/login or newgrp)',
                    'newgrp docker',
                    '',
                    '# Test Docker access',
                    'docker ps'
                ],
                'additional_info': [
                    'Docker is required for service orchestration',
                    'Services include LLM, TTS, Vision AI, and Persistence Platform',
                    'Group membership changes require logout/login to take effect'
                ],
                'severity': 'high'
            }
        else:
            return {
                'error_type': 'missing_dependency',
                'description': 'Docker is not installed or not running',
                'likely_cause': 'Docker is required for service containerization',
                'fix_commands': [
                    '# Install Docker',
                    'curl -fsSL https://get.docker.com -o get-docker.sh',
                    'sudo sh get-docker.sh',
                    '',
                    '# Start Docker service',
                    'sudo systemctl start docker',
                    'sudo systemctl enable docker',
                    '',
                    '# Verify installation',
                    'docker --version',
                    'docker ps'
                ],
                'additional_info': [
                    'Docker provides containerized services for the voice-first platform',
                    'Required for LLM, TTS, Vision AI, and database services',
                    'Essential for the independent, self-contained architecture'
                ],
                'severity': 'high'
            }
    
    def _handle_port_conflicts(self, error: str, context: str) -> Dict:
        return {
            'error_type': 'configuration_issue',
            'description': 'Port conflict detected',
            'likely_cause': 'Another service is already using the required port',
            'fix_commands': [
                '# Check what\'s using the port (replace 8080 with actual port)',
                'sudo netstat -tlnp | grep :8080',
                'sudo lsof -i :8080',
                '',
                '# Stop conflicting service if safe to do so',
                'sudo systemctl stop <service-name>',
                '',
                '# Or use the port management system',
                'python3 control/network/port_manager.py --resolve-conflicts',
                '',
                '# Check current port allocations',
                'make ports'
            ],
            'additional_info': [
                'The system uses categorical port allocation to prevent conflicts',
                'AI services: 1100-1199, Data services: 1200-1299, etc.',
                'Use the unified port manager to resolve conflicts automatically'
            ],
            'severity': 'medium'
        }
    
    def _handle_disk_space(self, error: str, context: str) -> Dict:
        return {
            'error_type': 'system_resource',
            'description': 'Insufficient disk space',
            'likely_cause': 'The build process requires disk space for compilation and caching',
            'fix_commands': [
                '# Check disk usage',
                'df -h',
                'du -sh .build-cache/',
                '',
                '# Clean build cache',
                'rm -rf .build-cache/*',
                '',
                '# Clean Docker images and containers',
                'docker system prune -f',
                'docker image prune -a -f',
                '',
                '# Check space again',
                'df -h'
            ],
            'additional_info': [
                'Build cache can grow large over time',
                'Docker images for services require significant space',
                'Consider increasing disk space or cleaning unused files'
            ],
            'severity': 'high'
        }
    
    def _handle_permissions(self, error: str, context: str) -> Dict:
        return {
            'error_type': 'permission_issue',
            'description': 'Permission denied error',
            'likely_cause': 'Insufficient permissions to access files or directories',
            'fix_commands': [
                '# Check file permissions',
                'ls -la',
                '',
                '# Fix ownership if needed (be careful!)',
                'sudo chown -R $USER:$USER .',
                '',
                '# Make scripts executable',
                'chmod +x build/python/setup.py',
                'chmod +x control/service_launcher.py',
                '',
                '# Check if running in correct directory',
                'pwd'
            ],
            'additional_info': [
                'Permission issues often occur after sudo operations',
                'Ensure you\'re running commands from the project root',
                'Some operations may require sudo, others should not use sudo'
            ],
            'severity': 'medium'
        }
    
    def _handle_timeouts(self, error: str, context: str) -> Dict:
        return {
            'error_type': 'performance_issue',
            'description': 'Operation timed out',
            'likely_cause': 'Process took longer than expected, possibly due to system load',
            'fix_commands': [
                '# Check system resources',
                'top',
                'free -h',
                'df -h',
                '',
                '# Try with increased timeout',
                'python3 build/build.py build <target> --timeout 600',
                '',
                '# Check for hanging processes',
                'ps aux | grep cmake',
                'ps aux | grep gcc'
            ],
            'additional_info': [
                'Timeouts can occur during heavy compilation',
                'System may be under high load or low on resources',
                'Consider running builds when system is less busy'
            ],
            'severity': 'medium'
        }
    
    def _handle_network_issues(self, error: str, context: str) -> Dict:
        return {
            'error_type': 'network_issue',
            'description': 'Network connectivity problem',
            'likely_cause': 'Unable to reach external services or repositories',
            'fix_commands': [
                '# Check network connectivity',
                'ping -c 3 8.8.8.8',
                'curl -I https://github.com',
                '',
                '# Check DNS resolution',
                'nslookup github.com',
                '',
                '# Try with different DNS',
                'echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf.backup',
                '',
                '# Check proxy settings if in corporate environment',
                'echo $http_proxy',
                'echo $https_proxy'
            ],
            'additional_info': [
                'Network issues can prevent package downloads',
                'Some corporate networks require proxy configuration',
                'The system is designed to work offline once dependencies are installed'
            ],
            'severity': 'medium'
        }


def format_error_guidance(guidance: Dict) -> str:
    """Format error guidance for display"""
    severity_colors = {
        'critical': '🔴',
        'high': '🟠', 
        'medium': '🟡',
        'low': '🟢'
    }
    
    color = severity_colors.get(guidance['severity'], '🔵')
    
    output = [
        f"\n{color} ERROR ANALYSIS",
        "=" * 50,
        f"Error Type: {guidance['error_type']}",
        f"Description: {guidance['description']}",
        f"Likely Cause: {guidance['likely_cause']}",
        f"Severity: {guidance['severity'].upper()}",
        ""
    ]
    
    if guidance['fix_commands']:
        output.extend([
            "🔧 RECOMMENDED FIXES:",
            "-" * 30
        ])
        for cmd in guidance['fix_commands']:
            output.append(cmd)
        output.append("")
    
    if guidance['additional_info']:
        output.extend([
            "💡 ADDITIONAL INFORMATION:",
            "-" * 30
        ])
        for info in guidance['additional_info']:
            output.append(f"• {info}")
        output.append("")
    
    return "\n".join(output)
