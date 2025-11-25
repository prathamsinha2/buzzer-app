class BuzzerApp {
    constructor() {
        this.currentGroup = null;
        this.groups = [];
        this.devices = [];
        this.myDevices = [];
    }

    toggleSidebar() {
        const sidebar = document.getElementById("sidebar");
        sidebar.classList.toggle("open");

        // Create or toggle overlay
        let overlay = document.getElementById("sidebar-overlay");
        if (!overlay) {
            overlay = document.createElement("div");
            overlay.id = "sidebar-overlay";
            overlay.className = "sidebar-overlay";
            overlay.onclick = () => this.toggleSidebar();
            document.body.appendChild(overlay);
        }

        if (sidebar.classList.contains("open")) {
            overlay.style.display = "block";
        } else {
            overlay.style.display = "none";
        }
    }

    async init() {
        // Check authentication
        if (!auth.isAuthenticated()) {
            console.log("Not authenticated, redirecting to login");
            auth.logout(); // Ensure token is cleared
            window.location.href = "/";
            return;
        }

        console.log("Initializing Buzzer App");

        // Set user name in sidebar
        if (auth.user && auth.user.full_name) {
            document.getElementById("current-user-name").textContent = auth.user.full_name;
        }

        try {
            // Register device
            await deviceManager.registerDevice(auth.token);
            console.log("Device registered:", deviceManager.deviceId);

            // Initialize WebSocket
            wsClient = new WebSocketClient(deviceManager.deviceId, auth.token);
            this.setupWebSocketHandlers();
            wsClient.connect();

            // Initialize Notifications
            const notificationsEnabled = await notificationManager.init();
            if (!notificationsEnabled && 'Notification' in window && Notification.permission !== 'granted') {
                document.getElementById('notification-permission-area').style.display = 'block';
            }

            // Load groups and devices
            await this.loadGroups();

            // Default view
            this.showMyDevices();

            // Setup event listeners
            this.setupEventListeners();

            console.log("App initialized successfully");
        } catch (error) {
            console.error("Failed to initialize app:", error);
            showError("Failed to initialize app: " + error.message);
        }
    }

    showMyDevices() {
        this.currentGroup = null;

        // Update UI
        document.getElementById("view-my-devices").style.display = "block";
        document.getElementById("view-group").style.display = "none";
        document.getElementById("page-title").textContent = "My Devices";

        // Update Sidebar Active State
        document.querySelectorAll(".nav-item").forEach(el => el.classList.remove("active"));
        document.getElementById("nav-my-devices").classList.add("active");

        this.loadMyDevices();
    }

    async showGroup(groupId) {
        this.currentGroup = groupId;
        const group = this.groups.find(g => g.id === groupId);

        // Update UI
        document.getElementById("view-my-devices").style.display = "none";
        document.getElementById("view-group").style.display = "block";
        document.getElementById("page-title").textContent = group ? "# " + group.name : "Group";
        document.getElementById("current-group-code").textContent = group ? `Code: ${group.invite_code}` : "";

        // Update Sidebar Active State
        document.querySelectorAll(".nav-item").forEach(el => el.classList.remove("active"));
        const groupNavItem = document.getElementById(`nav-group-${groupId}`);
        if (groupNavItem) groupNavItem.classList.add("active");

        this.loadGroupDevices(groupId);
    }

    setupWebSocketHandlers() {
        // Handle ring command (now just a visual buzz)
        wsClient.on("ring_command", async (data) => {
            console.log("Received buzz:", data);

            // Show visual overlay
            this.showRingingUI(data);

            // Send confirmation
            wsClient.send({
                type: "ring_started",
                ring_session_id: data.ring_session_id,
                device_id: deviceManager.deviceId
            });
        });

        // Handle stop command
        wsClient.on("stop_command", (data) => {
            this.hideRingingUI();
        });

        // Handle device status updates
        wsClient.on("device_status_changed", (data) => {
            console.log("Device status changed:", data);
            this.updateDeviceStatus(data.device_id, data.online);
        });
    }

    async loadGroups() {
        try {
            const response = await fetch("/api/groups/", {
                headers: auth.getAuthHeader()
            });

            if (!response.ok) throw new Error("Failed to load groups");

            this.groups = await response.json();
            this.renderGroups();
        } catch (error) {
            console.error("Failed to load groups:", error);
            showError("Failed to load groups");
        }
    }

    async loadMyDevices() {
        const container = document.getElementById("my-devices-container");
        container.innerHTML = '<div class="loading">Loading your devices...</div>';

        try {
            const response = await fetch("/api/devices/", {
                headers: auth.getAuthHeader()
            });

            if (!response.ok) throw new Error("Failed to load devices");

            this.myDevices = await response.json();
            this.renderMyDevices();
        } catch (error) {
            console.error("Failed to load devices:", error);
            container.innerHTML = '<div class="empty-state">Failed to load devices</div>';
        }
    }

    async loadGroupDevices(groupId) {
        const container = document.getElementById("group-devices-container");
        container.innerHTML = '<div class="loading">Loading devices...</div>';

        try {
            const response = await fetch(`/api/devices/group/${groupId}`, {
                headers: auth.getAuthHeader()
            });

            if (!response.ok) throw new Error("Failed to load group devices");

            this.devices = await response.json();
            this.renderGroupDevices();
        } catch (error) {
            console.error("Failed to load group devices:", error);
            container.innerHTML = '<div class="empty-state">Failed to load devices</div>';
        }
    }

    renderGroups() {
        const container = document.getElementById("groups-list");
        if (!this.groups || this.groups.length === 0) {
            container.innerHTML = '<div style="padding: 8px 12px; font-size: 13px; color: #666;">No groups yet</div>';
            return;
        }

        container.innerHTML = this.groups.map(group => `
            <div class="nav-item ${this.currentGroup === group.id ? 'active' : ''}"
                 id="nav-group-${group.id}"
                 onclick="app.showGroup(${group.id})">
                <span class="nav-icon">#</span> ${group.name}
            </div>
        `).join("");
    }

    renderGroupDevices() {
        const container = document.getElementById("group-devices-container");
        if (!this.devices || this.devices.length === 0) {
            container.innerHTML = '<div class="empty-state">No devices in this group</div>';
            return;
        }

        container.innerHTML = this.devices.map(device => this.createDeviceCard(device)).join("");
    }

    renderMyDevices() {
        const container = document.getElementById("my-devices-container");
        if (!this.myDevices || this.myDevices.length === 0) {
            container.innerHTML = '<div class="empty-state">You have no registered devices</div>';
            return;
        }

        container.innerHTML = this.myDevices.map(device => this.createDeviceCard(device, true)).join("");
    }

    createDeviceCard(device, isMyDevice = false) {
        const isMe = device.user_id === auth.user.id;

        return `
            <div class="device-item">
                <div class="device-header">
                    <div class="device-info">
                        <h4>${device.device_name}</h4>
                        ${device.user_name ? `<div class="device-owner">${device.user_name} ${isMe ? '(You)' : ''}</div>` : ''}
                    </div>
                    <span class="device-status ${device.is_online ? 'status-online-device' : 'status-offline-device'}">
                        ${device.is_online ? "Online" : "Offline"}
                    </span>
                </div>

                <div class="device-actions">
                    ${isMe ?
                (isMyDevice ?
                    `<div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px;">
                        <button class="btn btn-primary btn-sm" onclick="app.notifyDevice(${device.id}, '${device.device_name}')">Buzz</button>
                        <button class="btn btn-danger btn-sm" onclick="app.deleteDevice(${device.id})">Delete</button>
                     </div>`
                    : '<button class="btn btn-secondary btn-sm" disabled>Your Device</button>')
                :
                (device.is_online ?
                    `<button class="btn btn-primary btn-block" onclick="app.notifyDevice(${device.id}, '${device.device_name}')">Buzz</button>` :
                    `<button class="btn btn-secondary btn-block" disabled>Offline</button>`
                )
            }
                </div>
            </div>
        `;
    }

    async notifyDevice(deviceId, deviceName) {
        try {
            const response = await fetch("/api/rings/start", {
                method: "POST",
                headers: auth.getAuthHeader(),
                body: JSON.stringify({
                    target_device_id: deviceId,
                    duration_seconds: 5 // Default short duration for the record
                })
            });

            if (!response.ok) throw new Error("Failed to buzz device");

            showSuccess(`Buzzed ${deviceName}!`);
        } catch (error) {
            console.error("Failed to buzz device:", error);
            showError(error.message);
        }
    }

    showRingingUI(data) {
        const overlay = document.getElementById("ringing-overlay");
        const message = document.getElementById("ringing-message");
        const stopBtn = document.getElementById("stop-ring-btn");

        message.textContent = `${data.initiator_name || 'Someone'} buzzed you!`;
        overlay.style.display = "flex";

        // Setup dismiss button
        stopBtn.onclick = () => {
            this.hideRingingUI();
            // Optional: Tell server we dismissed it
        };

        // Auto-hide after 5 seconds
        setTimeout(() => {
            this.hideRingingUI();
        }, 5000);
    }

    hideRingingUI() {
        document.getElementById("ringing-overlay").style.display = "none";
    }

    updateDeviceStatus(deviceId, online) {
        // Update devices in list
        const device = this.devices.find(d => d.device_id === deviceId);
        if (device) {
            device.is_online = online;
            this.renderGroupDevices();
        }

        // Update my devices
        const myDevice = this.myDevices.find(d => d.device_id === deviceId);
        if (myDevice) {
            myDevice.is_online = online;
            this.renderMyDevices();
        }
    }

    async deleteDevice(deviceId) {
        if (!confirm("Delete this device?")) return;

        try {
            const response = await fetch(`/api/devices/${deviceId}`, {
                method: "DELETE",
                headers: auth.getAuthHeader()
            });

            if (!response.ok) throw new Error("Failed to delete device");

            showSuccess("Device deleted");
            await this.loadMyDevices();
        } catch (error) {
            console.error("Failed to delete device:", error);
            showError(error.message);
        }
    }

    async leaveGroup(groupId) {
        if (!confirm("Leave this group?")) return;

        try {
            const response = await fetch(`/api/groups/${groupId}/leave`, {
                method: "POST",
                headers: auth.getAuthHeader()
            });

            if (!response.ok) throw new Error("Failed to leave group");

            showSuccess("Left group");
            await this.loadGroups();
            if (this.currentGroup === groupId) {
                this.currentGroup = null;
                document.getElementById("group-devices-container").innerHTML =
                    '<div class="empty-state">Select a group to see devices</div>';
            }
        } catch (error) {
            console.error("Failed to leave group:", error);
            showError(error.message);
        }
    }

    async createGroup() {
        const name = document.getElementById("group-name-input").value;
        if (!name) {
            showError("Group name required");
            return;
        }

        try {
            const response = await fetch("/api/groups/create", {
                method: "POST",
                headers: auth.getAuthHeader(),
                body: JSON.stringify({ name })
            });

            if (!response.ok) throw new Error("Failed to create group");

            showSuccess("Group created");
            closeModal("create-group-modal");
            document.getElementById("group-name-input").value = "";
            await this.loadGroups();
        } catch (error) {
            showError(error.message);
        }
    }

    async joinGroup() {
        const code = document.getElementById("invite-code-input").value;
        if (!code) {
            showError("Invite code required");
            return;
        }

        try {
            const response = await fetch("/api/groups/join", {
                method: "POST",
                headers: auth.getAuthHeader(),
                body: JSON.stringify({ invite_code: code })
            });

            if (!response.ok) throw new Error("Failed to join group");

            showSuccess("Joined group");
            closeModal("join-group-modal");
            document.getElementById("invite-code-input").value = "";
            await this.loadGroups();
        } catch (error) {
            showError(error.message);
        }
    }

    setupEventListeners() {
        // Logout
        document.getElementById("logout-btn").addEventListener("click", () => {
            auth.logout();
            window.location.href = "/";
        });

        // Create group (Open Modal)
        document.getElementById("create-group-btn").addEventListener("click", () => {
            openModal("create-group-modal");
        });

        // Join group (Open Modal)
        document.getElementById("join-group-btn").addEventListener("click", () => {
            openModal("join-group-modal");
        });
    }
}

const app = new BuzzerApp();

// Initialize when page loads
document.addEventListener("DOMContentLoaded", () => {
    app.init();
});
