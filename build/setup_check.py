#!/usr/bin/env python3
"""
Setup Check System - Ensures man pages and CLI are properly installed

Integrates with ./unhinged entry point to verify:
1. Man pages are installed to system MANPATH
2. 'unhinged' command is available in PATH
3. Environment is properly configured

Usage:
    from build.setup_check import SetupChecker

    checker = SetupChecker()
    checker.run_setup_checks()
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


class SetupChecker:
    """Handles setup verification and installation"""

    def __init__(self, project_root: Path | None = None):
        """Initialize setup checker

        Args:
            project_root: Project root directory (auto-detected if None)
        """
        if project_root is None:
            current = Path(__file__).parent
            self.project_root = current.parent if current.name == "build" else current
        else:
            self.project_root = Path(project_root)

    def check_man_pages(self) -> bool:
        """Check if man pages are installed"""
        man_dir = self.project_root / "man" / "man1"
        if not man_dir.exists():
            print("❌ Man pages directory not found")
            return False

        # Count both main unhinged.1 and subcommand pages
        man_files = list(man_dir.glob("unhinged*.1"))
        if not man_files:
            print("❌ No man pages found")
            return False

        print(f"✅ Found {len(man_files)} man pages")
        return True

    def install_man_pages(self) -> bool:
        """Install man pages to ~/.local/share/man (no sudo needed)"""
        try:
            man_src = self.project_root / "man" / "man1"
            man_dest = Path.home() / ".local" / "share" / "man" / "man1"

            if not man_src.exists():
                print("❌ Man pages source directory not found")
                return False

            # Create destination if needed
            man_dest.mkdir(parents=True, exist_ok=True)

            # Copy man pages
            for man_file in man_src.glob("unhinged-*.1"):
                dest_file = man_dest / man_file.name
                shutil.copy2(man_file, dest_file)
                print(f"   ✅ Installed {man_file.name}")

            print("✅ Man pages installed to ~/.local/share/man/man1")

            # Check if MANPATH includes ~/.local/share/man
            manpath_env = os.environ.get("MANPATH", "")
            local_man = str(Path.home() / ".local" / "share" / "man")
            if local_man not in manpath_env:
                print("\n⚠️  ~/.local/share/man is not in your MANPATH")
                print("   Add to ~/.bashrc or ~/.zshrc:")
                print('   export MANPATH="$HOME/.local/share/man:$MANPATH"')

            return True

        except Exception as e:
            print(f"❌ Error installing man pages: {e}")
            return False

    def check_unhinged_in_path(self) -> bool:
        """Check if 'unhinged' command is in PATH"""
        result = subprocess.run(["which", "unhinged"], capture_output=True)
        if result.returncode == 0:
            print(f"✅ 'unhinged' command found in PATH: {result.stdout.decode().strip()}")
            return True
        else:
            # Check if it's in local bin
            local_bin = Path.home() / ".local" / "bin" / "unhinged"
            if local_bin.exists():
                print("✅ 'unhinged' command found in ~/.local/bin")
                return True
            print("⚠️  'unhinged' command not in PATH")
            return False

    def install_unhinged_symlink(self) -> bool:
        """Create symlink for 'unhinged' command in ~/.local/bin (no sudo needed)"""
        try:
            unhinged_script = self.project_root / "unhinged"
            local_bin = Path.home() / ".local" / "bin"
            symlink_path = local_bin / "unhinged"

            if not unhinged_script.exists():
                print("❌ ./unhinged script not found")
                return False

            # Create ~/.local/bin if needed
            local_bin.mkdir(parents=True, exist_ok=True)

            # Remove existing symlink if present
            if symlink_path.exists() or symlink_path.is_symlink():
                symlink_path.unlink()

            # Create symlink
            symlink_path.symlink_to(unhinged_script)
            print(f"✅ Created symlink: ~/.local/bin/unhinged -> {unhinged_script}")

            # Check if ~/.local/bin is in PATH
            path_env = os.environ.get("PATH", "")
            if str(local_bin) not in path_env:
                print("\n⚠️  ~/.local/bin is not in your PATH")
                print("   Add to ~/.bashrc or ~/.zshrc:")
                print('   export PATH="$HOME/.local/bin:$PATH"')

            return True

        except Exception as e:
            print(f"❌ Error creating symlink: {e}")
            return False

    def run_setup_checks(self) -> bool:
        """Run all setup checks

        Returns:
            True if all checks pass, False otherwise
        """
        print("🚀 Running setup checks...")
        print(f"📁 Project root: {self.project_root}\n")

        checks = [
            ("Man pages", self.check_man_pages),
            ("'unhinged' in PATH", self.check_unhinged_in_path),
        ]

        all_passed = True
        for name, check_fn in checks:
            print(f"🔍 Checking {name}...")
            if not check_fn():
                all_passed = False
            print()

        if all_passed:
            print("✅ All setup checks PASSED")
        else:
            print("⚠️  Some setup checks failed. Run setup to fix:")
            print("   sudo python3 build/setup_check.py setup")

        return all_passed

    def run_setup(self) -> bool:
        """Run full setup installation"""
        print("🔧 Running setup installation...\n")

        success = True

        print("📦 Installing man pages to ~/.local/share/man...")
        if not self.install_man_pages():
            success = False
        print()

        print("🔗 Creating symlink in ~/.local/bin...")
        if not self.install_unhinged_symlink():
            success = False
        print()

        if success:
            print("✅ Setup installation COMPLETE")
            print("\n📝 Next steps:")
            print("   1. Add to ~/.bashrc (if not already present):")
            print('      export PATH="$HOME/.local/bin:$PATH"')
            print('      export MANPATH="$HOME/.local/share/man:$MANPATH"')
            print("   2. Reload shell: source ~/.bashrc")
            print("   3. Test: unhinged --help")
            print("   4. Test: man unhinged-generate")
        else:
            print("⚠️  Setup installation incomplete")

        return success


def main():
    """CLI interface for setup checker"""
    import argparse

    parser = argparse.ArgumentParser(description="Unhinged Setup Checker")
    parser.add_argument(
        "command", choices=["check", "setup", "install-man-pages", "install-symlink"], help="Command to execute"
    )

    args = parser.parse_args()
    checker = SetupChecker()

    if args.command == "check":
        success = checker.run_setup_checks()
        sys.exit(0 if success else 1)
    elif args.command == "setup":
        success = checker.run_setup()
        sys.exit(0 if success else 1)
    elif args.command == "install-man-pages":
        success = checker.install_man_pages()
        sys.exit(0 if success else 1)
    elif args.command == "install-symlink":
        success = checker.install_unhinged_symlink()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
