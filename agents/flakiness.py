"""Flakiness Analyzer Agent for FlakyGuard-AI.

Statistically analyzes CI execution histories across identical commit SHAs to detect
non-deterministic test behavior, compute pass rates and variance, and recommend
quarantine over noisy code patching.
"""

import math
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Literal, Optional


@dataclass
class TestRunRecord:
    __test__ = False
    run_id: str
    commit_sha: str
    status: Literal["passed", "failed"]
    duration_seconds: float
    timestamp: str


@dataclass
class FlakinessReport:
    __test__ = False
    test_identifier: str
    is_flaky: bool
    pass_rate: float
    failure_rate: float
    variance: float
    sample_size: int
    recommendation: Literal["quarantine", "patch", "investigate", "stable"]
    rationale: str
    runs: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FlakinessAnalyzer:
    """Analyzes test execution sequences and computes flakiness probabilities."""

    def __init__(self, flakiness_threshold: float = 0.15, **kwargs):
        self.flakiness_threshold = kwargs.get("flaky_threshold", flakiness_threshold)

    def analyze_test_history(
        self,
        test_identifier: str,
        execution_records: List[TestRunRecord],
        current_commit: Optional[str] = None,
    ) -> FlakinessReport:
        """Evaluate history for non-deterministic outcomes on identical commit SHAs."""
        if not execution_records:
            return FlakinessReport(
                test_identifier=test_identifier,
                is_flaky=False,
                pass_rate=0.0,
                failure_rate=1.0,
                variance=0.0,
                sample_size=0,
                recommendation="investigate",
                rationale="Insufficient historical runs to compute flakiness.",
                runs=[],
            )

        total_runs = len(execution_records)
        passed_runs = sum(1 for r in execution_records if r.status == "passed")
        failed_runs = total_runs - passed_runs

        pass_rate = passed_runs / total_runs
        failure_rate = failed_runs / total_runs

        # Statistical binomial variance: p * (1 - p)
        variance = round(pass_rate * (1.0 - pass_rate), 4)

        # Commit-level variance check: Did the test both pass and fail on the same SHA?
        commits_to_statuses: Dict[str, set] = {}
        for r in execution_records:
            commits_to_statuses.setdefault(r.commit_sha, set()).add(r.status)

        inconsistent_commits = [
            sha for sha, statuses in commits_to_statuses.items() if len(statuses) > 1
        ]

        # Determine Recommendation
        if inconsistent_commits:
            is_flaky = True
            recommendation = "quarantine"
            rationale = (
                f"Test produced inconsistent outcomes (both PASSED and FAILED) on identical commit "
                f"SHA(s): {', '.join(inconsistent_commits[:3])}. Recommending quarantine to avoid false alarms."
            )
        elif 0.10 <= pass_rate <= 0.90:
            is_flaky = True
            recommendation = "quarantine"
            rationale = (
                f"High outcome variance ({variance}) with pass rate {pass_rate:.1%} indicates an "
                f"unstable race condition or timing variance. Quarantine recommended."
            )
        elif failure_rate == 1.0:
            is_flaky = False
            recommendation = "patch"
            rationale = (
                f"Test consistently fails (0/{total_runs} passed across commits). "
                f"Consistent regression indicates a true code defect suitable for automated patching."
            )
        else:
            is_flaky = False
            recommendation = "stable"
            rationale = f"Test demonstrates consistent stability with {pass_rate:.1%} pass rate."

        return FlakinessReport(
            test_identifier=test_identifier,
            is_flaky=is_flaky,
            pass_rate=round(pass_rate, 4),
            failure_rate=round(failure_rate, 4),
            variance=variance,
            sample_size=total_runs,
            recommendation=recommendation,
            rationale=rationale,
            runs=[asdict(r) for r in execution_records],
        )


# Global flakiness analyzer instance
flakiness_analyzer = FlakinessAnalyzer()
