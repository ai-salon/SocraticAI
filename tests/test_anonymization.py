import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock

from socraticai.transcribe.utils import anonymize_transcript, _get_nlp_model, NAME_LIST

# Mark all tests in this file as unit tests
pytestmark = pytest.mark.unit


def _make_mock_doc(persons):
    """Create a mock spaCy doc with the given PERSON entities."""
    mock_doc = MagicMock()
    entities = []
    for name in persons:
        ent = MagicMock()
        ent.text = name
        ent.label_ = "PERSON"
        entities.append(ent)
    mock_doc.ents = entities
    return mock_doc


def _write_temp_file(content):
    """Write content to a temp file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


class TestAnonymizeTranscript:
    """Tests for the anonymize_transcript function."""

    @patch("socraticai.transcribe.utils._get_nlp_model")
    def test_full_text_scanning(self, mock_get_nlp):
        """Name appearing only in the last quarter of text is still anonymized."""
        # Build text where "Alice" only appears near the end
        filler = "This is some filler text with no names. " * 100
        text = filler + "Alice said something important."

        mock_nlp = MagicMock()
        mock_nlp.return_value = _make_mock_doc(["Alice"])
        mock_get_nlp.return_value = mock_nlp

        path = _write_temp_file(text)
        try:
            result, count = anonymize_transcript(path)
            # The full text was passed to spaCy (not just first 1/6)
            called_text = mock_nlp.call_args[0][0]
            assert "Alice" in called_text
            # Alice should be replaced
            assert "Alice" not in result
            assert count == 1
        finally:
            os.unlink(path)

    @patch("socraticai.transcribe.utils._get_nlp_model")
    def test_word_boundary_matching(self, mock_get_nlp):
        """'John' should not replace inside 'Johnson' or 'Johnny'."""
        text = "John talked to Johnson and Johnny about the project."

        mock_nlp = MagicMock()
        mock_nlp.return_value = _make_mock_doc(["John"])
        mock_get_nlp.return_value = mock_nlp

        path = _write_temp_file(text)
        try:
            result, count = anonymize_transcript(path)
            # "John" (standalone) should be replaced
            assert "John talked" not in result
            # "Johnson" and "Johnny" should remain intact
            assert "Johnson" in result
            assert "Johnny" in result
            assert count == 1
        finally:
            os.unlink(path)

    @patch("socraticai.transcribe.utils._get_nlp_model")
    def test_basic_happy_path(self, mock_get_nlp):
        """Known names are replaced with names from the list."""
        text = "Bob and Carol discussed the topic."

        mock_nlp = MagicMock()
        mock_nlp.return_value = _make_mock_doc(["Bob", "Carol"])
        mock_get_nlp.return_value = mock_nlp

        path = _write_temp_file(text)
        try:
            result, count = anonymize_transcript(path)
            assert "Bob" not in result
            assert "Carol" not in result
            assert count == 2
            # Should have the anonymity header
            assert result.startswith("Names have been changed to preserve anonymity.")
        finally:
            os.unlink(path)

    @patch("socraticai.transcribe.utils._get_nlp_model")
    def test_no_names_found(self, mock_get_nlp):
        """Text with no PERSON entities returns unchanged (except the prepended header)."""
        text = "The weather was nice today."

        mock_nlp = MagicMock()
        mock_nlp.return_value = _make_mock_doc([])
        mock_get_nlp.return_value = mock_nlp

        path = _write_temp_file(text)
        try:
            result, count = anonymize_transcript(path)
            assert count == 0
            assert "The weather was nice today." in result
            assert result.startswith("Names have been changed to preserve anonymity.")
        finally:
            os.unlink(path)

    @patch("socraticai.transcribe.utils.spacy")
    def test_spacy_lazy_loading(self, mock_spacy):
        """Second call reuses cached model (spacy.load called once)."""
        import socraticai.transcribe.utils as utils_module

        # Reset the cache
        original = utils_module._nlp_model
        utils_module._nlp_model = None

        mock_model = MagicMock()
        mock_spacy.load.return_value = mock_model

        try:
            _get_nlp_model()
            _get_nlp_model()
            # spacy.load should only be called once due to caching
            mock_spacy.load.assert_called_once()
        finally:
            utils_module._nlp_model = original

    @patch("socraticai.transcribe.utils._get_nlp_model")
    def test_save_path(self, mock_get_nlp):
        """When save_path is provided, the anonymized text is written to it."""
        text = "Dave said hello."

        mock_nlp = MagicMock()
        mock_nlp.return_value = _make_mock_doc(["Dave"])
        mock_get_nlp.return_value = mock_nlp

        path = _write_temp_file(text)
        fd, save_path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        try:
            result, count = anonymize_transcript(path, save_path=save_path)
            with open(save_path, "r") as f:
                saved = f.read()
            assert saved == result
            assert "Dave" not in saved
        finally:
            os.unlink(path)
            os.unlink(save_path)
