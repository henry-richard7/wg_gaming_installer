"""
FastAPI Web UI backend and service runner for WireGuard Gaming Manager.
"""

from __future__ import annotations

import argparse
import base64
import io
import os
import secrets
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv6Address,
    IPv6Interface,
    ip_address,
)
from typing import Any

import psutil
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field

from wg_gaming_installer.install_scripts import Paths, create_wg_peer_str
from wg_gaming_installer.shell_scripts import (
    ServiceStatus,
    get_wg_service_status,
)
from wg_gaming_installer.sqlite_scripts import (
    OSInfo,
    PeerConfig,
    ServerIFConfig,
    ServerWGConfig,
    add_peer_config,
    conf_db_connected,
    delete_peer_config,
    parse_forward_ports,
    read_all_peer_configs,
    read_os_info,
    read_server_nic_config,
    read_wg_config,
)
from wg_gaming_installer.web_static import HTML_DASHBOARD

_PATHS = Paths()
security = HTTPBasic()

_AUTH_USERNAME: str = os.getenv("WG_WEB_USERNAME", "admin")
_AUTH_PASSWORD: str | None = os.getenv("WG_WEB_PASSWORD", None)
_AUTH_ENABLED: bool = True


def set_auth_credentials(username: str, password: str | None, enabled: bool = True) -> None:
    """
    Set authentication username, password, and enabled status.
    """
    global _AUTH_USERNAME, _AUTH_PASSWORD, _AUTH_ENABLED
    _AUTH_USERNAME = username
    _AUTH_PASSWORD = password
    _AUTH_ENABLED = enabled


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """
    Verify HTTP Basic Authentication credentials.
    """
    if not _AUTH_ENABLED:
        return "authenticated"

    if not _AUTH_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Server authentication password not configured.",
            headers={"WWW-Authenticate": 'Basic realm="WireGuard Control Panel"'},
        )

    is_user_ok = secrets.compare_digest(credentials.username.encode("utf-8"), _AUTH_USERNAME.encode("utf-8"))
    is_pass_ok = secrets.compare_digest(credentials.password.encode("utf-8"), _AUTH_PASSWORD.encode("utf-8"))

    if not (is_user_ok and is_pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": 'Basic realm="WireGuard Control Panel"'},
        )
    return credentials.username


app = FastAPI(
    title="WireGuard Gaming Control Panel",
    description="Web dashboard & REST API to manage WireGuard VPN server and gaming port forwarding rules.",
    version="0.1.0",
    dependencies=[Depends(verify_credentials)],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next: Any) -> Response:
    """
    Add security response headers to prevent clickjacking, MIME-sniffing, and XSS attacks.
    """
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


def _gen_keys() -> tuple[str, str, str]:
    """
    Generate WireGuard private key, public key, and preshared key.
    Falls back to secure base64 random generation if wg command is not installed.
    """
    try:
        from wg_gaming_installer.shell_scripts import (
            gen_wg_keypair,
            gen_wg_preshared_key,
        )
        priv, pub = gen_wg_keypair()
        psk = gen_wg_preshared_key()
        return priv, pub, psk
    except Exception:
        priv = base64.b64encode(os.urandom(32)).decode("utf-8")
        pub = base64.b64encode(os.urandom(32)).decode("utf-8")
        psk = base64.b64encode(os.urandom(32)).decode("utf-8")
        return priv, pub, psk


def _allocate_peer_ips(
    wg_config: ServerWGConfig, existing_peers: list[PeerConfig]
) -> tuple[IPv4Interface, IPv6Interface | None]:
    """
    Auto-allocate the next available IPv4 and IPv6 addresses for a new peer.
    """
    used_v4 = {peer.ipv4.ip for peer in existing_peers}
    used_v4.add(wg_config.ipv4.ip)

    v4_net = wg_config.ipv4.network
    allocated_v4: IPv4Address | None = None
    for host in v4_net.hosts():
        if host not in used_v4:
            allocated_v4 = host
            break

    if not allocated_v4:
        raise ValueError("No available IPv4 addresses remaining in server subnet.")

    allocated_v6: IPv6Interface | None = None
    if wg_config.ipv6:
        used_v6 = {peer.ipv6.ip for peer in existing_peers if peer.ipv6}
        used_v6.add(wg_config.ipv6.ip)
        v6_net = wg_config.ipv6.network
        for host6 in v6_net.hosts():
            if host6 not in used_v6:
                allocated_v6 = IPv6Interface(f"{host6}/128")
                break

    return IPv4Interface(f"{allocated_v4}/32"), allocated_v6


class PeerCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    ipv4: str | None = None
    ipv6: str | None = None
    dns: list[str] = Field(default_factory=lambda: ["1.1.1.1", "1.0.0.1"])
    forward_ports: list[str] = Field(default_factory=list)


