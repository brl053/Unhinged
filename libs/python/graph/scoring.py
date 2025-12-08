"""
@llm-type library.graph.scoring
@llm-does text-to-graph matching score calculation

Scoring Module
--------------

Single source of truth for matching user input text to graph metadata.
Used by both graph session matching and pre-flight rubric checks.

Default weights:
    - tag exact match: 2.0
    - tag partial match: 1.0
    - name word match: 1.5
    - description word match: 0.5 (words > 3 chars only)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ScoringRubric:
    """Weights for scoring text against graph metadata."""

    tag_exact: float = 2.0
    tag_partial: float = 1.0
    name_word: float = 1.5
    desc_word: float = 0.5
    desc_min_word_len: int = 3
    threshold: float = 1.0


DEFAULT_RUBRIC = ScoringRubric()


def score_text_to_graph(
    text: str,
    tags: list[str],
    name: str,
    description: str = "",
    rubric: ScoringRubric | None = None,
) -> float:
    """Calculate match score between input text and graph metadata.

    Args:
        text: User input text to match
        tags: Graph tags (e.g., ["gmail", "email"])
        name: Graph name (e.g., "Gmail to Social")
        description: Graph description
        rubric: Scoring weights (uses DEFAULT_RUBRIC if None)

    Returns:
        Match score (higher = better match)
    """
    if not text:
        return 0.0

    rubric = rubric or DEFAULT_RUBRIC
    text_lower = text.lower()
    words = set(text_lower.split())
    tags_lower = [t.lower() for t in tags]
    name_lower = name.lower()
    desc_lower = description.lower()

    score = 0.0

    # Tag matching
    for tag in tags_lower:
        if tag in text_lower:
            score += rubric.tag_exact
        for word in words:
            if word in tag or tag in word:
                score += rubric.tag_partial

    # Name matching
    for word in words:
        if word in name_lower:
            score += rubric.name_word

    # Description matching (longer words only)
    for word in words:
        if len(word) > rubric.desc_min_word_len and word in desc_lower:
            score += rubric.desc_word

    return score


def match_best_graph(
    text: str,
    graphs: list[Any],
    rubric: ScoringRubric | None = None,
) -> tuple[Any | None, float]:
    """Find best matching graph for input text.

    Args:
        text: User input text
        graphs: List of graph documents (with .data dict containing tags, name, description)
        rubric: Scoring weights

    Returns:
        (best_match, score) tuple. best_match is None if no graphs provided.
    """
    rubric = rubric or DEFAULT_RUBRIC
    best_match = None
    best_score = 0.0

    for doc in graphs:
        data = doc.data if hasattr(doc, "data") else doc
        score = score_text_to_graph(
            text=text,
            tags=data.get("tags", []),
            name=data.get("name", ""),
            description=data.get("description", ""),
            rubric=rubric,
        )

        if score > best_score:
            best_score = score
            best_match = doc

    return best_match, best_score
