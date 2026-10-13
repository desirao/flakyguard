"""Test PromptManager and prompt catalog integrity."""

import pytest
from llm.prompts import prompt_manager


def test_required_prompts_exist():
    expected_prompts = [
        ("router", "v1"),
        ("router", "v2"),
        ("specialist_sre", "v1"),
        ("patch", "v1"),
        ("refactor", "v1"),
        ("testgen", "v1"),
        ("explain", "v1"),
        ("judge", "v1"),
    ]
    for name, version in expected_prompts:
        content = prompt_manager.load_prompt(name, version)
        assert len(content) > 20
        assert "FlakyGuard" in content or "Incident" in content or "Remediation" in content or "Test" in content


def test_list_prompts():
    prompts = prompt_manager.list_prompts()
    assert len(prompts) >= 8
    names = [p["name"] for p in prompts]
    assert "router" in names
    assert "specialist_sre" in names
    assert "patch" in names
    assert "refactor" in names


def test_format_router_prompt():
    formatted = prompt_manager.format_prompt("router", "v2", raw_log="AssertionError: 500 != 200")
    assert "AssertionError: 500 != 200" in formatted
    assert "<<<CI_LOG_START>>>" in formatted
    assert "<<<CI_LOG_END>>>" in formatted


def test_missing_prompt_raises_file_not_found():
    with pytest.raises(FileNotFoundError):
        prompt_manager.load_prompt("non_existent_prompt", "v99")


def test_missing_template_variable_raises_key_error():
    with pytest.raises(KeyError):
        # router_v1 expects raw_log
        prompt_manager.format_prompt("router", "v1")