GAMING_PRESETS: list[dict[str, str]] = [
    {"name": "Minecraft", "icon": "⛏️", "ports": "25565"},
    {"name": "Steam / Valve P2P", "icon": "🎮", "ports": "27015-27030"},
    {"name": "Call of Duty / Warzone", "icon": "🎯", "ports": "3074"},
    {"name": "Palworld", "icon": "🦖", "ports": "8211"},
    {"name": "Rust", "icon": "🛠️", "ports": "28015"},
    {"name": "FiveM / GTA V", "icon": "🚗", "ports": "30120"},
    {"name": "ARK / DayZ", "icon": "🧟", "ports": "7777, 27015"},
    {"name": "Discord / VOIP", "icon": "🔊", "ports": "50000-50020"},
]


@app.get("/api/presets")
def get_gaming_presets() -> list[dict[str, str]]:
    """
    Get 1-click gaming port forwarding presets catalog.
    """
    return GAMING_PRESETS


@app.get("/", response_class=HTMLResponse)
def get_dashboard() -> str:
    """
    Serve the embedded single-page Web UI dashboard.
    """
    return HTML_DASHBOARD


@app.get("/api/status")
def get_status() -> dict[str, Any]:
    """
    Get server status, network interface config, WireGuard config, and system metrics.
    """
    db_path = _PATHS.server_conf_db_path
    if not db_path.exists():
        return {
            "server_configured": False,
            "status": "not_installed",
            "message": "Configuration database does not exist yet.",
        }

    try:
        with conf_db_connected(db_path=db_path) as conn:
            os_info: OSInfo | None = read_os_info(conn)
            server_config: ServerIFConfig | None = read_server_nic_config(conn)
            wg_config: ServerWGConfig | None = read_wg_config(conn)
            peers: list[PeerConfig] = read_all_peer_configs(conn)

        status_str = "inactive"
        if wg_config:
            try:
                svc_status = get_wg_service_status(wg_config.wg_name)
                status_str = "active" if svc_status == ServiceStatus.ACTIVE else "inactive"
            except Exception:
                status_str = "inactive"

        return {
            "server_configured": wg_config is not None,
            "status": status_str,
            "os_info": (
                {
                    "os_name": os_info.os_name,
                    "os_version": os_info.os_version,
                    "userspace_wg": os_info.userspace_wg,
                }
                if os_info
                else None
            ),
            "server_nic": (
                {
                    "nic_name": server_config.nic_name,
                    "nic_ipv4": str(server_config.nic_ipv4),
                    "nic_ipv6": str(server_config.nic_ipv6) if server_config.nic_ipv6 else None,
                }
                if server_config
                else None
            ),
            "server_wg": (
                {
                    "wg_name": wg_config.wg_name,
                    "ipv4": str(wg_config.ipv4),
                    "ipv6": str(wg_config.ipv6) if wg_config.ipv6 else None,
                    "listen_port": wg_config.listen_port,
                    "public_key": wg_config.public_key,
                    "mtu": wg_config.mtu,
                }
                if wg_config
                else None
            ),
            "peer_count": len(peers),
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
            },
        }
    except Exception as e:
        return {"server_configured": False, "status": "error", "message": str(e)}


@app.post("/api/service/start")
def start_service() -> dict[str, str]:
    """
    Start the WireGuard service and apply nftables rules.
    """
    from wg_gaming_installer.install_scripts import _server_start_wg_service_step

    try:
        _server_start_wg_service_step()
        return {"status": "success", "message": "WireGuard service started successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start service: {e}") from e


@app.post("/api/service/stop")
def stop_service() -> dict[str, str]:
    """
    Stop the WireGuard service and remove nftables rules.
    """
    from wg_gaming_installer.install_scripts import _server_stop_wg_service_step

    try:
        _server_stop_wg_service_step()
        return {"status": "success", "message": "WireGuard service stopped successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop service: {e}") from e


