class AuthManager {
    constructor() {
        this.token = localStorage.getItem("authToken");
        this.user = JSON.parse(localStorage.getItem("user") || "null");
    }

    async register(email, password, fullName) {
        const response = await fetch("/api/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                email,
                password,
                full_name: fullName
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Registration failed");
        }

        const data = await response.json();
        this.setToken(data.access_token);
        this.setUser(data.user);
        return data;
    }

    async login(email, password) {
        const response = await fetch("/api/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Login failed");
        }

        const data = await response.json();
        this.setToken(data.access_token);
        this.setUser(data.user);
        return data;
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem("authToken", token);
    }

    setUser(user) {
        this.user = user;
        localStorage.setItem("user", JSON.stringify(user));
    }

    logout() {
        this.token = null;
        this.user = null;
        localStorage.removeItem("authToken");
        localStorage.removeItem("user");
    }

    isAuthenticated() {
        return !!this.token;
    }

    getAuthHeader() {
        return {
            "Authorization": `Bearer ${this.token}`,
            "Content-Type": "application/json"
        };
    }
}

const auth = new AuthManager();

// UI Functions
function switchToRegister(e) {
    e.preventDefault();
    document.getElementById("login-form").style.display = "none";
    document.getElementById("register-form").style.display = "block";
    document.getElementById("auth-error").style.display = "none";
}

function switchToLogin(e) {
    e.preventDefault();
    document.getElementById("register-form").style.display = "none";
    document.getElementById("login-form").style.display = "block";
    document.getElementById("auth-error").style.display = "none";
}

function showAuthError(message) {
    const errorEl = document.getElementById("auth-error");
    errorEl.textContent = message;
    errorEl.style.display = "block";
}

function hideAuthError() {
    document.getElementById("auth-error").style.display = "none";
}

function showLoading(show = true) {
    document.getElementById("auth-loading").style.display = show ? "block" : "none";
}

// Initialize auth page
document.addEventListener("DOMContentLoaded", () => {
    // If already logged in, show message instead of auto-redirecting (to prevent loops)
    if (auth.isAuthenticated()) {
        console.log("User is authenticated. Token:", auth.token);

        // Hide forms and show "Already logged in" message
        document.getElementById("login-form").style.display = "none";
        document.getElementById("register-form").style.display = "none";

        const container = document.querySelector(".auth-box");
        const msgDiv = document.createElement("div");
        msgDiv.className = "auth-form";
        msgDiv.innerHTML = `
            <h2>Welcome Back!</h2>
            <p>You are already logged in.</p>
            <button class="btn btn-primary" onclick="window.location.href='/dashboard.html'">Go to Dashboard</button>
            <button class="btn btn-secondary" onclick="auth.logout(); window.location.reload();" style="margin-top: 10px;">Logout</button>
        `;
        container.appendChild(msgDiv);

        return;
    }

    // Setup login button
    document.getElementById("login-btn").addEventListener("click", async () => {
        const email = document.getElementById("login-email").value;
        const password = document.getElementById("login-password").value;

        if (!email || !password) {
            showAuthError("Please fill in all fields");
            return;
        }

        showLoading(true);
        hideAuthError();

        try {
            await auth.login(email, password);
            window.location.href = "/dashboard.html";
        } catch (err) {
            showAuthError(err.message);
        } finally {
            showLoading(false);
        }
    });

    // Setup register button
    document.getElementById("register-btn").addEventListener("click", async () => {
        const email = document.getElementById("register-email").value;
        const password = document.getElementById("register-password").value;
        const fullName = document.getElementById("register-name").value;

        if (!email || !password || !fullName) {
            showAuthError("Please fill in all fields");
            return;
        }

        showLoading(true);
        hideAuthError();

        try {
            await auth.register(email, password, fullName);
            window.location.href = "/dashboard.html";
        } catch (err) {
            showAuthError(err.message);
        } finally {
            showLoading(false);
        }
    });

    // Handle Enter key
    document.getElementById("login-password").addEventListener("keypress", (e) => {
        if (e.key === "Enter") document.getElementById("login-btn").click();
    });

    document.getElementById("register-password").addEventListener("keypress", (e) => {
        if (e.key === "Enter") document.getElementById("register-btn").click();
    });
});
