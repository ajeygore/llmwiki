#!/usr/bin/env python3
"""Self-test for ./llmwiki/lint using good/bad fixture wikis.

Run directly: `python3 tests/test_lint.py` (no framework needed). Exits 0 when
all assertions pass, non-zero otherwise — this is what CI runs.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LINT = os.path.join(HERE, "..", "lint")


def run(fixture, *flags):
    return subprocess.run(
        [sys.executable, LINT, os.path.join(HERE, fixture), *flags],
        capture_output=True, text=True,
    )


def main():
    # A clean wiki passes even under --strict.
    r = run("fixture_good", "--strict")
    assert r.returncode == 0, f"good fixture should pass --strict:\n{r.stdout}\n{r.stderr}"

    # A wiki with broken links fails (broken links are errors) regardless of --strict.
    r = run("fixture_bad")
    assert r.returncode == 1, f"bad fixture should fail on broken links:\n{r.stdout}"
    assert "BROKEN" in r.stdout, "expected a BROKEN link report"
    assert "missing.md" in r.stdout and "nope.md" in r.stdout, "expected both broken targets"

    # The bad fixture's warnings are also surfaced.
    assert "ORPHAN" in r.stdout, "expected orphan.md flagged"
    assert "NO-FRONTMATTER" in r.stdout, "expected page-a.md flagged for missing frontmatter"
    assert "LOG-FMT" in r.stdout, "expected malformed log entry flagged"

    # A clean wiki with no --strict is also healthy (0 warnings in the good fixture).
    r = run("fixture_good")
    assert r.returncode == 0, f"good fixture should be clean:\n{r.stdout}"

    print("all lint tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
