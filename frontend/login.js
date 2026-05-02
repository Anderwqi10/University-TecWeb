const LOGIN_URL = "/auth/login";
const TOKEN_KEY = "access_token";

document.addEventListener("DOMContentLoaded", () => {
    setupLoginPage();
});

function setupLoginPage() {
    const loginForm = document.getElementById("login-form");
    const loginError = document.getElementById("login-error");
    const params = new URLSearchParams(window.location.search);
    const email = params.get("email");
    const emailInput = document.getElementById("login-email");

    if (emailInput && email) {
        emailInput.value = email;
    }

    if (!loginForm) return;

    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (loginError) {
            loginError.style.display = "none";
            loginError.textContent = "";
        }

        const loginEmail = document.getElementById("login-email").value.trim();
        const password = document.getElementById("login-password").value;

        try {
            const res = await fetch(LOGIN_URL, {
                method: "POST",
                headers: { "content-type": "application/json" },
                body: JSON.stringify({ email: loginEmail, password }),
            });

            const data = await res.json().catch(() => ({}));
            if (!res.ok) {
                if (loginError) {
                    if (res.status === 403 && loginEmail) {
                        const q = encodeURIComponent(loginEmail);
                        loginError.innerHTML = `${data?.detail || "Cuenta no verificada"} — <a class="btn-link" href="/verify?email=${q}" style="display:inline;padding:4px 8px;">Verificar correo</a>`;
                    } else {
                        loginError.textContent = data?.detail || "No se pudo iniciar sesión";
                    }
                    loginError.style.display = "block";
                }
                return;
            }

            if (data?.access_token) {
                localStorage.setItem(TOKEN_KEY, data.access_token);
                window.location.href = "/";
            }
        } catch {
            if (loginError) {
                loginError.textContent = "Error de red";
                loginError.style.display = "block";
            }
        }
    });
}
