#!/usr/bin/env python3
"""Self-test for ./llmwiki/setup.py target-directory resolution.

Run directly: `python3 tests/test_setup.py` (no framework needed). Exits 0 when
all assertions pass, non-zero otherwise — this is what CI runs.

The regression under test: setup.py resolves its target from the engine's own
location, never from the current working directory. update.md's upgrade flow
told readers to cd into a scratch directory and run the workspace's setup.py to
generate throwaway templates for diffing — which instead wrote a fresh skeleton
straight into the live workspace. --root is what makes that flow expressible.
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SETUP = os.path.join(HERE, "..", "setup.py")


def run(cwd, *flags):
    return subprocess.run(
        [sys.executable, SETUP, *flags],
        capture_output=True, text=True, cwd=cwd,
    )


def install_engine(workspace):
    """Lay out a workspace the way a real install does: engine in llmwiki/."""
    engine = os.path.join(workspace, "llmwiki")
    os.makedirs(engine, exist_ok=True)
    shutil.copy2(SETUP, os.path.join(engine, "setup.py"))
    return os.path.join(engine, "setup.py")


def main():
    # --root generates into the directory it names, and leaves the engine's own
    # workspace untouched. This is the case update.md depends on.
    with tempfile.TemporaryDirectory() as tmp:
        workspace = os.path.join(tmp, "workspace")
        scratch = os.path.join(tmp, "scratch")
        os.makedirs(scratch)
        engine_setup = install_engine(workspace)

        r = subprocess.run(
            [sys.executable, engine_setup, "--name", "Scratch", "--root", scratch],
            capture_output=True, text=True, cwd=tmp,
        )
        assert r.returncode == 0, f"--root run should succeed:\n{r.stdout}\n{r.stderr}"
        assert os.path.isfile(os.path.join(scratch, "index.html")), \
            f"--root should generate into the named directory:\n{r.stdout}"
        assert os.path.isdir(os.path.join(scratch, "wiki")), \
            "--root should generate the wiki/ skeleton into the named directory"
        assert not os.path.exists(os.path.join(workspace, "index.html")), \
            "--root must not write into the engine's own workspace"

    # Without --root the target is the engine's parent, whatever the cwd is.
    # Running from an unrelated directory must not generate anything there.
    with tempfile.TemporaryDirectory() as tmp:
        workspace = os.path.join(tmp, "workspace")
        elsewhere = os.path.join(tmp, "elsewhere")
        os.makedirs(elsewhere)
        engine_setup = install_engine(workspace)

        r = subprocess.run(
            [sys.executable, engine_setup, "--name", "Workspace"],
            capture_output=True, text=True, cwd=elsewhere,
        )
        assert r.returncode == 0, f"default run should succeed:\n{r.stdout}\n{r.stderr}"
        assert os.path.isfile(os.path.join(workspace, "index.html")), \
            "default target should be the engine's parent directory"
        assert not os.path.exists(os.path.join(elsewhere, "index.html")), \
            "the current working directory is not a target and must stay empty"

    # An explicit --root that does not exist yet is created rather than refused.
    with tempfile.TemporaryDirectory() as tmp:
        workspace = os.path.join(tmp, "workspace")
        fresh = os.path.join(tmp, "does-not-exist-yet")
        engine_setup = install_engine(workspace)

        r = subprocess.run(
            [sys.executable, engine_setup, "--root", fresh],
            capture_output=True, text=True, cwd=tmp,
        )
        assert r.returncode == 0, f"--root on a missing dir should succeed:\n{r.stdout}\n{r.stderr}"
        assert os.path.isfile(os.path.join(fresh, "index.html")), \
            "--root should create the target directory when it is missing"

    print("✓ setup.py target-directory tests passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
