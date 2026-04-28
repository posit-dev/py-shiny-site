"""Artifact tests for _build/llms-full.txt.

These tests validate the generated output file rather than the generation code.
Run after `make llms-full-txt`. Tests are skipped if the artifact doesn't exist.
"""

import pytest
from pathlib import Path

ARTIFACT = Path(__file__).parent.parent / "_build" / "llms-full.txt"

EXPECTED_SECTIONS = [
    "Get Started",
    "Concepts",
    "Components",
    "Layouts",
    "API Reference",
    "Templates",
]


@pytest.fixture(scope="module")
def content():
    if not ARTIFACT.exists():
        pytest.skip("_build/llms-full.txt not found — run 'make llms-full-txt' first")
    return ARTIFACT.read_text()


@pytest.fixture(scope="module")
def lines(content):
    return content.splitlines()


# ---------------------------------------------------------------------------
# Structure
# ---------------------------------------------------------------------------


def test_starts_with_shiny_header(content):
    assert content.startswith("# Shiny for Python\n")


def test_section_order(content):
    """All expected sections are present and appear in the correct order."""
    for section in EXPECTED_SECTIONS:
        assert f"## {section}" in content, f"Missing section: {section}"
    positions = {s: content.index(f"## {s}") for s in EXPECTED_SECTIONS}
    for a, b in zip(EXPECTED_SECTIONS, EXPECTED_SECTIONS[1:]):
        assert positions[a] < positions[b], f"Section '{a}' must come before '{b}'"


def test_minimum_page_count(content):
    """Catches silent truncation — page count should never drop significantly."""
    count = content.count("\nSource: https://")
    assert count >= 400, f"Expected ≥400 pages, found {count}"


# ---------------------------------------------------------------------------
# Per-page requirements
# ---------------------------------------------------------------------------


def test_source_urls_are_well_formed(lines):
    """Every Source: line must point to the expected base URL."""
    for i, line in enumerate(lines):
        if line.startswith("Source: "):
            assert line.startswith("Source: https://shiny.posit.co/py/"), (
                f"Malformed Source URL at line {i + 1}: {line!r}"
            )


# ---------------------------------------------------------------------------
# Content quality regressions
# ---------------------------------------------------------------------------


def test_no_shinylive_fences(content):
    assert "```shinylive-" not in content, "shinylive fence not normalized to python"
    assert "```numberSource" not in content, "numberSource fence not normalized to python"


def test_balanced_code_fences(lines):
    """Unbalanced fences produce malformed Markdown that breaks parsers."""
    depth = 0
    for line in lines:
        if line.strip().startswith("```"):
            depth += 1
    assert depth % 2 == 0, f"Odd number of code fence markers ({depth}) — likely an unclosed fence"
