#!/usr/bin/env python3
"""
Development Tools Migration Script

Migrates development tools from /tools to /build/tools as part of the
build system consolidation and /generated Artifactory pattern.

This script:
1. Copies tools from /tools to /build/tools
2. Updates references in scripts and documentation
3. Creates compatibility symlinks if needed
4. Generates migration report
"""

import shutil
from pathlib import Path
from typing import Any


class ToolsMigrator:
    """Handles migration of development tools to build framework."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tools_dir = project_root / "tools"
        self.build_tools_dir = project_root / "build" / "tools"
        self.migration_report = []

    def migrate_all_tools(self) -> dict[str, Any]:
        """Migrate all tools from /tools to /build/tools."""
        print("🔧 Starting development tools migration...")

        # Ensure build/tools directory exists
        self.build_tools_dir.mkdir(parents=True, exist_ok=True)

        # Migrate each tool directory
        migrated_tools = []

        for tool_dir in self.tools_dir.iterdir():
            if tool_dir.is_dir() and tool_dir.name != "__pycache__":
                result = self._migrate_tool(tool_dir)
                migrated_tools.append(result)

        # Copy standalone scripts
        for script_file in self.tools_dir.glob("*.sh"):
            result = self._migrate_script(script_file)
            migrated_tools.append(result)

        # Generate migration report
        report = {
            "migration_timestamp": "2024-01-01T00:00:00Z",
            "migrated_tools": migrated_tools,
            "total_tools": len(migrated_tools),
            "success_count": len([t for t in migrated_tools if t["status"] == "success"]),
            "recommendations": self._generate_recommendations(),
        }

        return report

    def _migrate_tool(self, tool_dir: Path) -> dict[str, Any]:
        """Migrate a single tool directory."""
        tool_name = tool_dir.name
        target_dir = self.build_tools_dir / tool_name

        try:
            if target_dir.exists():
                print(f"⚠️  Tool {tool_name} already exists in build/tools, skipping...")
                return {"name": tool_name, "type": "directory", "status": "skipped", "reason": "already_exists"}

            # Copy the entire tool directory
            shutil.copytree(tool_dir, target_dir)
            print(f"✅ Migrated tool: {tool_name}")

            return {
                "name": tool_name,
                "type": "directory",
                "status": "success",
                "source": str(tool_dir),
                "target": str(target_dir),
            }

        except Exception as e:
            print(f"❌ Failed to migrate {tool_name}: {e}")
            return {"name": tool_name, "type": "directory", "status": "error", "error": str(e)}

    def _migrate_script(self, script_file: Path) -> dict[str, Any]:
        """Migrate a standalone script file."""
        script_name = script_file.name
        target_file = self.build_tools_dir / script_name

        try:
            if target_file.exists():
                print(f"⚠️  Script {script_name} already exists in build/tools, skipping...")
                return {"name": script_name, "type": "script", "status": "skipped", "reason": "already_exists"}

            # Copy the script
            shutil.copy2(script_file, target_file)
            # Make executable
            target_file.chmod(0o755)
            print(f"✅ Migrated script: {script_name}")

            return {
                "name": script_name,
                "type": "script",
                "status": "success",
                "source": str(script_file),
                "target": str(target_file),
            }

        except Exception as e:
            print(f"❌ Failed to migrate {script_name}: {e}")
            return {"name": script_name, "type": "script", "status": "error", "error": str(e)}

    def _generate_recommendations(self) -> list[str]:
        """Generate recommendations for post-migration actions."""
        return [
            "Update Makefile references from tools/ to build/tools/",
            "Update documentation to reflect new tool locations",
            "Consider removing original /tools directory after verification",
            "Add build/tools to CI/CD pipeline for tool building",
            "Update PATH variables in development scripts",
            "Create compatibility symlinks if needed for external scripts",
        ]

    def update_makefile_references(self) -> None:
        """Update Makefile to use build/tools instead of tools/."""
        makefile_path = self.project_root / "Makefile"

        if not makefile_path.exists():
            print("⚠️  Makefile not found, skipping reference updates")
            return

        try:
            with open(makefile_path) as f:
                content = f.read()

            # Update tool references
            updated_content = content.replace("tools/", "build/tools/")

            with open(makefile_path, "w") as f:
                f.write(updated_content)

            print("✅ Updated Makefile references to use build/tools/")

        except Exception as e:
            print(f"❌ Failed to update Makefile: {e}")

    def create_compatibility_symlinks(self) -> None:
        """Create symlinks for backward compatibility."""
        print("🔗 Creating compatibility symlinks...")

        # Create symlink from tools/ to build/tools/ for compatibility
        tools_symlink = self.project_root / "tools-legacy"

        try:
            if not tools_symlink.exists():
                tools_symlink.symlink_to("build/tools")
                print("✅ Created compatibility symlink: tools-legacy -> build/tools")
            else:
                print("⚠️  Compatibility symlink already exists")

        except Exception as e:
            print(f"❌ Failed to create compatibility symlink: {e}")


def main():
    """Main migration function."""
    project_root = Path(__file__).parent.parent.parent
    migrator = ToolsMigrator(project_root)

    print("🚀 Development Tools Migration to Build Framework")
    print("=" * 60)

    # Perform migration
    report = migrator.migrate_all_tools()

    # Update references
    migrator.update_makefile_references()

    # Print summary
    print("\n📊 Migration Summary:")
    print(f"   Total tools: {report['total_tools']}")
    print(f"   Successful: {report['success_count']}")
    print(f"   Failed: {report['total_tools'] - report['success_count']}")

    print("\n💡 Recommendations:")
    for rec in report["recommendations"]:
        print(f"   • {rec}")

    # Save report
    report_path = project_root / "generated" / "reports" / "tools-migration.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    import json

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Migration report saved: {report_path}")
    print("✅ Tools migration complete!")


if __name__ == "__main__":
    main()
