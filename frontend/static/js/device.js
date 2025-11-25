class DeviceManager {
    constructor() {
        this.deviceId = this.getOrCreateDeviceId();
        this.deviceInfo = this.collectDeviceInfo();
    }

    getOrCreateDeviceId() {
        let deviceId = localStorage.getItem("deviceId");
        if (!deviceId) {
            deviceId = this.generateUUID();
            localStorage.setItem("deviceId", deviceId);
        }
        return deviceId;
    }

    generateUUID() {
        return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
            const r = Math.random() * 16 | 0;
            const v = c === "x" ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    collectDeviceInfo() {
        return {
            userAgent: navigator.userAgent,
            platform: navigator.platform,
            language: navigator.language,
            screenWidth: window.screen.width,
            screenHeight: window.screen.height,
            standalone: window.navigator.standalone || window.matchMedia("(display-mode: standalone)").matches
        };
    }

    async registerDevice(token) {
        const deviceName = this.getDefaultDeviceName();

        const response = await fetch("/api/devices/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                device_id: this.deviceId,
                device_name: deviceName,
                device_info: this.deviceInfo
            })
        });

        if (!response.ok) {
            throw new Error("Failed to register device");
        }

        return await response.json();
    }

    getDefaultDeviceName() {
        const ua = navigator.userAgent;
        if (ua.includes("iPhone")) return "iPhone";
        if (ua.includes("iPad")) return "iPad";
        return "Device";
    }
}

const deviceManager = new DeviceManager();
