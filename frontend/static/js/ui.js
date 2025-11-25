function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = "flex";
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = "none";
    }
}

function showError(message) {
    const errorEl = document.getElementById("error-toast");
    errorEl.textContent = message;
    errorEl.style.display = "block";

    setTimeout(() => {
        errorEl.style.display = "none";
    }, 4000);
}

function showSuccess(message) {
    const successEl = document.getElementById("success-toast");
    successEl.textContent = message;
    successEl.style.display = "block";

    setTimeout(() => {
        successEl.style.display = "none";
    }, 4000);
}

// Close modals when clicking outside
document.addEventListener("click", (e) => {
    if (e.target.classList.contains("modal")) {
        e.target.style.display = "none";
    }
});

// Handle escape key
document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
        document.querySelectorAll(".modal").forEach(modal => {
            modal.style.display = "none";
        });
    }
});
