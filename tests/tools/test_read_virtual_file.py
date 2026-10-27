"""Read actual procfs text rather than treating its zero stat size as EOF."""
from pathlib import Path

import pytest

from tools.environments.local import LocalEnvironment
from tools.file_operations import ShellFileOperations

pytestmark = pytest.mark.platforms("linux")


def test_zero_stat_size_virtual_file_preserves_text(tmp_path, monkeypatch):
    monkeypatch.delenv("HERMES_NATIVE_FILE_READ", raising=False)
    ops = ShellFileOperations(LocalEnvironment(cwd=str(tmp_path)))
    path = Path("/proc/sys/kernel/osrelease")
    expected = path.read_bytes()
    assert path.stat().st_size == 0 and expected

    result = ops.read_file(str(path))
    assert result.error is None
    assert result.content == "1|" + expected.decode().rstrip("\n")
    assert result.total_lines == 1
    assert result.file_size == len(expected)
    assert "empty" not in (result.hint or "")
    beyond = ops.read_file(str(path), offset=2)
    assert beyond.content == "" and beyond.total_lines == 1
    assert "beyond the end" in (beyond.hint or "")

    empty = tmp_path / "empty.txt"
    empty.touch()
    result = ops.read_file(str(empty))
    assert result.error is None and result.content == ""
    assert result.total_lines == 0 and result.file_size == 0
    assert "empty" in (result.hint or "")
