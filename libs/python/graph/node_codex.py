"""Node Codex - Reference documentation for all graph node types.

@llm-type library.graph.reference
@llm-does provides structured documentation for all node types in the graph system

This module provides programmatic access to node type documentation,
including capabilities, configuration options, I/O specifications, and
integration patterns. Used by the TUI for help panels and by tooling
for graph validation hints.

All data is structured for both programmatic queries and human-readable rendering.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from libs.python.models.graph.schema import NodeType


class NodeCategory(str, Enum):
    """Functional categories for node types."""

    GENERATION = "Generation"  # Content creation (text, image, audio, video)
    ANALYSIS = "Analysis"  # Data processing and classification
    CONTROL_FLOW = "Control Flow"  # Branching, looping, orchestration
    IO = "I/O"  # External communication (HTTP, shell, user)
    MEMORY = "Memory"  # Context and state management


@dataclass(frozen=True)
class ConfigOption:
    """A configurable parameter for a node type."""

    name: str
    type: str  # "string", "int", "float", "bool", "list", "dict"
    description: str
    default: str | None = None
    required: bool = False
    constraints: str | None = None  # e.g., "0.0-1.0", "positive integer"


@dataclass(frozen=True)
class IOSpec:
    """Input/output specification for a node type."""

    name: str
    type: str  # e.g., "string", "dict", "list[dict]"
    description: str
    optional: bool = False


@dataclass(frozen=True)
class NodeCodexEntry:
    """Complete documentation for a single node type."""

    node_type: NodeType
    name: str  # Human-readable name
    icon: str  # Emoji icon
    category: NodeCategory
    summary: str  # One-line description
    description: str  # Detailed description
    inputs: tuple[IOSpec, ...] = field(default_factory=tuple)
    outputs: tuple[IOSpec, ...] = field(default_factory=tuple)
    config: tuple[ConfigOption, ...] = field(default_factory=tuple)
    integrations: tuple[NodeType, ...] = field(default_factory=tuple)  # Compatible node types
    latency: str = "Low"  # "Low", "Medium", "High", "Variable"
    resource_notes: str = ""  # API costs, token usage, etc.
    implementation_class: str = ""  # Python class name

    def as_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "node_type": self.node_type.value,
            "name": self.name,
            "icon": self.icon,
            "category": self.category.value,
            "summary": self.summary,
            "description": self.description,
            "inputs": [
                {"name": i.name, "type": i.type, "description": i.description, "optional": i.optional}
                for i in self.inputs
            ],
            "outputs": [
                {"name": o.name, "type": o.type, "description": o.description, "optional": o.optional}
                for o in self.outputs
            ],
            "config": [
                {
                    "name": c.name,
                    "type": c.type,
                    "description": c.description,
                    "default": c.default,
                    "required": c.required,
                    "constraints": c.constraints,
                }
                for c in self.config
            ],
            "integrations": [nt.value for nt in self.integrations],
            "latency": self.latency,
            "resource_notes": self.resource_notes,
            "implementation_class": self.implementation_class,
        }


# =============================================================================
# Node Codex Entries
# =============================================================================

CODEX: dict[NodeType, NodeCodexEntry] = {}


def _register(entry: NodeCodexEntry) -> None:
    """Register a codex entry."""
    CODEX[entry.node_type] = entry


# -----------------------------------------------------------------------------
# LLM_CHAT - Conversational LLM node
# -----------------------------------------------------------------------------
_register(
    NodeCodexEntry(
        node_type=NodeType.LLM_CHAT,
        name="LLM Chat",
        icon="💬",
        category=NodeCategory.GENERATION,
        summary="Conversational LLM with system prompt and template interpolation",
        description="""Executes a large language model call with configurable system prompt
and user input template. Supports template variables for dynamic prompt construction:
- {{node_id.field}} - Reference upstream node outputs
- {{session.key}} - Access session context data
- {{env.VAR}} - Read environment variables

