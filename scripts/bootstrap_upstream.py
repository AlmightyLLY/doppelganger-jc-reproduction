#!/usr/bin/env python3
"""Install the pinned upstream Doppelganger-JC data layout.

The benchmark data remain governed by the upstream data terms.  This helper
clones the authoritative repository at the commit used in this reproduction
and creates local symlinks expected by the experiment scripts.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_URL = "https://github.com/0017-alt/Doppelganger-JC.git"
UPSTREAM_COMMIT = "eb1c4f3f17403af238046bf218dc49643bc2e2e2"
LINKS = (
    "questions",
    "cognate_fixed",
    "calc_ppl_translation.py",
    "models.txt",
)


def run(*args: str, cwd: Path | None = None) -> str:
    completed = subprocess.run(
        args,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return completed.stdout.strip()


def validate_source(source: Path) -> None:
    if not (source / ".git").exists():
        raise RuntimeError(f"Not a Git checkout: {source}")
    run("git", "cat-file", "-e", f"{UPSTREAM_COMMIT}^{{commit}}", cwd=source)
    changed = subprocess.run(
        [
            "git",
            "diff",
            "--quiet",
            UPSTREAM_COMMIT,
            "--",
            *LINKS,
        ],
        cwd=source,
    ).returncode
    if changed:
        raise RuntimeError(
            "The supplied checkout changes benchmark files relative to the "
            f"pinned commit {UPSTREAM_COMMIT}."
        )
    missing = [name for name in LINKS if not (source / name).exists()]
    if missing:
        raise RuntimeError(f"Upstream checkout is missing: {', '.join(missing)}")


def obtain_default_checkout(destination: Path) -> Path:
    if not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        run("git", "clone", "--no-checkout", UPSTREAM_URL, str(destination))
        run("git", "checkout", "--detach", UPSTREAM_COMMIT, cwd=destination)
    else:
        head = run("git", "rev-parse", "HEAD", cwd=destination)
        if head != UPSTREAM_COMMIT:
            raise RuntimeError(
                f"{destination} is at {head}, not the pinned commit "
                f"{UPSTREAM_COMMIT}. Remove or move it, then run this command again."
            )
    validate_source(destination)
    return destination


def install_links(source: Path) -> None:
    for name in LINKS:
        target = PROJECT_ROOT / name
        expected = source / name
        if target.is_symlink():
            if target.resolve() != expected.resolve():
                raise RuntimeError(f"Existing link points elsewhere: {target}")
            print(f"already linked: {target.relative_to(PROJECT_ROOT)}")
            continue
        if target.exists():
            raise RuntimeError(
                f"Refusing to replace existing path: {target}. Move it first."
            )
        relative_source = Path(os.path.relpath(expected, start=PROJECT_ROOT))
        target.symlink_to(relative_source, target_is_directory=expected.is_dir())
        print(f"linked: {target.relative_to(PROJECT_ROOT)} -> {relative_source}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        help=(
            "Use an existing upstream checkout instead of cloning. Its benchmark "
            "files must match the pinned commit."
        ),
    )
    args = parser.parse_args()

    source = (
        args.source.expanduser().resolve()
        if args.source
        else obtain_default_checkout(PROJECT_ROOT / "external" / "Doppelganger-JC")
    )
    if args.source:
        validate_source(source)
    install_links(source)
    print(f"upstream commit: {UPSTREAM_COMMIT}")
    print("READY: benchmark files are available without copying them into this repository.")


if __name__ == "__main__":
    main()
