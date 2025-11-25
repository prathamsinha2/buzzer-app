self.addEventListener('push', function (event) {
    let data = {};
    if (event.data) {
        data = event.data.json();
    }

    const title = data.title || 'Buzzer';
    const options = {
        body: data.body || 'You have a new notification',
        icon: data.icon || '/static/images/icon-192.png',
        badge: '/static/images/badge-72.png',
        vibrate: [200, 100, 200],
        data: {
            url: data.url || '/dashboard.html'
        }
    };

    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

self.addEventListener('notificationclick', function (event) {
    event.notification.close();

    event.waitUntil(
        clients.matchAll({ type: 'window' }).then(function (windowClients) {
            // Check if there is already a window/tab open with the target URL
            for (var i = 0; i < windowClients.length; i++) {
                var client = windowClients[i];
                // If so, just focus it.
                if (client.url.includes('dashboard.html') && 'focus' in client) {
                    return client.focus();
                }
            }
            // If not, open a new window/tab.
            if (clients.openWindow) {
                return clients.openWindow(event.notification.data.url);
            }
        })
    );
});
