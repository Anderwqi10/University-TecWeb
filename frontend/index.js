const API_URL = "http://localhost:8000/students";

document.addEventListener("DOMContentLoaded", () => {
    setupForm();
})

setupForm = () => {
    const form = document.getElementById("student-form");
    const cancelBtn = document.getElementById("cancel-btn");

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        saveStudent();
    })

    cancelBtn.addEventListener("click", () => {
        document.getElementById("student-form").reset();
    })
}

function saveStudent() {
    const id = document.getElementById("student-id").value;
    const name = document.getElementById("name").value;
    const age = document.getElementById("age").value;
    const grade = document.getElementById("grade").value;

    const studentData = { name, age, grade }

    const method = id ? "PUT" : "POST";
    const url = id ? `${API_URL}/${id}` : API_URL;

    fetch(url, {
        method: method,
        headers: {
            "content-type": "application/json" //MIME
        },
        body: JSON.stringify(studentData)
    }).then(response => {
        if (!response.ok) {
            return "Error en la operación"
        }
        return response.json();
    }).then(data => {
        alert("Estudiante guardado");
    }).catch(error => {
        alert(error)
    })
}