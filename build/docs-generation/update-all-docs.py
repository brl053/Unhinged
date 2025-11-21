#!/usr/bin/env python3
"""
Master Documentation Update Script

This script orchestrates all documentation generation and updates.
It ensures all documentation stays current with code changes.
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


class DocumentationUpdater:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.scripts_dir = self.root_path / "build" / "docs-generation"
        self.docs_dir = self.root_path / "docs"

    def update_all(self):
        """Update all documentation"""
        print("🚀 Starting comprehensive documentation update...")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("")

        success_count = 0
        total_count = 0

        # Update Makefile documentation
        total_count += 1
        if self._update_makefile_docs():
            success_count += 1

        # Update project structure documentation
        total_count += 1
        if self._update_project_structure():
            success_count += 1

        # Update API documentation
        total_count += 1
        if self._update_api_docs():
            success_count += 1

        # Update service documentation
        total_count += 1
        if self._update_service_docs():
            success_count += 1

        # Update LLM comment documentation
        total_count += 1
        if self._update_llm_comment_docs():
            success_count += 1

        # Validate documentation
        total_count += 1
        if self._validate_docs():
            success_count += 1

        # Generate summary
        self._generate_update_summary(success_count, total_count)

        print("")
        print(f"✅ Documentation update complete: {success_count}/{total_count} successful")

        return success_count == total_count

    def _update_makefile_docs(self) -> bool:
        """Update Makefile reference documentation"""
        print("📖 Updating Makefile documentation...")

        try:
            script_path = self.scripts_dir / "generate-makefile-docs.py"
            if not script_path.exists():
                print(f"❌ Script not found: {script_path}")
                return False

            result = subprocess.run(
                [sys.executable, str(script_path)], capture_output=True, text=True, cwd=self.root_path
            )

            if result.returncode == 0:
                print("✅ Makefile documentation updated")
                return True
            else:
                print(f"❌ Makefile documentation failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Error updating Makefile docs: {e}")
            return False

    def _update_project_structure(self) -> bool:
        """Update project structure documentation"""
        print("🏗️ Updating project structure documentation...")

        try:
            script_path = self.scripts_dir / "generate-project-structure.py"
            if not script_path.exists():
                print(f"❌ Script not found: {script_path}")
                return False

            result = subprocess.run(
                [sys.executable, str(script_path)], capture_output=True, text=True, cwd=self.root_path
            )

            if result.returncode == 0:
                print("✅ Project structure documentation updated")
                return True
            else:
                print(f"❌ Project structure documentation failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Error updating project structure docs: {e}")
            return False

    def _update_api_docs(self) -> bool:
        """Update API documentation from proto files"""
        print("📡 Updating API documentation...")

        try:
            # Check if proto files exist
            proto_dir = self.root_path / "proto"
            if not proto_dir.exists():
                print("⚠️ No proto directory found, skipping API docs")
                return True

            # Count proto files
            proto_files = list(proto_dir.glob("*.proto"))
            if not proto_files:
                print("⚠️ No proto files found, skipping API docs")
                return True

            # Generate API documentation
            api_doc_path = self.docs_dir / "api" / "generated-api-reference.md"
            api_doc_path.parent.mkdir(parents=True, exist_ok=True)

            with open(api_doc_path, "w") as f:
                f.write("# 📡 API Reference - Auto-Generated\n\n")
                f.write(f"> **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"> **Proto Files**: {len(proto_files)}\n\n")

                for proto_file in proto_files:
                    f.write(f"## {proto_file.name}\n\n")
                    f.write(f"**Path**: `{proto_file.relative_to(self.root_path)}`\n\n")

                    # Read proto file content
                    try:
                        with open(proto_file) as pf:
                            content = pf.read()
                            # Extract service definitions
                            if "service " in content:
                                f.write("**Services**:\n")
                                for line in content.split("\n"):
                                    if line.strip().startswith("service "):
                                        service_name = line.strip().split()[1]
                                        f.write(f"- {service_name}\n")
                                f.write("\n")
                    except Exception as e:
                        f.write(f"*Error reading file: {e}*\n\n")

            print("✅ API documentation updated")
            return True

        except Exception as e:
            print(f"❌ Error updating API docs: {e}")
            return False

    def _update_service_docs(self) -> bool:
        """Update service documentation"""
        print("🚀 Updating service documentation...")

        try:
            services_dir = self.root_path / "services"
            if not services_dir.exists():
                print("⚠️ No services directory found")
                return True

            # Generate services overview
            services_doc_path = self.docs_dir / "services" / "overview.md"
            services_doc_path.parent.mkdir(parents=True, exist_ok=True)

            with open(services_doc_path, "w") as f:
                f.write("# 🚀 Services Overview - Auto-Generated\n\n")
                f.write(f"> **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                service_dirs = [d for d in services_dir.iterdir() if d.is_dir()]
                f.write(f"**Total Services**: {len(service_dirs)}\n\n")

                for service_dir in service_dirs:
                    f.write(f"## {service_dir.name}\n\n")
                    f.write(f"**Path**: `{service_dir.relative_to(self.root_path)}`\n\n")

                    # Check for README
                    readme_path = service_dir / "README.md"
                    if readme_path.exists():
                        f.write("**Documentation**: ✅ Has README.md\n")
                    else:
                        f.write("**Documentation**: ❌ No README.md\n")

                    # Check for Dockerfile
                    dockerfile_path = service_dir / "Dockerfile"
                    if dockerfile_path.exists():
                        f.write("**Containerized**: ✅ Has Dockerfile\n")
                    else:
                        f.write("**Containerized**: ❌ No Dockerfile\n")

                    f.write("\n")

            print("✅ Service documentation updated")
            return True

        except Exception as e:
            print(f"❌ Error updating service docs: {e}")
            return False

    def _update_llm_comment_docs(self) -> bool:
        """Update documentation from LLM comments"""
        print("🤖 Updating LLM comment documentation...")

        try:
            script_path = self.scripts_dir / "extract-llm-comments.py"
            if not script_path.exists():
                print(f"❌ Script not found: {script_path}")
                return False

            result = subprocess.run(
                [sys.executable, str(script_path)], capture_output=True, text=True, cwd=self.root_path
            )

            if result.returncode == 0:
                print("✅ LLM comment documentation updated")
                return True
            else:
                print(f"❌ LLM comment documentation failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Error updating LLM comment docs: {e}")
            return False

    def _validate_docs(self) -> bool:
        """Validate documentation for consistency and completeness"""
        print("🔍 Validating documentation...")

        try:
            issues = []

            # Check for required documentation files
            required_docs = [
                "docs/contributing/llm-quickstart.md",
                "docs/development/makefile-reference.md",
                "docs/development/workflow.md",
            ]

            for doc_path in required_docs:
                full_path = self.root_path / doc_path
                if not full_path.exists():
                    issues.append(f"Missing required doc: {doc_path}")

            # Check for broken internal links (basic check)
            for doc_file in self.docs_dir.rglob("*.md"):
                try:
                    with open(doc_file) as f:
                        content = f.read()
                        # Check for common issues
                        if "TODO" in content:
                            issues.append(f"TODO found in {doc_file.relative_to(self.root_path)}")
                        if "FIXME" in content:
                            issues.append(f"FIXME found in {doc_file.relative_to(self.root_path)}")
                except Exception:
                    pass

            # Validate LLM comments
            try:
                llm_validator_path = self.scripts_dir / "validate-llm-comments.py"
                if llm_validator_path.exists():
                    result = subprocess.run(
                        [sys.executable, str(llm_validator_path)], capture_output=True, text=True, cwd=self.root_path
                    )

                    if result.returncode != 0:
                        issues.append("LLM comment validation failed - check validation report")
            except Exception as e:
                issues.append(f"Could not validate LLM comments: {e}")

            if issues:
                print("⚠️ Documentation validation issues found:")
                for issue in issues:
                    print(f"  - {issue}")
                return False
            else:
                print("✅ Documentation validation passed")
                return True

        except Exception as e:
            print(f"❌ Error validating docs: {e}")
            return False

    def _generate_update_summary(self, success_count: int, total_count: int):
        """Generate update summary"""
        summary_path = self.docs_dir / "LAST_UPDATE.md"

        try:
            with open(summary_path, "w") as f:
                f.write("# 📋 Documentation Update Summary\n\n")
                f.write(f"**Last Update**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Success Rate**: {success_count}/{total_count}\n")
                f.write(f"**Status**: {'✅ All Updated' if success_count == total_count else '⚠️ Some Issues'}\n\n")

                f.write("## Updated Documentation\n\n")
                f.write("- Makefile Reference\n")
                f.write("- Project Structure\n")
                f.write("- API Reference\n")
                f.write("- Service Overview\n")
                f.write("- Documentation Validation\n\n")

                f.write("## Next Steps\n\n")
                if success_count < total_count:
                    f.write("- Review and fix documentation generation issues\n")
                    f.write("- Re-run `make docs-update` after fixes\n")
                else:
                    f.write("- Documentation is up to date\n")
                    f.write("- Run `make docs-update` after significant code changes\n")

        except Exception as e:
            print(f"⚠️ Could not generate update summary: {e}")


def main():
    """Main function"""
    updater = DocumentationUpdater()
    success = updater.update_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
