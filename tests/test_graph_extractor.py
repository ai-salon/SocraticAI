"""Tests for GraphExtractor.

Unit tests cover each parser in isolation.
Integration tests run against real meta.json fixtures from AiSalonContent.
"""

import json
from pathlib import Path

import pytest

from socraticai.content.knowledge_graph.graph_extractor import (
    GraphExtractor,
    GraphExtractionResult,
    NodeCandidate,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

FIXTURE_DIR = Path(__file__).parent.parent.parent / "AiSalonContent" / "outputs" / "articles"


def load_meta(filename: str) -> dict:
    path = FIXTURE_DIR / filename
    if not path.exists():
        pytest.skip(f"Fixture not found: {path}")
    with open(path) as f:
        return json.load(f)


THEMES_TEXT = """\
## Africa's Role in AI
Supporting quotes:
- "Africa has unique challenges requiring tailored solutions."
- "The young population is a competitive advantage."

## Community and Collaboration
Supporting quotes:
- "If you want to go far, go together."
- "We're building the same thing across different countries."
"""

INSIGHTS_TEXT = """\
1. Africa has unique challenges requiring tailored AI solutions rather than adopting Western benchmarks.
2. With 60% of Africans under 30, Africa's young population represents a competitive advantage.
3. Many participants believe success is not about competing with Western countries but solving local problems.
"""

QUESTIONS_TEXT = """\
1. How can Africa balance building AI solutions for local problems versus participating in global AI development?
2. Is Africa truly in competition with the rest of the world in AI, or should it focus on its own development path?
3. How can Africa retain talent when many skilled professionals are migrating to Western countries?
"""

PULL_QUOTES_TEXT = """\
1. "Fall seven times and stand up eight."
2. "I see futuristic cities — beautiful black African people."
"""


# ---------------------------------------------------------------------------
# Unit: _parse_numbered_list
# ---------------------------------------------------------------------------

class TestParseNumberedList:
    def test_basic(self):
        result = GraphExtractor._parse_numbered_list(INSIGHTS_TEXT)
        assert len(result) == 3
        assert result[0].startswith("Africa has unique challenges")

    def test_period_and_paren_delimiters(self):
        text = "1) First item\n2) Second item\n3. Third item"
        result = GraphExtractor._parse_numbered_list(text)
        assert result == ["First item", "Second item", "Third item"]

    def test_empty_returns_empty(self):
        assert GraphExtractor._parse_numbered_list("") == []
        assert GraphExtractor._parse_numbered_list("   ") == []
        assert GraphExtractor._parse_numbered_list(None) == []

    def test_multiline_item(self):
        text = "1. First line\n   continuation of first\n2. Second item"
        result = GraphExtractor._parse_numbered_list(text)
        assert len(result) == 2
        assert "continuation of first" in result[0]

    def test_strips_whitespace(self):
        text = "1.   Leading spaces   \n2.   Also leading   "
        result = GraphExtractor._parse_numbered_list(text)
        assert result[0] == "Leading spaces"
        assert result[1] == "Also leading"


# ---------------------------------------------------------------------------
# Unit: _extract_themes
# ---------------------------------------------------------------------------

class TestExtractThemes:
    def setup_method(self):
        self.extractor = GraphExtractor({})

    def test_extracts_correct_count(self):
        candidates = self.extractor._extract_themes(THEMES_TEXT)
        assert len(candidates) == 2

    def test_label_is_heading(self):
        candidates = self.extractor._extract_themes(THEMES_TEXT)
        labels = [c.label for c in candidates]
        assert "Africa's Role in AI" in labels
        assert "Community and Collaboration" in labels

    def test_type_is_concept(self):
        candidates = self.extractor._extract_themes(THEMES_TEXT)
        assert all(c.type == "concept" for c in candidates)

    def test_description_contains_quotes(self):
        candidates = self.extractor._extract_themes(THEMES_TEXT)
        africa_candidate = next(c for c in candidates if "Africa" in c.label)
        assert "tailored solutions" in africa_candidate.description

    def test_empty_returns_empty(self):
        assert self.extractor._extract_themes("") == []
        assert self.extractor._extract_themes(None) == []

    def test_source_text_preserved(self):
        candidates = self.extractor._extract_themes(THEMES_TEXT)
        assert all(c.source_text for c in candidates)


# ---------------------------------------------------------------------------
# Unit: _extract_insights
# ---------------------------------------------------------------------------

class TestExtractInsights:
    def setup_method(self):
        self.extractor = GraphExtractor({})

    def test_extracts_correct_count(self):
        candidates = self.extractor._extract_insights(INSIGHTS_TEXT)
        assert len(candidates) == 3

    def test_type_is_concept(self):
        candidates = self.extractor._extract_insights(INSIGHTS_TEXT)
        assert all(c.type == "concept" for c in candidates)

    def test_label_and_description_match(self):
        candidates = self.extractor._extract_insights(INSIGHTS_TEXT)
        for c in candidates:
            assert c.label == c.description

    def test_empty_returns_empty(self):
        assert self.extractor._extract_insights("") == []


# ---------------------------------------------------------------------------
# Unit: _extract_questions
# ---------------------------------------------------------------------------

class TestExtractQuestions:
    def setup_method(self):
        self.extractor = GraphExtractor({})

    def test_extracts_correct_count(self):
        candidates = self.extractor._extract_questions(QUESTIONS_TEXT)
        assert len(candidates) == 3

    def test_type_is_question(self):
        candidates = self.extractor._extract_questions(QUESTIONS_TEXT)
        assert all(c.type == "question" for c in candidates)

    def test_label_starts_with_how_or_is(self):
        candidates = self.extractor._extract_questions(QUESTIONS_TEXT)
        assert candidates[0].label.startswith("How can Africa")
        assert candidates[1].label.startswith("Is Africa")


# ---------------------------------------------------------------------------
# Unit: full extract()
# ---------------------------------------------------------------------------

class TestExtract:
    def _make_meta(self, **analysis_kwargs) -> dict:
        return {"analysis": analysis_kwargs}

    def test_returns_graph_extraction_result(self):
        meta = self._make_meta(
            themes=THEMES_TEXT,
            insights=INSIGHTS_TEXT,
            questions=QUESTIONS_TEXT,
            pull_quotes=PULL_QUOTES_TEXT,
        )
        result = GraphExtractor(meta).extract()
        assert isinstance(result, GraphExtractionResult)

    def test_concept_candidates_include_themes_and_insights(self):
        meta = self._make_meta(
            themes=THEMES_TEXT,
            insights=INSIGHTS_TEXT,
            questions=QUESTIONS_TEXT,
        )
        result = GraphExtractor(meta).extract()
        # 2 themes + 3 insights = 5 concept candidates
        assert len(result.concept_candidates) == 5

    def test_question_candidates_count(self):
        meta = self._make_meta(questions=QUESTIONS_TEXT)
        result = GraphExtractor(meta).extract()
        assert len(result.question_candidates) == 3

    def test_pull_quotes_in_article_properties(self):
        meta = self._make_meta(pull_quotes=PULL_QUOTES_TEXT)
        result = GraphExtractor(meta).extract()
        assert "pull_quotes" in result.article_properties
        assert len(result.article_properties["pull_quotes"]) == 2

    def test_insights_in_article_properties(self):
        meta = self._make_meta(insights=INSIGHTS_TEXT)
        result = GraphExtractor(meta).extract()
        assert "insights" in result.article_properties
        assert len(result.article_properties["insights"]) == 3

    def test_missing_fields_return_empty(self):
        result = GraphExtractor({}).extract()
        assert result.concept_candidates == []
        assert result.question_candidates == []

    def test_analysis_summary_key_fallback(self):
        """Older meta.json uses 'analysis_summary' instead of 'analysis'."""
        meta = {
            "analysis_summary": {
                "themes": THEMES_TEXT,
                "questions": QUESTIONS_TEXT,
                "insights": INSIGHTS_TEXT,
                "pull_quotes": "",
            }
        }
        result = GraphExtractor(meta).extract()
        assert len(result.concept_candidates) == 5
        assert len(result.question_candidates) == 3

    def test_analysis_takes_priority_over_analysis_summary(self):
        meta = {
            "analysis": {"themes": THEMES_TEXT, "insights": "", "questions": "", "pull_quotes": ""},
            "analysis_summary": {"themes": "", "insights": INSIGHTS_TEXT, "questions": "", "pull_quotes": ""},
        }
        result = GraphExtractor(meta).extract()
        # Should use 'analysis' (2 theme concepts, no insight concepts)
        assert len(result.concept_candidates) == 2


# ---------------------------------------------------------------------------
# Integration: real meta.json fixtures
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestGraphExtractorIntegration:
    def test_africa_article(self):
        meta = load_meta("2025-04-04-Africa_s Practical Path - Francis Sani_meta.json")
        result = GraphExtractor(meta).extract()

        # Some articles in AiSalonContent use a truncated analysis_summary format;
        # just verify extraction runs without error and returns valid structures.
        assert isinstance(result, GraphExtractionResult)
        assert isinstance(result.concept_candidates, list)
        assert isinstance(result.question_candidates, list)
        assert all(isinstance(c, NodeCandidate) for c in result.concept_candidates)
        assert all(isinstance(c, NodeCandidate) for c in result.question_candidates)

    def test_decentralization_article(self):
        meta = load_meta("2023-11-25 Ai salon - decentralization_meta.json")
        result = GraphExtractor(meta).extract()
        assert len(result.concept_candidates) > 0
        assert len(result.question_candidates) > 0

    def test_science_article_old_format(self):
        """2023-07-23 article uses 'analysis_summary' key — older format."""
        meta = load_meta("2023-07-23 - Salon_Science_meta.json")
        result = GraphExtractor(meta).extract()
        assert len(result.concept_candidates) > 0

    def test_no_duplicate_labels_within_result(self):
        """Within a single article, concept labels should be distinct."""
        meta = load_meta("2025-04-04-Africa_s Practical Path - Francis Sani_meta.json")
        result = GraphExtractor(meta).extract()
        labels = [c.label for c in result.concept_candidates]
        assert len(labels) == len(set(labels)), "Duplicate concept labels within one article"
