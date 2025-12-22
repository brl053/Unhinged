"""Analytical (non-generative) model nodes.

@llm-type library.graph.analytical
@llm-does preprocessing nodes using BERT, SBERT, YOLO, etc. for structured analysis

These nodes act as "food processors" - they take raw input and output structured
data that can be piped to LLM nodes or used for routing decisions.

All models are lazy-loaded to avoid startup overhead.
"""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from .nodes import GraphNode

if TYPE_CHECKING:
    from .context import SessionContext


class AnalyticalNode(GraphNode):
    """Base class for analytical (non-generative) model nodes.

    Analytical nodes:
    - Take raw input (text, audio, image path)
    - Run a specialized model (BERT, YOLO, etc.)
    - Output structured data (labels, embeddings, bounding boxes)
    - Support lazy model loading
    """

    def __init__(self, node_id: str) -> None:
        super().__init__(node_id)
        self._session: SessionContext | None = None
        self._model: Any = None

    def set_session(self, session: SessionContext | None) -> None:
        """Set session context for CDC events."""
        self._session = session

    @abstractmethod
    def _load_model(self) -> Any:
        """Lazy-load the model. Called once on first execute."""

    @abstractmethod
    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute analysis and return structured output."""


class TextClassifierNode(AnalyticalNode):
    """Classify text into predefined categories using sentence embeddings.

    Uses sentence-transformers (SBERT) for embedding-based classification.
    Fast, no fine-tuning needed, works with any labels.

    Config:
    - model_name: SBERT model (default: all-MiniLM-L6-v2, 80MB, Apache 2.0)
    - labels: list of classification labels
    - threshold: minimum confidence to return a label (default: 0.3)

    Output:
    - label: predicted class label
    - confidence: cosine similarity score (0-1)
    - scores: dict of all label scores
    - success: True
    """

    # Default labels for intent classification
    DEFAULT_LABELS = [
        "engineering_task",  # needs planning, approval, multi-step
        "simple_command",  # run a single command
        "question",  # asking for information
        "unclear",  # can't determine intent
    ]

    def __init__(
        self,
        node_id: str,
        model_name: str = "all-MiniLM-L6-v2",
        labels: list[str] | None = None,
        threshold: float = 0.3,
    ) -> None:
        super().__init__(node_id)
        self.model_name = model_name
        self.labels = labels or self.DEFAULT_LABELS
        self.threshold = threshold
        self._label_embeddings: Any = None

    def _load_model(self) -> Any:
        """Load sentence-transformers model."""
        try:
            from sentence_transformers import SentenceTransformer

            return SentenceTransformer(self.model_name)
        except ImportError as e:
            raise ImportError("sentence-transformers required. Install: pip install sentence-transformers") from e

    def _compute_label_embeddings(self) -> None:
        """Pre-compute embeddings for all labels."""
        if self._label_embeddings is None:
            # Expand labels with descriptive phrases for better semantic matching
            # Multiple example phrases help the embedding capture the intent
            label_descriptions = {
                "engineering_task": (
                    "I want to build an application. Create a new feature for me. "
                    "Implement this functionality. Write code to do something. "
                    "Build a website. Create a static HTML page. Make an app. "
                    "Develop a program. Set up a project. Design and implement. "
                    "Create a REST API. Build a backend service. Make a CLI tool. "
                    "Write a script that does this. Implement authentication. "
                    "Set up a database. Create a microservice. Build with Flask. "
                    "Please create me a tool. Make me a simple page. "
                    "Create an internal tool. Build a proof of concept. "
                    "Generate a webpage. Create HTML and JavaScript. "
                    "Make something and open it in browser. Create and view in Firefox."
                ),
                "simple_command": (
                    "List files. Show directory contents. Run this command. "
                    "Check the status. Display output. Execute ls. "
                    "What files are here. Show me the processes. "
                    "Print working directory. Cat this file. "
                    "Delete this file. Move this. Copy that. "
                    "Show disk usage. Check memory. Run grep."
                ),
                "question": (
                    "What is this? How does it work? Explain this to me. "
                    "Can you tell me about? Why does this happen? "
                    "What does this mean? Help me understand. "
                    "I have a question. What are the differences between? "
                    "How do I use this? What command should I run?"
                ),
                "unclear": (
                    "asdf random gibberish. I don't know. Maybe. "
                    "hmm. ok. yes. no. hello. hi there. "
                    "thanks. goodbye. see you later."
                ),
            }
            descriptions = [label_descriptions.get(l, l) for l in self.labels]
            self._label_embeddings = self._model.encode(descriptions)

    async def execute(self, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Classify input text against predefined labels."""
        import numpy as np

        input_data = input_data or {}
        text = input_data.get("stdin") or input_data.get("text") or input_data.get("input", {}).get("topic", "")

        if not text:
            return {
                "label": "unclear",
                "confidence": 0.0,
                "scores": {},
                "stdout": "unclear",
                "success": True,
            }

        # Lazy load model
        if self._model is None:
            self._model = self._load_model()
            self._compute_label_embeddings()

        # Encode input text
        text_embedding = self._model.encode([text])[0]

        # Compute cosine similarity with each label
        from numpy.linalg import norm

        scores = {}
        for i, label in enumerate(self.labels):
            label_emb = self._label_embeddings[i]
            similarity = float(np.dot(text_embedding, label_emb) / (norm(text_embedding) * norm(label_emb)))
            scores[label] = similarity

        # Get best label
        best_label = max(scores, key=scores.get)
        best_score = scores[best_label]

        # Apply threshold
        if best_score < self.threshold:
            best_label = "unclear"

        return {
            "label": best_label,
            "confidence": best_score,
            "scores": scores,
            "stdout": best_label,  # For piping
            "text": text,
            "success": True,
        }
