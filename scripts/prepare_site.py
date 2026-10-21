#!/usr/bin/env python3
# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Build committed source and prepare a local site branch. Never push."""
import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile


def run(*args, cwd, env=None, capture=True):
    result = subprocess.run(args, cwd=cwd, env=env, check=True, text=True,
                            stdout=subprocess.PIPE if capture else None)
    return result.stdout.strip() if capture else None


def git(repo, *args, **kwargs):
    return run("git", *args, cwd=repo, **kwargs)


def site_tip(repo):
    result = subprocess.run(["git", "rev-parse", "--verify", "--quiet", "refs/heads/site"],
                            cwd=repo, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode == 1:
        return None
    result.check_returncode()
    return result.stdout.strip()


def check_worktrees(repo):
    listing = git(repo, "worktree", "list", "--porcelain")
    if "branch refs/heads/site" in listing.splitlines():
        raise ValueError("site is checked out in a worktree. Switch that worktree to another branch first.")


def build(repo, revision):
    flake = "git+" + repo.as_uri() + "?rev=" + revision
    run("nix", "flake", "check", "--no-write-lock-file", flake, cwd=repo, capture=False)
    outputs = json.loads(run("nix", "build", "--no-write-lock-file", "--no-link", "--json",
                             flake + "#site", cwd=repo))
    return Path(outputs[0]["outputs"]["out"])


def prepare(repo, source_ref="main", builder=build):
    repo = Path(git(repo, "rev-parse", "--show-toplevel")).resolve()
    if git(repo, "status", "--porcelain", "--untracked-files=normal"):
        raise ValueError("Commit or stash source changes first; preparation requires a clean checkout.")
    revision = git(repo, "rev-parse", "--verify", "--end-of-options", source_ref + "^{commit}")
    if source_ref == "site" or source_ref == "refs/heads/site":
        raise ValueError("site is generated output, not a source branch.")
    check_worktrees(repo)
    previous = site_tip(repo)
    if previous:
        # Existing branches must already be publications, not source history.
        git(repo, "cat-file", "-e", previous + ":publication.json")
    elif subprocess.run(["git", "show-ref", "--verify", "--quiet", "refs/remotes/origin/site"],
                        cwd=repo).returncode == 0:
        raise ValueError("origin/site exists. Run git branch --track site origin/site to preserve its history.")
    # Verify identity before an expensive build.
    git(repo, "var", "GIT_AUTHOR_IDENT")
    git(repo, "var", "GIT_COMMITTER_IDENT")
    print(f"Building committed {source_ref} at {revision}.", flush=True)
    artifact = builder(repo, revision).resolve()
    if not (artifact / "index.html").is_file():
        raise ValueError("The site build is missing index.html.")
    if (artifact / ".git").exists():
        raise ValueError("The site artifact must not contain Git metadata.")
    with tempfile.TemporaryDirectory(prefix="ontology-site-") as temporary:
        temporary = Path(temporary)
        content = temporary / "content"
        shutil.copytree(artifact, content)
        # Nix store directories are read-only; allow the provenance sidecar.
        content.chmod(content.stat().st_mode | stat.S_IWUSR)
        (content / "publication.json").write_text(json.dumps({"source_commit": revision}, indent=2) + "\n")
        # A private index builds a fresh tree, removing stale files without
        # touching the user's checkout, index or any existing worktree.
        environment = os.environ.copy()
        environment.update(GIT_DIR=git(repo, "rev-parse", "--absolute-git-dir"),
                           GIT_WORK_TREE=str(content), GIT_INDEX_FILE=str(temporary / "index"))
        git(content, "read-tree", "--empty", env=environment)
        git(content, "-c", "core.autocrlf=false", "-c", "core.attributesFile=/dev/null",
            "add", "--all", "--force", ".", env=environment)
        tree = git(content, "write-tree", env=environment)
        if previous and tree == git(repo, "rev-parse", previous + "^{tree}"):
            print(f"site already contains the publication of {revision}. Nothing changed.")
            return previous
        parent = ["-p", previous] if previous else []
        publication = git(repo, "commit-tree", tree, *parent, "-m", "Build site from " + revision)
        check_worktrees(repo)
        # Compare-and-swap: refuse to overwrite a publication made during build.
        git(repo, "update-ref", "-m", "Prepare static site", "refs/heads/site", publication,
            previous or "0" * len(revision))
    print(f"Prepared local site commit {publication}. Nothing pushed.")
    print("Review: git log -1 site; git diff site~ site (after the first publication)")
    print("Publish separately: git push origin site")
    return publication


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-ref", default="main",
                        help="Committed source to build (default: local main); use HEAD for a candidate")
    args = parser.parse_args()
    try:
        prepare(Path.cwd(), source_ref=args.source_ref)
    except (ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Site preparation failed: {error}\n")


if __name__ == "__main__":
    main()
