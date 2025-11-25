class BuzzerApp {
    constructor() {
        this.currentGroup = null;
        this.groups = [];
        this.devices = [];
        this.myDevices = [];
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

        try {
            // Register device
            await deviceManager.registerDevice(auth.token);
            console.log("Device registered:", deviceManager.deviceId);

            // Initialize WebSocket
            wsClient = new WebSocketClient(deviceManager.deviceId, auth.token);
            this.setupWebSocketHandlers();
            wsClient.connect();

            // Load groups and devices
            await this.loadGroups();
            await this.loadMyDevices();

            // Setup event listeners
            this.setupEventListeners();

            console.log("App initialized successfully");
        } catch (error) {
            console.error("Failed to initialize app:", error);
            showError("Failed to initialize app: " + error.message);
        }
    }

    setupWebSocketHandlers() {
        // Handle ring command
        wsClient.on("ring_command", async (data) => {
            console.log("Received ring command:", data);
            const success = await audioManager.startRinging(data.duration);

            if (success) {
                this.showRingingUI(data);

                // Send confirmation
                wsClient.send({
                    type: "ring_started",
                    ring_session_id: data.ring_session_id,
                    device_id: deviceManager.deviceId
                });

                // If there's a duration, timer is already set in audio manager
                // Just wait for it to complete
            }
        });

        // Handle stop command
        wsClient.on("stop_command", (data) => {
            console.log("Received stop command:", data);
            audioManager.stopRinging();
            this.hideRingingUI();

            wsClient.send({
                type: "ring_stopped",
                ring_session_id: data.ring_session_id,
                device_id: deviceManager.deviceId
            });
        });

        // Handle device status updates
        wsClient.on("device_status_changed", (data) => {
            console.log("Device status changed:", data);
            this.updateDeviceStatus(data.device_id, data.online);
        });

        // Handle pong (heartbeat response)
        wsClient.on("pong", (data) => {
            console.log("Pong received");
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
        try {
            const response = await fetch("/api/devices/", {
                headers: auth.getAuthHeader()
            });

            if (!response.ok) throw new Error("Failed to load devices");

            this.myDevices = await response.json();
            this.renderMyDevices();
        } catch (error) {
            console.error("Failed to load devices:", error);
            showError("Failed to load devices");
        }
    }

    async loadGroupDevices(groupId) {
        try {
            const response = await fetch(`/api/devices/group/${groupId}`, {
                headers: auth.getAuthHeader()
            });

            if (!response.ok) throw new Error("Failed to load group devices");

            this.devices = await response.json();
            this.renderGroupDevices();
        } catch (error) {
            console.error("Failed to load group devices:", error);
            showError("Failed to load group devices");
        }
    }

    renderGroups() {
        const container = document.getElementById("groups-container");
        if (!this.groups || this.groups.length === 0) {
            container.innerHTML = '<div class="empty-state">No groups yet</div>';
            return;
        }

        container.innerHTML = this.groups.map(group => `
            <div class="group-item" onclick="app.selectGroup(${group.id}, '${group.name}')">
                <div class="group-name">${group.name}</div>
                <div class="group-code">Code: ${group.invite_code}</div>
                <div class="group-member-count">${group.members.length} member(s)</div>
                ${group.owner_id === auth.user.id ?
                '<button class="group-action-btn" onclick="event.stopPropagation(); app.leaveGroup(' + group.id + ')">Leave</button>' :
                ''}
            </div>
        `).join("");
    }

    renderGroupDevices() {
        const container = document.getElementById("devices-container");
        if (!this.devices || this.devices.length === 0) {
            container.innerHTML = '<div class="empty-state">No devices in this group</div>';
            return;
        }

        container.innerHTML = this.devices.map(device => `
            <div class="device-item">
                <div class="device-info">
                    <div class="device-name">${device.device_name}</div>
                    <span class="device-status ${device.is_online ? 'status-online-device' : 'status-offline-device'}">
                        ${device.is_online ? "Online" : "Offline"}
                    </span>
                </div>
                <div class="device-actions">
                    ${device.is_online ?
                `<button class="btn btn-primary" onclick="app.ringDevice(${device.id}, '${device.device_name}')">Ring</button>` :
                '<button class="btn btn-secondary" disabled>Offline</button>'}
                </div>
            </div>
        `).join("");
    }

    renderMyDevices() {
        const container = document.getElementById("my-devices-container");
        if (!this.myDevices || this.myDevices.length === 0) {
            container.innerHTML = '<div class="empty-state">No devices registered</div>';
            return;
        }

        container.innerHTML = this.myDevices.map(device => `
            <div class="device-item">
                <div class="device-info">
                    <div class="device-name">${device.device_name}</div>
                    <span class="device-status ${device.is_online ? 'status-online-device' : 'status-offline-device'}">
                        ${device.is_online ? "Online" : "Offline"}
                    </span>
                </div>
                <div class="device-actions">
                    <button class="btn btn-secondary" onclick="app.deleteDevice(${device.id})">Delete</button>
                </div>
            </div>
        `).join("");
    }

    selectGroup(groupId, groupName) {
        this.currentGroup = groupId;
        document.querySelectorAll(".group-item").forEach(el => {
            el.style.borderColor = el.dataset.groupId == groupId ? "#007AFF" : "#eee";
        });
        this.loadGroupDevices(groupId);
    }

    async ringDevice(deviceId, deviceName) {
        // Show ring options modal
        document.getElementById("ring-device-name").textContent = "Ring " + deviceName;
        const modal = document.getElementById("ring-options-modal");
        openModal("ring-options-modal");

        // Handle ring option selection
        const handleRingOption = async (duration) => {
            document.querySelectorAll(".ring-option-btn").forEach(btn => {
                btn.removeEventListener("click", handleRingOption);
            });

            const durationSeconds = duration === "null" ? null : parseInt(duration);
            await this.initiateRing(deviceId, durationSeconds);
            closeModal("ring-options-modal");
        };

        document.querySelectorAll(".ring-option-btn").forEach(btn => {
            btn.onclick = async () => {
                const duration = btn.dataset.duration;
                await handleRingOption(duration);
            };
        });
    }

    async initiateRing(deviceId, duration) {
        try {
            const response = await fetch("/api/rings/start", {
                method: "POST",
                headers: auth.getAuthHeader(),
                body: JSON.stringify({
                    target_device_id: deviceId,
                    duration_seconds: duration
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || "Failed to ring device");
            }

            showSuccess("Ringing device...");
        } catch (error) {
            console.error("Failed to ring device:", error);
            showError(error.message);
        }
    }

    showRingingUI(data) {
        const overlay = document.getElementById("ringing-overlay");
        overlay.style.display = "flex";

        const message = document.getElementById("ringing-message");
        message.textContent = "Someone is ringing you!";

        const stopBtn = document.getElementById("stop-ring-btn");
        stopBtn.onclick = () => {
            audioManager.stopRinging();
            this.hideRingingUI();

            wsClient.send({
                type: "ring_stopped",
                ring_session_id: data.ring_session_id,
                device_id: deviceManager.deviceId
            });
        };
    }

    hideRingingUI() {
        const overlay = document.getElementById("ringing-overlay");
        overlay.style.display = "none";
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
                document.getElementById("devices-container").innerHTML =
                    '<div class="empty-state">Select a group to see devices</div>';
            }
        } catch (error) {
            console.error("Failed to leave group:", error);
            showError(error.message);
        }
    }

    setupEventListeners() {
        // Logout
        document.getElementById("logout-btn").addEventListener("click", () => {
            auth.logout();
            window.location.href = "/";
        });

        // Create group
        document.getElementById("create-group-btn").addEventListener("click", () => {
            openModal("create-group-modal");
        });

        document.getElementById("create-group-submit").addEventListener("click", async () => {
            const name = document.getElementById("group-name").value;
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
                document.getElementById("group-name").value = "";
                await this.loadGroups();
            } catch (error) {
                showError(error.message);
            }
        });

        // Join group
        document.getElementById("join-group-btn").addEventListener("click", () => {
            openModal("join-group-modal");
        });

        document.getElementById("join-group-submit").addEventListener("click", async () => {
            const code = document.getElementById("invite-code").value;
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
                document.getElementById("invite-code").value = "";
                await this.loadGroups();
            } catch (error) {
                showError(error.message);
            }
        });
    }
}

const app = new BuzzerApp();

// Initialize when page loads
document.addEventListener("DOMContentLoaded", () => {
    app.init();
});
