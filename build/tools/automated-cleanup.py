#!/usr/bin/env python3
"""
Automated Build Artifact Cleanup System

Implements time and size-based retention policies for build artifacts,
logs, cache files, and temporary data as recommended by expert assessment.

Usage:
    python build/tools/automated-cleanup.py [--dry-run] [--verbose]
"""

import argparse
import json
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any


class BuildCleanupManager:
    """Manages cleanup of build artifacts with configurable retention policies."""

    def __init__(self, project_root: Path, dry_run: bool = False, verbose: bool = False):
        self.project_root = project_root
        self.build_dir = project_root / "build"
        self.dry_run = dry_run
        self.verbose = verbose

        # Cleanup policies as recommended by expert
        self.policies = {
            "logs": {"max_age_days": 7, "max_count": 100, "patterns": ["*.log", "unhinged-session-*.log"]},
            "cache": {"max_size_gb": 10, "max_age_days": 30, "patterns": ["*.cache", "*.pkl", "__pycache__"]},
            "artifacts": {"max_age_days": 14, "patterns": ["*.whl", "*.tar.gz", "*.jar", "*.class"]},
            "checksums": {
                "max_entries": 1000,  # Down from 19,927
                "file": "code_checksums.json",
            },
        }

    def cleanup_all(self) -> dict[str, Any]:
        """Execute all cleanup policies and return summary."""
        print(f"🧹 Starting automated cleanup (dry_run={self.dry_run})")

        results = {
            "start_time": datetime.now().isoformat(),
            "policies_executed": [],
            "files_removed": 0,
            "bytes_freed": 0,
            "errors": [],
        }

        try:
            # Clean temporary logs
            log_result = self._cleanup_logs()
            results["policies_executed"].append(log_result)
            results["files_removed"] += log_result["files_removed"]
            results["bytes_freed"] += log_result["bytes_freed"]

            # Clean cache files
            cache_result = self._cleanup_cache()
            results["policies_executed"].append(cache_result)
            results["files_removed"] += cache_result["files_removed"]
            results["bytes_freed"] += cache_result["bytes_freed"]

            # Clean old artifacts
            artifact_result = self._cleanup_artifacts()
            results["policies_executed"].append(artifact_result)
            results["files_removed"] += artifact_result["files_removed"]
            results["bytes_freed"] += artifact_result["bytes_freed"]

            # Prune checksum file
            checksum_result = self._cleanup_checksums()
            results["policies_executed"].append(checksum_result)
            results["bytes_freed"] += checksum_result["bytes_freed"]

        except Exception as e:
            results["errors"].append(f"Cleanup failed: {e}")

        results["end_time"] = datetime.now().isoformat()
        self._print_summary(results)
        return results

    def _cleanup_logs(self) -> dict[str, Any]:
        """Clean up session logs and build logs."""
        policy = self.policies["logs"]
        result = {"policy": "logs", "files_removed": 0, "bytes_freed": 0, "details": []}

        tmp_dir = self.build_dir / "tmp"
        if not tmp_dir.exists():
            return result

        # Get all log files
        log_files = []
        for pattern in policy["patterns"]:
            log_files.extend(tmp_dir.glob(pattern))

        # Sort by modification time (newest first)
        log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        cutoff_time = time.time() - (policy["max_age_days"] * 24 * 3600)
        files_to_remove = []

        # Remove files older than max_age_days
        for log_file in log_files:
            if log_file.stat().st_mtime < cutoff_time:
                files_to_remove.append(log_file)

        # Remove excess files beyond max_count
        if len(log_files) > policy["max_count"]:
            files_to_remove.extend(log_files[policy["max_count"] :])

        # Remove duplicates
        files_to_remove = list(set(files_to_remove))

        for file_path in files_to_remove:
            try:
                file_size = file_path.stat().st_size
                if self.dry_run:
                    print(f"  Would remove: {file_path} ({file_size:,} bytes)")
                else:
                    file_path.unlink()
                    if self.verbose:
                        print(f"  Removed: {file_path} ({file_size:,} bytes)")

                result["files_removed"] += 1
                result["bytes_freed"] += file_size
                result["details"].append(str(file_path))

            except Exception as e:
                print(f"  Error removing {file_path}: {e}")

        return result

    def _cleanup_cache(self) -> dict[str, Any]:
        """Clean up cache files and directories."""
        policy = self.policies["cache"]
        result = {"policy": "cache", "files_removed": 0, "bytes_freed": 0, "details": []}

        cutoff_time = time.time() - (policy["max_age_days"] * 24 * 3600)

        # Find cache files throughout build directory
        for pattern in policy["patterns"]:
            for cache_item in self.build_dir.rglob(pattern):
                try:
                    if cache_item.stat().st_mtime < cutoff_time:
                        if cache_item.is_file():
                            file_size = cache_item.stat().st_size
                            if self.dry_run:
                                print(f"  Would remove cache file: {cache_item}")
                            else:
                                cache_item.unlink()
                                if self.verbose:
                                    print(f"  Removed cache file: {cache_item}")

                            result["files_removed"] += 1
                            result["bytes_freed"] += file_size

                        elif cache_item.is_dir() and pattern == "__pycache__":
                            dir_size = sum(f.stat().st_size for f in cache_item.rglob("*") if f.is_file())
                            if self.dry_run:
                                print(f"  Would remove cache dir: {cache_item}")
                            else:
                                shutil.rmtree(cache_item)
                                if self.verbose:
                                    print(f"  Removed cache dir: {cache_item}")

                            result["files_removed"] += 1
                            result["bytes_freed"] += dir_size

                except Exception as e:
                    print(f"  Error processing cache item {cache_item}: {e}")

        return result

    def _cleanup_artifacts(self) -> dict[str, Any]:
        """Clean up old build artifacts."""
        policy = self.policies["artifacts"]
        result = {"policy": "artifacts", "files_removed": 0, "bytes_freed": 0, "details": []}

        cutoff_time = time.time() - (policy["max_age_days"] * 24 * 3600)

        # Look for artifacts in generated/ and build/ directories
        search_dirs = [self.project_root / "generated", self.build_dir]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for pattern in policy["patterns"]:
                for artifact in search_dir.rglob(pattern):
                    try:
                        if artifact.stat().st_mtime < cutoff_time:
                            file_size = artifact.stat().st_size
                            if self.dry_run:
                                print(f"  Would remove artifact: {artifact}")
                            else:
                                artifact.unlink()
                                if self.verbose:
                                    print(f"  Removed artifact: {artifact}")

                            result["files_removed"] += 1
                            result["bytes_freed"] += file_size
                            result["details"].append(str(artifact))

                    except Exception as e:
                        print(f"  Error removing artifact {artifact}: {e}")

        return result

    def _cleanup_checksums(self) -> dict[str, Any]:
        """Prune excessive entries from checksum file."""
        policy = self.policies["checksums"]
        result = {"policy": "checksums", "files_removed": 0, "bytes_freed": 0, "details": []}

        checksum_file = self.build_dir / policy["file"]
        if not checksum_file.exists():
            return result

        try:
            with open(checksum_file) as f:
                data = json.load(f)

            original_size = checksum_file.stat().st_size
            original_count = len(data.get("checksums", {}))

            if original_count <= policy["max_entries"]:
                return result

            # Keep most recently updated entries
            checksums = data.get("checksums", {})

            # Sort by file modification time if available, otherwise keep arbitrary subset
            sorted_items = list(checksums.items())[: policy["max_entries"]]

            data["checksums"] = dict(sorted_items)
            data["metadata"]["pruned_at"] = datetime.now().isoformat()
            data["metadata"]["original_count"] = original_count

            if self.dry_run:
                print(f"  Would prune checksums: {original_count} → {len(sorted_items)} entries")
            else:
                with open(checksum_file, "w") as f:
                    json.dump(data, f, indent=2)

                new_size = checksum_file.stat().st_size
                result["bytes_freed"] = original_size - new_size
                result["details"].append(f"Pruned {original_count - len(sorted_items)} checksum entries")

                if self.verbose:
                    print(f"  Pruned checksums: {original_count} → {len(sorted_items)} entries")

        except Exception as e:
            print(f"  Error pruning checksums: {e}")

        return result

    def _print_summary(self, results: dict[str, Any]):
        """Print cleanup summary."""
        print("\n📊 Cleanup Summary:")
        print(f"   Files removed: {results['files_removed']:,}")
        print(f"   Space freed: {results['bytes_freed']:,} bytes ({results['bytes_freed'] / 1024 / 1024:.1f} MB)")
        print(f"   Policies executed: {len(results['policies_executed'])}")

        if results["errors"]:
            print(f"   Errors: {len(results['errors'])}")
            for error in results["errors"]:
                print(f"     • {error}")


def main():
    """Main cleanup function."""
    parser = argparse.ArgumentParser(description="Automated build artifact cleanup")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be cleaned without removing")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    cleanup_manager = BuildCleanupManager(project_root, args.dry_run, args.verbose)

    results = cleanup_manager.cleanup_all()

    # Save results for monitoring
    if not args.dry_run:
        results_file = project_root / "build" / "tmp" / "last_cleanup.json"
        results_file.parent.mkdir(exist_ok=True)
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

    return 0 if not results["errors"] else 1


if __name__ == "__main__":
    sys.exit(main())
