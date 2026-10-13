"""Prompt loader, versioning manager, and formatter for FlakyGuard-AI."""

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


class PromptManager:
    """Manages versioned markdown prompts and variable interpolation."""

    def __init__(self, directory: Optional[Path] = None):
        self.directory = directory or PROMPTS_DIR

    def get_prompt_path(self, name: str, version: str = "v1") -> Path:
        """Resolve path to prompt file, e.g. router_v2.md or specialist_sre_v1.md."""
        filename = f"{name}_{version}.md"
        return self.directory / filename

    def load_prompt(self, name: str, version: str = "v1") -> str:
        """Load raw prompt text by name and version."""
        path = self.get_prompt_path(name, version)
        if not path.exists():
            raise FileNotFoundError(
                f"Prompt '{name}' version '{version}' not found at {path}"
            )
        return path.read_text(encoding="utf-8")

    def format_prompt(self, name: str, version: str = "v1", **kwargs: Any) -> str:
        """Load prompt and safely replace {placeholder} fields with kwargs without choking on JSON braces."""
        raw_prompt = self.load_prompt(name, version)
        
        # Discover all {key} placeholders in prompt that match valid python identifiers
        placeholders = set(re.findall(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}", raw_prompt))
        
        # Check for missing required parameters
        missing = [key for key in placeholders if key not in kwargs]
        if missing:
            raise KeyError(
                f"Missing required parameter '{missing[0]}' for prompt '{name}_{version}'"
            )

        formatted = raw_prompt
        for key, value in kwargs.items():
            formatted = formatted.replace(f"{{{key}}}", str(value))
        return formatted


    def list_prompts(self) -> List[Dict[str, str]]:
        """List all available versioned prompts in the prompts directory."""
        if not self.directory.exists():
            return []

        prompts = []
        for file in sorted(self.directory.glob("*_v*.md")):
            parts = file.stem.rsplit("_", 1)
            if len(parts) == 2:
                name, version = parts
                prompts.append({
                    "name": name,
                    "version": version,
                    "filename": file.name,
                    "path": str(file),
                })
        return prompts


# Global singleton instance
prompt_manager = PromptManager()
