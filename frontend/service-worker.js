const CACHE_NAME = "buzzer-v1";
const urlsToCache = [
    "/",
    "/index.html",
    "/dashboard.html",
    "/offline.html",
    "/manifest.json",
    "/static/css/main.css",
    "/static/css/dashboard.css",
    "/static/js/auth.js",
    "/static/js/app.js",
    "/static/js/device.js",
    "/static/js/websocket.js",
    "/static/js/audio.js",
    "/static/js/ui.js",
    "/static/audio/ringtone.wav",
    "/static/icons/icon-192x192.png",
    "/static/icons/icon-512x512.png"
];

// Install event
self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log("Opened cache");
            return cache.addAll(urlsToCache).catch((error) => {
                console.error("Cache.addAll error:", error);
                // Don't fail on cache errors
            });
        })
    );
});

// Fetch event - Cache first, fallback to network
self.addEventListener("fetch", (event) => {
    // Skip WebSocket requests
    if (event.request.url.startsWith("ws://") || event.request.url.startsWith("wss://")) {
        return;
    }

    event.respondWith(
        caches.match(event.request).then((response) => {
            // Cache hit - return response
            if (response) {
                return response;
            }

            // Clone the request
            const fetchRequest = event.request.clone();

            return fetch(fetchRequest).then((response) => {
                // Check if valid response
                if (!response || response.status !== 200 || response.type === "error") {
                    return response;
                }

                // Clone the response
                const responseToCache = response.clone();

                // Cache it
                caches.open(CACHE_NAME).then((cache) => {
                    cache.put(event.request, responseToCache);
                });

                return response;
            }).catch(() => {
                // Return offline page for navigation requests
                if (event.request.mode === "navigate") {
                    return caches.match("/offline.html");
                }
                return null;
            });
        })
    );
});

// Activate event - Clean up old caches
self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log("Deleting old cache:", cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});
