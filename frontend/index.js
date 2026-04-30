const API_URL = "http://localhost:8000/students";

document.addEventListener("DOMContentLoaded", () => {
    setupForm();
    loadStudents();
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
        loadStudents();
    }).catch(error => {
        alert(error)
    })
}

function loadStudents() {
    fetch(API_URL)
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById("student-list");
            table.innerHTML = "";

            data.forEach(student => {
                table.innerHTML += `
                <tr>
                    <td>${student.id}</td>
                    <td>${student.name}</td>
                    <td>${student.grade}</td>
                    <td>
                        <button onclick="editStudent(${student.id}, '${student.name}', ${student.age}, ${student.grade})">Editar</button>
                        <button onclick="deleteStudent(${student.id})">Eliminar</button>
                    </td>
                </tr>
                `;
            });
        });
}

function deleteStudent(id) {
    fetch(`${API_URL}/${id}`, {
        method: "DELETE"
    }).then(() => {
        loadStudents();
    });
}

function editStudent(id, name, age, grade) {
    document.getElementById("student-id").value = id;
    document.getElementById("name").value = name;
    document.getElementById("age").value = age;
    document.getElementById("grade").value = grade;
}