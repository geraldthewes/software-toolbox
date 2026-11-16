#!/usr/bin/env python3
"""Resolve where a repository's design index is stored.

The in-repo file remains the index until this user chooses user-level
storage. That choice is a marker under the config home, keyed by the
origin remote, so every worktree of that remote shares one index.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

_SEGMENT = re.compile(r"^[a-z0-9._-]+$")
_SCP = re.compile(r"^(?:[^@\s]+@)?(?P<host>[^:@/\s]+):(?P<path>.+)$")
_USER_MARKER = b"user\n"
_REPO_MARKER = b"repo\n"


class DesignIndexError(Exception):
    """A located failure the command should print and exit with."""

    def __init__(self, message: str, code: int) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class Resolved:
    """Paths for one worktree. The marker has not been read yet."""

    root: Path
    origin: str
    repo_index: Path
    user_index: Path | None
    location_file: Path | None


@dataclass(frozen=True)
class Location:
    """The index the skills must use for one worktree."""

    mode: str
    origin: str
    root: Path
    index: Path
    index_exists: bool
    repo_index: Path
    user_index: Path | None
    location_file: Path | None


def parse_origin(url: str) -> str | None:
    """Return the lowercased ``host/path`` id for a supported origin URL.

    Userinfo and the port are discarded. One trailing ``.git`` is removed.
    An unsupported URL returns ``None`` so a token cannot land in a path.
    """
    host, path = _split_origin(url.strip())
    if host is None or path is None:
        return None
    trimmed = path.rstrip("/")
    if trimmed.lower().endswith(".git"):
        trimmed = trimmed[: -len(".git")]
    trimmed = trimmed.strip("/")
    if not trimmed:
        return None
    segments = [host.lower(), *(part.lower() for part in trimmed.split("/"))]
    if any(not _valid_segment(part) for part in segments):
        return None
    return "/".join(segments)


def config_home() -> Path:
    """Return the absolute config home, treating an empty XDG value as unset."""
    raw = os.environ.get("XDG_CONFIG_HOME")
    if raw is None or raw == "":
        base = Path.home() / ".config"
    else:
        base = Path(raw).expanduser()
    return base.resolve()


def resolve(repo: Path) -> Resolved:
    """Resolve the worktree, origin id, and both index paths."""
    root = _worktree_root(repo)
    origin = _origin_id(root)
    repo_index = root / "knowledge" / "designs" / "index.yaml"
    if origin is None:
        return Resolved(root, "", repo_index, None, None)
    directory = _origin_directory(origin)
    return Resolved(
        root,
        origin,
        repo_index,
        directory / "designs" / "index.yaml",
        directory / "design-index-location",
    )


def locate(repo: Path) -> Location:
    """Return the active index. A bad marker is an error, not a guess."""
    resolved = resolve(repo)
    if resolved.location_file is None or resolved.user_index is None:
        index = resolved.repo_index
        mode = "repo"
    else:
        mode = _marker_mode(resolved.location_file)
        index = resolved.user_index if mode == "user" else resolved.repo_index
    return Location(
        mode=mode,
        origin=resolved.origin,
        root=resolved.root,
        index=index,
        index_exists=index.is_file(),
        repo_index=resolved.repo_index,
        user_index=resolved.user_index,
        location_file=resolved.location_file,
    )


def choose(repo: Path, mode: str) -> None:
    """Record ``user`` or ``repo``. Do not create or edit either index."""
    if mode not in {"user", "repo"}:
        raise DesignIndexError(f"unknown design index location: {mode}", 1)
    resolved = resolve(repo)
    if resolved.location_file is None:
        if _origin_url(resolved.root) is None:
            raise DesignIndexError("user-level storage needs an origin remote", 1)
        raise DesignIndexError("unsupported origin remote", 1)
    resolved.location_file.parent.mkdir(parents=True, exist_ok=True)
    payload = _USER_MARKER if mode == "user" else _REPO_MARKER
    resolved.location_file.write_bytes(payload)


def write_index(repo: Path, body: bytes) -> None:
    """Write the index body to the active location and nowhere else."""
    location = locate(repo)
    if location.mode == "user":
        if location.user_index is None:
            raise DesignIndexError("user-level storage needs an origin remote", 1)
        destination = location.user_index
        if _is_inside(destination, location.root):
            raise DesignIndexError(
                "refusing to write the user index inside the worktree",
                1,
            )
    else:
        destination = location.repo_index
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(body)


def format_status(location: Location) -> str:
    """Render status as ``key=value`` lines."""
    rows = (
        ("mode", location.mode),
        ("origin", location.origin),
        ("root", str(location.root)),
        ("index", str(location.index)),
        ("index_exists", "true" if location.index_exists else "false"),
        ("repo_index", str(location.repo_index)),
        ("user_index", "" if location.user_index is None else str(location.user_index)),
        (
            "location_file",
            "" if location.location_file is None else str(location.location_file),
        ),
    )
    return "".join(f"{key}={value}\n" for key, value in rows)


def main(argv: list[str] | None = None) -> int:
    """Run a status, choose, or write command."""
    parser = argparse.ArgumentParser(prog="design_index.py")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--repo", default=".")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status", parents=[common])
    choose_command = commands.add_parser("choose", parents=[common])
    choose_command.add_argument("mode", choices=("user", "repo"))
    commands.add_parser("write", parents=[common])
    args = parser.parse_args(argv)
    try:
        repo = Path(args.repo)
        if args.command == "status":
            sys.stdout.write(format_status(locate(repo)))
        elif args.command == "choose":
            choose(repo, args.mode)
        elif args.command == "write":
            write_index(repo, sys.stdin.buffer.read())
        else:
            parser.error(f"unknown command: {args.command}")
    except DesignIndexError as error:
        print(error, file=sys.stderr)
        return error.code
    return 0


def _split_origin(url: str) -> tuple[str | None, str | None]:
    if not url or any(character.isspace() for character in url):
        return None, None
    if "://" in url:
        parsed = urlparse(url)
        if not parsed.hostname:
            return None, None
        return parsed.hostname, parsed.path
    matched = _SCP.fullmatch(url)
    if matched is None:
        return None, None
    return matched.group("host"), matched.group("path")


def _valid_segment(segment: str) -> bool:
    if segment in {".", ".."}:
        return False
    return _SEGMENT.fullmatch(segment) is not None


def _worktree_root(repo: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--show-toplevel"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or f"not a git worktree: {repo}"
        raise DesignIndexError(detail, 2)
    toplevel = result.stdout.strip()
    if not toplevel:
        raise DesignIndexError(f"not a git worktree: {repo}", 2)
    return Path(toplevel)


def _origin_url(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(root), "remote", "get-url", "origin"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    url = result.stdout.strip()
    return url or None


def _origin_id(root: Path) -> str | None:
    url = _origin_url(root)
    if url is None:
        return None
    return parse_origin(url)


def _origin_directory(origin: str) -> Path:
    directory = config_home() / "software-toolbox" / "repositories"
    for segment in origin.split("/"):
        if not _valid_segment(segment):
            raise DesignIndexError("invalid origin id", 1)
        directory = directory / segment
    return directory


def _marker_mode(path: Path) -> str:
    # A missing marker means this user has not chosen user-level storage.
    if path.is_symlink() and not path.exists():
        raise DesignIndexError(f"invalid design index location: {path}", 1)
    if not path.exists():
        return "repo"
    if not path.is_file():
        raise DesignIndexError(f"invalid design index location: {path}", 1)
    data = path.read_bytes()
    if data == _USER_MARKER:
        return "user"
    if data == _REPO_MARKER:
        return "repo"
    raise DesignIndexError(f"invalid design index location: {path}", 1)


def _is_inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


if __name__ == "__main__":
    sys.exit(main())
