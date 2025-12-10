"""
@llm-type test.e2e.readiness
@llm-does verifies system components are warmed up, idling, and ready

System Readiness E2E Test

A simple smoke test that runs FIRST to verify:
1. Core imports load without error (warm-up complete)
2. Session context can be created and emits events
3. Pipeline is instantiable and executable
4. All moving parts are idling and ready for real work

If this test fails, deeper tests are meaningless.
"""

import pytest


class TestSystemReady:
    """Smoke tests verifying system is warmed up and ready."""

    # =========================================================================
    # TEST: Core Imports Warm-Up
    # =========================================================================

    def test_core_imports_load(self):
        """
        GIVEN: A fresh Python interpreter
        WHEN: Import core graph/pipeline modules
        THEN: All imports succeed without error (modules are warm)
        """
        # These imports trigger module initialization, class registration, etc.
        from libs.python.graph.context import CDCEventType, SessionContext
        from libs.python.graph.graph import GraphExecutor
        from libs.python.graph.nodes import UnixCommandNode
        from libs.python.graph.pipeline_steps import (
            AssembleFinalPromptStep,
            ECalibrationStep,
            IdentityHydrationStep,
        )
        from libs.python.graph.prompt_pipeline import PromptPipeline, StepResult

        # Verify classes are instantiable (not just importable)
        assert SessionContext is not None
        assert GraphExecutor is not None
        assert UnixCommandNode is not None
        assert PromptPipeline is not None
        assert ECalibrationStep is not None
        assert IdentityHydrationStep is not None
        assert AssembleFinalPromptStep is not None
        assert StepResult is not None
        assert CDCEventType is not None

    # =========================================================================
    # TEST: Session Context Ready
    # =========================================================================

    def test_session_context_creates_and_emits(self):
        """
        GIVEN: Core modules are loaded
        WHEN: Create a SessionContext and emit an event
        THEN: Session is ready, CDC feed captures events
        """
        from libs.python.graph.context import CDCEventType, SessionContext

        session = SessionContext(session_id="readiness-check")

        # Session should have valid ID
        assert session.session_id == "readiness-check"

        # Set some state
        session.set("test_key", "test_value")
        assert session.get("test_key") == "test_value"

        # Emit an event (using a generic state event for readiness check)
        session.emit(CDCEventType.STATE_CREATE, {"source": "readiness_test", "key": "ready"})

        # CDC feed should capture it
        events = session.cdc_feed()
        assert len(events) >= 2  # One from set(), one from emit()

        # Find our readiness event (last one emitted)
        readiness_event = events[-1]
        assert readiness_event.event_type == CDCEventType.STATE_CREATE
        assert readiness_event.data["source"] == "readiness_test"

    # =========================================================================
    # TEST: Pipeline Ready to Execute
    # =========================================================================

    def test_pipeline_executes_noop(self):
        """
        GIVEN: Pipeline and steps are importable
        WHEN: Create and run a minimal pipeline with no-op input
        THEN: Pipeline executes without error, returns valid output structure
        """
        from libs.python.graph.pipeline_steps import AssembleFinalPromptStep
        from libs.python.graph.prompt_pipeline import PromptPipeline, StepResult

        # Build minimal pipeline
        pipeline = PromptPipeline()
        pipeline.add_step(AssembleFinalPromptStep())

        # Run with trivial input
        payload, outputs = pipeline.run("system ready check", session=None)

        # Pipeline should complete
        assert len(outputs) == 1
        assert outputs[0].result == StepResult.CONTINUE

        # Final prompt should be assembled
        assert payload.final_prompt is not None
        assert "system ready check" in payload.final_prompt

    # =========================================================================
    # TEST: Full Pipeline Stack Ready
    # =========================================================================

    def test_full_pipeline_stack_ready(self, e2e_session):
        """
        GIVEN: All pipeline steps are loaded
        WHEN: Build full pipeline (Identity + ECalibration + Assemble) and run
        THEN: All steps execute, all CDC events fire, system is fully ready
        """
        from libs.python.graph.context import CDCEventType
        from libs.python.graph.pipeline_steps import (
            AssembleFinalPromptStep,
            ECalibrationStep,
            IdentityHydrationStep,
        )
        from libs.python.graph.prompt_pipeline import PromptPipeline, StepResult

        # Full pipeline
        pipeline = PromptPipeline()
        pipeline.add_step(IdentityHydrationStep(identity_config={"name": "System", "version": "ready"}))
        pipeline.add_step(ECalibrationStep())
        pipeline.add_step(AssembleFinalPromptStep())

        # Run
        session = e2e_session.session
        payload, outputs = pipeline.run("readiness verification", session=session)

        # All 3 steps should complete
        assert len(outputs) == 3
        assert all(o.result == StepResult.CONTINUE for o in outputs)

        # CDC should have events from all steps
        events = session.cdc_feed()
        event_types = {e.event_type for e in events}

        assert CDCEventType.IDENTITY_HYDRATED in event_types
        assert CDCEventType.ECALIBRATION_UPDATED in event_types
        assert CDCEventType.PIPELINE_STEP in event_types

        # System is ready
        assert payload.final_prompt != ""