Ideal for complex reasoning, planning, and multi-turn conversations.""",
        inputs=(IOSpec("input_data", "dict", "Upstream node outputs for template interpolation"),),
        outputs=(
            IOSpec("stdout", "string", "Raw LLM response text"),
            IOSpec("text", "string", "Alias for stdout"),
            IOSpec("model", "string", "Model used for generation"),
            IOSpec("provider", "string", "Provider used (e.g., ollama)"),
            IOSpec("success", "bool", "Whether generation succeeded"),
        ),
        config=(
            ConfigOption("model", "string", "LLM model name", default="llama2"),
            ConfigOption("provider", "string", "LLM provider", default="ollama"),
            ConfigOption("system_prompt", "string", "System prompt for context"),
            ConfigOption("input_template", "string", "User prompt template with {{...}} placeholders"),
            ConfigOption("max_tokens", "int", "Maximum tokens in response", default="1024"),
            ConfigOption("temperature", "float", "Sampling temperature", default="0.7", constraints="0.0-2.0"),
        ),
        integrations=(NodeType.DATA_TRANSFORM, NodeType.CONDITIONAL, NodeType.CONTEXT_HYDRATION),
        latency="Medium",
        resource_notes="Token consumption varies by model. Local models (ollama) have no API cost.",
        implementation_class="LLMNode",
    )
)

# -----------------------------------------------------------------------------
# LLM_COMPLETION - Structured output LLM node
# -----------------------------------------------------------------------------
_register(
    NodeCodexEntry(
        node_type=NodeType.LLM_COMPLETION,
        name="LLM Completion (Structured)",
        icon="💬",
        category=NodeCategory.GENERATION,
        summary="LLM with JSON schema validation and retry logic",
        description="""Extends LLM Chat with automatic JSON parsing and schema validation.
If the LLM output is not valid JSON or doesn't match the schema, the node
retries with feedback up to max_retries times.

Use for extracting structured data, generating configuration, or any case
where you need guaranteed JSON output format.""",
        inputs=(IOSpec("input_data", "dict", "Upstream node outputs for template interpolation"),),
        outputs=(
            IOSpec("stdout", "string", "Raw LLM response text"),
            IOSpec("parsed", "dict", "Parsed and validated JSON object"),
            IOSpec("validation_errors", "list", "Schema validation errors if any"),
            IOSpec("success", "bool", "Whether parsing and validation succeeded"),
        ),
        config=(
            ConfigOption("model", "string", "LLM model name", default="llama2"),
            ConfigOption("json_schema", "dict", "JSON schema for validation"),
            ConfigOption("max_retries", "int", "Retry attempts on validation failure", default="2"),
            ConfigOption("temperature", "float", "Sampling temperature", default="0.7"),
        ),
        integrations=(NodeType.DATA_TRANSFORM, NodeType.CONDITIONAL),
        latency="Medium-High",
        resource_notes="May consume 2-3x tokens due to retries. Consider lower temperature for structured output.",
        implementation_class="StructuredOutputNode",
    )
)

# -----------------------------------------------------------------------------
# CUSTOM_SERVICE - Generic extensible node
# -----------------------------------------------------------------------------
_register(
    NodeCodexEntry(
        node_type=NodeType.CUSTOM_SERVICE,
        name="Custom Service",
        icon="□",
        category=NodeCategory.IO,
        summary="Extensible node for shell commands, subgraphs, and custom integrations",
        description="""Umbrella type for several runtime node implementations:

- UnixCommandNode: Execute shell commands with template interpolation
- SubgraphNode: Execute nested graphs as a single node
- UserInputNode: Prompt user for input during execution
- HumanFeedbackNode: Block for human review with optional choices
- VideoGenerationNode: Generate video content

