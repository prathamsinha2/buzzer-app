class AudioManager {
    constructor() {
        this.audio = new Audio("/static/audio/ringtone.wav");
        this.audio.loop = true;
        this.audio.preload = "auto";
        this.isPlaying = false;
        this.unlocked = false;
        this.wakeLock = null;

        // iOS audio unlock - must happen on user interaction
        this.initAudioUnlock();
    }

    // CRITICAL FOR iOS: Audio must be unlocked by user interaction
    initAudioUnlock() {
        const unlock = () => {
            if (this.unlocked) return;

            // Mute before unlocking
            this.audio.volume = 0;

            // Try to play and immediately pause to "unlock" audio on iOS
            const playPromise = this.audio.play();
            if (playPromise !== undefined) {
                playPromise
                    .then(() => {
                        this.audio.pause();
                        this.audio.currentTime = 0;
                        this.unlocked = true;
                        console.log("Audio unlocked for iOS");

                        // Remove listeners after unlock
                        document.body.removeEventListener("touchstart", unlock);
                        document.body.removeEventListener("click", unlock);
                    })
                    .catch((err) => {
                        console.log("Audio unlock failed:", err);
                    });
            }
        };

        // Listen for ANY user interaction
        document.body.addEventListener("touchstart", unlock, { once: false });
        document.body.addEventListener("click", unlock, { once: false });
    }

    async startRinging(duration = null) {
        if (!this.unlocked) {
            console.error("Audio not unlocked - user interaction required");
            return false;
        }

        try {
            this.audio.currentTime = 0;
            await this.audio.play();
            this.isPlaying = true;

            // Set maximum volume
            this.audio.volume = 1.0;

            console.log("Ringing started. Duration:", duration, "seconds");

            // Auto-stop after duration if specified
            if (duration && duration > 0) {
                setTimeout(() => {
                    this.stopRinging();
                }, duration * 1000);
            }

            // Request Wake Lock to prevent screen sleep
            await this.requestWakeLock();

            return true;
        } catch (error) {
            console.error("Failed to start ringing:", error);
            return false;
        }
    }

    stopRinging() {
        try {
            this.audio.pause();
            this.audio.currentTime = 0;
            this.isPlaying = false;
            this.releaseWakeLock();
            console.log("Ringing stopped");
        } catch (error) {
            console.error("Error stopping ringing:", error);
        }
    }

    async requestWakeLock() {
        if ("wakeLock" in navigator) {
            try {
                this.wakeLock = await navigator.wakeLock.request("screen");
                console.log("Wake lock acquired");
            } catch (err) {
                console.log("Wake lock error:", err);
            }
        }
    }

    releaseWakeLock() {
        if (this.wakeLock) {
            this.wakeLock.release();
            this.wakeLock = null;
            console.log("Wake lock released");
        }
    }

    // Ensure audio unlocks when page becomes visible
    setupVisibilityHandler() {
        document.addEventListener("visibilitychange", () => {
            if (!document.hidden && !this.unlocked) {
                // Page became visible - we still need user interaction to unlock
                console.log("Page visible, waiting for interaction to unlock audio");
            }
        });
    }
}

const audioManager = new AudioManager();

// Setup visibility handler
document.addEventListener("DOMContentLoaded", () => {
    audioManager.setupVisibilityHandler();
});
