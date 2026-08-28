"""
Unit tests for WireGuard Gaming Web UI backend API routes.
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

    # Monkeypatch _PATHS to point to tmp_path
    class MockPaths:
        wg_conf_folder = wg_folder
        server_conf_db_path = db_path

    monkeypatch.setattr(web_scripts, "_PATHS", MockPaths())
    return db_path


def test_get_dashboard_html() -> None:
    client = TestClient(web_scripts.app)
    response = client.get("/")
    assert response.status_code == 200
    assert "WireGuard Gaming Panel" in response.text
    assert "<!DOCTYPE html>" in response.text


def test_get_status(mock_db: Path) -> None:
    client = TestClient(web_scripts.app)
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["server_configured"] is True
    assert data["server_nic"]["nic_name"] == "eth0"
    assert data["server_wg"]["wg_name"] == "wg0"
    assert data["server_wg"]["listen_port"] == 51820
    assert data["peer_count"] == 0


def test_peer_crud_lifecycle(mock_db: Path) -> None:
    client = TestClient(web_scripts.app)

    # 1. Initially no peers
    res = client.get("/api/peers")
    assert res.status_code == 200
    assert res.json() == []

    # 2. Add peer
    add_payload = {
        "name": "gamer-pc",
        "dns": ["1.1.1.1", "8.8.8.8"],
        "forward_ports": ["25565", "27015-27030"],
    }
    create_res = client.post("/api/peers", json=add_payload)
    assert create_res.status_code == 200
    assert create_res.json()["status"] == "success"
    assert create_res.json()["name"] == "gamer-pc"

    # 3. Verify peer list
    list_res = client.get("/api/peers")
    assert list_res.status_code == 200
    peers = list_res.json()
    assert len(peers) == 1
    assert peers[0]["name"] == "gamer-pc"
    assert peers[0]["forward_ports"] == ["25565", "27015-27030"]

    # 4. Download config & QR code
    conf_res = client.get("/api/peers/gamer-pc/config")
    assert conf_res.status_code == 200
    assert "[Interface]" in conf_res.text
    assert "[Peer]" in conf_res.text

    qr_res = client.get("/api/peers/gamer-pc/qr")
    assert qr_res.status_code == 200
    assert qr_res.json()["qr_url"].startswith("data:image/")

    # 5. Update peer
    update_payload = {
        "name": "gamer-pc",
        "dns": ["9.9.9.9"],
        "forward_ports": ["7777"],
    }
    put_res = client.put("/api/peers/gamer-pc", json=update_payload)
    assert put_res.status_code == 200

    list_res2 = client.get("/api/peers")
    assert list_res2.json()[0]["forward_ports"] == ["7777"]

    # 6. Delete peer
    del_res = client.delete("/api/peers/gamer-pc")
    assert del_res.status_code == 200

    list_res3 = client.get("/api/peers")
    assert list_res3.json() == []
