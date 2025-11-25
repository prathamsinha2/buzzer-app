class WebSocketClient {
    constructor(deviceId, token) {
        this.deviceId = deviceId;
        this.token = token;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 3000;
        this.messageHandlers = {};
        this.heartbeatInterval = null;
    }

    connect() {
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const wsUrl = `${protocol}//${window.location.host}/ws/${this.deviceId}?token=${this.token}`;

        console.log("Connecting to WebSocket:", wsUrl);
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log("WebSocket connected");
            this.reconnectAttempts = 0;
            this.onConnectionChange(true);
            this.startHeartbeat();
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log("WebSocket message received:", data);
                this.handleMessage(data);
            } catch (e) {
                console.error("Error parsing WebSocket message:", e);
            }
        };

        this.ws.onclose = () => {
            console.log("WebSocket disconnected");
            this.stopHeartbeat();
            this.onConnectionChange(false);
            this.attemptReconnect();
        };

        this.ws.onerror = (error) => {
            console.error("WebSocket error:", error);
        };
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);

            setTimeout(() => {
                this.connect();
            }, this.reconnectDelay);
        } else {
            console.error("Max reconnection attempts reached");
            this.onMaxReconnectAttemptsReached();
        }
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        } else {
            console.error("WebSocket not connected");
        }
    }

    handleMessage(data) {
        const handler = this.messageHandlers[data.type];
        if (handler) {
            handler(data);
        } else {
            console.log("Unhandled message type:", data.type);
        }
    }

    on(messageType, handler) {
        this.messageHandlers[messageType] = handler;
    }

    isConnected() {
        return this.ws && this.ws.readyState === WebSocket.OPEN;
    }

    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected()) {
                this.send({
                    type: "heartbeat",
                    deviceId: this.deviceId,
                    timestamp: new Date().toISOString()
                });
            }
        }, 30000); // 30 seconds
    }

    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }

    onConnectionChange(connected) {
        // Update UI to show connection status
        const statusEl = document.getElementById("connection-status");
        if (statusEl) {
            if (connected) {
                statusEl.textContent = "Connected";
                statusEl.className = "connection-status status-online";
            } else {
                statusEl.textContent = "Offline";
                statusEl.className = "connection-status status-offline";
            }
        }
    }

    onMaxReconnectAttemptsReached() {
        // Notify user and offer to reload
        const statusEl = document.getElementById("connection-status");
        if (statusEl) {
            statusEl.textContent = "Connection Lost";
        }
    }

    disconnect() {
        this.stopHeartbeat();
        if (this.ws) {
            this.ws.close();
        }
    }
}

let wsClient = null;
