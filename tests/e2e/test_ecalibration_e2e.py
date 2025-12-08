"""
@llm-type test.e2e.ecalibration
@llm-does end-to-end tests for ECalibration pipeline flow

E2E Tests for E-Calibration

These tests verify that text input flows through the full pipeline
and produces correct calibration + CDC events, using real infrastructure.

Tests:
1. test_simple_happy_path - Clean text, formal user, basic calibration
2. test_complex_happy_path - Profane text triggers correct tone matching
3. test_simple_error_path - Missing session context handled gracefully
"""

import pytest

from libs.python.graph.context import CDCEventType, SessionContext
from libs.python.graph.pipeline_steps import (
    AssembleFinalPromptStep,
    ECalibrationStep,
    IdentityHydrationStep,
)
from libs.python.graph.prompt_pipeline import PromptPipeline, StepResult


class TestECalibrationE2E:
    """E2E tests for the ECalibration pipeline flow."""

    # =========================================================================
    # TEST 1: Simple Happy Path
    # =========================================================================

    def test_simple_happy_path_formal_input(self, e2e_session):
        """
        GIVEN: A formal, professional text input
        WHEN: Run through PromptPipeline with ECalibrationStep
        THEN: Calibration detects formal style, CDC events emitted, prompt assembled
        """
        text_input = (
            "Good afternoon. I would appreciate your assistance with a technical issue. "
            "The build process is failing intermittently, and I believe it may be related "
            "to memory allocation during compilation."
        )

        # Build pipeline
        pipeline = PromptPipeline()
        pipeline.add_step(ECalibrationStep())
        pipeline.add_step(AssembleFinalPromptStep())

        # Run with session context
        session = e2e_session.session
        payload, outputs = pipeline.run(text_input, session=session)

        # Assertions: Calibration worked
        assert outputs[0].result == StepResult.CONTINUE
        assert outputs[0].metrics["profanity_level"] < 0.2  # Low profanity
        assert outputs[0].metrics["formality"] > 0.5  # High formality

        # Assertions: CDC events emitted
        cdc_events = session.cdc_feed()
        pipeline_events = [e for e in cdc_events if e.event_type == CDCEventType.PIPELINE_STEP]
        assert len(pipeline_events) >= 2  # At least ECalibration + Assemble

        # Assertions: Final prompt assembled
        assert payload.final_prompt != ""
        assert text_input in payload.final_prompt

    # =========================================================================
    # TEST 2: Complex Happy Path - Profane/Casual Input
    # =========================================================================

    def test_complex_happy_path_profane_casual_input(self, e2e_session):
        """
        GIVEN: A profane, casual text input (Unhinged Senior Engineer mode)
        WHEN: Run through PromptPipeline with ECalibrationStep
        THEN: Calibration detects high profanity, casual tone, injects guidance
        """
        text_input = (
            "what the fuck is this bullshit? I've been debugging this goddamn thing "
            "for three hours and the shit keeps breaking every time I push. "
            "can you just tell me where the crap I went wrong?"
        )

        # Build pipeline with identity
        pipeline = PromptPipeline()
        pipeline.add_step(IdentityHydrationStep(identity_config={"name": "Unhinged", "role": "engineer"}))
        pipeline.add_step(ECalibrationStep())
        pipeline.add_step(AssembleFinalPromptStep())

        # Run with session context
        session = e2e_session.session
        session.set_stage("pre_flight")
        payload, outputs = pipeline.run(text_input, session=session)

        # Assertions: High profanity detected
        ecal_output = outputs[1]  # Second step is ECalibrationStep
        assert ecal_output.metrics["profanity_level"] >= 0.8  # High profanity
        assert ecal_output.metrics["formality"] <= 0.5  # Not formal (neutral or casual)

        # Assertions: Tone guidance injected
        guidance_found = (
            "casual" in payload.system_prompt.lower()
            or "profane" in payload.system_prompt.lower()
            or any("tone" in block.lower() for block in payload.context_blocks)
        )
        assert guidance_found, "Expected tone calibration guidance in prompt"

        # Assertions: CDC shows calibration event
        cdc_events = session.cdc_feed()
        calibration_events = [e for e in cdc_events if e.event_type == CDCEventType.ECALIBRATION_UPDATED]
        assert len(calibration_events) >= 1

        # Assertions: Identity was hydrated
        identity_events = [e for e in cdc_events if e.event_type == CDCEventType.IDENTITY_HYDRATED]
        assert len(identity_events) >= 1

    # =========================================================================
    # TEST 3: Simple Error Path - Graceful Handling
    # =========================================================================

    def test_simple_error_path_no_session(self):
        """
        GIVEN: A text input processed WITHOUT session context
        WHEN: Run through PromptPipeline
        THEN: Pipeline completes successfully (no crash), no CDC events
        """
        text_input = "testing without session context - should still work"

        # Build pipeline
        pipeline = PromptPipeline()
        pipeline.add_step(ECalibrationStep())
        pipeline.add_step(AssembleFinalPromptStep())

        # Run WITHOUT session context (session=None)
        payload, outputs = pipeline.run(text_input, session=None)

        # Assertions: Pipeline completed
        assert outputs[0].result == StepResult.CONTINUE
        assert outputs[1].result == StepResult.CONTINUE

        # Assertions: Final prompt still assembled
        assert payload.final_prompt != ""
        assert text_input in payload.final_prompt

        # Assertions: Calibration metrics still calculated
        assert "profanity_level" in outputs[0].metrics
        assert "formality" in outputs[0].metrics
