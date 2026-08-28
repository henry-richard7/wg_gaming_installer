"""
Embedded Web UI Frontend HTML for WireGuard Gaming Manager.
"""

HTML_DASHBOARD = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WireGuard Gaming Control Panel</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0f172a;
            --bg-card: rgba(30, 41, 59, 0.7);
            --bg-card-hover: rgba(51, 65, 85, 0.8);
            --border-color: rgba(255, 255, 255, 0.1);
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --primary-glow: rgba(99, 102, 241, 0.35);
            --secondary: #06b6d4;
            --success: #10b981;
            --success-glow: rgba(16, 185, 129, 0.3);
            --danger: #ef4444;
            --danger-hover: #dc2626;
            --warning: #f59e0b;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --radius-lg: 16px;
            --radius-md: 12px;
            --radius-sm: 8px;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        body {
            background-color: var(--bg-dark);
            background-image:
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(6, 182, 212, 0.15) 0px, transparent 50%);
            background-attachment: fixed;
            color: var(--text-main);
            min-height: 100vh;
            padding-bottom: 60px;
        }

        header {
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border-color);
            position: sticky;
            top: 0;
            z-index: 100;
            padding: 18px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo-area {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .logo-icon {
            width: 42px;
            height: 42px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border-radius: var(--radius-md);
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 0 20px var(--primary-glow);
        }

        .logo-icon svg {
            width: 24px;
            height: 24px;
            fill: none;
            stroke: white;
            stroke-width: 2.2;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        .logo-text h1 {
            font-size: 1.35rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff 30%, #a5b4fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .logo-text p {
            font-size: 0.8rem;
            color: var(--text-muted);
        }

        .header-actions {
            display: flex;
            gap: 12px;
            align-items: center;
        }

        .status-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
            border: 1px solid var(--border-color);
            background: rgba(30, 41, 59, 0.6);
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--text-muted);
        }

        .status-active .status-dot {
            background: var(--success);
            box-shadow: 0 0 10px var(--success);
        }

        .status-active {
            color: #6ee7b7;
            border-color: rgba(16, 185, 129, 0.3);
            background: rgba(16, 185, 129, 0.1);
        }

        .status-inactive .status-dot {
            background: var(--danger);
        }

        .status-inactive {
            color: #fca5a5;
            border-color: rgba(239, 68, 68, 0.3);
            background: rgba(239, 68, 68, 0.1);
        }

        .container {
            max-width: 1200px;
            margin: 36px auto;
            padding: 0 24px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 36px;
        }

        .stat-card {
            background: var(--bg-card);
            backdrop-filter: blur(8px);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 22px;
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-3px);
            border-color: rgba(99, 102, 241, 0.4);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
        }

        .stat-title {
            font-size: 0.85rem;
            color: var(--text-muted);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 10px;
        }

        .stat-value {
            font-size: 1.5rem;
            font-weight: 700;
            color: #fff;
            word-break: break-all;
        }

        .stat-sub {
            font-size: 0.8rem;
            color: var(--secondary);
            margin-top: 6px;
        }

        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }

        .section-title {
            font-size: 1.4rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 10px 20px;
            border-radius: var(--radius-md);
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            border: none;
            transition: all 0.2s ease;
            text-decoration: none;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--primary), var(--primary-hover));
            color: white;
            box-shadow: 0 4px 14px var(--primary-glow);
        }

        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px var(--primary-glow);
            filter: brightness(1.1);
        }

        .btn-secondary {
            background: rgba(51, 65, 85, 0.7);
            color: white;
            border: 1px solid var(--border-color);
        }

        .btn-secondary:hover {
            background: rgba(71, 85, 105, 0.9);
        }

        .btn-danger {
            background: rgba(239, 68, 68, 0.15);
            color: #fca5a5;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }

        .btn-danger:hover {
            background: var(--danger);
            color: white;
        }

        .btn-sm {
            padding: 6px 12px;
            font-size: 0.8rem;
            border-radius: var(--radius-sm);
        }

        .peers-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 24px;
        }

        .peer-card {
            background: var(--bg-card);
            backdrop-filter: blur(8px);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            padding: 24px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .peer-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            opacity: 0.7;
        }

        .peer-card:hover {
            border-color: rgba(99, 102, 241, 0.5);
            transform: translateY(-4px);
            box-shadow: 0 12px 36px rgba(0, 0, 0, 0.3);
        }

        .peer-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 16px;
        }

        .peer-name {
            font-size: 1.2rem;
            font-weight: 700;
            color: #fff;
        }

        .peer-info {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-bottom: 20px;
        }

        .info-row {
            display: flex;
            justify-content: space-between;
            font-size: 0.88rem;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        .info-label {
            color: var(--text-muted);
        }

        .info-value {
            font-family: 'JetBrains Mono', monospace;
            color: #e2e8f0;
            font-weight: 500;
        }

        .tag {
            display: inline-block;
            background: rgba(99, 102, 241, 0.15);
            color: #a5b4fc;
            border: 1px solid rgba(99, 102, 241, 0.3);
            padding: 2px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-family: 'JetBrains Mono', monospace;
        }

        .peer-actions {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 12px;
        }

        /* Modal styling */
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(10px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
            transition: all 0.3s ease;
        }

        .modal-overlay.active {
            opacity: 1;
            pointer-events: auto;
        }

        .modal {
            background: #1e293b;
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            width: 90%;
            max-width: 560px;
            padding: 32px;
            box-shadow: 0 24px 48px rgba(0, 0, 0, 0.4);
            transform: scale(0.95);
            transition: all 0.3s ease;
            max-height: 90vh;
            overflow-y: auto;
        }

        .modal-overlay.active .modal {
            transform: scale(1);
        }

        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
        }

        .modal-title {
            font-size: 1.3rem;
            font-weight: 700;
        }

        .close-btn {
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-size: 1.5rem;
            cursor: pointer;
            line-height: 1;
        }

        .close-btn:hover {
            color: white;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-label {
            display: block;
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-muted);
            margin-bottom: 8px;
        }

        .form-input {
            width: 100%;
            padding: 12px 16px;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            color: white;
            font-size: 0.95rem;
            outline: none;
            transition: all 0.2s;
        }

        .form-input:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px var(--primary-glow);
        }

        .qr-container {
            text-align: center;
            margin: 20px 0;
        }

        .qr-image {
            background: white;
            padding: 16px;
            border-radius: var(--radius-md);
            max-width: 240px;
            margin: 0 auto 16px auto;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }

        .conf-code {
            background: #0f172a;
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
            color: #38bdf8;
            white-space: pre-wrap;
            word-break: break-all;
            max-height: 200px;
            overflow-y: auto;
            text-align: left;
        }

        .empty-state {
            text-align: center;
            padding: 60px 20px;
            background: var(--bg-card);
            border: 1px dashed var(--border-color);
            border-radius: var(--radius-lg);
            grid-column: 1 / -1;
        }

        .empty-state h3 {
            font-size: 1.2rem;
            color: #e2e8f0;
            margin-bottom: 8px;
        }

        .empty-state p {
            color: var(--text-muted);
            font-size: 0.9rem;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <header>
        <div class="logo-area">
            <div class="logo-icon">
                <svg viewBox="0 0 24 24">
                    <rect x="2" y="2" width="20" height="8" rx="2" />
                    <rect x="2" y="14" width="20" height="8" rx="2" />
                    <line x1="6" y1="6" x2="6.01" y2="6" />
                    <line x1="6" y1="18" x2="6.01" y2="18" />
                </svg>
            </div>
            <div class="logo-text">
                <h1>WireGuard Gaming Panel</h1>
                <p>High Performance VPN & Gaming Port Forwarder</p>
            </div>
        </div>
        <div class="header-actions">
            <div id="serviceStatusBadge" class="status-badge status-inactive">
                <span class="status-dot"></span>
                <span id="serviceStatusText">Loading...</span>
            </div>
            <button id="toggleServiceBtn" class="btn btn-secondary btn-sm" onclick="toggleService()">Toggle Service</button>
        </div>
    </header>

    <div class="container">
        <!-- Stats Row -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-title">Server Public Endpoint</div>
                <div class="stat-value" id="statEndpoint">--</div>
                <div class="stat-sub" id="statInterface">NIC: --</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">WireGuard Network</div>
                <div class="stat-value" id="statWgIp">--</div>
                <div class="stat-sub" id="statWgPort">Port: 51820</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Active Gaming Peers</div>
                <div class="stat-value" id="statPeerCount">0</div>
                <div class="stat-sub" id="statMtu">MTU: 1420</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">System Status</div>
                <div class="stat-value" id="statOs">Linux</div>
                <div class="stat-sub" id="statSysInfo">CPU & RAM OK</div>
            </div>
        </div>

        <!-- Peer Section -->
        <div class="section-header">
            <div class="section-title">
                Connected Gaming Peers
            </div>
            <div style="display: flex; gap: 12px;">
                <a class="btn btn-secondary" href="/api/peers/export/zip" download="wireguard_peers_all.zip">
                    📦 Export All (.zip)
                </a>
                <button class="btn btn-primary" onclick="openAddPeerModal()">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                    Add New Peer
                </button>
            </div>
        </div>

        <div class="peers-grid" id="peersGrid">
            <div class="empty-state">
                <h3>Loading Peers...</h3>
                <p>Please wait while fetching server configuration.</p>
            </div>
        </div>

        <!-- Gaming Hub: Chat & File Sharing -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 32px;">
            <!-- Chatroom Panel -->
            <div class="card" style="display: flex; flex-direction: column; height: 420px;">
                <div class="section-title" style="margin-bottom: 12px; font-size: 1.1rem; display: flex; align-items: center; gap: 8px;">
                    💬 LAN Gaming Chatroom
                </div>
                <div id="chatMessages" style="flex: 1; overflow-y: auto; background: rgba(0, 0, 0, 0.2); border-radius: 8px; padding: 12px; font-size: 0.85rem; display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px; border: 1px solid var(--border);">
                    <div style="color: var(--text-muted); text-align: center; margin-top: 40px;">No messages yet. Send a message to get started!</div>
                </div>
                <form id="chatForm" onsubmit="handleSendChat(event)" style="display: flex; gap: 8px;">
                    <input type="text" id="chatSender" class="form-input" style="width: 110px;" value="Admin" placeholder="Your Name" required>
                    <input type="text" id="chatInput" class="form-input" style="flex: 1;" placeholder="Type a message or game server IP..." required>
                    <button type="submit" class="btn btn-primary" style="padding: 0 16px;">Send</button>
                </form>
            </div>

            <!-- File Sharing Panel -->
            <div class="card" style="display: flex; flex-direction: column; height: 420px;">
                <div class="section-title" style="margin-bottom: 12px; font-size: 1.1rem; display: flex; justify-content: space-between; align-items: center;">
                    <span>📁 VPN File Share Hub</span>
                    <label class="btn btn-secondary btn-sm" style="cursor: pointer; padding: 4px 10px; font-size: 0.8rem;">
                        + Upload File
                        <input type="file" id="fileUploadInput" onchange="handleFileUpload(event)" style="display: none;">
                    </label>
                </div>
                <div id="filesList" style="flex: 1; overflow-y: auto; background: rgba(0, 0, 0, 0.2); border-radius: 8px; padding: 12px; font-size: 0.85rem; display: flex; flex-direction: column; gap: 8px; border: 1px solid var(--border);">
                    <div style="color: var(--text-muted); text-align: center; margin-top: 40px;">No shared files yet. Click "+ Upload File" to share mods, maps, or configs.</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Add Peer Modal -->
    <div class="modal-overlay" id="addPeerModal">
        <div class="modal">
            <div class="modal-header">
                <div class="modal-title" id="peerModalTitle">Add New Gaming Peer</div>
                <button class="close-btn" onclick="closeModal('addPeerModal')">&times;</button>
            </div>
            <form id="peerForm" onsubmit="handlePeerFormSubmit(event)">
                <input type="hidden" id="editOriginalName" value="">
                <div class="form-group">
                    <label class="form-label" for="peerName">Peer Name / Gaming Client</label>
                    <input type="text" id="peerName" class="form-input" placeholder="e.g., desktop-pc, phone, game-server" required>
                </div>
                <div class="form-group">
                    <label class="form-label" for="peerIpv4">Peer IPv4 Address (Optional auto-assign)</label>
                    <input type="text" id="peerIpv4" class="form-input" placeholder="e.g., 10.66.66.2/32 (Leave empty for next available)">
                </div>
                <div class="form-group">
                    <label class="form-label" for="peerDns">DNS Servers (Comma separated)</label>
                    <input type="text" id="peerDns" class="form-input" value="1.1.1.1, 1.0.0.1">
                </div>
                <div class="form-group">
                    <label class="form-label" for="peerPorts">Forwarded Gaming Ports (Public -> Peer)</label>
                    <input type="text" id="peerPorts" class="form-input" placeholder="e.g., 25565, 27015-27030 (Minecraft, Steam)">
                    <div style="margin-top: 8px; font-size: 0.8rem; color: var(--text-muted);">
                        ⚡ 1-Click Gaming Presets:
                        <div id="presetsContainer" style="display: flex; gap: 6px; flex-wrap: wrap; margin-top: 6px;"></div>
                    </div>
                </div>
                <div style="display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px;">
                    <button type="button" class="btn btn-secondary" onclick="closeModal('addPeerModal')">Cancel</button>
                    <button type="submit" class="btn btn-primary" id="savePeerBtn">Save Peer</button>
                </div>
            </form>
        </div>
    </div>

    <!-- View Config / QR Modal -->
    <div class="modal-overlay" id="qrModal">
        <div class="modal">
            <div class="modal-header">
                <div class="modal-title" id="qrModalTitle">Peer WireGuard Configuration</div>
                <button class="close-btn" onclick="closeModal('qrModal')">&times;</button>
            </div>
            <div class="qr-container">
                <img id="qrImage" class="qr-image" src="" alt="WireGuard QR Code">
                <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 16px;">Scan with mobile WireGuard App or download client config below.</div>
                <div class="conf-code" id="confText"></div>
            </div>
            <div style="display: flex; justify-content: flex-end; gap: 12px; margin-top: 20px;">
                <button class="btn btn-secondary" onclick="copyConfText()">Copy Config</button>
                <a id="downloadConfLink" class="btn btn-primary" download>Download .conf File</a>
            </div>
        </div>
    </div>

    <script>
        let currentStatus = null;
        let currentPeers = [];

        async function fetchStatus() {
            try {
                const res = await fetch('/api/status');
                const data = await res.json();
                currentStatus = data;
                renderStatus(data);
            } catch (err) {
                console.error("Failed to load status:", err);
            }
        }

        function renderStatus(data) {
            const badge = document.getElementById('serviceStatusBadge');
            const text = document.getElementById('serviceStatusText');

            if (!data.server_configured) {
                badge.className = 'status-badge status-inactive';
                text.textContent = 'Setup Required';
                document.getElementById('statEndpoint').textContent = 'Not Configured';
                document.getElementById('statInterface').textContent = 'Run wg-gaming-installer first';
                return;
            }

            if (data.status === 'active') {
                badge.className = 'status-badge status-active';
                text.textContent = 'Service Active';
            } else {
                badge.className = 'status-badge status-inactive';
                text.textContent = 'Service Stopped';
            }

            if (data.server_nic) {
                document.getElementById('statEndpoint').textContent = `${data.server_nic.nic_ipv4}:${data.server_wg?.listen_port || 51820}`;
                document.getElementById('statInterface').textContent = `NIC: ${data.server_nic.nic_name}`;
            }

            if (data.server_wg) {
                document.getElementById('statWgIp').textContent = data.server_wg.ipv4;
                document.getElementById('statWgPort').textContent = `Port: ${data.server_wg.listen_port}`;
                document.getElementById('statMtu').textContent = `MTU: ${data.server_wg.mtu}`;
            }

            document.getElementById('statPeerCount').textContent = data.peer_count || 0;
            if (data.os_info) {
                document.getElementById('statOs').textContent = `${data.os_info.os_name} ${data.os_info.os_version}`;
            }
        }

        async function fetchPeers() {
            try {
                const res = await fetch('/api/peers');
                const peers = await res.json();
                currentPeers = peers;
                renderPeers(peers);
            } catch (err) {
                console.error("Failed to load peers:", err);
            }
        }

        function renderPeers(peers) {
            const grid = document.getElementById('peersGrid');
            if (!peers || peers.length === 0) {
                grid.innerHTML = `
                    <div class="empty-state">
                        <h3>No Peers Configured Yet</h3>
                        <p>Click "Add New Peer" to generate a WireGuard client configuration.</p>
                        <button class="btn btn-primary btn-sm" onclick="openAddPeerModal()">+ Add First Peer</button>
                    </div>
                `;
                return;
            }

            grid.innerHTML = peers.map(peer => {
                const portsStr = peer.forward_ports && peer.forward_ports.length > 0 ? peer.forward_ports.join(', ') : 'None';
                const isOnline = peer.online;
                const statusClass = isOnline ? 'status-active' : 'status-inactive';
                const statusText = isOnline ? 'Online' : 'Offline';
                return `
                    <div class="peer-card">
                        <div class="peer-header">
                            <div>
                                <div class="peer-name">${escapeHtml(peer.name)}</div>
                                <span class="tag" style="margin-top: 4px;">${escapeHtml(peer.ipv4)}</span>
                            </div>
                            <span class="status-badge ${statusClass}" style="padding: 4px 10px; font-size: 0.75rem;">
                                <span class="status-dot"></span>${statusText}
                            </span>
                        </div>
                        <div class="peer-info">
                            <div class="info-row">
                                <span class="info-label">Traffic Rx / Tx:</span>
                                <span class="info-value" style="color: #6ee7b7;">⬇️ ${escapeHtml(peer.transfer_rx_formatted || '0 B')} / ⬆️ ${escapeHtml(peer.transfer_tx_formatted || '0 B')}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">Last Handshake:</span>
                                <span class="info-value">${escapeHtml(peer.latest_handshake_relative || 'Never')}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">DNS:</span>
                                <span class="info-value">${escapeHtml(peer.dns.join(', '))}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">Forwarded Ports (TCP & UDP):</span>
                                <span class="info-value" style="color: var(--secondary);">${escapeHtml(portsStr)}</span>
                            </div>
                        </div>
                        <div class="peer-actions">
                            <button class="btn btn-secondary btn-sm" onclick="showQrModal('${escapeHtml(peer.name)}')">📱 QR / Config</button>
                            <a class="btn btn-secondary btn-sm" href="/api/peers/${encodeURIComponent(peer.name)}/download" download="${escapeHtml(peer.name)}.conf">📥 Download .conf</a>
                            <button class="btn btn-secondary btn-sm" onclick="openEditPeerModal('${escapeHtml(peer.name)}')">✏️ Edit</button>
                            <button class="btn btn-danger btn-sm" onclick="deletePeer('${escapeHtml(peer.name)}')">🗑️</button>
                        </div>
                    </div>
                `;
            }).join('');
        }

        async function toggleService() {
            if (!currentStatus) return;
            const action = currentStatus.status === 'active' ? 'stop' : 'start';
            try {
                const res = await fetch(`/api/service/${action}`, { method: 'POST' });
                const result = await res.json();
                await fetchStatus();
            } catch (err) {
                alert("Error toggling service: " + err);
            }
        }

        function openAddPeerModal() {
            document.getElementById('peerModalTitle').textContent = 'Add New Gaming Peer';
            document.getElementById('editOriginalName').value = '';
            document.getElementById('peerName').value = '';
            document.getElementById('peerIpv4').value = '';
            document.getElementById('peerDns').value = '1.1.1.1, 1.0.0.1';
            document.getElementById('peerPorts').value = '';
            document.getElementById('addPeerModal').classList.add('active');
        }

        function openEditPeerModal(peerName) {
            const peer = currentPeers.find(p => p.name === peerName);
            if (!peer) return;
            document.getElementById('peerModalTitle').textContent = `Edit Peer: ${peer.name}`;
            document.getElementById('editOriginalName').value = peer.name;
            document.getElementById('peerName').value = peer.name;
            document.getElementById('peerIpv4').value = peer.ipv4 || '';
            document.getElementById('peerDns').value = (peer.dns || []).join(', ');
            document.getElementById('peerPorts').value = (peer.forward_ports || []).join(', ');
            document.getElementById('addPeerModal').classList.add('active');
        }

        function closeModal(id) {
            document.getElementById(id).classList.remove('active');
        }

        async function handlePeerFormSubmit(e) {
            e.preventDefault();
            const originalName = document.getElementById('editOriginalName').value;
            const name = document.getElementById('peerName').value.trim();
            const ipv4 = document.getElementById('peerIpv4').value.trim();
            const dnsStr = document.getElementById('peerDns').value.trim();
            const portsStr = document.getElementById('peerPorts').value.trim();

            const payload = {
                name: name,
                ipv4: ipv4 || null,
                dns: dnsStr ? dnsStr.split(',').map(s => s.trim()) : ["1.1.1.1"],
                forward_ports: portsStr ? portsStr.split(',').map(s => s.trim()) : []
            };

            try {
                let res;
                if (originalName) {
                    res = await fetch(`/api/peers/${encodeURIComponent(originalName)}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                } else {
                    res = await fetch('/api/peers', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                }

                if (!res.ok) {
                    const errData = await res.json();
                    alert("Error saving peer: " + (errData.detail || "Unknown error"));
                    return;
                }

                closeModal('addPeerModal');
                await fetchPeers();
                await fetchStatus();
                showQrModal(name);
            } catch (err) {
                alert("Failed to submit peer: " + err);
            }
        }

        async function deletePeer(peerName) {
            if (!confirm(`Are you sure you want to delete peer '${peerName}'?`)) return;
            try {
                const res = await fetch(`/api/peers/${encodeURIComponent(peerName)}`, { method: 'DELETE' });
                if (res.ok) {
                    await fetchPeers();
                    await fetchStatus();
                } else {
                    const err = await res.json();
                    alert("Failed to delete peer: " + err.detail);
                }
            } catch (err) {
                alert("Error deleting peer: " + err);
            }
        }

        async function showQrModal(peerName) {
            try {
                document.getElementById('qrModalTitle').textContent = `WireGuard Config - ${peerName}`;
                const qrRes = await fetch(`/api/peers/${encodeURIComponent(peerName)}/qr`);
                const qrData = await qrRes.json();

                const confRes = await fetch(`/api/peers/${encodeURIComponent(peerName)}/config`);
                const confText = await confRes.text();

                document.getElementById('qrImage').src = qrData.qr_url;
                document.getElementById('confText').textContent = confText;

                const downloadLink = document.getElementById('downloadConfLink');
                downloadLink.href = `/api/peers/${encodeURIComponent(peerName)}/download`;
                downloadLink.download = `${peerName}.conf`;

                document.getElementById('qrModal').classList.add('active');
            } catch (err) {
                alert("Failed to load QR code/config: " + err);
            }
        }

        function copyConfText() {
            const text = document.getElementById('confText').textContent;
            navigator.clipboard.writeText(text).then(() => {
                alert("Configuration copied to clipboard!");
            });
        }

        function escapeHtml(str) {
            if (!str) return '';
            return String(str)
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }

        async function loadPresets() {
            try {
                const res = await fetch('/api/presets');
                const presets = await res.json();
                const container = document.getElementById('presetsContainer');
                if (!container) return;
                container.innerHTML = presets.map(p => `
                    <button type="button" class="btn btn-secondary btn-sm" style="padding: 3px 8px; font-size: 0.75rem;" onclick="appendPreset('${escapeHtml(p.ports)}')">
                        ${p.icon} ${escapeHtml(p.name)} (${escapeHtml(p.ports)})
                    </button>
                `).join('');
            } catch (err) {
                console.error("Failed to load presets:", err);
            }
        }

        function appendPreset(portsStr) {
            const input = document.getElementById('peerPorts');
            const val = input.value.trim();
            if (!val) {
                input.value = portsStr;
            } else {
                if (!val.includes(portsStr)) {
                    input.value = `${val}, ${portsStr}`;
                }
            }
        }

        async function fetchChatMessages() {
            try {
                const res = await fetch('/api/chat/messages');
                const msgs = await res.json();
                const container = document.getElementById('chatMessages');
                if (!container) return;
                if (!msgs || msgs.length === 0) {
                    container.innerHTML = '<div style="color: var(--text-muted); text-align: center; margin-top: 40px;">No messages yet. Send a message to get started!</div>';
                    return;
                }
                const isScrolledToBottom = container.scrollHeight - container.clientHeight <= container.scrollTop + 50;
                container.innerHTML = msgs.map(m => `
                    <div style="background: rgba(255,255,255,0.03); padding: 8px 12px; border-radius: 6px; border-left: 3px solid var(--primary);">
                        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted); margin-bottom: 2px;">
                            <strong style="color: #6ee7b7;">${escapeHtml(m.sender)}</strong>
                            <span>${escapeHtml(m.timestamp)}</span>
                        </div>
                        <div style="color: var(--text-main); word-break: break-word;">${escapeHtml(m.message)}</div>
                    </div>
                `).join('');
                if (isScrolledToBottom) {
                    container.scrollTop = container.scrollHeight;
                }
            } catch (err) {
                console.error("Failed to fetch chat:", err);
            }
        }

        async function handleSendChat(e) {
            e.preventDefault();
            const sender = document.getElementById('chatSender').value.trim();
            const message = document.getElementById('chatInput').value.trim();
            if (!sender || !message) return;

            try {
                await fetch('/api/chat/messages', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sender, message })
                });
                document.getElementById('chatInput').value = '';
                fetchChatMessages();
            } catch (err) {
                alert("Failed to send message: " + err);
            }
        }

        async function fetchSharedFiles() {
            try {
                const res = await fetch('/api/files');
                const files = await res.json();
                const container = document.getElementById('filesList');
                if (!container) return;
                if (!files || files.length === 0) {
                    container.innerHTML = '<div style="color: var(--text-muted); text-align: center; margin-top: 40px;">No shared files yet. Click "+ Upload File" to share mods, maps, or configs.</div>';
                    return;
                }
                container.innerHTML = files.map(f => `
                    <div style="display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.03); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05);">
                        <div style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-right: 8px;">
                            <div style="font-weight: 500; color: var(--text-main);">${escapeHtml(f.filename)}</div>
                            <div style="font-size: 0.75rem; color: var(--text-muted);">${escapeHtml(f.size_formatted)} • Uploaded by ${escapeHtml(f.uploader)}</div>
                        </div>
                        <div style="display: flex; gap: 6px; flex-shrink: 0;">
                            <a href="/api/files/download/${f.id}" class="btn btn-secondary btn-sm" style="padding: 2px 8px; font-size: 0.75rem;" download>⬇️ Download</a>
                            <button class="btn btn-danger btn-sm" style="padding: 2px 8px; font-size: 0.75rem;" onclick="deleteSharedFile(${f.id})">&times;</button>
                        </div>
                    </div>
                `).join('');
            } catch (err) {
                console.error("Failed to fetch files:", err);
            }
        }

        async function handleFileUpload(e) {
            const file = e.target.files[0];
            if (!file) return;
            const formData = new FormData();
            formData.append('file', file);
            const uploader = document.getElementById('chatSender').value || 'Admin';

            try {
                await fetch(`/api/files/upload?uploader=${encodeURIComponent(uploader)}`, {
                    method: 'POST',
                    body: formData
                });
                e.target.value = '';
                fetchSharedFiles();
            } catch (err) {
                alert("Failed to upload file: " + err);
            }
        }

        async function deleteSharedFile(id) {
            if (!confirm("Are you sure you want to delete this shared file?")) return;
            try {
                await fetch(`/api/files/${id}`, { method: 'DELETE' });
                fetchSharedFiles();
            } catch (err) {
                alert("Failed to delete file: " + err);
            }
        }

        // Initial Load
        fetchStatus();
        fetchPeers();
        loadPresets();
        fetchChatMessages();
        fetchSharedFiles();
        setInterval(fetchStatus, 10000);
        setInterval(fetchChatMessages, 3000);
        setInterval(fetchSharedFiles, 10000);
    </script>
</body>
</html>
"""