Configuration depends on the specific implementation.""",
        inputs=(
            IOSpec("input_data", "dict", "Node-specific input data"),
            IOSpec("stdin", "string", "Standard input for shell commands", optional=True),
        ),
        outputs=(
            IOSpec("stdout", "string", "Primary output (text or file path)"),
            IOSpec("stderr", "string", "Error output (for shell commands)"),
            IOSpec("returncode", "int", "Exit code (for shell commands)", optional=True),
            IOSpec("success", "bool", "Whether execution succeeded"),
        ),
        config=(
            ConfigOption("command", "string", "Shell command template (UnixCommandNode)"),
            ConfigOption("timeout", "float", "Command timeout in seconds", default="30.0"),
            ConfigOption("prompt", "string", "User prompt text (UserInputNode/HumanFeedbackNode)"),
            ConfigOption("options", "list", "Valid options for user selection", default="[]"),
        ),
        integrations=(NodeType.LLM_CHAT, NodeType.CONDITIONAL, NodeType.DATA_TRANSFORM),
        latency="Variable",
        resource_notes="Shell commands may have arbitrary resource usage. Subgraphs inherit child node costs.",
        implementation_class="UnixCommandNode/SubgraphNode/UserInputNode/HumanFeedbackNode",
    )
)

# -----------------------------------------------------------------------------
# IMAGE_GENERATION - Image synthesis node
# -----------------------------------------------------------------------------
_register(
    NodeCodexEntry(
        node_type=NodeType.IMAGE_GENERATION,
        name="Image Generation",
        icon="□",
        category=NodeCategory.GENERATION,
        summary="Generate images from text prompts using diffusion models",
        description="""Wraps ImageGenerationService for graph-based image synthesis.
Uses Stable Diffusion or compatible models to generate images from text prompts.

Output is a file path to the generated image, suitable for downstream
processing or display.""",
        inputs=(IOSpec("input_data", "dict", "Upstream outputs for prompt template interpolation"),),
        outputs=(
            IOSpec("stdout", "string", "Path to generated image file"),
            IOSpec("file_path", "string", "Alias for stdout"),
            IOSpec("metadata", "dict", "Generation metadata (dimensions, seed, etc.)"),
            IOSpec("prompt", "string", "The interpolated prompt used"),
            IOSpec("success", "bool", "Whether generation succeeded"),
        ),
        config=(
            ConfigOption("prompt_template", "string", "Text prompt with {{...}} placeholders"),
            ConfigOption("width", "int", "Image width in pixels", default="512"),
            ConfigOption("height", "int", "Image height in pixels", default="512"),
            ConfigOption("num_inference_steps", "int", "Diffusion steps (quality vs speed)", default="20"),
            ConfigOption("guidance_scale", "float", "Prompt adherence strength", default="7.5", constraints="1.0-20.0"),
            ConfigOption("output_dir", "string", "Directory for generated images"),
        ),
        integrations=(NodeType.LLM_CHAT, NodeType.PROMPT_ENHANCEMENT),
        latency="High",
        resource_notes="GPU-intensive. 512x512 @ 20 steps takes ~5-15s depending on hardware.",
        implementation_class="ImageGenerationNode",
    )
)

# -----------------------------------------------------------------------------
# TEXT_TO_SPEECH - Audio synthesis node
# -----------------------------------------------------------------------------
_register(
    NodeCodexEntry(
        node_type=NodeType.TEXT_TO_SPEECH,
        name="Text to Speech",
        icon="🔊",
        category=NodeCategory.GENERATION,
        summary="Convert text to spoken audio",
        description="""Wraps TTSService for graph-based text-to-speech generation.
Generates audio files from text input with configurable voice and speed.

