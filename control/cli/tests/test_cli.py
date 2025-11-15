"""CLI command tests using Click's test runner."""

import pytest
from click.testing import CliRunner

from control.cli.main import cli


@pytest.fixture
def runner():
    """Create a Click test runner."""
    return CliRunner()


class TestSystemCommands:
    """Test system command group."""

    def test_system_help(self, runner):
        """Test system help."""
        result = runner.invoke(cli, ['system', '--help'])
        assert result.exit_code == 0
        assert 'System commands' in result.output
        assert 'start' in result.output
        assert 'stop' in result.output
        assert 'status' in result.output
        assert 'restart' in result.output

    def test_system_status_help(self, runner):
        """Test system status help."""
        result = runner.invoke(cli, ['system', 'status', '--help'])
        assert result.exit_code == 0
        assert 'Show system health' in result.output


class TestDevCommands:
    """Test dev command group."""

    def test_dev_help(self, runner):
        """Test dev help."""
        result = runner.invoke(cli, ['dev', '--help'])
        assert result.exit_code == 0
        assert 'Development commands' in result.output
        assert 'build' in result.output
        assert 'test' in result.output
        assert 'lint' in result.output
        assert 'fix' in result.output
        assert 'clean' in result.output

    def test_dev_lint_help(self, runner):
        """Test dev lint help."""
        result = runner.invoke(cli, ['dev', 'lint', '--help'])
        assert result.exit_code == 0
        assert 'Check code' in result.output
        assert '--verbose' in result.output

    def test_dev_test_help(self, runner):
        """Test dev test help."""
        result = runner.invoke(cli, ['dev', 'test', '--help'])
        assert result.exit_code == 0
        assert 'Run tests' in result.output


class TestAdminCommands:
    """Test admin command group."""

    def test_admin_help(self, runner):
        """Test admin help."""
        result = runner.invoke(cli, ['admin', '--help'])
        assert result.exit_code == 0
        assert 'Admin and debug' in result.output
        assert 'services' in result.output
        assert 'debug' in result.output
        assert 'preflight' in result.output

    def test_admin_services_help(self, runner):
        """Test admin services help."""
        result = runner.invoke(cli, ['admin', 'services', '--help'])
        assert result.exit_code == 0
        assert 'Service management' in result.output

    def test_admin_preflight_help(self, runner):
        """Test admin preflight help."""
        result = runner.invoke(cli, ['admin', 'preflight', '--help'])
        assert result.exit_code == 0
        assert 'Preflight' in result.output


class TestVMCommands:
    """Test vm command group."""

    def test_vm_help(self, runner):
        """Test vm help."""
        result = runner.invoke(cli, ['vm', '--help'])
        assert result.exit_code == 0
        assert 'Virtual machine' in result.output
        assert 'win10' in result.output
        assert 'templeos' in result.output
        assert 'stop' in result.output


class TestCLIRoot:
    """Test root CLI."""

    def test_cli_help(self, runner):
        """Test root help."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Unhinged' in result.output
        assert 'system' in result.output
        assert 'dev' in result.output
        assert 'admin' in result.output
        assert 'vm' in result.output

    def test_cli_no_args(self, runner):
        """Test CLI with no arguments shows help."""
        result = runner.invoke(cli, [])
        assert result.exit_code == 0
        assert 'Unhinged' in result.output

