// Frontend principal de la app:
// - Dashboard de estudiantes (CRUD).
// - Requiere token JWT en localStorage.
const STUDENTS_URL = "/students";
const TOKEN_KEY = "access_token";
let studentFormWired = false;

document.addEventListener("DOMContentLoaded", () => {
    setupAppPage();
});

function setupAppPage() {
    // Esta vista requiere token; si no existe, redirige a login.
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) {
        window.location.href = "/login";
        return;
    }

    const logoutBtn = document.getElementById("logout-btn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", () => {
            localStorage.removeItem(TOKEN_KEY);
            window.location.href = "/login";
        });
    }

    setupStudentForm();
}

function authHeaders() {
    // Inyecta Authorization para endpoints protegidos.
    const token = localStorage.getItem(TOKEN_KEY);
    return token ? { Authorization: `Bearer ${token}` } : {};
}

function setupStudentForm() {
    const form = document.getElementById("student-form");
    const cancelBtn = document.getElementById("cancel-btn");

    if (!form || !cancelBtn) return;

    loadStudents();

    // Evita listeners duplicados si setup se ejecuta más de una vez.
    if (studentFormWired) return;
    studentFormWired = true;

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        saveStudent();
    });

    cancelBtn.addEventListener("click", () => {
        form.reset();
        document.getElementById("student-id").value = "";
    });
}

function renderStudents(students) {
    // Renderiza tabla completa de estudiantes.
    const tbody = document.getElementById("student-list");
    if (!tbody) return;

    tbody.innerHTML = "";
    if (!Array.isArray(students) || students.length === 0) {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td colspan="5" style="color: rgba(255,255,255,0.7); padding: 12px;">No hay estudiantes aún</td>`;
        tbody.appendChild(tr);
        return;
    }

    for (const s of students) {
        const tr = document.createElement("tr");
        tr.dataset.studentId = String(s.id ?? "");
        tr.innerHTML = `
            <td>${s.id ?? ""}</td>
            <td>${s.name ?? ""}</td>
            <td>${s.age ?? ""}</td>
            <td>${s.grade ?? ""}</td>
            <td>
                <div class="actions">
                    <button type="button" class="btn-primary" data-action="edit">Editar</button>
                    <button type="button" class="btn-danger" data-action="delete">Eliminar</button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    }
}

function loadStudents() {
    // Carga estudiantes del usuario actual.
    fetch(STUDENTS_URL, {
        method: "GET",
        headers: {
            ...authHeaders(),
        },
    })
        .then((res) => res.json())
        .then((data) => renderStudents(data))
        .catch((err) => {
            console.error("Error cargando estudiantes:", err);
            renderStudents([]);
        });
}

document.addEventListener("click", async (ev) => {
    // Delegación de eventos para botones Editar/Eliminar en la tabla.
    const target = ev.target;
    if (!(target instanceof HTMLElement)) return;

    const action = target.getAttribute("data-action");
    if (!action) return;

    const row = target.closest("tr");
    const id = row?.getAttribute("data-student-id");
    if (!id) return;

    if (action === "edit") {
        try {
            const res = await fetch(`${STUDENTS_URL}/${id}`, { headers: { ...authHeaders() } });
            if (!res.ok) return;
            const s = await res.json();
            document.getElementById("student-id").value = s.id ?? "";
            document.getElementById("name").value = s.name ?? "";
            document.getElementById("age").value = s.age ?? "";
            document.getElementById("grade").value = s.grade ?? "";
            document.getElementById("student-form").scrollIntoView({ behavior: "smooth", block: "start" });
        } catch (e) {
            console.error(e);
        }
    }

    if (action === "delete") {
        const ok = confirm("¿Eliminar este estudiante?");
        if (!ok) return;

        try {
            const res = await fetch(`${STUDENTS_URL}/${id}`, { method: "DELETE", headers: { ...authHeaders() } });
            if (!res.ok) return;
            const editingId = document.getElementById("student-id")?.value;
            if (editingId === id) {
                document.getElementById("student-form")?.reset();
                document.getElementById("student-id").value = "";
            }
            loadStudents();
        } catch (e) {
            console.error(e);
        }
    }
});

async function saveStudent() {
    // Crea o actualiza estudiante según exista id.
    const id = document.getElementById("student-id").value;
    const name = document.getElementById("name").value;
    const age = document.getElementById("age").value;
    const grade = document.getElementById("grade").value;

    const studentData = {
        name: String(name).trim(),
        age: Number(age),
        grade: Number(grade),
    };

    const method = id ? "PUT" : "POST";
    const url = id ? `${STUDENTS_URL}/${id}` : STUDENTS_URL;

    try {
        const response = await fetch(url, {
            method,
            headers: {
                "content-type": "application/json",
                ...authHeaders(),
            },
            body: JSON.stringify(studentData),
        });

        const payload = await response.json().catch(() => ({}));
        if (!response.ok) {
            throw new Error(payload?.detail || "No se pudo guardar el estudiante");
        }

        alert("Estudiante guardado");
        const form = document.getElementById("student-form");
        form.reset();
        document.getElementById("student-id").value = "";
        loadStudents();
    } catch (error) {
        alert(error instanceof Error ? error.message : "Error en la operación");
    }
}