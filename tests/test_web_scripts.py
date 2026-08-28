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

    # 1. Unauthenticated request -> 401
    unauth_res = client.get("/")
    assert unauth_res.status_code == 401
    assert "WWW-Authenticate" in unauth_res.headers

    # 2. Invalid credentials -> 401
    bad_res = client.get("/", auth=("admin", "wrong_password"))
    assert bad_res.status_code == 401

    # 3. Valid credentials -> 200
    good_res = client.get("/", auth=("admin", "secret123"))
    assert good_res.status_code == 200
    assert "WireGuard Gaming Panel" in good_res.text


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

    # 4. Download config & QR code
    conf_res = client.get("/api/peers/gamer-pc/config", auth=auth)
    assert conf_res.status_code == 200
    assert "[Interface]" in conf_res.text
    assert "[Peer]" in conf_res.text

    qr_res = client.get("/api/peers/gamer-pc/qr", auth=auth)
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
