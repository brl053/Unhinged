"""Command Executor - Voice Input → Executable CLI Commands.

Intercepts transcribed user text, parses intent via LLM, and executes
resulting CLI commands with CDC event emission.

Flow:
1. User says: "show me all graphs" or "run the build"
2. PromptPipeline builds hydrated prompt (capabilities + system info + session)
3. LLM parses intent and generates command plan
4. Commands execute with CDC events (SYS_CALL, EXEC_*)
5. Results displayed in transcript via MSG_SYSTEM
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from libs.python.graph.context import SessionContext

# Intent parsing prompt - injected into pipeline as system prompt
INTENT_SYSTEM_PROMPT = """You are a CLI command generator for the Unhinged system.

Given the user's natural language request and the available system capabilities,
generate CLI commands to fulfill the request.

Respond ONLY with valid JSON:
{
  "intent": "brief description of what user wants",
  "commands": [
    {"cmd": "command to run", "description": "what this does"}
  ],
  "response_template": "How to summarize results to user (use {output} placeholder)"
}

If the request is unclear, return:
{
  "intent": "unclear",
  "commands": [],
  "response_template": "I couldn't understand that request. Could you be more specific?"
}
"""


@dataclass
class CommandPlan:
    """Parsed intent and command plan from LLM."""

    intent: str
    commands: list[dict[str, str]]  # [{"cmd": ..., "description": ...}]
    response_template: str
    raw_response: str = ""


@dataclass
class CommandResult:
    """Result of executing a single command."""

    cmd: str
    stdout: str
    stderr: str
    returncode: int
    success: bool


def _build_intent_prompt(user_text: str, session_ctx: SessionContext) -> str:
    """Build hydrated prompt using PromptPipeline.

    Uses pipeline steps: CapabilitiesStep, SystemInfoStep, SessionHydrationStep.
    """
    from libs.python.graph.pipeline_steps import (
        AssembleFinalPromptStep,
        CapabilitiesStep,
        InjectSystemPromptStep,
        SessionHydrationStep,
        SystemInfoStep,
    )
    from libs.python.graph.prompt_pipeline import PromptPipeline

    pipeline = PromptPipeline()
    pipeline.add_step(InjectSystemPromptStep(INTENT_SYSTEM_PROMPT))
    pipeline.add_step(CapabilitiesStep())
    pipeline.add_step(SystemInfoStep())
    pipeline.add_step(SessionHydrationStep())
    pipeline.add_step(AssembleFinalPromptStep())

    payload, _ = pipeline.run(user_text, session=session_ctx)
    return payload.final_prompt


def parse_intent(user_text: str, session_ctx: SessionContext) -> CommandPlan:
    """Send user text to LLM and parse intent into command plan.

    Args:
        user_text: Raw transcribed text from user
        session_ctx: Session context for CDC event emission and hydration

    Returns:
        CommandPlan with intent and commands to execute
    """
    from libs.python.graph.context import CDCEventType

    session_ctx.emit(CDCEventType.NODE_START, {"node_id": "intent_parser", "node_type": "LLMNode"})

    try:
        from libs.python.clients.text_generation_service import TextGenerationService

        # Build prompt via pipeline (capabilities + system info + session hydration)
        prompt = _build_intent_prompt(user_text, session_ctx)

        # Emit LLM start with model info
        model_name = "mistral"
        session_ctx.emit(
            CDCEventType.NODE_START,
            {
                "node_id": "llm_generate",
                "node_type": "LLMCall",
                "provider": "ollama",
                "model": model_name,
                "prompt_length": len(prompt),
            },
        )

        service = TextGenerationService(model=model_name)
        response = service.generate(prompt, max_tokens=512, temperature=0.3)

        # Emit LLM complete with response info
        session_ctx.emit(
            CDCEventType.NODE_SUCCESS,
            {
                "node_id": "llm_generate",
                "provider": "ollama",
                "model": model_name,
                "response_length": len(response),
            },
        )

        session_ctx.emit(CDCEventType.NODE_OUTPUT, {"node_id": "intent_parser", "output": {"raw": response[:200]}})

        # Parse JSON from response
        plan = _parse_llm_response(response)
        session_ctx.emit(
            CDCEventType.NODE_SUCCESS,
            {"node_id": "intent_parser", "output": {"intent": plan.intent, "cmd_count": len(plan.commands)}},
        )
        return plan

    except Exception as e:
        session_ctx.emit(CDCEventType.NODE_FAILED, {"node_id": "intent_parser", "error": str(e)})
        return CommandPlan(
            intent="error",
            commands=[],
            response_template=f"Sorry, I couldn't process that request: {e}",
            raw_response="",
        )


def _parse_llm_response(response: str) -> CommandPlan:
    """Extract JSON command plan from LLM response."""
    import re

    # Try to find JSON in response
    json_match = re.search(r"\{.*\}", response, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group(0))
            return CommandPlan(
                intent=data.get("intent", "unknown"),
                commands=data.get("commands", []),
                response_template=data.get("response_template", "Done."),
                raw_response=response,
            )
        except json.JSONDecodeError:
            pass

    # Fallback: couldn't parse
    return CommandPlan(
        intent="parse_error",
        commands=[],
        response_template="I couldn't understand the response format.",
        raw_response=response,
    )


def execute_commands(plan: CommandPlan, session_ctx: SessionContext) -> list[CommandResult]:
    """Execute commands from plan with CDC event emission.

    Args:
        plan: CommandPlan with commands to execute
        session_ctx: Session context for CDC events

    Returns:
        List of CommandResult for each executed command
    """
    from libs.python.graph.context import CDCEventType

    results: list[CommandResult] = []

    for cmd_spec in plan.commands:
        cmd = cmd_spec.get("cmd", "")
        description = cmd_spec.get("description", "")

        if not cmd:
            continue

        # Emit SYS_CALL event before execution
        session_ctx.emit(CDCEventType.SYS_CALL, {"call": "subprocess", "args": [cmd], "description": description})
        session_ctx.emit(CDCEventType.EXEC_START, {"action": "shell_cmd", "cmd": cmd})

        try:
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30.0, cwd=".")

            result = CommandResult(
                cmd=cmd,
                stdout=proc.stdout.strip(),
                stderr=proc.stderr.strip(),
                returncode=proc.returncode,
                success=proc.returncode == 0,
            )

            # Emit stdout/stderr if present
            if result.stdout:
                session_ctx.emit(CDCEventType.EXEC_STDOUT, {"line": result.stdout[:500]})
            if result.stderr:
                session_ctx.emit(CDCEventType.EXEC_STDERR, {"line": result.stderr[:500]})

            session_ctx.emit(CDCEventType.EXEC_EXIT, {"action": "shell_cmd", "code": result.returncode})

        except subprocess.TimeoutExpired:
            result = CommandResult(
                cmd=cmd, stdout="", stderr="Command timed out after 30s", returncode=-1, success=False
            )
            session_ctx.emit(CDCEventType.EXEC_EXIT, {"action": "shell_cmd", "code": -1, "error": "timeout"})

        except Exception as e:
            result = CommandResult(cmd=cmd, stdout="", stderr=str(e), returncode=-1, success=False)
            session_ctx.emit(CDCEventType.EXEC_EXIT, {"action": "shell_cmd", "code": -1, "error": str(e)})

        results.append(result)

    return results


def format_response(plan: CommandPlan, results: list[CommandResult]) -> str:
    """Format command results into a user-friendly response.

    Args:
        plan: The command plan with response template
        results: List of command execution results

    Returns:
        Formatted response string for the user
    """
    if not results:
        return plan.response_template

    # Combine outputs from all commands
    outputs = []
    for r in results:
        if r.success and r.stdout:
            outputs.append(r.stdout)
        elif not r.success:
            outputs.append(f"[Error: {r.stderr or 'command failed'}]")

    combined_output = "\n".join(outputs) if outputs else "(no output)"

    # Apply template
    response = plan.response_template.replace("{output}", combined_output)

    # Truncate if too long
    if len(response) > 500:
        response = response[:497] + "..."

    return response


def _classify_intent(user_text: str, session_ctx: SessionContext) -> tuple[str, float]:
    """Classify user intent using TextClassifierNode (non-generative).

    Returns:
        Tuple of (label, confidence) where label is one of:
        - engineering_task: needs planning, approval, multi-step
        - simple_command: run a single command
        - question: asking for information
        - unclear: can't determine intent
    """
    import asyncio

    from libs.python.graph.analytical_nodes import TextClassifierNode
    from libs.python.graph.context import CDCEventType

    session_ctx.emit(CDCEventType.NODE_START, {"node_id": "intent_classifier", "node_type": "TextClassifierNode"})

    try:
        classifier = TextClassifierNode("intent_classifier")
        classifier.set_session(session_ctx)
        # Use asyncio.run() which creates its own event loop (works in any thread)
        result = asyncio.run(classifier.execute({"text": user_text}))

        label = result["label"]
        confidence = result["confidence"]

        session_ctx.emit(
            CDCEventType.NODE_SUCCESS,
            {"node_id": "intent_classifier", "output": {"label": label, "confidence": confidence}},
        )
        return label, confidence

    except Exception as e:
        session_ctx.emit(CDCEventType.NODE_FAILED, {"node_id": "intent_classifier", "error": str(e)})
        # Fallback to simple_command on error
        return "simple_command", 0.0


def _handle_engineering_task(user_text: str, session_ctx: SessionContext) -> str:
    """Handle engineering tasks by running the engineering_intake graph.

    Uses the full engineering_intake graph with HumanFeedbackNodes in async_mode.
    The graph execution runs in a background thread, and HumanFeedbackNodes
    emit CDC events and wait for voice input via provide_feedback().
    """
    import asyncio
    import threading
    from pathlib import Path

    from libs.python.graph.context import CDCEventType
    from libs.python.graph.graph import GraphExecutor
    from libs.python.graph.loader import load_graph_from_json
    from libs.python.graph.nodes import HumanFeedbackNode

    session_ctx.emit(CDCEventType.NODE_START, {"node_id": "engineering_intake", "node_type": "Graph"})

    try:
        # Load the full engineering intake graph (with approval/revise cycle)
        graph_path = (
            Path(__file__).parent.parent.parent.parent.parent / "examples" / "graphs" / "engineering_intake.json"
        )

        if not graph_path.exists():
            return f"Engineering intake graph not found at {graph_path}"

        graph = load_graph_from_json(str(graph_path))

        # Enable async_mode on all HumanFeedbackNodes for TUI integration
        for node_id, node in graph.nodes.items():
            if isinstance(node, HumanFeedbackNode):
                node.set_async_mode(True)
                node.set_session(session_ctx)

        executor = GraphExecutor(session_ctx=session_ctx)

        # Store graph and executor in session for feedback routing
        session_ctx.set("_active_graph", graph)
        session_ctx.set("_active_executor", executor)

        # Run graph execution in background thread so TUI can continue
        def run_graph():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(
                    executor.execute(graph, initial_inputs={"analyze": {"input": {"topic": user_text}}})
                )
                # Store result for later retrieval
                session_ctx.set("_graph_result", result)
                session_ctx.set("_active_graph", None)
                session_ctx.set("_active_executor", None)

                # Emit completion event
                if result.success:
                    session_ctx.emit(
                        CDCEventType.NODE_SUCCESS,
                        {"node_id": "engineering_intake", "output": {"success": True}},
                    )
                    # Get final output from terminal node
                    final_output = ""
                    for node_id in ["execute_plan", "rejected"]:
                        if node_id in result.node_results:
                            final_output = result.node_results[node_id].output.get("stdout", "")
                            break
                    if final_output:
                        session_ctx.msg_system(f"✅ {final_output}")
                else:
                    session_ctx.emit(
                        CDCEventType.NODE_FAILED,
                        {"node_id": "engineering_intake", "error": result.error_message},
                    )
            except Exception as e:
                session_ctx.emit(CDCEventType.NODE_FAILED, {"node_id": "engineering_intake", "error": str(e)})
            finally:
                loop.close()

        thread = threading.Thread(target=run_graph, daemon=True)
        thread.start()

        # Return immediately - the graph will emit CDC events as it progresses
        return "🔄 Analyzing your request... (speak when prompted)"

    except Exception as e:
        session_ctx.emit(CDCEventType.NODE_FAILED, {"node_id": "engineering_intake", "error": str(e)})
        return f"Error starting engineering intake: {e}"


def _handle_pending_feedback(user_text: str, session_ctx: SessionContext) -> str | None:
    """Check if there's a pending HumanFeedbackNode waiting for input.

    Routes voice input to the waiting node via provide_feedback().
    Returns acknowledgment if handled, None if no pending feedback.
    """
    from libs.python.graph.nodes import HumanFeedbackNode

    # Check for any pending feedback nodes in session
    active_graph = session_ctx.get("_active_graph")
    if not active_graph:
        return None

    # Find pending feedback node
    for node_id, node in active_graph.nodes.items():
        if isinstance(node, HumanFeedbackNode):
            pending_node = session_ctx.get(f"_pending_feedback_node_{node_id}")
            if pending_node is not None:
                # Route the voice input to this node
                pending_node.provide_feedback(user_text)
                return f"📝 Received: '{user_text[:50]}{'...' if len(user_text) > 50 else ''}'"

    return None


def _handle_approval_response(user_text: str, session_ctx: SessionContext) -> str | None:
    """Check if user is responding to a pending approval (legacy flow).

    This is kept for backward compatibility but the new flow uses
    _handle_pending_feedback() which routes to HumanFeedbackNodes.

    Returns response if handled, None if not an approval response.
    """
    pending = session_ctx.get("pending_engineering_plan")
    if not pending or not pending.get("awaiting_approval"):
        return None

    user_lower = user_text.lower().strip()

    if user_lower in ("approve", "approved", "yes", "go", "do it", "execute"):
        # Clear pending state
        session_ctx.set("pending_engineering_plan", None)
        return "✅ Plan approved! Execution starting..."

    elif user_lower in ("reject", "rejected", "no", "cancel", "stop"):
        session_ctx.set("pending_engineering_plan", None)
        return "❌ Plan rejected. Let me know if you'd like something different."

    elif user_lower in ("revise", "change", "modify", "redo"):
        session_ctx.set("pending_engineering_plan", None)
        return "🔄 What would you like me to change about the plan?"

    # Not an approval response
    return None


def process_user_utterance(user_text: str, session_ctx: SessionContext) -> str:
    """Main entry point: process transcribed user text into commands and execute.

    This is the function to call from _stop_recording() after transcription.

    Flow:
    1. Check if responding to pending HumanFeedbackNode (async graph execution)
    2. Check if responding to pending approval (legacy flow)
    3. Classify intent using non-generative model (TextClassifierNode)
    4. Route to appropriate handler based on intent:
       - engineering_task → run engineering_intake graph, present plan
       - simple_command → parse and execute commands
       - question → answer directly (via LLM)
       - unclear → ask for clarification

    Args:
        user_text: Raw transcribed text from user voice input
        session_ctx: Session context for CDC events and state

    Returns:
        Response text to display to the user (and emit as MSG_SYSTEM)
    """
    from libs.python.graph.context import CDCEventType

    # Skip empty or very short utterances
    if not user_text or len(user_text.strip()) < 3:
        return ""

    session_ctx.emit(CDCEventType.NODE_START, {"node_id": "command_executor", "node_type": "Pipeline"})

    try:
        # Step 0a: Check if responding to pending HumanFeedbackNode (async graph)
        feedback_response = _handle_pending_feedback(user_text, session_ctx)
        if feedback_response:
            session_ctx.emit(
                CDCEventType.NODE_SUCCESS,
                {"node_id": "command_executor", "output": {"type": "feedback_response"}},
            )
            session_ctx.msg_system(feedback_response)
            return feedback_response

        # Step 0b: Check if responding to pending approval (legacy flow)
        approval_response = _handle_approval_response(user_text, session_ctx)
        if approval_response:
            session_ctx.emit(
                CDCEventType.NODE_SUCCESS,
                {"node_id": "command_executor", "output": {"type": "approval_response"}},
            )
            session_ctx.msg_system(approval_response)
            return approval_response

        # Step 1: Classify intent using non-generative model
        intent_label, confidence = _classify_intent(user_text, session_ctx)

        # Step 2: Route based on intent
        if intent_label == "engineering_task" and confidence > 0.25:
            # Engineering task - generate plan and present for approval
            response = _handle_engineering_task(user_text, session_ctx)

        else:
            # Simple command, question, or unclear - use existing flow
            plan = parse_intent(user_text, session_ctx)

            if plan.commands:
                results = execute_commands(plan, session_ctx)
                response = format_response(plan, results)
            else:
                response = plan.response_template

        session_ctx.emit(
            CDCEventType.NODE_SUCCESS,
            {"node_id": "command_executor", "output": {"response_len": len(response), "intent": intent_label}},
        )

        # Emit as system message
        if response:
            session_ctx.msg_system(response)

        return response

    except Exception as e:
        error_msg = f"Error processing request: {e}"
        session_ctx.emit(CDCEventType.NODE_FAILED, {"node_id": "command_executor", "error": str(e)})
        session_ctx.msg_system(error_msg)
        return error_msg