@app.get("/api/peers")
def list_peers() -> list[dict[str, Any]]:
    """
    Get all configured WireGuard peers enriched with live traffic & handshake stats.
    """
    db_path = _PATHS.server_conf_db_path
    if not db_path.exists():
        return []

    with conf_db_connected(db_path=db_path) as conn:
        peers: list[PeerConfig] = read_all_peer_configs(conn)
        wg_config = read_wg_config(conn)

    wg_stats: dict[str, dict[str, Any]] = {}
    if wg_config:
        try:
            from wg_gaming_installer.shell_scripts import get_wg_peer_stats

            wg_stats = get_wg_peer_stats(wg_config.wg_name)
        except Exception:
            wg_stats = {}

    result: list[dict[str, Any]] = []
    for p in peers:
        p_stats = wg_stats.get(p.public_key, {})
        result.append(
            {
                "name": p.name,
                "ipv4": str(p.ipv4),
                "ipv6": str(p.ipv6) if p.ipv6 else None,
                "dns": [str(d) for d in p.dns],
                "public_key": p.public_key,
                "forward_ports": p.forward_ports_str.split(",") if p.forward_ports_str else [],
                "online": p_stats.get("online", False),
                "latest_handshake_relative": p_stats.get("latest_handshake_relative", "Never"),
                "transfer_rx_formatted": p_stats.get("transfer_rx_formatted", "0 B"),
                "transfer_tx_formatted": p_stats.get("transfer_tx_formatted", "0 B"),
                "endpoint": p_stats.get("endpoint", None),
            }
        )

    return result


@app.post("/api/peers")
def create_peer(req: PeerCreateRequest) -> dict[str, Any]:
    """
    Add a new peer with specified or auto-allocated IP address and gaming port forwards.
    """
    db_path = _PATHS.server_conf_db_path
    if not db_path.exists():
        raise HTTPException(status_code=400, detail="Server must be configured before adding peers.")

    with conf_db_connected(db_path=db_path) as conn:
        wg_config = read_wg_config(conn)
        server_config = read_server_nic_config(conn)
        existing_peers = read_all_peer_configs(conn)

        if not wg_config or not server_config:
            raise HTTPException(status_code=400, detail="Server network settings missing in database.")

        if any(p.name == req.name for p in existing_peers):
            raise HTTPException(status_code=400, detail=f"Peer with name '{req.name}' already exists.")

        if req.ipv4:
            clean_ip = req.ipv4.strip()
            if "/" not in clean_ip:
                clean_ip += "/32"
            peer_v4 = IPv4Interface(clean_ip)
            peer_v6 = IPv6Interface(req.ipv6.strip()) if req.ipv6 else None
        else:
            peer_v4, peer_v6 = _allocate_peer_ips(wg_config, existing_peers)

        parsed_dns: list[IPv4Address | IPv6Address] = [ip_address(d.strip()) for d in req.dns if d.strip()]
        ports_str = ",".join(p.strip() for p in req.forward_ports if p.strip())
        parsed_ports = parse_forward_ports(ports_str)

        priv, pub, psk = _gen_keys()

        peer = PeerConfig(
            name=req.name,
            ipv4=peer_v4,
            ipv6=peer_v6,
            dns=parsed_dns,
            public_key=pub,
            private_key=priv,
            preshared_key=psk,
            forward_ports=parsed_ports,
        )

        add_peer_config(conn, peer)

        try:
            if get_wg_service_status(wg_config.wg_name) == ServiceStatus.ACTIVE:
                from wg_gaming_installer.install_scripts import _restart_wg_if_active

                _restart_wg_if_active()
        except Exception:
            pass

    return {"status": "success", "name": peer.name, "ipv4": str(peer.ipv4)}


@app.put("/api/peers/{peer_name}")
def update_peer(peer_name: str, req: PeerCreateRequest) -> dict[str, Any]:
    """
    Update an existing peer's configuration.
    """
    db_path = _PATHS.server_conf_db_path
    if not db_path.exists():
        raise HTTPException(status_code=400, detail="Server not configured.")

    with conf_db_connected(db_path=db_path) as conn:
        existing_peers = read_all_peer_configs(conn)
        target = next((p for p in existing_peers if p.name == peer_name), None)
        if not target:
            raise HTTPException(status_code=404, detail=f"Peer '{peer_name}' not found.")

        delete_peer_config(conn, peer_name)

        wg_config = read_wg_config(conn)
        server_config = read_server_nic_config(conn)

        if not wg_config or not server_config:
            raise HTTPException(status_code=400, detail="Server network settings missing.")

        if req.ipv4:
            clean_ip = req.ipv4.strip()
            if "/" not in clean_ip:
                clean_ip += "/32"
            peer_v4 = IPv4Interface(clean_ip)
            peer_v6 = IPv6Interface(req.ipv6.strip()) if req.ipv6 else None
        else:
            peer_v4 = target.ipv4
            peer_v6 = target.ipv6

        parsed_dns = [ip_address(d.strip()) for d in req.dns if d.strip()]
        ports_str = ",".join(p.strip() for p in req.forward_ports if p.strip())
        parsed_ports = parse_forward_ports(ports_str)

        updated_peer = PeerConfig(
            name=req.name,
            ipv4=peer_v4,
            ipv6=peer_v6,
            dns=parsed_dns,
            public_key=target.public_key,
            private_key=target.private_key,
            preshared_key=target.preshared_key,
            forward_ports=parsed_ports,
        )

        add_peer_config(conn, updated_peer)

        try:
            if get_wg_service_status(wg_config.wg_name) == ServiceStatus.ACTIVE:
                from wg_gaming_installer.install_scripts import _restart_wg_if_active

                _restart_wg_if_active()
        except Exception:
            pass

    return {"status": "success", "name": updated_peer.name}


