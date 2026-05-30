"""Tests for the _Workspace helper in mtp.cli.tui_harness_tools."""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

import pytest
from mtp.cli.tui_harness_tools import _Workspace, _TEXT_EXTENSIONS, _DEFAULT_IGNORES


# ── resolve() ─────────────────────────────────────────────────────

class TestWorkspaceResolve:
    def test_resolve_root(self, tmp_path: pathlib.Path):
        ws = _Workspace(tmp_path)
        assert ws.resolve(".") == tmp_path

    def test_resolve_subdir(self, tmp_path: pathlib.Path):
        sub = tmp_path / "sub"
        sub.mkdir()
        ws = _Workspace(tmp_path)
        assert ws.resolve("sub") == sub

    def test_resolve_nested(self, tmp_path: pathlib.Path):
        deep = tmp_path / "a" / "b" / "c"
        deep.mkdir(parents=True)
        ws = _Workspace(tmp_path)
        assert ws.resolve("a/b/c") == deep

    def test_resolve_escape_raises(self, tmp_path: pathlib.Path):
        ws = _Workspace(tmp_path)
        with pytest.raises(ValueError, match="escapes workspace"):
            ws.resolve("../../..")

    def test_resolve_nonexistent_path(self, tmp_path: pathlib.Path):
        ws = _Workspace(tmp_path)
        # Should still resolve (strict=False)
        result = ws.resolve("does_not_exist")
        assert result == tmp_path / "does_not_exist"


# ── rel() ─────────────────────────────────────────────────────────

class TestWorkspaceRel:
    def test_rel_root(self, tmp_path: pathlib.Path):
        ws = _Workspace(tmp_path)
        assert ws.rel(tmp_path) == "."

    def test_rel_subdir(self, tmp_path: pathlib.Path):
        sub = tmp_path / "sub"
        sub.mkdir()
        ws = _Workspace(tmp_path)
        assert ws.rel(sub) == "sub"

    def test_rel_nested(self, tmp_path: pathlib.Path):
        deep = tmp_path / "a" / "b"
        deep.mkdir(parents=True)
        ws = _Workspace(tmp_path)
        assert ws.rel(deep) == "a/b"


# ── is_ignored() ──────────────────────────────────────────────────

class TestWorkspaceIsIgnored:
    def test_git_dir_ignored(self, tmp_path: pathlib.Path):
        ws = _Workspace(tmp_path)
        p = tmp_path / ".git" / "config"
        assert ws.is_ignored(p) is True

    def test_node_modules_ignored(self, tmp_path: pathlib.Path):
        ws = _Workspace(tmp_path)
        p = tmp_path / "node_modules" / "pkg" / "index.js"
        assert ws.is_ignored(p) is True

    def test_pycache_ignored(self, tmp_path: pathlib.Path):
        ws = _Workspace(tmp_path)
        p = tmp_path / "__pycache__" / "mod.cpython-312.pyc"
        assert ws.is_ignored(p) is True

    def test_normal_file_not_ignored(self, tmp_path: pathlib.Path):
        ws = _Workspace(tmp_path)
        p = tmp_path / "src" / "main.py"
        assert ws.is_ignored(p) is False

    def test_all_default_ignores(self, tmp_path: pathlib.Path):
        ws = _Workspace(tmp_path)
        for name in _DEFAULT_IGNORES:
            p = tmp_path / name / "file.txt"
            assert ws.is_ignored(p) is True, f"{name} should be ignored"


# ── root_entries() ────────────────────────────────────────────────

class TestWorkspaceRootEntries:
    def test_empty_dir(self, tmp_path: pathlib.Path):
        ws = _Workspace(tmp_path)
        assert ws.root_entries() == []

    def test_files_and_dirs(self, tmp_path: pathlib.Path):
        (tmp_path / "file.txt").write_text("x")
        (tmp_path / "dir").mkdir()
        ws = _Workspace(tmp_path)
        entries = ws.root_entries()
        names = [e["name"] for e in entries]
        assert "file.txt" in names
        assert "dir" in names

    def test_dirs_before_files(self, tmp_path: pathlib.Path):
        (tmp_path / "zz_file.txt").write_text("x")
        (tmp_path / "aa_dir").mkdir()
        ws = _Workspace(tmp_path)
        entries = ws.root_entries()
        # Directories should come before files
        types = [e["type"] for e in entries]
        first_file_idx = types.index("file")
        first_dir_idx = types.index("directory")
        assert first_dir_idx < first_file_idx

    def test_sorted_alphabetically(self, tmp_path: pathlib.Path):
        (tmp_path / "c.txt").write_text("x")
        (tmp_path / "a.txt").write_text("x")
        (tmp_path / "b.txt").write_text("x")
        ws = _Workspace(tmp_path)
        entries = ws.root_entries()
        names = [e["name"] for e in entries]
        assert names == sorted(names, key=str.lower)


# ── text_files() ──────────────────────────────────────────────────

class TestWorkspaceTextFiles:
    def test_finds_python_files(self, tmp_path: pathlib.Path):
        (tmp_path / "main.py").write_text("print('hi')")
        (tmp_path / "lib.js").write_text("console.log('hi')")
        ws = _Workspace(tmp_path)
        files = ws.text_files()
        names = [f.name for f in files]
        assert "main.py" in names
        assert "lib.js" in names

    def test_ignores_binary_extensions(self, tmp_path: pathlib.Path):
        (tmp_path / "image.png").write_bytes(b"\x89PNG")
        (tmp_path / "code.py").write_text("x=1")
        ws = _Workspace(tmp_path)
        files = ws.text_files()
        names = [f.name for f in files]
        assert "code.py" in names
        assert "image.png" not in names

    def test_ignores_ignored_dirs(self, tmp_path: pathlib.Path):
        (tmp_path / "__pycache__" / "mod.py").parent.mkdir()
        (tmp_path / "__pycache__" / "mod.py").write_text("x")
        (tmp_path / "real.py").write_text("x")
        ws = _Workspace(tmp_path)
        files = ws.text_files()
        names = [f.name for f in files]
        assert "real.py" in names
        assert "mod.py" not in names

    def test_single_file(self, tmp_path: pathlib.Path):
        f = tmp_path / "test.py"
        f.write_text("x=1")
        ws = _Workspace(tmp_path)
        files = ws.text_files("test.py")
        assert len(files) == 1
        assert files[0] == f

    def test_subdirectory(self, tmp_path: pathlib.Path):
        sub = tmp_path / "src"
        sub.mkdir()
        (sub / "a.py").write_text("a")
        (sub / "b.py").write_text("b")
        ws = _Workspace(tmp_path)
        files = ws.text_files("src")
        names = [f.name for f in files]
        assert "a.py" in names
        assert "b.py" in names

    def test_all_text_extensions_present(self):
        """Verify _TEXT_EXTENSIONS contains common file types."""
        assert ".py" in _TEXT_EXTENSIONS
        assert ".js" in _TEXT_EXTENSIONS
        assert ".ts" in _TEXT_EXTENSIONS
        assert ".json" in _TEXT_EXTENSIONS
        assert ".md" in _TEXT_EXTENSIONS
        assert ".html" in _TEXT_EXTENSIONS
        assert ".css" in _TEXT_EXTENSIONS
        assert ".yaml" in _TEXT_EXTENSIONS
        assert ".sh" in _TEXT_EXTENSIONS
