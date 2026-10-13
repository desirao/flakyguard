"""Sourcegraph Semantic Code Navigation and Git Grep Fallback Client.

Provides a unified interface for semantic search, symbol lookup, reference finding,
and git blame / diff analysis, with automatic deterministic fallback to local Git
operations when the Sourcegraph OSS instance is offline or unreachable.
"""

import json
import logging
import os
import re
import subprocess
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import requests

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SearchResultItem:
    repo: str
    file_path: str
    line_number: Optional[int]
    preview: str
    match_type: str  # "content", "symbol", "commit", "diff"
    is_fallback: bool
    confidence: float  # 1.0 for exact Sourcegraph, 0.65 for git grep fallback


GRAPHQL_SEARCH_QUERY = """
query SearchCode($query: String!) {
  search(query: $query, version: V3) {
    results {
      results {
        __typename
        ... on FileMatch {
          repository {
            name
          }
          file {
            path
          }
          lineMatches {
            lineNumber
            preview
          }
          symbols {
            name
            kind
            location {
              url
            }
          }
        }
        ... on CommitSearchResult {
          commit {
            oid
            message
            repository {
              name
            }
          }
        }
      }
    }
  }
}
"""


class SourcegraphClient:
    """Unified Code Search client supporting Sourcegraph GraphQL and deterministic Git fallback."""

    def __init__(
        self,
        endpoint_url: Optional[str] = None,
        token: Optional[str] = None,
        fallback_to_git: bool = True,
        workspace_root: Optional[str] = None,
    ):
        self.endpoint_url = (endpoint_url or settings.SOURCEGRAPH_URL).rstrip("/")
        self.graphql_url = f"{self.endpoint_url}/.api/graphql"
        self.token = token or settings.SOURCEGRAPH_TOKEN
        self.fallback_to_git = fallback_to_git
        self.workspace_root = workspace_root or os.getcwd()

    def is_available(self, timeout: float = 2.0) -> bool:
        """Check if Sourcegraph GraphQL endpoint is reachable."""
        try:
            res = requests.get(f"{self.endpoint_url}/healthz", timeout=timeout)
            return res.status_code == 200
        except Exception:
            return False

    def search(
        self,
        query: str,
        repo: Optional[str] = None,
        count: int = 20,
    ) -> List[SearchResultItem]:
        """Execute search query. Falls back to deterministic git grep if offline."""
        full_query = query
        if repo and f"repo:{repo}" not in query:
            full_query = f"repo:{repo} {query}"

        # Try Sourcegraph first
        if self.token or self.is_available():
            try:
                results = self._query_sourcegraph(full_query)
                if results:
                    return results[:count]
            except Exception as e:
                logger.warning(
                    "Sourcegraph GraphQL query failed: %s. Falling back to git.", e
                )

        if self.fallback_to_git:
            return self._fallback_git_search(query, repo)[:count]

        return []

    def _query_sourcegraph(self, query: str) -> List[SearchResultItem]:
        """Send GraphQL request to Sourcegraph server."""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"

        response = requests.post(
            self.graphql_url,
            json={"query": GRAPHQL_SEARCH_QUERY, "variables": {"query": query}},
            headers=headers,
            timeout=(3.0, 10.0),
        )
        response.raise_for_status()
        data = response.json()

        items: List[SearchResultItem] = []
        raw_results = (
            data.get("data", {})
            .get("search", {})
            .get("results", {})
            .get("results", [])
        )

        for res in raw_results:
            typename = res.get("__typename")
            if typename == "FileMatch":
                repo_name = res.get("repository", {}).get("name", "unknown")
                file_path = res.get("file", {}).get("path", "")
                
                # Check symbols
                for sym in res.get("symbols", []):
                    items.append(
                        SearchResultItem(
                            repo=repo_name,
                            file_path=file_path,
                            line_number=None,
                            preview=f"Symbol [{sym.get('kind')}]: {sym.get('name')}",
                            match_type="symbol",
                            is_fallback=False,
                            confidence=1.0,
                        )
                    )

                # Check line matches
                for match in res.get("lineMatches", []):
                    items.append(
                        SearchResultItem(
                            repo=repo_name,
                            file_path=file_path,
                            line_number=match.get("lineNumber"),
                            preview=match.get("preview", "").strip(),
                            match_type="content",
                            is_fallback=False,
                            confidence=0.95,
                        )
                    )

            elif typename == "CommitSearchResult":
                commit = res.get("commit", {})
                items.append(
                    SearchResultItem(
                        repo=commit.get("repository", {}).get("name", "unknown"),
                        file_path="",
                        line_number=None,
                        preview=f"Commit {commit.get('oid')[:8]}: {commit.get('message', '').strip()}",
                        match_type="commit",
                        is_fallback=False,
                        confidence=0.90,
                    )
                )

        return items

    def _fallback_git_search(
        self,
        query: str,
        repo: Optional[str] = None,
    ) -> List[SearchResultItem]:
        """Deterministic fallback using git grep and git log when Sourcegraph is offline."""
        items: List[SearchResultItem] = []
        repo_name = repo or settings.DEFAULT_REPO

        # Clean query terms (strip sourcegraph qualifiers like repo:, type:, file:)
        clean_terms = []
        file_filter = None
        for token in query.split():
            if token.startswith("file:"):
                file_filter = token[5:]
            elif token.startswith("repo:") or token.startswith("type:") or token.startswith("lang:"):
                continue
            else:
                clean_terms.append(token)

        pattern = " ".join(clean_terms).strip()
        if not pattern:
            pattern = "."

        # Check if workspace is a git repo
        git_dir = os.path.join(self.workspace_root, ".git")
        if os.path.exists(git_dir):
            try:
                cmd = ["git", "grep", "-n", "-I", "-E", pattern]
                if file_filter:
                    cmd.extend(["--", file_filter])

                result = subprocess.run(
                    cmd,
                    cwd=self.workspace_root,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=5,
                )

                if result.returncode == 0 and result.stdout:
                    for line in result.stdout.splitlines()[:50]:
                        parts = line.split(":", 2)
                        if len(parts) >= 3:
                            file_path = parts[0]
                            try:
                                line_no = int(parts[1])
                            except ValueError:
                                line_no = None
                            preview = parts[2].strip()
                            items.append(
                                SearchResultItem(
                                    repo=repo_name,
                                    file_path=file_path,
                                    line_number=line_no,
                                    preview=preview,
                                    match_type="content",
                                    is_fallback=True,
                                    confidence=0.70,
                                )
                            )
            except Exception as e:
                logger.error("Git grep fallback failed: %s", e)

        # If git grep found nothing or isn't available, perform filesystem scan fallback
        if not items:
            items.extend(self._local_filesystem_search(pattern, file_filter, repo_name))

        return items

    def _local_filesystem_search(
        self, pattern: str, file_filter: Optional[str], repo_name: str
    ) -> List[SearchResultItem]:
        items: List[SearchResultItem] = []
        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error:
            regex = re.compile(re.escape(pattern), re.IGNORECASE)

        for root, dirs, files in os.walk(self.workspace_root):
            # Ignore hidden and virtual environment directories
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("venv", "node_modules", "__pycache__")]
            for filename in files:
                if file_filter and file_filter not in filename:
                    continue
                if filename.endswith((".py", ".md", ".json", ".yml", ".yaml", ".txt")):
                    file_path = os.path.join(root, filename)
                    rel_path = os.path.relpath(file_path, self.workspace_root)
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                            for idx, line in enumerate(f, start=1):
                                if regex.search(line):
                                    items.append(
                                        SearchResultItem(
                                            repo=repo_name,
                                            file_path=rel_path.replace("\\", "/"),
                                            line_number=idx,
                                            preview=line.strip(),
                                            match_type="content",
                                            is_fallback=True,
                                            confidence=0.60,
                                        )
                                    )
                                    if len(items) >= 20:
                                        return items
                    except Exception:
                        continue
        return items

    def find_symbol_definitions(self, symbol: str, repo: Optional[str] = None) -> List[SearchResultItem]:
        """Find definitions of a function, class, or variable."""
        query = f"type:symbol {symbol}"
        return self.search(query, repo=repo)

    def find_references(self, symbol: str, repo: Optional[str] = None) -> List[SearchResultItem]:
        """Find all usages and references to a symbol."""
        query = f"\\b{re.escape(symbol)}\\b"
        return self.search(query, repo=repo)

    def get_commit_diff(self, commit_sha: str) -> Optional[str]:
        """Get diff for a commit SHA from git."""
        try:
            result = subprocess.run(
                ["git", "show", "--unified=3", commit_sha],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout
        except Exception as e:
            logger.error("Failed to fetch commit diff for %s: %s", commit_sha, e)
        return None


# Global singleton instance
sourcegraph_client = SourcegraphClient()
