const VERIFY_URL = "/auth/verify";
const PENDING_VERIFY_EMAIL_KEY = "pending_verify_email";

document.addEventListener("DOMContentLoaded", () => {
    setupVerifyPage();
});

function setupVerifyPage() {
    const verifyForm = document.getElementById("verify-form");
    const verifyError = document.getElementById("verify-error");
    const verifyEmail = document.getElementById("verify-email");
    const resendLink = document.getElementById("resend-link");
    const params = new URLSearchParams(window.location.search);
    const emailFromQuery = params.get("email");
    const emailFromStorage = localStorage.getItem(PENDING_VERIFY_EMAIL_KEY) || "";
    const email = emailFromQuery || emailFromStorage;

    if (verifyEmail && email) {
        verifyEmail.value = email;
    }
    if (resendLink && email) {
        resendLink.href = `/register?email=${encodeURIComponent(email)}`;
    }

    if (!verifyForm) return;
    verifyForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (verifyError) {
            verifyError.style.display = "none";
            verifyError.textContent = "";
        }

        const emailInput = document.getElementById("verify-email");
        const codeInput = document.getElementById("verify-code");
        const currentEmail = emailInput?.value?.trim() || "";
        const code = (codeInput?.value || "").replace(/\D/g, "");

        if (!currentEmail || code.length !== 6) {
            if (verifyError) {
                verifyError.textContent = "Correo y código de 6 dígitos";
                verifyError.style.display = "block";
            }
            return;
        }

        try {
            const res = await fetch(VERIFY_URL, {
                method: "POST",
                headers: { "content-type": "application/json" },
                body: JSON.stringify({ email: currentEmail, code }),
            });
            const data = await res.json().catch(() => ({}));
            if (!res.ok) {
                if (verifyError) {
                    verifyError.textContent = data?.detail || "Código inválido";
                    verifyError.style.display = "block";
                }
                return;
            }

            localStorage.removeItem(PENDING_VERIFY_EMAIL_KEY);
            window.location.href = `/login?email=${encodeURIComponent(currentEmail)}`;
        } catch {
            if (verifyError) {
                verifyError.textContent = "Error de red";
                verifyError.style.display = "block";
            }
        }
    });
}
