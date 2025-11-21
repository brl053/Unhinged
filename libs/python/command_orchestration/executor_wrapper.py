"""Command Executor wrapper with LLM-backed result interpretation.

@llm-type library.command_orchestration.executor_wrapper
@llm-does wrap CommandExecutor to add LLM-backed result interpretation
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from libs.python.command_orchestration.dag_builder import CommandDAG
from libs.python.command_orchestration.executor import (
    CommandExecutor,
    DAGExecutionResult,
    ExecutionResult,
)
from libs.python.command_orchestration.reasoning_engine import ReasoningEngine

logger = logging.getLogger(__name__)


@dataclass
class ExecutionResultWithInterpretation:
    """Execution result with LLM-backed interpretation"""

    result: ExecutionResult
    interpretation: str | None = None


@dataclass
class DAGExecutionResultWithInterpretation:
    """DAG execution result with LLM-backed interpretations"""

    dag_result: DAGExecutionResult
    result_interpretations: dict[str, ExecutionResultWithInterpretation] = field(default_factory=dict)

    def get_interpretation(self, node_id: str) -> str | None:
        """Get interpretation for a specific node result."""
        if node_id in self.result_interpretations:
            return self.result_interpretations[node_id].interpretation
        return None


class CommandExecutorWithReasoning:
    """Wraps CommandExecutor to add LLM-backed result interpretation.

    Enhances execution results with LLM-generated interpretations of what
    the results mean for system state and diagnostics.
    """

    def __init__(
        self,
        executor: CommandExecutor | None = None,
        reasoning_engine: ReasoningEngine | None = None,
        model: str = "mistral",
        provider: str = "ollama",
    ):
        """Initialize wrapper with executor and reasoning engine.

        Parameters
        ----------
        executor : Optional[CommandExecutor]
            The underlying command executor. If None, creates new one.
        reasoning_engine : Optional[ReasoningEngine]
            Optional pre-configured reasoning engine. If None, creates new one.
        model : str
            LLM model to use (default: mistral for local Ollama)
        provider : str
            LLM provider (default: ollama for on-premise deployment)
        """
        self.executor = executor or CommandExecutor()
        self.reasoning_engine = reasoning_engine or ReasoningEngine(model=model, provider=provider)

    async def execute_dag_with_interpretation(
        self,
        dag: CommandDAG,
        use_llm_interpretation: bool = True,
    ) -> DAGExecutionResultWithInterpretation:
        """Execute DAG and optionally add LLM result interpretation.

        Parameters
        ----------
        dag : CommandDAG
            The DAG to execute
        use_llm_interpretation : bool
            If True, use LLM for result interpretation

        Returns
        -------
        DAGExecutionResultWithInterpretation
            Execution results with optional LLM-backed interpretation
        """
        try:
            # Execute DAG
            dag_result = await self.executor.execute_dag(dag)
            result_with_interp = DAGExecutionResultWithInterpretation(dag_result=dag_result)

            if not use_llm_interpretation or not dag_result.results:
                # Wrap results without interpretation
                for node_id, exec_result in dag_result.results.items():
                    result_with_interp.result_interpretations[node_id] = ExecutionResultWithInterpretation(
                        result=exec_result
                    )
                return result_with_interp

            # Generate LLM interpretation for each result
            for node_id, exec_result in dag_result.results.items():
                try:
                    interpretation = await self.reasoning_engine.reason_execution_result(
                        command=exec_result.command,
                        exit_code=exec_result.returncode,
                        stdout=exec_result.stdout,
                        stderr=exec_result.stderr,
                    )

                    result_with_interp.result_interpretations[node_id] = ExecutionResultWithInterpretation(
                        result=exec_result,
                        interpretation=interpretation,
                    )

                except Exception as exc:
                    logger.warning(f"Failed to generate interpretation for {node_id}: {exc}")
                    result_with_interp.result_interpretations[node_id] = ExecutionResultWithInterpretation(
                        result=exec_result
                    )

            return result_with_interp

        except Exception as exc:
            logger.error(f"Execute DAG with interpretation failed: {exc}")
            raise

    async def execute_dag(self, dag: CommandDAG) -> DAGExecutionResult:
        """Synchronous DAG execution (delegates to underlying executor).

        Parameters
        ----------
        dag : CommandDAG
            The DAG to execute

        Returns
        -------
        DAGExecutionResult
            Execution results without interpretation
        """
        return await self.executor.execute_dag(dag)
