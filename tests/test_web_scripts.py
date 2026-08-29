"""
Unit tests for WireGuard Gaming Web UI backend API routes and security.
"""

import sqlite3
from ipaddress import IPv4Address, IPv4Interface, IPv6Address, IPv6Interface
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from wg_gaming_installer import web_scripts
from wg_gaming_installer.sqlite_scripts import (
    OSInfo,
    ServerIFConfig,
    ServerWGConfig,
    create_config_db,
    update_os_info,
    update_server_config,
    update_wg_config,
)


@pytest.fixture(autouse=True)
def configure_test_auth() -> None:
    """
    Set test authentication credentials before each test.
    """
    web_scripts.set_auth_credentials("admin", "secret123", enabled=True)


@pytest.fixture
def mock_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """
    Setup a temporary SQLite database for testing Web API endpoints.
    """
    wg_folder = tmp_path / "wireguard"
    wg_folder.mkdir(parents=True, exist_ok=True)
    db_path = wg_folder / "server_conf.db"

    # Create schema
    conn = sqlite3.connect(db_path)
    create_config_db(conn)

    update_os_info(conn, OSInfo("ubuntu", "22.04", False))
    update_server_config(
        conn,
        ServerIFConfig(
            nic_name="eth0",
            nic_ipv4=IPv4Address("192.168.1.100"),
            nic_ipv6=IPv6Address("2001:db8::1"),
        ),
    )
    update_wg_config(
        conn,
        ServerWGConfig(
            wg_name="wg0",
            ipv4=IPv4Interface("10.66.66.1/24"),
            ipv6=IPv6Interface("fd42:42:42::1/120"),
            listen_port=51820,
            private_key="server_private_key",
            public_key="server_public_key",
            mtu=1420,
        ),
    )
    conn.commit()
    conn.close()

    class MockPaths:
        wg_conf_folder = wg_folder
        server_conf_db_path = db_path

    monkeypatch.setattr(web_scripts, "_PATHS", MockPaths())
    return db_path


def test_auth_required() -> None:
    client = TestClient(web_scripts.app)

    # 1. Public routes succeed without auth
    public_res = client.get("/")
    assert public_res.status_code == 200
    assert "WireGuard Gaming Panel" in public_res.text

    # 2. Admin routes return 401 when unauthenticated
    unauth_peer = client.post("/api/peers", json={"name": "test"})
    assert unauth_peer.status_code == 401
    assert "WWW-Authenticate" in unauth_peer.headers

    bad_res = client.post("/api/peers", json={"name": "test"}, auth=("admin", "wrong_password"))
    assert bad_res.status_code == 401


def test_security_headers() -> None:
    client = TestClient(web_scripts.app)
    response = client.get("/", auth=("admin", "secret123"))
    assert response.status_code == 200
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"


def test_get_status(mock_db: Path) -> None:
    client = TestClient(web_scripts.app)
    response = client.get("/api/status", auth=("admin", "secret123"))
    assert response.status_code == 200
    data = response.json()
    assert data["server_configured"] is True
    assert data["server_nic"]["nic_name"] == "eth0"
    assert data["server_wg"]["wg_name"] == "wg0"
    assert data["server_wg"]["listen_port"] == 51820
    assert data["peer_count"] == 0


def test_peer_crud_lifecycle(mock_db: Path) -> None:
    client = TestClient(web_scripts.app)
    auth = ("admin", "secret123")

    # 1. Initially no peers
    res = client.get("/api/peers", auth=auth)
    assert res.status_code == 200
    assert res.json() == []

    # 2. Add peer
    add_payload = {
        "name": "gamer-pc",
        "dns": ["1.1.1.1", "8.8.8.8"],
        "forward_ports": ["25565", "27015-27030"],
    }
    create_res = client.post("/api/peers", json=add_payload, auth=auth)
    assert create_res.status_code == 200
    assert create_res.json()["status"] == "success"
    assert create_res.json()["name"] == "gamer-pc"

    # 3. Verify peer list
    list_res = client.get("/api/peers", auth=auth)
    assert list_res.status_code == 200
    peers = list_res.json()
    assert len(peers) == 1
    assert peers[0]["name"] == "gamer-pc"
    assert peers[0]["forward_ports"] == ["25565", "27015-27030"]

    # 4. Download config & QR code (Full tunneling default)
    conf_res = client.get("/api/peers/gamer-pc/config", auth=auth)
    assert conf_res.status_code == 200
    assert "[Interface]" in conf_res.text
    assert "[Peer]" in conf_res.text
    assert "AllowedIPs = 0.0.0.0/0,::/0" in conf_res.text

    # 4b. Download config with split tunneling enabled
    conf_split_res = client.get("/api/peers/gamer-pc/config?split_tunnel=true", auth=auth)
    assert conf_split_res.status_code == 200
    assert "AllowedIPs = 10.66.66.0/24, fd42:42:42::/120" in conf_split_res.text

    dl_split_res = client.get("/api/peers/gamer-pc/download?split_tunnel=true", auth=auth)
    assert dl_split_res.status_code == 200
    assert "gamer-pc_split.conf" in dl_split_res.headers.get("Content-Disposition", "")

    qr_res = client.get("/api/peers/gamer-pc/qr?split_tunnel=true", auth=auth)
    assert qr_res.status_code == 200
    assert qr_res.json()["qr_url"].startswith("data:image/")

    # 5. Update peer
    update_payload = {
        "name": "gamer-pc",
        "dns": ["9.9.9.9"],
        "forward_ports": ["7777"],
    }
    put_res = client.put("/api/peers/gamer-pc", json=update_payload, auth=auth)
    assert put_res.status_code == 200

    list_res2 = client.get("/api/peers", auth=auth)
    assert list_res2.json()[0]["forward_ports"] == ["7777"]

    # 6. Delete peer
    del_res = client.delete("/api/peers/gamer-pc", auth=auth)
    assert del_res.status_code == 200

    list_res3 = client.get("/api/peers", auth=auth)
    assert list_res3.json() == []


def test_get_gaming_presets() -> None:
    client = TestClient(web_scripts.app)
    response = client.get("/api/presets", auth=("admin", "secret123"))
    assert response.status_code == 200
    presets = response.json()
    assert len(presets) >= 5
    assert any(p["name"] == "Minecraft" and p["ports"] == "25565" for p in presets)


def test_export_peers_zip(mock_db: Path) -> None:
    import io
    import zipfile

    client = TestClient(web_scripts.app)
    auth = ("admin", "secret123")

    # Add a peer first
    client.post("/api/peers", json={"name": "peer1", "dns": ["1.1.1.1"]}, auth=auth)

    response = client.get("/api/peers/export/zip", auth=auth)
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/zip"

    # Verify ZIP content
    zip_bytes = io.BytesIO(response.content)
    with zipfile.ZipFile(zip_bytes, "r") as zf:
        namelist = zf.namelist()
        assert "peer1.conf" in namelist
        assert "peer1_qr.svg" in namelist
        conf_content = zf.read("peer1.conf").decode("utf-8")
        assert "[Interface]" in conf_content
