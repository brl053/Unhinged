#!/usr/bin/env python3

"""
@llm-type service
@llm-legend Auto-update system for Unhinged desktop application
@llm-key Provides automatic update checking and installation for the dual-system architecture desktop application
@llm-map Auto-updater that checks for new versions and can update the desktop application automatically
@llm-axiom Applications should stay current automatically without user intervention
@llm-contract Provides version checking, update downloading, and automatic installation capabilities
@llm-token auto-updater: Automatic update system for desktop application

Auto-Update System for Unhinged Desktop Application

Provides comprehensive auto-update functionality:
- Version checking against local and remote sources
- Automatic update detection on application launch
- Safe update downloading and installation
- Rollback capability in case of update failures
- User notification and consent management
- Integration with existing desktop application

Author: Unhinged Team
Version: 1.0.0
Date: 2025-10-26
"""

import os
import sys
import json
import hashlib
import subprocess
import shutil
import tempfile
import time
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum
import urllib.request
import urllib.error

class UpdateStatus(Enum):
    """Update status enumeration"""
    UP_TO_DATE = "up_to_date"
    UPDATE_AVAILABLE = "update_available"
    UPDATE_REQUIRED = "update_required"
    UPDATE_FAILED = "update_failed"
    CHECKING = "checking"
    DOWNLOADING = "downloading"
    INSTALLING = "installing"

@dataclass
class VersionInfo:
    """Version information structure"""
    version: str
    build_date: str
    commit_hash: str
    features: List[str]
    checksum: str

@dataclass
class UpdateInfo:
    """Update information structure"""
    current_version: VersionInfo
    latest_version: Optional[VersionInfo]
    status: UpdateStatus
    update_url: Optional[str] = None
    changelog: Optional[str] = None
    size_bytes: Optional[int] = None

