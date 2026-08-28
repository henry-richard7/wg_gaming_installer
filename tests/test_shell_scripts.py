"""Tests for wg_gaming_installer.shell_scripts."""

import hashlib
import socket
from pathlib import Path

import pytest

import wg_gaming_installer.shell_scripts as shell_scripts
from wg_gaming_installer.shell_scripts import (
    _verify_go_checksum,
    go_tarball_name,
    is_os_supported,
    validate_port_not_in_use,
)


def _free_port() -> int:
    with socket.socket(socket.AddressFamily.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def test_is_os_supported() -> None:
    assert is_os_supported("ubuntu", "22.04")
    assert is_os_supported("debian", "11.3")
    assert is_os_supported("arch", "rolling")


def test_is_os_supported_unsupported(capsys) -> None:
    assert not is_os_supported("windows", "10")
    assert "not supported" in capsys.readouterr().err


def test_is_os_supported_too_old(capsys) -> None:
    assert not is_os_supported("ubuntu", "18.04")
    assert "lower than" in capsys.readouterr().err


def test_validate_port_not_in_use_free() -> None:
    port = _free_port()
    assert validate_port_not_in_use(port, socket.AddressFamily.AF_INET)


def test_validate_port_in_use() -> None:
    with socket.socket(socket.AddressFamily.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        port = s.getsockname()[1]
        assert not validate_port_not_in_use(port, socket.AddressFamily.AF_INET)


def test_go_tarball_name() -> None:
    name = go_tarball_name()
    assert name.startswith("go")
    assert name.endswith(".tar.gz")
    assert "linux" in name


def test_verify_go_checksum(tmp_path: Path, monkeypatch) -> None:
    tarball = tmp_path / "go.tar.gz"
    data = b"hello world"
    tarball.write_bytes(data)
    expected = hashlib.sha256(data).hexdigest()
    monkeypatch.setitem(shell_scripts._GO_SHA256, shell_scripts._go_arch(), expected)
    _verify_go_checksum(tarball)  # should not raise

    monkeypatch.setitem(shell_scripts._GO_SHA256, shell_scripts._go_arch(), "0" * 64)
    with pytest.raises(RuntimeError, match="checksum mismatch"):
        _verify_go_checksum(tarball)


def test_format_bytes() -> None:
    assert shell_scripts.format_bytes(0) == "0 B"
    assert shell_scripts.format_bytes(512) == "512 B"
    assert shell_scripts.format_bytes(1024) == "1.0 KB"
    assert shell_scripts.format_bytes(1048576) == "1.0 MB"
    assert shell_scripts.format_bytes(1073741824) == "1.0 GB"


def test_format_relative_time() -> None:
    assert shell_scripts.format_relative_time(0) == "Never"
    import time

    now = int(time.time())
    assert shell_scripts.format_relative_time(now - 5) == "Just now"
    assert shell_scripts.format_relative_time(now - 120) == "2m ago"
    assert shell_scripts.format_relative_time(now - 7200) == "2h ago"
