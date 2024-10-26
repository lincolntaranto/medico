function queryExam(event) {
    event.preventDefault();
    const queryType = document.getElementById('queryExamType').value;
    const queryValue = queryType === 'id' ? document.getElementById('queryExamId').value : document.getElementById('queryExamPatientName').value;
    fetch(`/api/exam/query?type=${queryType}&value=${queryValue}`)
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            showAlert(data.message, 'warning');
        } else {
            let examInfo = '';
            if (Array.isArray(data)) {
                data.forEach(exam => {
                    examInfo += `
                        ID del paciente: ${exam.patient_id}<br>
                        Nombre del paciente: ${exam.patient_name}<br>
                        Nombre del Examen: ${exam.exam_type}<br>
                        Fecha: ${exam.date}<br>
                        Resultado: ${exam.results}<br>
                    `;
                });
            } else {
                examInfo = `
                    ID del paciente: ${data.patient_id}<br>
                    Nombre del paciente: ${data.patient_name}<br>
                    Nombre del Examen: ${data.exam_type}<br>
                    Fecha: ${data.date}<br>
                    Resultado: ${data.results}
                `;
            }
            showAlert(examInfo, 'success');
        }
    })
    .catch(error => {
        showAlert('Error al consultar examen', 'danger');
    });
    return false;
}

function toggleExamQueryField() {
    const queryType = document.getElementById('queryExamType').value;
    document.getElementById('queryExamIdField').style.display = queryType === 'id' ? 'block' : 'none';
    document.getElementById('queryExamNameField').style.display = queryType === 'name' ? 'block' : 'none';
}

function toggleEditQueryField() {
    const queryType = document.getElementById('editQueryType').value;
    document.getElementById('editIdField').style.display = queryType === 'id' ? 'block' : 'none';
    document.getElementById('editNameField').style.display = queryType === 'name' ? 'block' : 'none';
}

function editPatient(event) {
    event.preventDefault();
    const queryType = document.getElementById('editQueryType').value;
    const queryValue = queryType === 'id' ? document.getElementById('editPatientId').value : document.getElementById('editPatientName').value;
    const data = {
        name: document.getElementById('editPatientNewName').value,
        age: document.getElementById('editPatientAge').value,
        gender: document.getElementById('editPatientGender').value
    };
    fetch(`/api/patient/edit?type=${queryType}&value=${queryValue}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        showAlert(data.message, 'success');
        event.target.reset();
    })
    .catch(error => {
        showAlert('Erro ao editar paciente', 'danger');
    });
    return false;
}

function deletePatient(event) {
    event.preventDefault();
    const patientId = document.getElementById('deletePatientId').value;
    fetch(`/api/patient/delete/${patientId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        showAlert(data.message, 'success');
        event.target.reset();
    })
    .catch(error => {
        showAlert('Erro ao deletar paciente', 'danger');
    });
    return false;
}

function editExam(event) {
    event.preventDefault();
    const examId = document.getElementById('editExamId').value;
    const data = {
        exam_type: document.getElementById('editExamType').value,
        date: document.getElementById('editExamDate').value,
        results: document.getElementById('editExamResults').value
    };
    fetch(`/api/exam/edit/${examId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        showAlert(data.message, 'success');
        event.target.reset();
    })
    .catch(error => {
        showAlert('Erro ao editar exame', 'danger');
    });
    return false;
}

function deleteExam(event) {
    event.preventDefault();
    const examId = document.getElementById('deleteExamId').value;
    fetch(`/api/exam/delete/${examId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        showAlert(data.message, 'success');
        event.target.reset();
    })
    .catch(error => {
        showAlert('Erro ao deletar exame', 'danger');
    });
    return false;
}

function showEditPatientForm() {
    showForm('editPatientForm');
}

function showEditExamForm() {
    showForm('editExamForm');
}

function showDeletePatientForm() {
    showForm('deletePatientForm');
}

function showDeleteExamForm() {
    showForm('deleteExamForm');
}

function showRegisterPatientForm() {
    showForm('patientForm');
}

function showRegisterExamForm() {
    showForm('examForm');
}

function showQueryPatientForm() {
    showForm('queryPatientForm');
}

function showQueryExamForm() {
    showForm('queryExamForm');
}

function registerExam(event) {
    event.preventDefault();
    const data = {
        patient_id: document.getElementById('patientId').value,
        exam_type: document.getElementById('examType').value,
        date: document.getElementById('examDate').value,
        results: document.getElementById('examResults').value
    };
    fetch('/api/exam/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Paciente não encontrado') {
            showAlert(data.message, 'danger');
        } else {
            showAlert(data.message, 'success');
            event.target.reset();
        }
    })
    .catch(error => {
        showAlert('Erro ao registrar exame', 'danger');
    });
    return false;
}