Output is a file path to the generated audio, suitable for playback
or further audio processing.""",
        inputs=(IOSpec("input_data", "dict", "Upstream outputs for text template interpolation"),),
        outputs=(
            IOSpec("stdout", "string", "Path to generated audio file"),
            IOSpec("file_path", "string", "Alias for stdout"),
            IOSpec("duration", "float", "Audio duration in seconds"),
            IOSpec("voice", "string", "Voice used for synthesis"),
            IOSpec("success", "bool", "Whether generation succeeded"),
        ),
        config=(
            ConfigOption("prompt_template", "string", "Text to speak with {{...}} placeholders"),
            ConfigOption("voice", "string", "Voice selection (nova, echo, sage, shimmer)", default="nova"),
            ConfigOption("speed", "float", "Speech speed multiplier", default="1.0", constraints="0.5-2.0"),
            ConfigOption("output_dir", "string", "Directory for generated audio"),
        ),
        integrations=(NodeType.LLM_CHAT, NodeType.SPEECH_TO_TEXT),
        latency="Medium",
        resource_notes="API-based TTS may incur per-character costs. Local models are free but slower.",
        implementation_class="AudioGenerationNode",
    )
)

# -----------------------------------------------------------------------------
# SPEECH_TO_TEXT - Audio transcription node
# -----------------------------------------------------------------------------
_register(
    NodeCodexEntry(
        node_type=NodeType.SPEECH_TO_TEXT,
        name="Speech to Text",
        icon="🎤",
        category=NodeCategory.IO,
        summary="Transcribe audio to text",
        description="""Converts spoken audio to text using speech recognition models.
Accepts audio file paths or raw audio data as input.

Output is transcribed text suitable for downstream NLP processing.""",
        inputs=(IOSpec("audio_in", "string", "Path to audio file or raw audio bytes"),),
        outputs=(
            IOSpec("text_out", "string", "Transcribed text"),
            IOSpec("confidence", "float", "Transcription confidence score", optional=True),
            IOSpec("success", "bool", "Whether transcription succeeded"),
        ),
        config=(
            ConfigOption("model", "string", "STT model name", default="whisper"),
            ConfigOption("language", "string", "Language code (e.g., 'en', 'es')"),
        ),
        integrations=(NodeType.LLM_CHAT, NodeType.TEXT_TO_SPEECH, NodeType.DATA_TRANSFORM),
        latency="Medium",
        resource_notes="Processing time proportional to audio length. ~1s per 10s of audio on GPU.",
        implementation_class="SpeechToTextNode",
    )
)

# -----------------------------------------------------------------------------
# HTTP_REQUEST - Web request node
# -----------------------------------------------------------------------------
_register(
    NodeCodexEntry(
        node_type=NodeType.HTTP_REQUEST,
        name="HTTP Request",
        icon="🌐",
        category=NodeCategory.IO,
        summary="Make HTTP requests and web searches",
        description="""Executes HTTP requests or web searches with template interpolation.
Includes WebSearchNode implementation for DuckDuckGo searches with page content extraction.

For web search, returns both raw results and a formatted text summary
suitable for LLM consumption.""",
        inputs=(IOSpec("input_data", "dict", "Upstream outputs for query/URL template interpolation"),),
        outputs=(
            IOSpec("stdout", "string", "Response body or formatted search results"),
            IOSpec("results", "list", "Structured search results (for web search)"),
            IOSpec("text", "string", "Formatted text for LLM consumption"),
            IOSpec("query", "string", "The interpolated search query"),
            IOSpec("success", "bool", "Whether request succeeded"),
        ),
        config=(
            ConfigOption("url", "string", "Request URL with {{...}} placeholders"),
            ConfigOption("method", "string", "HTTP method", default="GET"),
            ConfigOption("query_template", "string", "Search query template (WebSearchNode)"),
            ConfigOption("max_results", "int", "Number of search results", default="5"),
            ConfigOption("max_content_chars", "int", "Max chars per page", default="3000"),
        ),
        integrations=(NodeType.LLM_CHAT, NodeType.DATA_TRANSFORM),
        latency="Variable",
        resource_notes="Network-dependent. Web searches may take 2-10s depending on result count.",
        implementation_class="HTTPRequestNode/WebSearchNode",
    )
)

# -----------------------------------------------------------------------------
# DATA_TRANSFORM - Data processing node
# -----------------------------------------------------------------------------
_register(
    NodeCodexEntry(
        node_type=NodeType.DATA_TRANSFORM,
        name="Data Transform",
        icon="⚙",
        category=NodeCategory.ANALYSIS,
        summary="Transform, filter, and process data between nodes",
        description="""General-purpose data transformation node for processing outputs
