"""Automated WCAG 2.1 AA accessibility and UI structure tests."""

import re
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
HTML_PATH = WORKSPACE / "app" / "static" / "index.html"
CSS_PATH = WORKSPACE / "app" / "static" / "style.css"


def test_html_accessibility_landmarks():
    assert HTML_PATH.exists()
    content = HTML_PATH.read_text(encoding="utf-8")

    # 1. Skip to content link
    assert 'class="skip-link"' in content
    assert 'href="#main-content"' in content

    # 2. Main content target
    assert 'id="main-content"' in content
    assert 'role="main"' in content

    # 3. Proper page title & language
    assert '<html lang="en">' in content
    assert "<title>" in content

    # 4. Heading structure
    assert "<h1" in content
    assert "<h2" in content

    # 5. Live region for dynamic feedback
    assert 'aria-live="polite"' in content


def test_html_form_labels():
    content = HTML_PATH.read_text(encoding="utf-8")

    # Verify input elements have associated labels
    input_ids = re.findall(r'<input[^>]+id="([^"]+)"', content)
    textarea_ids = re.findall(r'<textarea[^>]+id="([^"]+)"', content)
    select_ids = re.findall(r'<select[^>]+id="([^"]+)"', content)

    all_ids = set(input_ids + textarea_ids + select_ids)
    for field_id in all_ids:
        # Check label with matching for attribute exists
        assert f'for="{field_id}"' in content, f"Missing <label for='{field_id}'>"


def test_css_focus_visible_styling():
    assert CSS_PATH.exists()
    content = CSS_PATH.read_text(encoding="utf-8")

    # Focus-visible rule must exist
    assert ":focus-visible" in content
    assert "outline:" in content

    # High-contrast class must exist
    assert ".high-contrast" in content
