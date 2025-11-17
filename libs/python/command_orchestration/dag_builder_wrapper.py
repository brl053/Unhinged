"""DAG Builder wrapper with LLM-backed edge reasoning.

@llm-type library.command_orchestration.dag_builder_wrapper
@llm-does wrap DAGBuilder to add LLM-backed reasoning for DAG edges
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from libs.python.command_orchestration.reasoning_engine import ReasoningEngine
from libs.python.command_orchestration.dag_builder import (
    CommandDAG,
    CommandNode,
    DAGBuilder,
)

logger = logging.getLogger(__name__)


@dataclass
class DAGEdgeReasoning:
    """Reasoning for a DAG edge (data flow between commands)"""

    from_command: str
    to_command: str
    data_flow: str
    reasoning: str


@dataclass
class CommandDAGWithReasoning:
    """DAG with LLM-backed edge reasoning"""

    dag: CommandDAG
    edge_reasoning: dict[tuple[str, str], DAGEdgeReasoning] = field(
        default_factory=dict
    )

    def get_edge_reasoning(
        self, from_id: str, to_id: str
    ) -> DAGEdgeReasoning | None:
        """Get reasoning for a specific edge."""
        return self.edge_reasoning.get((from_id, to_id))


class DAGBuilderWithReasoning:
    """Wraps DAGBuilder to add LLM-backed edge reasoning.

    Enhances DAG edges with LLM-generated explanations for why commands
    are connected and how data flows between them.
    """

    def __init__(
        self,
        dag_builder: DAGBuilder | None = None,
        reasoning_engine: ReasoningEngine | None = None,
        model: str = "claude-3-5-sonnet-20241022",
        provider: str = "anthropic",
    ):
        """Initialize wrapper with DAG builder and reasoning engine.

        Parameters
        ----------
        dag_builder : Optional[DAGBuilder]
            The underlying DAG builder. If None, creates new one.
        reasoning_engine : Optional[ReasoningEngine]
            Optional pre-configured reasoning engine. If None, creates new one.
        model : str
            LLM model to use (default: Claude 3.5 Sonnet)
        provider : str
            LLM provider (anthropic, openai, ollama)
        """
        self.dag_builder = dag_builder or DAGBuilder()
        self.reasoning_engine = reasoning_engine or ReasoningEngine(
            model=model, provider=provider
        )

    async def parse_pipeline_with_reasoning(
        self,
        pipeline: str,
        use_llm_reasoning: bool = True,
    ) -> CommandDAGWithReasoning:
        """Parse pipeline and optionally add LLM edge reasoning.

        Parameters
        ----------
        pipeline : str
            Command pipeline (e.g., "pactl list-sinks | grep -i volume")
        use_llm_reasoning : bool
            If True, use LLM for edge reasoning

        Returns
        -------
        CommandDAGWithReasoning
            DAG with optional LLM-backed edge reasoning
        """
        try:
            # Parse pipeline into DAG
            dag = self.dag_builder.parse_pipeline(pipeline)
            dag_with_reasoning = CommandDAGWithReasoning(dag=dag)

            if not use_llm_reasoning or not dag.edges:
                return dag_with_reasoning

            # Generate LLM reasoning for each edge
            for from_id, to_id in dag.edges:
                try:
                    from_node = dag.nodes[from_id]
                    to_node = dag.nodes[to_id]

                    # Determine data flow
                    data_flow = f"{from_node.command} stdout → {to_node.command} stdin"

                    # Get LLM reasoning
                    reasoning = await self.reasoning_engine.reason_dag_edge(
                        from_command=from_node.command,
                        to_command=to_node.command,
                        data_flow=data_flow,
                    )

                    edge_reasoning = DAGEdgeReasoning(
                        from_command=from_node.command,
                        to_command=to_node.command,
                        data_flow=data_flow,
                        reasoning=reasoning,
                    )

                    dag_with_reasoning.edge_reasoning[(from_id, to_id)] = (
                        edge_reasoning
                    )

                except Exception as exc:
                    logger.warning(
                        f"Failed to generate reasoning for edge {from_id}→{to_id}: {exc}"
                    )

            return dag_with_reasoning

        except Exception as exc:
            logger.error(f"Parse pipeline with reasoning failed: {exc}")
            raise

    def parse_pipeline(self, pipeline: str) -> CommandDAG:
        """Synchronous pipeline parsing (delegates to underlying builder).

        Parameters
        ----------
        pipeline : str
            Command pipeline

        Returns
        -------
        CommandDAG
            DAG without reasoning
        """
        return self.dag_builder.parse_pipeline(pipeline)

    def build_from_commands(self, commands: list[str]) -> CommandDAG:
        """Build DAG from independent commands.

        Parameters
        ----------
        commands : List[str]
            List of commands

        Returns
        -------
        CommandDAG
            DAG of independent commands
        """
        return self.dag_builder.build_from_commands(commands)