between other nodes. Includes specialized implementations:

- TextClassifierNode: Classify text using SBERT embeddings
- RubricGradeNode: Grade content against quality rubrics

Used for data normalization, filtering, classification, and quality gates.""",
        inputs=(IOSpec("input_data", "dict", "Data to transform"),),
        outputs=(
            IOSpec("label", "string", "Classification label (TextClassifierNode)"),
            IOSpec("confidence", "float", "Classification confidence"),
            IOSpec("scores", "dict", "All label scores"),
            IOSpec("score", "float", "Rubric score (RubricGradeNode)"),
            IOSpec("passed", "bool", "Whether rubric threshold was met"),
            IOSpec("success", "bool", "Whether transform succeeded"),
        ),
        config=(
            ConfigOption("model_name", "string", "SBERT model", default="all-MiniLM-L6-v2"),
            ConfigOption("labels", "list", "Classification labels"),
            ConfigOption("threshold", "float", "Minimum confidence threshold", default="0.3"),
            ConfigOption("rubric_name", "string", "Rubric identifier (RubricGradeNode)"),
        ),
        integrations=(NodeType.LLM_CHAT, NodeType.CONDITIONAL),
        latency="Low",
        resource_notes="SBERT models are ~80MB. First load takes ~2s, subsequent calls <100ms.",
        implementation_class="TextClassifierNode/RubricGradeNode",
    )
)

# -----------------------------------------------------------------------------
# CONDITIONAL - Branch control flow
# -----------------------------------------------------------------------------
_register(
    NodeCodexEntry(
        node_type=NodeType.CONDITIONAL,
        name="Conditional",
        icon="◇",
        category=NodeCategory.CONTROL_FLOW,
        summary="Branch execution based on conditions",
        description="""Evaluates a condition and routes execution to different paths.
Supports boolean expressions that can reference upstream node outputs.

Output ports: 'true' and 'false' for conditional routing.""",
        inputs=(IOSpec("input_data", "dict", "Upstream outputs for condition evaluation"),),
        outputs=(
            IOSpec("result", "bool", "Condition evaluation result"),
            IOSpec("branch", "string", "Selected branch ('true' or 'false')"),
        ),
        config=(ConfigOption("expression", "string", "Boolean expression to evaluate", required=True),),
        integrations=(NodeType.LLM_CHAT, NodeType.DATA_TRANSFORM, NodeType.LOOP_BREAKER),
        latency="Low",
        resource_notes="Minimal. Expression evaluation only.",
        implementation_class="ConditionalNode",
    )
)

# -----------------------------------------------------------------------------
# LOOP_BREAKER - Iteration control
# -----------------------------------------------------------------------------
_register(
    NodeCodexEntry(
        node_type=NodeType.LOOP_BREAKER,
        name="Loop Breaker",
        icon="↻",
        category=NodeCategory.CONTROL_FLOW,
        summary="Control loop iteration with max iteration limits",
        description="""Manages cyclic graph execution by tracking iteration count
and breaking loops when a maximum is reached.

Output ports: 'continue' and 'break' for loop control.""",
        inputs=(IOSpec("input_data", "dict", "Data passed through the loop"),),
        outputs=(
            IOSpec("iteration", "int", "Current iteration number"),
            IOSpec("should_break", "bool", "Whether max iterations reached"),
        ),
        config=(ConfigOption("max_iterations", "int", "Maximum loop iterations", default="10"),),
        integrations=(NodeType.CONDITIONAL, NodeType.LLM_CHAT, NodeType.DATA_TRANSFORM),
        latency="Low",
        resource_notes="Minimal. Counter tracking only.",
        implementation_class="LoopBreakerNode",
    )
)

# -----------------------------------------------------------------------------
# CONTEXT_HYDRATION - Memory recall node
# -----------------------------------------------------------------------------
_register(
    NodeCodexEntry(
        node_type=NodeType.CONTEXT_HYDRATION,
        name="Context Hydration (Recall)",
        icon="□",
        category=NodeCategory.MEMORY,
        summary="Semantic recall from persisted sessions and documents",
        description="""Queries the vector store for documents matching a semantic query.
