"""Test git patch validation and draft PR creation engine."""

import os
from tools.patch_pr import PatchPRBot, PRCreationResult


def test_patch_bot_validation_invalid_diff():
    bot = PatchPRBot()
    # Malformed / unmatching patch
    invalid_diff = """--- a/non_existent_file_xyz.py
+++ b/non_existent_file_xyz.py
@@ -1,1 +1,1 @@
-broken
+fixed
"""
    applies, err = bot.validate_patch(invalid_diff)
    assert applies is False
    assert err is not None


def test_patch_bot_draft_pr_simulation():
    bot = PatchPRBot(token="", default_repo="desirao/flakyguard")
    # For simulation testing, provide empty diff or mock
    res = bot._simulate_draft_pr(
        incident_id="INC-999",
        branch_name="flakyguard/fix-INC-999",
        repo="desirao/flakyguard",
        title="Fix checkout NoneType regression",
        body="RCA and diff details",
    )
    assert isinstance(res, PRCreationResult)
    assert res.success is True
    assert res.is_simulation is True
    assert "INC-999" in res.pr_url
    assert res.branch_name == "flakyguard/fix-INC-999"

    # Check manifest file created
    manifest_path = os.path.join(bot.workspace_root, "data", "pull_requests", "pr_INC-999.json")
    assert os.path.exists(manifest_path)
