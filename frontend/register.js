const REGISTER_URL = "/auth/register";
const PENDING_VERIFY_EMAIL_KEY = "pending_verify_email";

document.addEventListener("DOMContentLoaded", () => {
    setupRegisterPage();
});

function setupRegisterPage() {
    const registerForm = document.getElementById("register-form");
    const registerError = document.getElementById("register-error");
    const emailInput = document.getElementById("register-email");
    const params = new URLSearchParams(window.location.search);
    const email = params.get("email");

    if (emailInput && email) {
        emailInput.value = email;
    }

    if (!registerForm) return;
    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (registerError) {
            registerError.style.display = "none";
            registerError.textContent = "";
        }

        const registerEmail = document.getElementById("register-email").value.trim();
        const password = document.getElementById("register-password").value;

        try {
            const res = await fetch(REGISTER_URL, {
                method: "POST",
                headers: { "content-type": "application/json" },
                body: JSON.stringify({ email: registerEmail, password }),
            });

            const data = await res.json().catch(() => ({}));
            if (!res.ok) {
                if (registerError) {
                    registerError.textContent = data?.detail || "No se pudo registrar";
                    registerError.style.display = "block";
                }
                return;
            }

            localStorage.setItem(PENDING_VERIFY_EMAIL_KEY, registerEmail);
            window.location.href = `/verify?email=${encodeURIComponent(registerEmail)}`;
        } catch {
            if (registerError) {
                registerError.textContent = "Error de red";
                registerError.style.display = "block";
            }
        }
    });
}
