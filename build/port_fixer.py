#!/usr/bin/env python3
"""
@llm-type build-tool
@llm-legend Port conflict detection and automatic resolution tool
@llm-key Standalone tool for analyzing and fixing port conflicts in docker-compose files
@llm-map Build-time port management utility with auto-fix capabilities
@llm-axiom Port conflicts must be resolved automatically with minimal manual intervention
@llm-token port-fixer: Automated port conflict resolution tool for build system
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List

# Add validators to path
sys.path.append(str(Path(__file__).parent))

try:
    from validators import PortValidator, PortConflict
    VALIDATORS_AVAILABLE = True
except ImportError:
    VALIDATORS_AVAILABLE = False
    print("❌ Validators not available. Please check installation.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PortFixer:
    """Automated port conflict detection and resolution"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.validator = PortValidator(project_root)
    
    def analyze_ports(self) -> List[PortConflict]:
        """Analyze current port configuration for conflicts"""
        logger.info("🔍 Analyzing port allocations...")
        conflicts = self.validator.validate_project()
        
        if not conflicts:
            logger.info("✅ No port conflicts detected!")
            return []
        
        logger.info(f"⚠️ Found {len(conflicts)} port issues:")
        for conflict in conflicts:
            severity_icon = "❌" if conflict.severity == "error" else "⚠️"
            logger.info(f"  {severity_icon} {conflict}")
        
        return conflicts
    
    def generate_fix_script(self, conflicts: List[PortConflict], output_file: str = "fix-ports.sh") -> str:
        """Generate automatic fix script"""
        if not conflicts:
            logger.info("✅ No conflicts to fix!")
            return ""
        
        script_content = self.validator.generate_fix_script(conflicts)
        output_path = self.project_root / output_file
        
        with open(output_path, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        output_path.chmod(0o755)
        
        logger.info(f"🔧 Generated fix script: {output_path}")
        logger.info("Run the script with: ./fix-ports.sh")
        
        return str(output_path)
    
    def generate_report(self, output_file: str = "port-allocation-report.md") -> str:
        """Generate comprehensive port allocation report"""
        logger.info("📊 Generating port allocation report...")
        
        allocations = []
        # Get allocations from validator
        allocations.extend(self.validator._analyze_docker_compose_files())
        allocations.extend(self.validator._analyze_build_config())
        
        report_content = self.validator.generate_port_allocation_report(allocations)
        output_path = self.project_root / output_file
        
        with open(output_path, 'w') as f:
            f.write(report_content)
        
        logger.info(f"📊 Generated report: {output_path}")
        return str(output_path)
    
    def validate_and_fix(self, auto_fix: bool = False) -> bool:
        """Complete validation and optional auto-fix workflow"""
        logger.info("🚀 Starting port validation and fix workflow...")
        
        # Step 1: Analyze
        conflicts = self.analyze_ports()
        
        if not conflicts:
            logger.info("🎉 No port conflicts found - system is ready!")
            return True
        
        # Step 2: Generate report
        self.generate_report()
        
        # Step 3: Generate fix script
        fix_script = self.generate_fix_script(conflicts)
        
        if auto_fix and fix_script:
            logger.info("🔧 Auto-fix enabled - applying fixes...")
            import subprocess
            try:
                result = subprocess.run([fix_script], shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("✅ Auto-fix completed successfully!")
                    
                    # Re-validate
                    logger.info("🔍 Re-validating after fixes...")
                    new_conflicts = self.analyze_ports()
                    if not new_conflicts:
                        logger.info("🎉 All conflicts resolved!")
                        return True
                    else:
                        logger.warning(f"⚠️ {len(new_conflicts)} conflicts remain after auto-fix")
                        return False
                else:
                    logger.error(f"❌ Auto-fix failed: {result.stderr}")
                    return False
            except Exception as e:
                logger.error(f"❌ Auto-fix execution failed: {e}")
                return False
        else:
            logger.info("🔧 Manual fix required - run the generated script: ./fix-ports.sh")
            return False


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Unhinged Port Conflict Detection and Resolution Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python port_fixer.py analyze                    # Analyze current port conflicts
  python port_fixer.py fix                        # Generate fix script
  python port_fixer.py fix --auto                 # Auto-apply fixes
  python port_fixer.py report                     # Generate allocation report
  python port_fixer.py validate                   # Full validation workflow
        """
    )
    
    parser.add_argument(
        'command',
        choices=['analyze', 'fix', 'report', 'validate'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Automatically apply fixes (use with caution)'
    )
    
    parser.add_argument(
        '--project-root',
        type=Path,
        default=Path.cwd(),
        help='Project root directory (default: current directory)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file name for generated scripts/reports'
    )
    
    args = parser.parse_args()
    
    # Initialize port fixer
    fixer = PortFixer(args.project_root)
    
    try:
        if args.command == 'analyze':
            conflicts = fixer.analyze_ports()
            sys.exit(0 if not conflicts else 1)
            
        elif args.command == 'fix':
            conflicts = fixer.analyze_ports()
            if conflicts:
                output_file = args.output or "fix-ports.sh"
                fixer.generate_fix_script(conflicts, output_file)
                if args.auto:
                    success = fixer.validate_and_fix(auto_fix=True)
                    sys.exit(0 if success else 1)
            sys.exit(0)
            
        elif args.command == 'report':
            output_file = args.output or "port-allocation-report.md"
            fixer.generate_report(output_file)
            sys.exit(0)
            
        elif args.command == 'validate':
            success = fixer.validate_and_fix(auto_fix=args.auto)
            sys.exit(0 if success else 1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
