#!/usr/bin/env python3
"""Tests for scripts/design_index.py."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "design_index.py"
sys.path.insert(0, str(ROOT / "scripts"))
import design_index  # noqa: E402


class ParseOriginTest(unittest.TestCase):
    def test_accepted_urls_map_to_one_id(self) -> None:
        cases = {
            "git@github.com:Acme/App.git": "github.com/acme/app",
            "git@GitHub.com:Acme/App.git": "github.com/acme/app",
            "ssh://git@github.com/Acme/App.git": "github.com/acme/app",
            "ssh://git@github.com:2222/Acme/App.git": "github.com/acme/app",
            "https://github.com/Acme/App.git": "github.com/acme/app",
            "https://GitHub.com/Acme/App.git": "github.com/acme/app",
            "https://github.com/Acme/App.git/": "github.com/acme/app",
            "https://user:token@github.com/Acme/App.git": "github.com/acme/app",
            "https://gitlab.com/Group/Sub/Repo.git": "gitlab.com/group/sub/repo",
            "https://github.com/acme/app.git.git": "github.com/acme/app.git",
        }
        for url, expected in cases.items():
            with self.subTest(url=url):
                origin = design_index.parse_origin(url)
                self.assertEqual(origin, expected)
                self.assertNotIn("token", origin or "")

    def test_rejected_urls(self) -> None:
        rejected = [
            "",
            "https://github.com",
            "https://github.com/.git",
            "file:///srv/git/repo.git",
            "/srv/git/repo.git",
            "git@github.com:acme/../../etc/passwd",
            "https://github.com/acme/app/../secret",
            "https://github.com/acme/bad segment",
            "https://github.com/acme//app",
            "https://github.com/acme/./app",
            "git@github.com:acme/foo/../bar.git",
        ]
        for url in rejected:
            with self.subTest(url=url):
                self.assertIsNone(design_index.parse_origin(url))


class DesignIndexCliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / "home"
        self.xdg = self.root / "xdg"
        self.home.mkdir()
        self.xdg.mkdir()
        self.env = self._environment(self.home, self.xdg)

    def test_missing_marker_uses_the_in_repo_index(self) -> None:
        repo = self.make_repo("repo")
        status = self.status(repo)
        self.assertEqual(status["mode"], "repo")
        self.assertEqual(status["origin"], "github.com/acme/app")
        self.assertEqual(Path(status["root"]), repo.resolve())
        self.assertEqual(status["index"], status["repo_index"])
        self.assertEqual(status["index_exists"], "false")
        self.assertTrue(status["user_index"])
        self.assertTrue(status["location_file"])
        self.assertFalse(Path(status["location_file"]).exists())
        self.assertFalse((repo / "knowledge").exists())
        self.assertFalse((self.xdg / "software-toolbox").exists())

    def test_choose_writes_only_the_marker(self) -> None:
        repo = self.make_repo("repo")
        for mode in ("repo", "user"):
            with self.subTest(mode=mode):
                self.assertEqual(self.invoke(repo, "choose", mode).returncode, 0)
                status = self.status(repo)
                self.assertEqual(status["mode"], mode)
                marker = Path(status["location_file"])
                self.assertEqual(marker.read_bytes(), f"{mode}\n".encode())
                self.assertFalse(Path(status["user_index"]).exists())
                self.assertFalse(Path(status["user_index"]).parent.exists())
                self.assertFalse((repo / "knowledge").exists())

    def test_choose_user_without_origin_writes_nothing(self) -> None:
        repo = self.make_repo("repo", origin=None)
        result = self.invoke(repo, "choose", "user")
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"origin remote", result.stderr)
        self.assertEqual(result.stdout, b"")
        self.assertFalse((self.xdg / "software-toolbox").exists())
        self.assertFalse((repo / "knowledge").exists())

    def test_choose_user_rejects_an_unsupported_origin_without_echoing_it(self) -> None:
        repo = self.make_repo(
            "repo", origin="https://user:secret@github.com/acme/../x.git"
        )
        result = self.invoke(repo, "choose", "user")
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"unsupported origin remote", result.stderr)
        self.assertNotIn(b"secret", result.stderr)
        self.assertNotIn(b"secret", result.stdout)
        self.assertFalse((self.xdg / "software-toolbox").exists())

    def test_status_hides_credentials_in_the_origin_url(self) -> None:
        repo = self.make_repo(
            "repo",
            origin="https://user:token@github.com/Acme/App.git",
        )
        result = self.invoke(repo, "status")
        self.assertEqual(result.returncode, 0)
        self.assertNotIn(b"token", result.stdout)
        self.assertEqual(self.status(repo)["origin"], "github.com/acme/app")

    def test_write_in_repo_mode_creates_only_the_in_repo_index(self) -> None:
        repo = self.make_repo("repo")
        body = b"version: 1\ndocuments: []\n"
        self.assertEqual(self.invoke(repo, "choose", "repo").returncode, 0)
        result = self.invoke(repo, "write", stdin=body)
        self.assertEqual(result.returncode, 0)
        status = self.status(repo)
        self.assertEqual(status["mode"], "repo")
        self.assertEqual(status["index_exists"], "true")
        self.assertEqual(Path(status["repo_index"]).read_bytes(), body)
        self.assertFalse(Path(status["user_index"]).exists())
        self.assertFalse(Path(status["user_index"]).parent.exists())

    def test_write_in_user_mode_leaves_the_in_repo_index_unchanged(self) -> None:
        repo = self.make_repo("repo")
        repo_index = repo / "knowledge" / "designs" / "index.yaml"
        repo_index.parent.mkdir(parents=True)
        repo_index.write_bytes(b"original\n")
        self.assertEqual(self.invoke(repo, "choose", "user").returncode, 0)
        before = self.status(repo)
        self.assertEqual(before["index_exists"], "false")
        self.assertNotEqual(before["index"], before["repo_index"])
        self.assertFalse(Path(before["user_index"]).exists())
        result = self.invoke(repo, "write", stdin=b"user-body\n")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(repo_index.read_bytes(), b"original\n")
        self.assertEqual(Path(before["user_index"]).read_bytes(), b"user-body\n")

    def test_user_mode_without_an_index_does_not_create_the_in_repo_file(self) -> None:
        repo = self.make_repo("repo")
        self.assertEqual(self.invoke(repo, "choose", "user").returncode, 0)
        status = self.status(repo)
        self.assertEqual(status["mode"], "user")
        self.assertEqual(status["index_exists"], "false")
        self.assertFalse((repo / "knowledge").exists())
        self.assertFalse(Path(status["user_index"]).exists())

    def test_worktrees_share_the_user_index(self) -> None:
        repo = self.make_repo("main")
        self.commit_readme(repo)
        other = self.root / "other"
        self.git(repo, "worktree", "add", "--detach", str(other))
        self.git(repo, "checkout", "-b", "feature")
        self.assertEqual(self.invoke(repo, "choose", "user").returncode, 0)
        main_status = self.status(repo)
        other_status = self.status(other)
        self.assertEqual(main_status["user_index"], other_status["user_index"])
        self.assertNotEqual(main_status["root"], other_status["root"])
        self.assertEqual(main_status["origin"], other_status["origin"])

    def test_another_clone_with_the_same_origin_shares_the_user_index(self) -> None:
        first = self.make_repo("first")
        second = self.make_repo("second")
        self.assertEqual(self.invoke(first, "choose", "user").returncode, 0)
        first_status = self.status(first)
        second_status = self.status(second)
        self.assertEqual(first_status["user_index"], second_status["user_index"])
        self.assertEqual(second_status["mode"], "user")
        self.assertNotEqual(first_status["root"], second_status["root"])

    def test_a_different_origin_gets_a_different_user_index(self) -> None:
        first = self.make_repo("first", origin="git@github.com:Acme/App.git")
        second = self.make_repo("second", origin="git@github.com:Acme/Other.git")
        self.assertNotEqual(
            self.status(first)["user_index"], self.status(second)["user_index"]
        )

    def test_two_config_homes_stay_independent(self) -> None:
        repo = self.make_repo("repo")
        other_xdg = self.root / "other-xdg"
        other_xdg.mkdir()
        other_env = self._environment(self.home, other_xdg)
        self.assertEqual(self.invoke(repo, "choose", "user").returncode, 0)
        self.assertEqual(self.invoke(repo, "write", stdin=b"alice\n").returncode, 0)
        alice = self.status(repo)
        bob = self.parse_status(
            self.invoke(repo, "status", env=other_env).stdout.decode()
        )
        self.assertNotEqual(alice["user_index"], bob["user_index"])
        self.assertEqual(alice["index_exists"], "true")
        self.assertEqual(bob["mode"], "repo")
        self.assertEqual(bob["index_exists"], "false")
        self.assertFalse(Path(bob["user_index"]).exists())
        self.assertEqual(Path(alice["user_index"]).read_bytes(), b"alice\n")

    def test_empty_and_unset_xdg_use_home_config(self) -> None:
        repo = self.make_repo("repo")
        for label, mutate in (
            ("empty", lambda env: env.__setitem__("XDG_CONFIG_HOME", "")),
            ("unset", lambda env: env.pop("XDG_CONFIG_HOME", None)),
        ):
            with self.subTest(label=label):
                env = self._environment(self.home, self.xdg)
                mutate(env)
                result = self.invoke(repo, "choose", "user", env=env)
                self.assertEqual(result.returncode, 0, result.stderr.decode())
                status = self.parse_status(
                    self.invoke(repo, "status", env=env).stdout.decode()
                )
                marker = Path(status["location_file"])
                self.assertTrue(marker.is_relative_to(self.home / ".config"))
                self.assertFalse(marker.is_relative_to(self.xdg))

    def test_bad_marker_is_an_error_and_writes_nothing(self) -> None:
        repo = self.make_repo("repo")
        before = self.status(repo)
        marker = Path(before["location_file"])
        marker.parent.mkdir(parents=True)
        marker.write_bytes(b"user")
        result = self.invoke(repo, "status")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"invalid design index location", result.stderr)
        self.assertEqual(marker.read_bytes(), b"user")
        self.assertFalse(Path(before["user_index"]).exists())
        self.assertFalse((repo / "knowledge").exists())
        write = self.invoke(repo, "write", stdin=b"nope\n")
        self.assertEqual(write.returncode, 1)
        self.assertFalse(Path(before["user_index"]).exists())
        self.assertFalse((repo / "knowledge").exists())

    def test_write_refuses_a_user_index_inside_the_worktree(self) -> None:
        repo = self.make_repo("repo")
        env = self._environment(self.home, repo / "xdg")
        self.assertEqual(self.invoke(repo, "choose", "user", env=env).returncode, 0)
        result = self.invoke(repo, "write", stdin=b"inside\n", env=env)
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"inside the worktree", result.stderr)
        status = self.parse_status(self.invoke(repo, "status", env=env).stdout.decode())
        self.assertFalse(Path(status["user_index"]).exists())
        self.assertFalse((repo / "knowledge").exists())

    def test_switching_to_repo_leaves_the_user_index_in_place(self) -> None:
        repo = self.make_repo("repo")
        self.assertEqual(self.invoke(repo, "choose", "user").returncode, 0)
        self.assertEqual(self.invoke(repo, "write", stdin=b"user-body\n").returncode, 0)
        user_index = Path(self.status(repo)["user_index"])
        self.assertEqual(self.invoke(repo, "choose", "repo").returncode, 0)
        self.assertEqual(self.invoke(repo, "write", stdin=b"repo-body\n").returncode, 0)
        self.assertEqual(user_index.read_bytes(), b"user-body\n")
        self.assertEqual(
            (repo / "knowledge" / "designs" / "index.yaml").read_bytes(), b"repo-body\n"
        )

    def test_not_a_worktree_exits_2(self) -> None:
        missing = self.root / "missing"
        missing.mkdir()
        result = self.invoke(missing, "status")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b"")
        self.assertTrue(result.stderr.strip())

    def make_repo(
        self, name: str, origin: str | None = "git@github.com:Acme/App.git"
    ) -> Path:
        repo = self.root / name
        self.git_raw("init", "-b", "main", str(repo))
        if origin is not None:
            self.git(repo, "remote", "add", "origin", origin)
        return repo.resolve()

    def commit_readme(self, repo: Path) -> None:
        (repo / "README").write_text("init\n")
        self.git(repo, "add", "README")
        self.git(
            repo,
            "-c",
            "user.name=Test",
            "-c",
            "user.email=test@example.com",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-m",
            "init",
        )

    def status(self, repo: Path) -> dict[str, str]:
        result = self.invoke(repo, "status")
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        return self.parse_status(result.stdout.decode())

    def invoke(
        self,
        repo: Path,
        *args: str,
        stdin: bytes = b"",
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--repo", str(repo)],
            input=stdin,
            capture_output=True,
            env=env or self.env,
            check=False,
        )

    def git(self, repo: Path, *args: str) -> None:
        self.git_raw("-C", str(repo), *args)

    def git_raw(self, *args: str) -> None:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            env=self.env,
            check=False,
        )
        if result.returncode != 0:
            raise AssertionError(result.stderr.decode())

    @staticmethod
    def parse_status(output: str) -> dict[str, str]:
        rows: dict[str, str] = {}
        for line in output.splitlines():
            key, value = line.split("=", 1)
            rows[key] = value
        return rows

    @staticmethod
    def _environment(home: Path, xdg: Path) -> dict[str, str]:
        env = os.environ.copy()
        for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_CONFIG_COUNT"):
            env.pop(name, None)
        env["HOME"] = str(home)
        env["XDG_CONFIG_HOME"] = str(xdg)
        env["GIT_CONFIG_NOSYSTEM"] = "1"
        env["GIT_CONFIG_GLOBAL"] = str(home / ".gitconfig")
        env["GIT_AUTHOR_NAME"] = "Test"
        env["GIT_AUTHOR_EMAIL"] = "test@example.com"
        env["GIT_COMMITTER_NAME"] = "Test"
        env["GIT_COMMITTER_EMAIL"] = "test@example.com"
        (home / ".gitconfig").write_text("")
        return env


if __name__ == "__main__":
    unittest.main()