@app.delete("/api/peers/{peer_name}")
def delete_peer(peer_name: str) -> dict[str, str]:
    """
    Delete a peer configuration.
    """
    db_path = _PATHS.server_conf_db_path
    if not db_path.exists():
        raise HTTPException(status_code=400, detail="Server not configured.")

    with conf_db_connected(db_path=db_path) as conn:
        existing_peers = read_all_peer_configs(conn)
        if not any(p.name == peer_name for p in existing_peers):
            raise HTTPException(status_code=404, detail=f"Peer '{peer_name}' not found.")

        delete_peer_config(conn, peer_name)
        wg_config = read_wg_config(conn)

        if wg_config:
            try:
                if get_wg_service_status(wg_config.wg_name) == ServiceStatus.ACTIVE:
                    from wg_gaming_installer.install_scripts import (
                        _restart_wg_if_active,
                    )

                    _restart_wg_if_active()
            except Exception:
                pass

    return {"status": "success", "message": f"Peer '{peer_name}' deleted."}


@app.get("/api/peers/{peer_name}/config")
def get_peer_config(peer_name: str) -> Response:
    """
    Get raw WireGuard configuration text string for a peer.
    """
    db_path = _PATHS.server_conf_db_path
    if not db_path.exists():
        raise HTTPException(status_code=400, detail="Server not configured.")

    with conf_db_connected(db_path=db_path) as conn:
        peers = read_all_peer_configs(conn)
        peer = next((p for p in peers if p.name == peer_name), None)
        wg_config = read_wg_config(conn)
        server_config = read_server_nic_config(conn)

        if not peer or not wg_config or not server_config:
            raise HTTPException(status_code=404, detail=f"Peer '{peer_name}' or server config not found.")

        conf_str = create_wg_peer_str(peer=peer, server_config=server_config, wg_config=wg_config)

    return Response(content=conf_str, media_type="text/plain")


@app.get("/api/peers/{peer_name}/download")
def download_peer_config(peer_name: str) -> Response:
    """
    Download client WireGuard configuration as a `.conf` file attachment.
    """
    conf_response = get_peer_config(peer_name)
    conf_response.headers["Content-Disposition"] = f'attachment; filename="{peer_name}.conf"'
    return conf_response


@app.get("/api/peers/{peer_name}/qr")
def get_peer_qr(peer_name: str) -> dict[str, str]:
    """
    Generate a base64 data URL of the WireGuard QR code for a peer.
    """
    conf_response = get_peer_config(peer_name)
    conf_text = conf_response.body.decode("utf-8")

    try:
        import qrcode.image.svg

        factory = qrcode.image.svg.SvgImage
        img = qrcode.make(conf_text, image_factory=factory)
        buf = io.BytesIO()
        img.save(buf)
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return {"peer_name": peer_name, "qr_url": f"data:image/svg+xml;base64,{b64}"}
    except Exception:
        import qrcode

        img = qrcode.make(conf_text)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return {"peer_name": peer_name, "qr_url": f"data:image/png;base64,{b64}"}


def main() -> None:
    """
    CLI launcher for the WireGuard Gaming Web UI server.
    """
    parser = argparse.ArgumentParser(description="WireGuard Gaming Web Control Panel")
    parser.add_argument("--host", default="0.0.0.0", help="Host interface to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    parser.add_argument("--username", default=os.getenv("WG_WEB_USERNAME", "admin"), help="Web UI admin username")
    parser.add_argument("--password", default=os.getenv("WG_WEB_PASSWORD", None), help="Web UI admin password")
    parser.add_argument("--disable-auth", action="store_true", help="Disable HTTP Basic Authentication")
    args = parser.parse_args()

    auth_enabled = not args.disable_auth
    auth_password = args.password

    if auth_enabled and not auth_password:
        auth_password = secrets.token_urlsafe(12)
        print("\n" + "=" * 60)
        print("🔐 WireGuard Gaming Web Control Panel Credentials")
        print("=" * 60)
        print(f"  Username : {args.username}")
        print(f"  Password : {auth_password}")
        print("=" * 60)
        print("  Set custom credentials via --password or WG_WEB_PASSWORD env var.\n")

    set_auth_credentials(username=args.username, password=auth_password, enabled=auth_enabled)

    print(f"🚀 Starting WireGuard Gaming Web Panel on http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
