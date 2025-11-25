const notificationManager = {
    publicKey: null,
    subscription: null,

    async init() {
        if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
            console.log('Push messaging is not supported');
            return false;
        }

        // Register Service Worker
        try {
            const registration = await navigator.serviceWorker.register('/service-worker.js');
            console.log('Service Worker registered:', registration);
        } catch (error) {
            console.error('Service Worker registration failed:', error);
            return false;
        }

        // Check current permission
        if (Notification.permission === 'granted') {
            this.subscribeUser();
        }

        return true;
    },

    async requestPermission() {
        // iOS Check: Must be in standalone mode for Push
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
        const isStandalone = window.navigator.standalone || window.matchMedia('(display-mode: standalone)').matches;

        if (isIOS && !isStandalone) {
            alert("On iPhone, you must add this app to your Home Screen to enable notifications.\n\nTap Share (box with arrow) -> 'Add to Home Screen'");
            return false;
        }

        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
            await this.subscribeUser();
            return true;
        }
        return false;
    },

    async subscribeUser() {
        try {
            // Get VAPID public key from backend
            const response = await fetch('/api/notifications/vapid-public-key', {
                headers: auth.getAuthHeader()
            });
            const data = await response.json();
            this.publicKey = data.publicKey;

            const registration = await navigator.serviceWorker.ready;

            // Subscribe
            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.urlBase64ToUint8Array(this.publicKey)
            });

            console.log('User is subscribed:', subscription);
            this.subscription = subscription;

            // Send subscription to backend
            await this.sendSubscriptionToBackend(subscription);

            // Update UI if needed (hide "Enable Notifications" button)
            const btn = document.getElementById('enable-notifications-btn');
            if (btn) btn.style.display = 'none';

        } catch (error) {
            console.error('Failed to subscribe the user: ', error);
        }
    },

    async sendSubscriptionToBackend(subscription) {
        try {
            await fetch('/api/notifications/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...auth.getAuthHeader()
                },
                body: JSON.stringify({
                    device_id: deviceManager.deviceId,
                    subscription: subscription
                })
            });
            console.log('Subscription sent to server');
        } catch (error) {
            console.error('Error sending subscription to server:', error);
        }
    },

    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/\-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }
};
