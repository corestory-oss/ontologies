# Copyright (c) 2026 CoreStory, Inc.
# SPDX-License-Identifier: Apache-2.0
"""Exercise publication against disposable Git repositories, without Nix or hosting."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.prepare_site import git, prepare, site_tip


class PrepareSiteTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "source"
        self.repo.mkdir()
        self.environment = patch.dict(os.environ, {
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
        })
        self.environment.start()
        self.addCleanup(self.environment.stop)
        git(self.repo, "init", "--quiet", "--initial-branch=main")
        git(self.repo, "config", "user.name", "Publication Test")
        git(self.repo, "config", "user.email", "publication@example.invalid")
        (self.repo / "source.txt").write_text("source\n")
        git(self.repo, "add", ".")
        git(self.repo, "commit", "--quiet", "-m", "Source")
        self.revision = git(self.repo, "rev-parse", "HEAD")
        self.artifact = self.root / "artifact"
        self.artifact.mkdir()
        (self.artifact / "index.html").write_text("<h1>Site</h1>\n")
        (self.artifact / "old.txt").write_text("remove me later\n")
        self.calls = []

    def builder(self, repo, revision):
        self.calls.append((repo, revision))
        return self.artifact

    def test_initial_publication_has_only_output_and_provenance(self):
        before = (self.repo / ".git/index").read_bytes()
        commit = prepare(self.repo, builder=self.builder)
        self.assertEqual(self.calls, [(self.repo.resolve(), self.revision)])
        self.assertEqual(git(self.repo, "branch", "--show-current"), "main")
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), self.revision)
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")
        self.assertEqual((self.repo / ".git/index").read_bytes(), before)
        self.assertEqual(set(git(self.repo, "ls-tree", "--name-only", "site").splitlines()),
                         {"index.html", "old.txt", "publication.json"})
        self.assertEqual(json.loads(git(self.repo, "show", "site:publication.json")),
                         {"source_commit": self.revision})
        self.assertEqual(git(self.repo, "rev-list", "--parents", "-n", "1", commit), commit)

    def test_repeated_build_is_noop_and_updates_preserve_history_remove_old_files(self):
        first = prepare(self.repo, builder=self.builder)
        self.assertEqual(prepare(self.repo, builder=self.builder), first)
        (self.artifact / "old.txt").unlink()
        (self.artifact / "index.html").write_text("<h1>Updated</h1>\n")
        second = prepare(self.repo, builder=self.builder)
        self.assertEqual(git(self.repo, "rev-parse", second + "^"), first)
        self.assertNotIn("old.txt", git(self.repo, "ls-tree", "--name-only", "site"))

    def test_read_only_nix_artifact_can_be_prepared(self):
        self.artifact.chmod(0o555)
        self.addCleanup(self.artifact.chmod, 0o755)
        commit = prepare(self.repo, builder=self.builder)
        self.assertEqual(site_tip(self.repo), commit)
        self.assertEqual(git(self.repo, "show", "site:index.html"), "<h1>Site</h1>")

    def test_dirty_source_is_rejected_before_build(self):
        (self.repo / "untracked.txt").write_text("unsaved\n")
        with self.assertRaisesRegex(ValueError, "clean checkout"):
            prepare(self.repo, builder=self.builder)
        self.assertEqual(self.calls, [])
        self.assertIsNone(site_tip(self.repo))

    def test_build_failure_does_not_change_site(self):
        previous = prepare(self.repo, builder=self.builder)
        def failure(*args):
            raise ValueError("Nix check failed")
        with self.assertRaisesRegex(ValueError, "Nix check failed"):
            prepare(self.repo, builder=failure)
        self.assertEqual(site_tip(self.repo), previous)

    def test_checked_out_site_is_rejected(self):
        prepare(self.repo, builder=self.builder)
        git(self.repo, "worktree", "add", "--quiet", str(self.root / "site-worktree"), "site")
        with self.assertRaisesRegex(ValueError, "checked out"):
            prepare(self.repo, builder=self.builder)

    def test_competing_preparation_is_not_overwritten(self):
        previous = prepare(self.repo, builder=self.builder)
        tree = git(self.repo, "rev-parse", previous + "^{tree}")
        competing = git(self.repo, "commit-tree", tree, "-p", previous, "-m", "Competing publication")
        (self.artifact / "index.html").write_text("<h1>Changed</h1>")
        def racing_builder(repo, revision):
            git(repo, "update-ref", "refs/heads/site", competing, previous)
            return self.artifact
        with self.assertRaises(subprocess.CalledProcessError):
            prepare(self.repo, builder=racing_builder)
        self.assertEqual(site_tip(self.repo), competing)

    def test_source_ref_is_resolved_before_build(self):
        git(self.repo, "checkout", "--quiet", "-b", "candidate")
        (self.repo / "source.txt").write_text("candidate\n")
        git(self.repo, "commit", "--quiet", "-am", "Candidate")
        candidate = git(self.repo, "rev-parse", "HEAD")
        prepare(self.repo, source_ref="HEAD", builder=self.builder)
        self.assertEqual(self.calls[-1][1], candidate)
        self.assertEqual(git(self.repo, "branch", "--show-current"), "candidate")

    def test_remote_history_is_not_silently_replaced(self):
        git(self.repo, "update-ref", "refs/remotes/origin/site", self.revision)
        with self.assertRaisesRegex(ValueError, "preserve its history"):
            prepare(self.repo, builder=self.builder)
        self.assertEqual(self.calls, [])


if __name__ == "__main__":
    unittest.main()