Used for self-reflection, context retrieval, and memory recall.

Returns ranked results with similarity scores and extracts the top result
text for easy chaining to LLM nodes.""",
        inputs=(IOSpec("query", "string", "Natural language search query"),),
        outputs=(
            IOSpec("results", "list", "Ranked recall results with score, text, document_id"),
            IOSpec("top_text", "string", "Text of highest-scoring result"),
            IOSpec("success", "bool", "Whether recall succeeded"),
        ),
        config=(
            ConfigOption("collection", "string", "Document collection to search"),
            ConfigOption("limit", "int", "Maximum results to return", default="5"),
            ConfigOption("threshold", "float", "Minimum similarity score", default="0.5", constraints="0.0-1.0"),
        ),
        integrations=(NodeType.LLM_CHAT, NodeType.PROMPT_ENHANCEMENT),
        latency="Low",
        resource_notes="Vector search is fast (~50-100ms). Index size affects memory usage.",
        implementation_class="RecallNode",
    )
)

# -----------------------------------------------------------------------------
# PROMPT_ENHANCEMENT - Prompt optimization
# -----------------------------------------------------------------------------
_register(
    NodeCodexEntry(
        node_type=NodeType.PROMPT_ENHANCEMENT,
        name="Prompt Enhancement",
        icon="□",
        category=NodeCategory.ANALYSIS,
        summary="Optimize prompts for better model outputs",
        description="""Preprocesses and enhances prompts before sending to generation nodes.
Can add context, reformat, or apply prompt engineering techniques.

Useful for consistent prompt formatting across different generation modalities.""",
        inputs=(
            IOSpec("prompt", "string", "Original prompt text"),
            IOSpec("context", "dict", "Additional context data", optional=True),
        ),
        outputs=(
            IOSpec("enhanced_prompt", "string", "Optimized prompt"),
            IOSpec("metadata", "dict", "Enhancement details"),
            IOSpec("success", "bool", "Whether enhancement succeeded"),
        ),
        config=(
            ConfigOption("strategy", "string", "Enhancement strategy", default="default"),
            ConfigOption("max_context_tokens", "int", "Max tokens for context injection"),
        ),
        integrations=(NodeType.LLM_CHAT, NodeType.IMAGE_GENERATION, NodeType.CONTEXT_HYDRATION),
        latency="Low",
        resource_notes="Minimal. Text processing only.",
        implementation_class="PromptEnhancementNode",
    )
)

# -----------------------------------------------------------------------------
# VISION_AI - Image analysis node
# -----------------------------------------------------------------------------
_register(
    NodeCodexEntry(
        node_type=NodeType.VISION_AI,
        name="Vision AI",
        icon="□",
        category=NodeCategory.ANALYSIS,
        summary="Analyze images using vision models",
        description="""Processes images using computer vision models for analysis,
object detection, or image-to-text tasks.

