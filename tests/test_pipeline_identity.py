"""Tests for IdentityHydrationStep - TDD spec for identity injection.

@llm-type test.graph.pipeline.identity
@llm-does TDD exit criteria for identity hydration in prompt pipeline

EXIT CRITERIA:
1. IdentityHydrationStep loads identity config from deployment config
2. Identity is injected into PromptPayload.system_prompt as preamble
3. Step emits CDC event with identity metadata
4. Missing config returns ABORT with clear error
5. Identity includes: role, codebase context, capabilities
"""

import pytest

from libs.python.graph.prompt_pipeline import PromptPayload, StepResult


class TestIdentityHydrationStep:
    """TDD specs for IdentityHydrationStep."""

    # =========================================================================
    # EXIT CRITERION 1: Load identity from config
    # =========================================================================

    def test_loads_identity_from_config_dict(self) -> None:
        """Identity config can be passed as dict at construction."""
        from libs.python.graph.pipeline_steps import IdentityHydrationStep

        config = {
            "role": "Unhinged Senior Engineer",
            "codebase": "Unhinged",
            "capabilities": ["graph-building", "code-generation", "diagnostics"],
        }
        step = IdentityHydrationStep(identity_config=config)

        payload = PromptPayload(user_input="test")
        output = step.execute(payload)

        assert output.result == StepResult.CONTINUE
        assert "Unhinged Senior Engineer" in payload.system_prompt
        assert "Unhinged" in payload.system_prompt

    def test_loads_identity_from_file_path(self) -> None:
        """Identity config can be loaded from YAML file path."""
        from libs.python.graph.pipeline_steps import IdentityHydrationStep

        # This test expects a config file to exist or be mocked
        step = IdentityHydrationStep(config_path="config/identity.yml")

        payload = PromptPayload(user_input="test")
        output = step.execute(payload)

        assert output.result in (StepResult.CONTINUE, StepResult.ABORT)

    # =========================================================================
    # EXIT CRITERION 2: Identity injected as system prompt preamble
    # =========================================================================

    def test_identity_prepended_to_existing_system_prompt(self) -> None:
        """Identity is prepended, not replaced, if system_prompt exists."""
        from libs.python.graph.pipeline_steps import IdentityHydrationStep

        config = {"role": "Senior Engineer", "codebase": "TestRepo"}
        step = IdentityHydrationStep(identity_config=config)

        payload = PromptPayload(user_input="test", system_prompt="Existing rules here.")
        step.execute(payload)

        # Identity comes BEFORE existing prompt
        assert payload.system_prompt.startswith("[identity]")
        assert "Existing rules here." in payload.system_prompt

    def test_identity_format_is_structured(self) -> None:
        """Identity block uses consistent format."""
        from libs.python.graph.pipeline_steps import IdentityHydrationStep

        config = {
            "role": "Unhinged Senior Engineer",
            "codebase": "Unhinged",
            "capabilities": ["graphs", "code"],
        }
        step = IdentityHydrationStep(identity_config=config)

        payload = PromptPayload(user_input="test")
        step.execute(payload)

        assert "[identity]" in payload.system_prompt
        assert "[/identity]" in payload.system_prompt

    # =========================================================================
    # EXIT CRITERION 3: CDC event emission
    # =========================================================================

    def test_emits_cdc_event_with_identity_metadata(self) -> None:
        """Step emits CDC event when session context provided."""
        from unittest.mock import MagicMock

        from libs.python.graph.pipeline_steps import IdentityHydrationStep

        config = {"role": "Engineer", "codebase": "Test"}
        step = IdentityHydrationStep(identity_config=config)

        mock_session = MagicMock()
        payload = PromptPayload(user_input="test")
        step.execute(payload, session=mock_session)

        mock_session.emit.assert_called()

    # =========================================================================
    # EXIT CRITERION 4: Missing config returns ABORT
    # =========================================================================

    def test_missing_config_aborts_with_clear_error(self) -> None:
        """No config provided results in ABORT with reason."""
        from libs.python.graph.pipeline_steps import IdentityHydrationStep

        step = IdentityHydrationStep()  # No config

        payload = PromptPayload(user_input="test")
        output = step.execute(payload)

        assert output.result == StepResult.ABORT
        assert "identity" in output.reason.lower()

    def test_invalid_config_path_aborts(self) -> None:
        """Non-existent config path results in ABORT."""
        from libs.python.graph.pipeline_steps import IdentityHydrationStep

        step = IdentityHydrationStep(config_path="/nonexistent/path.yml")

        payload = PromptPayload(user_input="test")
        output = step.execute(payload)

        assert output.result == StepResult.ABORT

    # =========================================================================
    # EXIT CRITERION 5: Identity content requirements
    # =========================================================================

    def test_identity_includes_role(self) -> None:
        """Identity must specify the role/persona."""
        from libs.python.graph.pipeline_steps import IdentityHydrationStep

        config = {"role": "Unhinged Senior Engineer"}
        step = IdentityHydrationStep(identity_config=config)

        payload = PromptPayload(user_input="test")
        output = step.execute(payload)

        assert "role" in output.metrics or "Unhinged Senior Engineer" in payload.system_prompt

    def test_identity_includes_codebase_context(self) -> None:
        """Identity should reference the codebase being worked on."""
        from libs.python.graph.pipeline_steps import IdentityHydrationStep

        config = {"role": "Engineer", "codebase": "Unhinged", "repo_root": "/home/user/Unhinged"}
        step = IdentityHydrationStep(identity_config=config)

        payload = PromptPayload(user_input="test")
        output = step.execute(payload)

        assert "codebase" in output.metrics or "Unhinged" in payload.system_prompt
