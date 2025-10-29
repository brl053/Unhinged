#!/usr/bin/env python3

"""
@llm-type service.api
@llm-does enhanced cli interface for the unhinged build
"""

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Import our build system components
try:
    # Try absolute imports first (when run as module)
    from orchestrator import BuildOrchestrator, BuildResult
    from modules import BuildContext, register_module
    from modules.kotlin_builder import KotlinBuilder
    from llm_integration import LLMBuildIntegration, BuildError
except ImportError:
    try:
        # Try relative imports (when run as package)
        from .orchestrator import BuildOrchestrator, BuildResult
        from .modules import BuildContext, register_module
        from .modules.kotlin_builder import KotlinBuilder
        from .llm_integration import LLMBuildIntegration, BuildError
    except ImportError:
        # Final fallback - add current directory to path
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent))
        from orchestrator import BuildOrchestrator, BuildResult
        from modules import BuildContext, register_module
        from modules.kotlin_builder import KotlinBuilder
        from llm_integration import LLMBuildIntegration, BuildError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BuildCLI:
    """Enhanced CLI for the build system"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.orchestrator = None
        self.llm_integration = LLMBuildIntegration(self.project_root)
        self._setup_orchestrator()
    
    def _setup_orchestrator(self):
        """Initialize the build orchestrator and register modules"""
        try:
            # Use consolidated build-config.yml (v1)
            config_path = self.project_root / "build" / "config" / "build-config.yml"
            self.orchestrator = BuildOrchestrator(config_path)
            
            # Register build modules
            context = BuildContext(
                project_root=self.project_root,
                target_name="",  # Will be set per build
                config=self.orchestrator.config
            )

            # Import and register all build modules
            try:
                from modules.kotlin_builder import KotlinBuilder
                from modules.typescript_builder import TypeScriptBuilder
                from modules.python_builder import PythonBuilder
                from modules.proto_client_builder import ProtoClientBuilder
                from modules.service_discovery_builder import ServiceDiscoveryBuilder
                from modules.c_builder import CBuilder
            except ImportError:
                from .modules.kotlin_builder import KotlinBuilder
                from .modules.typescript_builder import TypeScriptBuilder
                from .modules.python_builder import PythonBuilder
                from .modules.proto_client_builder import ProtoClientBuilder
                from .modules.service_discovery_builder import ServiceDiscoveryBuilder
                from .modules.c_builder import CBuilder

            kotlin_builder = KotlinBuilder(context)
            typescript_builder = TypeScriptBuilder(context)
            python_builder = PythonBuilder(context)
            proto_client_builder = ProtoClientBuilder(context)
            service_discovery_builder = ServiceDiscoveryBuilder(context)
            c_builder = CBuilder(context)

            register_module(kotlin_builder)
            register_module(typescript_builder)
            register_module(python_builder)
            register_module(proto_client_builder)
            register_module(service_discovery_builder)
            register_module(c_builder)
            
            logger.info("✅ Build system (v1) initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize build orchestrator: {e}")
            sys.exit(1)
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser"""
        parser = argparse.ArgumentParser(
            description="Enhanced Unhinged Build System",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s build backend-build                    # Build backend
  %(prog)s build dev-fast --parallel              # Fast development build
  %(prog)s status                                 # Show build status
  %(prog)s explain backend-build                  # Explain what will be built
  %(prog)s profile dev-full                       # Profile build performance
  %(prog)s clean --smart                          # Smart cleanup
  %(prog)s watch backend-compile                  # Watch mode
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Build command
        build_parser = subparsers.add_parser('build', help='Build targets')
        build_parser.add_argument('targets', nargs='+', help='Build targets to execute')
        build_parser.add_argument('--parallel', action='store_true', help='Enable parallel execution')
        build_parser.add_argument('--no-cache', action='store_true', help='Disable caching')
        build_parser.add_argument('--environment', choices=['development', 'staging', 'production'], 
                                default='development', help='Build environment')
        build_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
        build_parser.add_argument('--dry-run', action='store_true', help='Show what would be built')
        
        # Status command
        status_parser = subparsers.add_parser('status', help='Show build status')
        status_parser.add_argument('--json', action='store_true', help='Output in JSON format')
        
        # List command
        list_parser = subparsers.add_parser('list', help='List available targets')
        list_parser.add_argument('--detailed', action='store_true', help='Show detailed information')
        
        # Explain command
        explain_parser = subparsers.add_parser('explain', help='Explain build target')
        explain_parser.add_argument('target', help='Target to explain')
        explain_parser.add_argument('--dependencies', action='store_true', help='Show dependencies')
        
        # Clean command
        clean_parser = subparsers.add_parser('clean', help='Clean build artifacts')
        clean_parser.add_argument('--smart', action='store_true', help='Smart cleanup (preserve cache)')
        clean_parser.add_argument('--all', action='store_true', help='Clean everything')
        clean_parser.add_argument('targets', nargs='*', help='Specific targets to clean')
        
        # Profile command
        profile_parser = subparsers.add_parser('profile', help='Profile build performance')
        profile_parser.add_argument('targets', nargs='+', help='Targets to profile')
        profile_parser.add_argument('--iterations', type=int, default=1, help='Number of iterations')
        
        # Watch command
        watch_parser = subparsers.add_parser('watch', help='Watch mode with auto-rebuild')
        watch_parser.add_argument('target', help='Target to watch')
        watch_parser.add_argument('--interval', type=int, default=2, help='Check interval in seconds')

        # LLM integration commands
        llm_parser = subparsers.add_parser('llm', help='LLM-powered build assistance')
        llm_subparsers = llm_parser.add_subparsers(dest='llm_command', help='LLM commands')

        # Generate context
        context_parser = llm_subparsers.add_parser('context', help='Generate build context for LLM')
        context_parser.add_argument('--targets', nargs='*', help='Specific targets to include')
        context_parser.add_argument('--format', choices=['yaml', 'json'], default='yaml', help='Output format')

        # Explain error
        error_parser = llm_subparsers.add_parser('explain-error', help='Explain build error')
        error_parser.add_argument('target', help='Target that failed')
        error_parser.add_argument('--error-message', required=True, help='Error message')
        error_parser.add_argument('--command', help='Command that failed')

        # Onboarding guide
        onboard_parser = llm_subparsers.add_parser('onboard', help='Generate onboarding guide')

        # Performance monitoring commands
        perf_parser = subparsers.add_parser('performance', help='Performance monitoring and analysis')
        perf_subparsers = perf_parser.add_subparsers(dest='perf_command', help='Performance commands')

        # Performance report
        report_parser = perf_subparsers.add_parser('report', help='Generate performance report')
        report_parser.add_argument('--hours', type=int, default=24, help='Report period in hours')
        report_parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')

        # Performance metrics
        metrics_parser = perf_subparsers.add_parser('metrics', help='Show current performance metrics')
        metrics_parser.add_argument('--json', action='store_true', help='Output in JSON format')

        # Port validation commands
        port_parser = subparsers.add_parser('validate-ports', help='Validate and fix port conflicts')
        port_parser.add_argument('--fix', action='store_true', help='Generate fix script')
        port_parser.add_argument('--auto-fix', action='store_true', help='Automatically apply fixes')
        port_parser.add_argument('--report', action='store_true', help='Generate allocation report')

        return parser
    
    async def run_build(self, args) -> int:
        """Execute build command"""
        if args.dry_run:
            return self._dry_run_build(args.targets)
        
        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        
        print(f"🚀 Building targets: {', '.join(args.targets)}")
        print(f"📋 Environment: {args.environment}")
        print(f"⚡ Parallel: {'enabled' if args.parallel else 'disabled'}")
        print(f"💾 Cache: {'disabled' if args.no_cache else 'enabled'}")
        print()
        
        start_time = time.time()
        
        try:
            results = await self.orchestrator.build_targets(args.targets)
            total_duration = time.time() - start_time
            
            # Display results
            self._display_build_results(results, total_duration)
            
            # Return appropriate exit code
            return 0 if all(r.success for r in results) else 1
            
        except Exception as e:
            logger.error(f"❌ Build failed with error: {e}")
            return 1
    
    def run_status(self, args) -> int:
        """Show build status"""
        status_info = {
            'cache_stats': self._get_cache_stats(),
            'recent_builds': self._get_recent_builds(),
            'system_info': self._get_system_info()
        }
        
        if args.json:
            print(json.dumps(status_info, indent=2))
        else:
            self._display_status(status_info)
        
        return 0
    
    def run_list(self, args) -> int:
        """List available targets"""
        targets = self.orchestrator.dependency_graph.targets
        
        if args.detailed:
            for name, target in targets.items():
                print(f"📋 {name}")
                print(f"   Description: {target.description}")
                print(f"   Dependencies: {', '.join(target.dependencies) if target.dependencies else 'None'}")
                print(f"   Estimated duration: {target.estimated_duration:.1f}s")
                print()
        else:
            print("📋 Available targets:")
            for name, target in targets.items():
                print(f"  • {name}: {target.description}")
        
        return 0
    
    def run_explain(self, args) -> int:
        """Explain a build target"""
        target = self.orchestrator.dependency_graph.targets.get(args.target)
        
        if not target:
            print(f"❌ Target '{args.target}' not found")
            return 1
        
        print(f"📋 Target: {target.name}")
        print(f"📝 Description: {target.description}")
        print(f"⏱️  Estimated duration: {target.estimated_duration:.1f}s")
        print(f"🔄 Parallel safe: {'Yes' if target.parallel_safe else 'No'}")
        
        if target.dependencies:
            print(f"📦 Dependencies: {', '.join(target.dependencies)}")
        
        if target.commands:
            print("💻 Commands:")
            for i, cmd in enumerate(target.commands, 1):
                print(f"  {i}. {cmd}")
        
        if args.dependencies:
            try:
                execution_order = self.orchestrator.dependency_graph.get_execution_order([args.target])
                print("\n🔗 Execution order:")
                for i, group in enumerate(execution_order, 1):
                    print(f"  Group {i}: {', '.join(group)}")
            except ValueError as e:
                print(f"❌ Dependency error: {e}")
        
        return 0

    def run_llm_command(self, args) -> int:
        """Handle LLM integration commands"""
        if args.llm_command == 'context':
            return self._generate_llm_context(args)
        elif args.llm_command == 'explain-error':
            return self._explain_build_error(args)
        elif args.llm_command == 'onboard':
            return self._generate_onboarding_guide(args)
        else:
            print(f"❌ Unknown LLM command: {args.llm_command}")
            return 1

    def _generate_llm_context(self, args) -> int:
        """Generate LLM context for build assistance"""
        try:
            context = self.llm_integration.generate_build_context(args.targets)

            if args.format == 'json':
                # Convert YAML to JSON for JSON output
                import yaml
                data = yaml.safe_load(context)
                import json
                print(json.dumps(data, indent=2))
            else:
                print(context)

            return 0
        except Exception as e:
            logger.error(f"Failed to generate LLM context: {e}")
            return 1

    def _explain_build_error(self, args) -> int:
        """Generate LLM explanation for build error"""
        try:
            error = BuildError(
                target=args.target,
                error_message=args.error_message,
                command=args.command or "unknown",
                exit_code=1,
                stdout="",
                stderr=args.error_message,
                context={}
            )

            explanation = self.llm_integration.explain_build_error(error)
            print(explanation)

            return 0
        except Exception as e:
            logger.error(f"Failed to explain build error: {e}")
            return 1

    def _generate_onboarding_guide(self, args) -> int:
        """Generate developer onboarding guide"""
        try:
            guide = self.llm_integration.generate_onboarding_guide()
            print(guide)
            return 0
        except Exception as e:
            logger.error(f"Failed to generate onboarding guide: {e}")
            return 1

    def run_performance_command(self, args) -> int:
        """Handle performance monitoring commands"""
        if args.perf_command == 'report':
            return self._generate_performance_report(args)
        elif args.perf_command == 'metrics':
            return self._show_performance_metrics(args)
        else:
            print(f"❌ Unknown performance command: {args.perf_command}")
            return 1

    def _generate_performance_report(self, args) -> int:
        """Generate performance report"""
        try:
            if not self.orchestrator.monitor:
                print("❌ Performance monitoring not available")
                return 1

            report = self.orchestrator.monitor.generate_performance_report(args.hours)

            if args.format == 'json':
                import json
                from dataclasses import asdict
                print(json.dumps(asdict(report), indent=2, default=str))
            else:
                self._display_performance_report(report)

            return 0
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            return 1

    def _show_performance_metrics(self, args) -> int:
        """Show current performance metrics"""
        try:
            if not self.orchestrator.monitor:
                print("❌ Performance monitoring not available")
                return 1

            cache_metrics = self.orchestrator.monitor.get_cache_metrics()
            system_metrics = self.orchestrator.monitor.get_system_metrics()

            if args.json:
                import json
                from dataclasses import asdict
                metrics = {
                    'cache': asdict(cache_metrics),
                    'system': asdict(system_metrics)
                }
                print(json.dumps(metrics, indent=2))
            else:
                self._display_current_metrics(cache_metrics, system_metrics)

            return 0
        except Exception as e:
            logger.error(f"Failed to show performance metrics: {e}")
            return 1

    def _display_performance_report(self, report):
        """Display performance report in human-readable format"""
        print("📊 BUILD PERFORMANCE REPORT")
        print("=" * 60)
        print(f"📅 Period: {report.period_start} to {report.period_end}")
        print(f"🔨 Total builds: {report.total_builds}")
        print(f"✅ Successful: {report.successful_builds}")
        print(f"❌ Failed: {report.failed_builds}")
        print(f"⏱️  Average time: {report.average_build_time:.2f}s")
        print(f"🚀 Fastest: {report.fastest_build_time:.2f}s")
        print(f"🐌 Slowest: {report.slowest_build_time:.2f}s")
        print()

        print("💾 CACHE PERFORMANCE")
        print("-" * 30)
        cache = report.cache_metrics
        print(f"📦 Entries: {cache.total_entries}")
        print(f"💿 Size: {cache.total_size_mb:.1f} MB")
        print(f"🎯 Hit rate: {cache.hit_rate:.1f}%")
        print(f"❌ Miss rate: {cache.miss_rate:.1f}%")
        print()

        print("🖥️  SYSTEM METRICS")
        print("-" * 30)
        system = report.system_metrics
        print(f"⚡ CPU cores: {system.cpu_cores}")
        print(f"📊 CPU usage: {system.cpu_usage_percent:.1f}%")
        print(f"💾 Memory: {system.memory_available_gb:.1f}GB / {system.memory_total_gb:.1f}GB")
        print(f"💿 Disk free: {system.disk_free_gb:.1f}GB / {system.disk_total_gb:.1f}GB")
        print()

        if report.target_performance:
            print("🎯 TARGET PERFORMANCE")
            print("-" * 30)
            for target, stats in report.target_performance.items():
                print(f"📋 {target}:")
                print(f"   Average: {stats['average']:.2f}s")
                print(f"   Range: {stats['min']:.2f}s - {stats['max']:.2f}s")
                print(f"   Builds: {stats['count']}")
            print()

        if report.optimization_recommendations:
            print("💡 OPTIMIZATION RECOMMENDATIONS")
            print("-" * 30)
            for i, rec in enumerate(report.optimization_recommendations, 1):
                print(f"{i}. {rec}")

    def _display_current_metrics(self, cache_metrics, system_metrics):
        """Display current metrics"""
        print("📊 CURRENT PERFORMANCE METRICS")
        print("=" * 40)

        print("💾 Cache Status:")
        print(f"  📦 Entries: {cache_metrics.total_entries}")
        print(f"  💿 Size: {cache_metrics.total_size_mb:.1f} MB")
        print(f"  🎯 Hit rate: {cache_metrics.hit_rate:.1f}%")
        print()

        print("🖥️  System Status:")
        print(f"  ⚡ CPU: {system_metrics.cpu_usage_percent:.1f}% ({system_metrics.cpu_cores} cores)")
        print(f"  💾 Memory: {system_metrics.memory_available_gb:.1f}GB available")
        print(f"  💿 Disk: {system_metrics.disk_free_gb:.1f}GB free")
        if system_metrics.load_average:
            print(f"  📊 Load: {system_metrics.load_average[0]:.2f}")

    def _dry_run_build(self, targets: List[str]) -> int:
        """Show what would be built without executing"""
        print("🔍 Dry run - showing what would be built:")
        print()
        
        try:
            execution_order = self.orchestrator.dependency_graph.get_execution_order(targets)
            
            for i, group in enumerate(execution_order, 1):
                print(f"📋 Group {i} (parallel):")
                for target_name in group:
                    target = self.orchestrator.dependency_graph.targets[target_name]
                    print(f"  • {target_name}: {target.description}")
                    
                    # Show cache status
                    if target.cache_key and self.orchestrator.cache.is_cached(target.cache_key):
                        print(f"    💾 Cache: HIT")
                    else:
                        print(f"    💾 Cache: MISS")
                print()
            
            return 0
            
        except ValueError as e:
            print(f"❌ Dependency error: {e}")
            return 1
    
    def _display_build_results(self, results: List[BuildResult], total_duration: float):
        """Display build results in a user-friendly format"""
        print("\n" + "="*60)
        print("📊 BUILD RESULTS")
        print("="*60)
        
        successful = 0
        failed = 0
        cache_hits = 0
        
        for result in results:
            status = "✅" if result.success else "❌"
            cache_status = "💾" if result.cache_hit else "🔨"
            
            print(f"{status} {cache_status} {result.target:<20} {result.duration:>6.2f}s")
            
            if result.success:
                successful += 1
                if result.cache_hit:
                    cache_hits += 1
            else:
                failed += 1
                if result.error_message:
                    print(f"    Error: {result.error_message}")
        
        print("-" * 60)
        print(f"📈 Summary: {successful} successful, {failed} failed")
        print(f"💾 Cache hits: {cache_hits}/{len(results)} ({cache_hits/len(results)*100:.1f}%)")
        print(f"⏱️  Total time: {total_duration:.2f}s")
        
        if failed > 0:
            print("\n💡 Tip: Use 'build explain <target>' for more information")
    
    def _get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        cache_dir = self.orchestrator.cache.cache_dir
        
        if not cache_dir.exists():
            return {'enabled': False}
        
        cache_files = list(cache_dir.glob('*'))
        total_size = sum(f.stat().st_size for f in cache_files if f.is_file())
        
        return {
            'enabled': True,
            'entries': len(cache_files),
            'total_size_mb': total_size / (1024 * 1024),
            'location': str(cache_dir)
        }
    
    def _get_recent_builds(self) -> List[Dict]:
        """Get recent build information"""
        # This would typically read from a build history file
        return []
    
    def _get_system_info(self) -> Dict:
        """Get system information relevant to builds"""
        import platform
        import psutil
        
        return {
            'platform': platform.system(),
            'python_version': platform.python_version(),
            'cpu_count': psutil.cpu_count(),
            'memory_gb': psutil.virtual_memory().total / (1024**3),
            'disk_free_gb': psutil.disk_usage('.').free / (1024**3)
        }
    
    def _display_status(self, status_info: Dict):
        """Display status information"""
        print("📊 BUILD SYSTEM STATUS")
        print("=" * 40)
        
        # Cache stats
        cache = status_info['cache_stats']
        if cache['enabled']:
            print(f"💾 Cache: {cache['entries']} entries, {cache['total_size_mb']:.1f} MB")
        else:
            print("💾 Cache: disabled")
        
        # System info
        sys_info = status_info['system_info']
        print(f"🖥️  System: {sys_info['platform']}")
        print(f"🐍 Python: {sys_info['python_version']}")
        print(f"⚡ CPU cores: {sys_info['cpu_count']}")
        print(f"💾 Memory: {sys_info['memory_gb']:.1f} GB")
        print(f"💿 Disk free: {sys_info['disk_free_gb']:.1f} GB")

    def run_port_validation(self, args) -> int:
        """Run port validation and conflict resolution"""
        try:
            # Import port fixer
            from port_fixer import PortFixer

            fixer = PortFixer(self.project_root)

            if args.report:
                # Generate allocation report
                report_file = fixer.generate_report()
                print(f"📊 Port allocation report generated: {report_file}")
                return 0

            elif args.fix or args.auto_fix:
                # Run validation and fix workflow
                success = fixer.validate_and_fix(auto_fix=args.auto_fix)
                return 0 if success else 1

            else:
                # Just analyze conflicts
                conflicts = fixer.analyze_ports()
                return 0 if not conflicts else 1

        except ImportError:
            print("❌ Port validation tools not available")
            return 1
        except Exception as e:
            logger.error(f"❌ Port validation failed: {e}")
            return 1

def main():
    """Main CLI entry point"""
    cli = BuildCLI()
    parser = cli.create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'build':
            return asyncio.run(cli.run_build(args))
        elif args.command == 'status':
            return cli.run_status(args)
        elif args.command == 'list':
            return cli.run_list(args)
        elif args.command == 'explain':
            return cli.run_explain(args)
        elif args.command == 'llm':
            return cli.run_llm_command(args)
        elif args.command == 'performance':
            return cli.run_performance_command(args)
        elif args.command == 'validate-ports':
            return cli.run_port_validation(args)
        else:
            print(f"❌ Command '{args.command}' not implemented yet")
            return 1
    
    except KeyboardInterrupt:
        print("\n⚠️  Build interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
