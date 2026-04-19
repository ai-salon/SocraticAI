"""Extract graph node candidates from article meta.json analysis.

Pure transformation — no LLM calls, no DB, no filesystem.
Consumes the structured analysis already computed by ArticleGenerator
and returns typed candidates ready for the platform's ingestion service.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class NodeCandidate:
    """A candidate graph node extracted from article analysis."""
    type: str           # 'concept' | 'question'
    label: str          # display name / primary text
    description: str    # one-paragraph description or the full insight sentence
    source_text: str    # original excerpt from meta that produced this candidate


@dataclass
class GraphExtractionResult:
    """All graph data extracted from a single article's meta."""
    concept_candidates: list[NodeCandidate] = field(default_factory=list)
    question_candidates: list[NodeCandidate] = field(default_factory=list)
    article_properties: dict[str, Any] = field(default_factory=dict)


class GraphExtractor:
    """
    Extract graph node candidates from an article's meta dict.

    Handles two historical meta formats:
    - 'analysis' key (current format, 2023-11-25 onwards)
    - 'analysis_summary' key (older format, pre-2023-11-25)

    Extraction mapping:
    - analysis.themes   → concept candidates (theme heading as label)
    - analysis.insights → concept candidates (full insight as label + description)
    - analysis.questions → question candidates
    - analysis.pull_quotes → stored in article_properties, not graph nodes
    """

    def __init__(self, meta: dict[str, Any]) -> None:
        self._meta = meta
        self._analysis = meta.get("analysis") or meta.get("analysis_summary") or {}

    def extract(self) -> GraphExtractionResult:
        """Run full extraction. Returns GraphExtractionResult."""
        result = GraphExtractionResult()

        themes_text = self._analysis.get("themes", "")
        insights_text = self._analysis.get("insights", "")
        questions_text = self._analysis.get("questions", "")
        pull_quotes_text = self._analysis.get("pull_quotes", "")

        result.concept_candidates.extend(self._extract_themes(themes_text))
        result.concept_candidates.extend(self._extract_insights(insights_text))
        result.question_candidates.extend(self._extract_questions(questions_text))

        result.article_properties = {
            "pull_quotes": self._parse_numbered_list(pull_quotes_text),
            "insights": self._parse_numbered_list(insights_text),
        }

        return result

    # ------------------------------------------------------------------
    # Private parsers
    # ------------------------------------------------------------------

    def _extract_themes(self, text: str) -> list[NodeCandidate]:
        """
        Parse '## Theme Title\nSupporting quotes:\n- "..."\n...' blocks.

        Returns one NodeCandidate per theme. The label is the heading;
        the description is built from the supporting quotes.
        """
        if not text or not text.strip():
            return []

        candidates: list[NodeCandidate] = []

        # Split on '## ' headings — works for both 2 and 3 # levels
        sections = re.split(r"\n(?=##\s)", text.strip())

        for section in sections:
            section = section.strip()
            if not section:
                continue

            # Extract heading
            heading_match = re.match(r"^#{1,3}\s+(.+)", section)
            if not heading_match:
                continue

            label = heading_match.group(1).strip()

            # Everything after the heading is description/quotes context
            body = section[heading_match.end():].strip()

            # Strip "Supporting quotes:" header if present; keep the quotes
            body = re.sub(r"^Supporting quotes:\s*", "", body, flags=re.IGNORECASE).strip()

            # Collapse bullet quote lines into a single description paragraph
            quote_lines = [
                line.lstrip("-• ").strip()
                for line in body.splitlines()
                if line.strip().startswith(("-", "•", '"'))
            ]
            description = " ".join(quote_lines) if quote_lines else label

            candidates.append(NodeCandidate(
                type="concept",
                label=label,
                description=description,
                source_text=section,
            ))

        return candidates

    def _extract_insights(self, text: str) -> list[NodeCandidate]:
        """
        Parse numbered insights list into concept candidates.

        Each insight is a full sentence used as both label and description.
        Concept-level deduplication in the platform will cluster related
        insights and derive cleaner labels over time.
        """
        if not text or not text.strip():
            return []

        candidates: list[NodeCandidate] = []
        for item in self._parse_numbered_list(text):
            if not item:
                continue
            candidates.append(NodeCandidate(
                type="concept",
                label=item,
                description=item,
                source_text=item,
            ))
        return candidates

    def _extract_questions(self, text: str) -> list[NodeCandidate]:
        """Parse numbered questions list into question candidates."""
        if not text or not text.strip():
            return []

        candidates: list[NodeCandidate] = []
        for item in self._parse_numbered_list(text):
            if not item:
                continue
            candidates.append(NodeCandidate(
                type="question",
                label=item,
                description=item,
                source_text=item,
            ))
        return candidates

    @staticmethod
    def _parse_numbered_list(text: str) -> list[str]:
        """
        Parse a numbered list like '1. Foo\\n2. Bar\\n3. Baz' into ['Foo', 'Bar', 'Baz'].

        Handles:
        - '1.' and '1)' delimiters
        - Leading/trailing whitespace
        - Multi-line items (continuation lines without a number prefix)
        - Extra blank lines between items
        """
        if not text or not text.strip():
            return []

        items: list[str] = []
        current: list[str] = []

        for line in text.splitlines():
            stripped = line.strip()
            # Match lines starting with a number followed by '.' or ')'
            number_match = re.match(r"^\d+[.)]\s+(.*)", stripped)
            if number_match:
                if current:
                    items.append(" ".join(current))
                current = [number_match.group(1).strip()]
            elif stripped and current:
                # Continuation line — append to current item
                current.append(stripped)

        if current:
            items.append(" ".join(current))

        return [item for item in items if item]