Accepts image file paths and outputs structured analysis results.""",
        inputs=(
            IOSpec("image_path", "string", "Path to image file"),
            IOSpec("prompt", "string", "Analysis prompt or question", optional=True),
        ),
        outputs=(
            IOSpec("analysis", "dict", "Structured analysis results"),
            IOSpec("text", "string", "Textual description or response"),
            IOSpec("objects", "list", "Detected objects (if applicable)", optional=True),
            IOSpec("success", "bool", "Whether analysis succeeded"),
        ),
        config=(
            ConfigOption("model", "string", "Vision model name"),
            ConfigOption("task", "string", "Analysis task type", default="describe"),
        ),
        integrations=(NodeType.IMAGE_GENERATION, NodeType.LLM_CHAT, NodeType.DATA_TRANSFORM),
        latency="Medium-High",
        resource_notes="GPU-intensive for large images. Processing time varies by model complexity.",
        implementation_class="VisionAINode",
    )
)


# =============================================================================
# Codex Access Functions
# =============================================================================


def get_entry(node_type: NodeType) -> NodeCodexEntry | None:
    """Get codex entry for a node type."""
    return CODEX.get(node_type)


def get_all_entries() -> list[NodeCodexEntry]:
    """Get all codex entries."""
    return list(CODEX.values())


def get_by_category(category: NodeCategory) -> list[NodeCodexEntry]:
    """Get all entries in a category."""
    return [e for e in CODEX.values() if e.category == category]


def get_integrations(node_type: NodeType) -> list[NodeCodexEntry]:
    """Get entries for node types that integrate well with the given type."""
    entry = CODEX.get(node_type)
    if not entry:
        return []
    return [CODEX[nt] for nt in entry.integrations if nt in CODEX]


def search_by_capability(keyword: str) -> list[NodeCodexEntry]:
    """Search entries by keyword in name, summary, or description."""
    keyword = keyword.lower()
    return [
        e
        for e in CODEX.values()
        if keyword in e.name.lower() or keyword in e.summary.lower() or keyword in e.description.lower()
    ]


def render_entry_text(entry: NodeCodexEntry, width: int = 80) -> list[str]:
    """Render a codex entry as formatted text lines for TUI display.

    Args:
        entry: The codex entry to render.
        width: Maximum line width.

    Returns:
        List of text lines suitable for terminal display.
    """
    lines: list[str] = []

    # Header
    lines.append(f"{entry.icon} {entry.name}")
    lines.append("=" * min(len(entry.name) + 4, width))
    lines.append("")

    # Category and latency
    lines.append(f"Category: {entry.category.value}")
    lines.append(f"Latency:  {entry.latency}")
    lines.append("")

    # Summary
    lines.append(entry.summary)
    lines.append("")

    # Description (word-wrapped)
    lines.append("Description:")
    desc_lines = entry.description.strip().split("\n")
    for desc_line in desc_lines:
        # Simple word wrap
        while len(desc_line) > width - 2:
            split_at = desc_line.rfind(" ", 0, width - 2)
            if split_at == -1:
                split_at = width - 2
            lines.append(f"  {desc_line[:split_at]}")
            desc_line = desc_line[split_at:].lstrip()
        if desc_line:
            lines.append(f"  {desc_line}")
    lines.append("")

    # Configuration
    if entry.config:
        lines.append("Configuration:")
        for cfg in entry.config:
            req = " (required)" if cfg.required else ""
            default = f" [default: {cfg.default}]" if cfg.default else ""
            constraints = f" ({cfg.constraints})" if cfg.constraints else ""
            lines.append(f"  {cfg.name}: {cfg.type}{req}{default}{constraints}")
            if cfg.description:
                lines.append(f"    {cfg.description}")
        lines.append("")

    # Inputs
    if entry.inputs:
        lines.append("Inputs:")
        for io in entry.inputs:
            opt = " (optional)" if io.optional else ""
            lines.append(f"  {io.name}: {io.type}{opt}")
            lines.append(f"    {io.description}")
        lines.append("")

    # Outputs
    if entry.outputs:
        lines.append("Outputs:")
        for io in entry.outputs:
            opt = " (optional)" if io.optional else ""
            lines.append(f"  {io.name}: {io.type}{opt}")
            lines.append(f"    {io.description}")
        lines.append("")

    # Integrations
    if entry.integrations:
        int_names = [CODEX[nt].name if nt in CODEX else nt.value for nt in entry.integrations]
        lines.append(f"Integrates with: {', '.join(int_names)}")
        lines.append("")

    # Resource notes
    if entry.resource_notes:
        lines.append(f"Resources: {entry.resource_notes}")

    return lines
