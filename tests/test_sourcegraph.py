"""Test Sourcegraph client and deterministic git fallback."""

import os
from tools.sourcegraph import SourcegraphClient, SearchResultItem


def test_sourcegraph_initialization():
    client = SourcegraphClient(endpoint_url="http://localhost:7080", token="test_token")
    assert client.endpoint_url == "http://localhost:7080"
    assert client.graphql_url == "http://localhost:7080/.api/graphql"
    assert client.token == "test_token"
    assert client.fallback_to_git is True


def test_sourcegraph_fallback_search():
    client = SourcegraphClient(
        endpoint_url="http://invalid-unreachable-host:9999",
        fallback_to_git=True,
        workspace_root=os.getcwd(),
    )
    # Search for an existing symbol in the repo
    results = client.search("SourcegraphClient")
    assert isinstance(results, list)
    assert len(results) > 0

    # Ensure result structure and fallback metadata
    first = results[0]
    assert isinstance(first, SearchResultItem)
    assert first.is_fallback is True
    assert first.confidence <= 0.75
    assert "sourcegraph.py" in first.file_path or "SourcegraphClient" in first.preview


def test_find_symbol_definitions():
    client = SourcegraphClient(
        endpoint_url="http://invalid-unreachable-host:9999",
        fallback_to_git=True,
    )
    results = client.find_symbol_definitions("PromptManager")
    assert len(results) > 0
    assert any("prompts.py" in r.file_path for r in results)


def test_find_references():
    client = SourcegraphClient(
        endpoint_url="http://invalid-unreachable-host:9999",
        fallback_to_git=True,
    )
    results = client.find_references("Settings")
    assert len(results) > 0
