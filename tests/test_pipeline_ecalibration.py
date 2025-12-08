"""Tests for ECalibrationStep - TDD spec for user tone calibration.

@llm-type test.graph.pipeline.ecalibration
@llm-does TDD exit criteria for e-calibration (user communication style matching)

EXIT CRITERIA:
1. ECalibrationStep analyzes user input for communication style signals
2. Calibration profile is stored in session context
3. Profile includes: profanity_level, formality, pace, hostility_signals
4. Calibration updates adaptively across session (not just first message)
5. System prompt is annotated with calibration guidance
6. No external LLM call required (rule-based for v1)
"""

import pytest

from libs.python.graph.prompt_pipeline import PromptPayload, StepResult


class TestECalibrationStep:
    """TDD specs for ECalibrationStep."""

    # =========================================================================
    # EXIT CRITERION 1: Analyze user input for style signals
    # =========================================================================

    def test_detects_high_profanity_level(self) -> None:
        """Profanity in user input is detected and quantified."""
        from libs.python.graph.pipeline_steps import ECalibrationStep

        step = ECalibrationStep()
        payload = PromptPayload(user_input="What the fuck is going on with this shit?")
        output = step.execute(payload)

        assert output.result == StepResult.CONTINUE
        assert output.metrics.get("profanity_level", 0) > 0.5

    def test_detects_low_profanity_level(self) -> None:
        """Clean language results in low profanity score."""
        from libs.python.graph.pipeline_steps import ECalibrationStep

        step = ECalibrationStep()
        payload = PromptPayload(user_input="Please help me understand this issue.")
        output = step.execute(payload)

        assert output.metrics.get("profanity_level", 1) < 0.2

    def test_detects_formality_level(self) -> None:
        """Formality is assessed from vocabulary and structure."""
        from libs.python.graph.pipeline_steps import ECalibrationStep

        step = ECalibrationStep()

        # Informal
        payload_informal = PromptPayload(user_input="yo whats up with this thing lol")
        output_informal = step.execute(payload_informal)

        # Formal
        payload_formal = PromptPayload(user_input="I would appreciate your assistance in diagnosing this issue.")
        output_formal = step.execute(payload_formal)

        assert output_informal.metrics.get("formality", 1) < output_formal.metrics.get("formality", 0)

    # =========================================================================
    # EXIT CRITERION 2: Profile stored in session context
    # =========================================================================

    def test_stores_calibration_in_session(self) -> None:
        """Calibration profile is persisted to session context."""
        from unittest.mock import MagicMock

        from libs.python.graph.pipeline_steps import ECalibrationStep

        step = ECalibrationStep()
        mock_session = MagicMock()
        mock_session.get_meta.return_value = {}

        payload = PromptPayload(user_input="fuck this is confusing")
        step.execute(payload, session=mock_session)

        mock_session.set_meta.assert_called()
        call_args = mock_session.set_meta.call_args
        assert "ecalibration" in call_args[0][0] or "calibration" in str(call_args)

    # =========================================================================
    # EXIT CRITERION 3: Profile structure
    # =========================================================================

    def test_profile_includes_required_dimensions(self) -> None:
        """Calibration profile includes all required dimensions."""
        from libs.python.graph.pipeline_steps import ECalibrationStep

        step = ECalibrationStep()
        payload = PromptPayload(user_input="testing the calibration system")
        output = step.execute(payload)

        required_keys = {"profanity_level", "formality", "pace"}
        assert required_keys.issubset(set(output.metrics.keys()))

    # =========================================================================
    # EXIT CRITERION 4: Adaptive updates across session
    # =========================================================================

    def test_calibration_updates_with_new_input(self) -> None:
        """Subsequent messages update the calibration, not replace."""
        from unittest.mock import MagicMock

        from libs.python.graph.pipeline_steps import ECalibrationStep

        step = ECalibrationStep()
        mock_session = MagicMock()

        # Simulate existing calibration from previous messages
        existing_calibration = {"profanity_level": 0.1, "formality": 0.8, "message_count": 3}
        mock_session.get_meta.return_value = existing_calibration

        # New message with high profanity
        payload = PromptPayload(user_input="damn this is harder than I thought")
        step.execute(payload, session=mock_session)

        # Should update, not reset
        call_args = mock_session.set_meta.call_args[0][1]
        assert call_args.get("message_count", 0) > 3

    # =========================================================================
    # EXIT CRITERION 5: System prompt annotation
    # =========================================================================

    def test_injects_calibration_guidance_into_prompt(self) -> None:
        """Calibration adds tone guidance to system prompt or context."""
        from libs.python.graph.pipeline_steps import ECalibrationStep

        step = ECalibrationStep()
        payload = PromptPayload(user_input="fuck yeah let's do this")
        step.execute(payload)

        # Either in system_prompt or context_blocks
        has_guidance = (
            "tone" in payload.system_prompt.lower()
            or "casual" in payload.system_prompt.lower()
            or any("tone" in block.lower() for block in payload.context_blocks)
        )
        assert has_guidance or len(payload.context_blocks) > 0

    # =========================================================================
    # EXIT CRITERION 6: No LLM call (rule-based v1)
    # =========================================================================

    def test_no_external_llm_call(self) -> None:
        """v1 uses rule-based detection, no LLM dependency."""
        from libs.python.graph.pipeline_steps import ECalibrationStep

        step = ECalibrationStep()

        # Should not have _call_llm method or similar
        assert not hasattr(step, "_call_llm")
        assert not hasattr(step, "_client")

        payload = PromptPayload(user_input="test message")
        output = step.execute(payload)

        # Should complete synchronously without async
        assert output.result == StepResult.CONTINUE