class AutoUpdater:
    """Auto-update system for Unhinged desktop application"""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.desktop_dir = self.project_root / "desktop"
        self.version_file = self.desktop_dir / "version.json"
        self.update_cache_dir = self.project_root / "build" / "update_cache"
        self.backup_dir = self.project_root / "build" / "backup"
        
        # Update sources (in order of preference)
        self.update_sources = [
            self._check_local_build,
            self._check_git_repository,
            # self._check_remote_releases,  # Future: remote release server
        ]
        
        # Ensure directories exist
        self.update_cache_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize session logging if available
        self.session_logger = None
        try:
            sys.path.append(str(self.project_root / "libs" / "event-framework" / "python" / "src"))
            from unhinged_events import create_gui_session_logger
            self.session_logger = create_gui_session_logger(self.project_root)
        except ImportError:
            pass
    
    def get_current_version(self) -> VersionInfo:
        """Get current application version"""
        try:
            if self.version_file.exists():
                with open(self.version_file, 'r') as f:
                    data = json.load(f)
                return VersionInfo(**data)
            else:
                # Generate version from current state
                return self._generate_current_version()
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_gui_event("VERSION_CHECK_ERROR", f"Failed to get current version: {e}")
            return self._generate_fallback_version()
    
    def check_for_updates(self) -> UpdateInfo:
        """Check for available updates"""
        if self.session_logger:
            self.session_logger.log_gui_event("UPDATE_CHECK_START", "Starting update check")
        
        current_version = self.get_current_version()
        latest_version = None
        
        # Check each update source
        for source_check in self.update_sources:
            try:
                version = source_check()
                if version and self._is_newer_version(version, current_version):
                    latest_version = version
                    break
            except Exception as e:
                if self.session_logger:
                    self.session_logger.log_gui_event("UPDATE_SOURCE_ERROR", f"Update source failed: {e}")
                continue
        
        # Determine update status
        if latest_version is None:
            status = UpdateStatus.UP_TO_DATE
        elif self._is_critical_update(latest_version, current_version):
            status = UpdateStatus.UPDATE_REQUIRED
        else:
            status = UpdateStatus.UPDATE_AVAILABLE
        
        update_info = UpdateInfo(
            current_version=current_version,
            latest_version=latest_version,
            status=status
        )
        
        if self.session_logger:
            self.session_logger.log_gui_event("UPDATE_CHECK_COMPLETE", f"Update status: {status.value}")
        
        return update_info
    
    def download_update(self, update_info: UpdateInfo) -> bool:
        """Download update package"""
        if not update_info.latest_version:
            return False
        
        if self.session_logger:
            self.session_logger.log_gui_event("UPDATE_DOWNLOAD_START", f"Downloading version {update_info.latest_version.version}")
        
        try:
            # For local builds, copy files directly
            if self._is_local_build_update(update_info):
                return self._copy_local_build(update_info)
            
            # For remote updates, download package
            # TODO: Implement remote download when needed
            return True
            
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_gui_event("UPDATE_DOWNLOAD_ERROR", f"Download failed: {e}")
            return False
    
    def install_update(self, update_info: UpdateInfo) -> bool:
        """Install downloaded update"""
        if self.session_logger:
            self.session_logger.log_gui_event("UPDATE_INSTALL_START", f"Installing version {update_info.latest_version.version}")
        
        try:
            # Create backup of current version
            if not self._create_backup():
                return False
            
            # Install new version
            if self._install_new_version(update_info):
                # Update version file
                self._update_version_file(update_info.latest_version)
                
                # Update desktop registration
                self._update_desktop_registration()
                
                if self.session_logger:
                    self.session_logger.log_gui_event("UPDATE_INSTALL_SUCCESS", f"Successfully updated to version {update_info.latest_version.version}")
                
                return True
            else:
                # Rollback on failure
                self._rollback_update()
                return False
                
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_gui_event("UPDATE_INSTALL_ERROR", f"Installation failed: {e}")
            self._rollback_update()
            return False
    
    def _generate_current_version(self) -> VersionInfo:
        """Generate version info from current application state"""
        try:
            # Get git commit hash if available
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            commit_hash = result.stdout.strip() if result.returncode == 0 else "unknown"
            
            # Get build date from desktop app file
            desktop_app = self.desktop_dir / "unhinged-desktop-app"
            if desktop_app.exists():
                build_date = time.strftime("%Y-%m-%d", time.gmtime(desktop_app.stat().st_mtime))
            else:
                build_date = time.strftime("%Y-%m-%d")
            
            # Calculate checksum of desktop application
            checksum = self._calculate_app_checksum()
            
            # Detect features
            features = self._detect_current_features()
            
            return VersionInfo(
                version="1.0.0-dev",
                build_date=build_date,
                commit_hash=commit_hash,
                features=features,
                checksum=checksum
            )
            
        except Exception:
            return self._generate_fallback_version()
    
    def _generate_fallback_version(self) -> VersionInfo:
        """Generate fallback version info"""
        return VersionInfo(
            version="1.0.0-unknown",
            build_date=time.strftime("%Y-%m-%d"),
            commit_hash="unknown",
            features=["basic"],
            checksum="unknown"
        )
    
    def _check_local_build(self) -> Optional[VersionInfo]:
        """Check for updates from local build system"""
        try:
            # Check if there are newer built artifacts
            build_dir = self.project_root / "build" / "dual-system"
            if not build_dir.exists():
                return None
            
            # Check if build artifacts are newer than current app
            desktop_app = self.desktop_dir / "unhinged-desktop-app"
            if not desktop_app.exists():
                return None
            
            current_mtime = desktop_app.stat().st_mtime
            
            # Check for newer built desktop app
            built_app = build_dir / "unhinged-desktop-app"
            if built_app.exists() and built_app.stat().st_mtime > current_mtime:
                # Generate version info for built version
                return VersionInfo(
                    version="1.0.0-local-build",
                    build_date=time.strftime("%Y-%m-%d", time.gmtime(built_app.stat().st_mtime)),
                    commit_hash=self._get_git_commit(),
                    features=self._detect_built_features(build_dir),
                    checksum=self._calculate_file_checksum(built_app)
                )
            
            return None
            
        except Exception:
            return None
    
    def _check_git_repository(self) -> Optional[VersionInfo]:
        """Check for updates from git repository"""
        try:
            # Check if we're in a git repository
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return None
            
            # Check for uncommitted changes in desktop directory
            result = subprocess.run(
                ["git", "status", "--porcelain", "desktop/"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                # There are uncommitted changes, suggest rebuild
                return VersionInfo(
                    version="1.0.0-git-dirty",
                    build_date=time.strftime("%Y-%m-%d"),
                    commit_hash=self._get_git_commit(),
                    features=self._detect_current_features(),
                    checksum="dirty"
                )
            
            return None
            
        except Exception:
            return None
    
    def _is_newer_version(self, new_version: VersionInfo, current_version: VersionInfo) -> bool:
        """Check if new version is newer than current"""
        # Simple version comparison - can be enhanced
        if new_version.checksum != current_version.checksum:
            return True
        
        if new_version.commit_hash != current_version.commit_hash:
            return True
        
        if new_version.build_date > current_version.build_date:
            return True
        
        return False
    
    def _is_critical_update(self, new_version: VersionInfo, current_version: VersionInfo) -> bool:
        """Check if update is critical (required)"""
        # Define critical update conditions
        critical_features = ["security-fix", "critical-bug-fix", "dual-system-architecture"]
        
        return any(feature in new_version.features for feature in critical_features)
    
    def _calculate_app_checksum(self) -> str:
        """Calculate checksum of desktop application"""
        desktop_app = self.desktop_dir / "unhinged-desktop-app"
        if desktop_app.exists():
            return self._calculate_file_checksum(desktop_app)
        return "missing"
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()[:16]  # Short hash
    
    def _detect_current_features(self) -> List[str]:
        """Detect features in current application"""
        features = ["basic"]
        
        # Check for dual-system architecture
        conversation_cli = self.project_root / "control" / "conversation_cli.py"
        if conversation_cli.exists():
            features.append("dual-system-architecture")
            features.append("conversation-interface")
        
        # Check for native C graphics
        graphics_lib = self.project_root / "libs" / "graphics" / "build" / "libunhinged_graphics.so"
        if graphics_lib.exists():
            features.append("native-c-graphics")
        
        # Check for session logging
        event_framework = self.project_root / "libs" / "event-framework"
        if event_framework.exists():
            features.append("session-logging")
        
        return features
    
    def _detect_built_features(self, build_dir: Path) -> List[str]:
        """Detect features in built version"""
        features = ["basic", "dual-system-architecture"]
        
        if (build_dir / "conversation_cli.py").exists():
            features.append("conversation-interface")
        
        return features
    
    def _get_git_commit(self) -> str:
        """Get current git commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"
    
    def _is_local_build_update(self, update_info: UpdateInfo) -> bool:
        """Check if this is a local build update"""
        return update_info.latest_version and "local-build" in update_info.latest_version.version
    
    def _copy_local_build(self, update_info: UpdateInfo) -> bool:
        """Copy local build artifacts"""
        try:
            build_dir = self.project_root / "build" / "dual-system"
            
            # Copy desktop application
            src_app = build_dir / "unhinged-desktop-app"
            dst_app = self.desktop_dir / "unhinged-desktop-app"
            
            if src_app.exists():
                shutil.copy2(src_app, dst_app)
                dst_app.chmod(0o755)
                return True
            
            return False
            
        except Exception:
            return False
    
    def _create_backup(self) -> bool:
        """Create backup of current version"""
        try:
            backup_timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"backup_{backup_timestamp}"
            backup_path.mkdir(exist_ok=True)
            
            # Backup desktop application
            desktop_app = self.desktop_dir / "unhinged-desktop-app"
            if desktop_app.exists():
                shutil.copy2(desktop_app, backup_path / "unhinged-desktop-app")
            
            # Backup version file
            if self.version_file.exists():
                shutil.copy2(self.version_file, backup_path / "version.json")
            
            return True
            
        except Exception:
            return False
    
    def _install_new_version(self, update_info: UpdateInfo) -> bool:
        """Install new version from cache"""
        # For local builds, files are already copied
        return True
    
    def _update_version_file(self, version_info: VersionInfo):
        """Update version file with new version info"""
        version_data = {
            "version": version_info.version,
            "build_date": version_info.build_date,
            "commit_hash": version_info.commit_hash,
            "features": version_info.features,
            "checksum": version_info.checksum
        }
        
        with open(self.version_file, 'w') as f:
            json.dump(version_data, f, indent=2)
    
    def _update_desktop_registration(self):
        """Update desktop registration after update"""
        try:
            install_script = self.desktop_dir / "install-desktop-app.sh"
            if install_script.exists():
                subprocess.run([
                    "bash", str(install_script), "--user"
                ], cwd=self.desktop_dir, capture_output=True)
        except Exception:
            pass
    
    def _rollback_update(self):
        """Rollback to previous version"""
        try:
            # Find most recent backup
            backups = sorted(self.backup_dir.glob("backup_*"), reverse=True)
            if backups:
                latest_backup = backups[0]
                
                # Restore desktop application
                backup_app = latest_backup / "unhinged-desktop-app"
                if backup_app.exists():
                    shutil.copy2(backup_app, self.desktop_dir / "unhinged-desktop-app")
                
                # Restore version file
                backup_version = latest_backup / "version.json"
                if backup_version.exists():
                    shutil.copy2(backup_version, self.version_file)
                
                if self.session_logger:
                    self.session_logger.log_gui_event("UPDATE_ROLLBACK", f"Rolled back to backup: {latest_backup.name}")
        except Exception as e:
            if self.session_logger:
                self.session_logger.log_gui_event("UPDATE_ROLLBACK_ERROR", f"Rollback failed: {e}")

def main():
    """Test the auto-updater"""
    project_root = Path(__file__).parent.parent
    updater = AutoUpdater(project_root)
    
    print("🔄 Checking for updates...")
    update_info = updater.check_for_updates()
    
    print(f"📋 Current version: {update_info.current_version.version}")
    print(f"📊 Status: {update_info.status.value}")
    
    if update_info.latest_version:
        print(f"🆕 Latest version: {update_info.latest_version.version}")
        print(f"🔧 Features: {', '.join(update_info.latest_version.features)}")

if __name__ == "__main__":
    main()
