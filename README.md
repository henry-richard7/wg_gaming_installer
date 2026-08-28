# wg_gaming_installer — WireGuard installer & manager

Lightweight installer/manager for a personal WireGuard server with optional port forwarding for gaming and similar use-cases. This repository contains the original bash installer (in the `legacy_script` branch) and a rewritten Python package `wg_gaming_installer` (recommended).

## Table of Contents

- [Quick Start](#quick-start)
- [Web UI Dashboard](#web-ui-dashboard)
- [Why the Python version](#why-the-python-version)
- [Supported platforms](#supported-platforms)
- [Prerequisites](#prerequisites)
- [Main menu](#main-menu)
- [Port forwarding](#port-forwarding)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [Legacy installer](#legacy-installer)
- [License](#license)

## Step-by-Step Installation & Usage Guide

### Step 1: Clone the Repository
```bash
git clone https://github.com/henry-richard7/wg_gaming_installer
cd wg_gaming_installer
```

### Step 2: Run the Quick Setup
```bash
chmod +x setup.sh
./setup.sh
```
*Note: `setup.sh` automatically installs `uv` (if missing) and resolves all Python dependencies.*

---

### Step 3: Run the Manager

> [!NOTE]
> WireGuard server configuration and firewall NAT operations require `sudo`.

#### Option A: Web Control Panel (Recommended)
Launch the web interface:
```bash
sudo uv run wg-gaming-web --host 0.0.0.0 --port 8000
```
Open **`http://<SERVER_PUBLIC_IP>:8000`** in your browser to manage peers, view real-time server metrics, scan QR codes, and configure port forwarding.

#### Option B: Terminal CLI Menu
Launch the interactive CLI menu:
```bash
sudo uv run wg-gaming-installer
```
Follow the step-by-step terminal prompts to configure network interfaces, add peers, or set up port forwarding.

---

### Step 4: Connect Clients
- **Mobile Devices (iOS / Android)**: Scan the generated QR code in the official WireGuard App.
- **Desktop (Windows / macOS / Linux)**: Download the client `.conf` file and import it into your WireGuard client app.

## Web UI Dashboard

WireGuard Gaming Installer includes a built-in modern web control panel:

- 📊 **Real-time Server Metrics**: Status, Listen Port, Public IP, MTU, and Active Peers.
- 📱 **QR Code & Config Download**: One-click WireGuard `.conf` file downloads and mobile QR code scanner.
- 🎮 **Gaming Port Forwarding**: Effortlessly add and view nftables DNAT port forward rules per peer.
- ⚡ **Instant Peer Management**: Add, edit, or delete peers visually.

## Why the Python version

- Safer, clearer prompts and input validation.
- SQLite-backed config for persistent server & peer metadata.
- More portable across distributions using Python libraries.

## Supported platforms

Officially supported minimums:

| Distribution | Minimum | Notes |
|---|---:|---|
| `ubuntu` | 22.04 | 26.04 recommended |
| `debian` | 12 | Bullseye |

Also commonly compatible: `centos`/`rocky`/`almalinux` (9), `fedora` (32), `arch` (rolling).

- Requires a Linux host with a public IP or correct NAT/public endpoint.
- On OpenVZ/LXC you may need TUN/TAP enabled and `wireguard-go` will be installed.

## Prerequisites

- Root privileges.
- Python 3.10+ and `python3-venv`.
- A non-production host is recommended; the installer modifies networking and firewall rules.

## Main menu

After installation, the interactive menu provides these actions:

- Stop/Start WireGuard service
- Uninstall and remove generated files
- List peers; show peer config + QR code
- Add / Remove / Edit peers
- Re-configure server (purges all settings and re-runs server configuration)

## Port forwarding

The installer adds nftables DNAT rules that forward chosen public ports to a peer's WireGuard IP (IPv4 & IPv6 supported). **Both TCP and UDP protocols are supported and forwarded automatically** for all specified ports (essential for game servers, voice chat, and peer-to-peer multiplayer).

Example: forwarding `25565` forwards both TCP and UDP `25565` from `SERVER_PUBLIC_IP:25565` to `10.66.66.2:25565`.

Important: do not forward ports already used by server-local services (SSH, etc.).

## Customization

Recommended safe workflow:

1. Stop the service from the management menu.
2. Edit `wg_gaming_installer/exec_scripts.py` to change what the installer generates (WireGuard config, start/stop scripts, nftables rules).
3. Edit the `Paths` dataclass in `wg_gaming_installer/install_scripts.py` to customize file locations (config folder, scripts, TUN device, shell).
4. Restart the service using the management menu.

The WireGuard MTU is prompted during install (default `1420`) and written to both the server `wg0.conf` and generated peer configs.

## Troubleshooting

- If the installer detects a non-public IP (e.g. `10.x.x.x`), supply your public IP when prompted (common on cloud providers).

## Legacy installer

The original bash installer is in the `legacy_script` branch:

```bash
git switch legacy_script
./install.sh
```

Note: the legacy installer is not compatible with the Python version; choose one approach.

## License

This project is licensed under the MIT License — see `LICENSE` for details.
