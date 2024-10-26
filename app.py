from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db, get_db
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'seu_segredo_aqui'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if user:
        return User(user['id'], user['username'], user['password'])
    return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user and check_password_hash(user['password'], password):
            user_obj = User(user['id'], user['username'], user['password'])
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        flash('Usuario o contraseña inválidos')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        if db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone() is not None:
            flash('Nombre de usuario ya existe')
        else:
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                       (username, generate_password_hash(password)))
            db.commit()
            flash('¡Registro exitoso! Inicie sesión.')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/api/patient/register', methods=['POST'])
@login_required
def api_register_patient():
    data = request.json
    db = get_db()
    db.execute('INSERT INTO patients (name, age, gender) VALUES (?, ?, ?)',
               (data['name'], data['age'], data['gender']))
    db.commit()
    return jsonify({'message': 'Paciente registrado con éxito!'}), 201

@app.route('/api/exam/register', methods=['POST'])
@login_required
def api_register_exam():
    data = request.json
    db = get_db()
    
    # Verificar se o paciente existe
    patient = db.execute('SELECT * FROM patients WHERE id = ?', (data['patient_id'],)).fetchone()
    if not patient:
        return jsonify({'message': 'Paciente não encontrado'}), 404
    
    # Registrar o exame se o paciente existir
    db.execute('INSERT INTO exams (patient_id, exam_type, date, results) VALUES (?, ?, ?, ?)',
               (data['patient_id'], data['exam_type'], data['date'], data['results']))
    db.commit()
    return jsonify({'message': 'Exame registrado com sucesso!'}), 201

@app.route('/api/patient/query', methods=['GET'])
@login_required
def api_query_patient():
    query_type = request.args.get('type')
    query_value = request.args.get('value')
    db = get_db()
    if query_type == 'id':
        patient = db.execute('SELECT * FROM patients WHERE id = ?', (query_value,)).fetchone()
    else:
        patient = db.execute('SELECT * FROM patients WHERE name = ?', (query_value,)).fetchone()
    
    if patient:
        exams = db.execute('SELECT exam_type FROM exams WHERE patient_id = ?', (patient['id'],)).fetchall()
        exam_names = [exam['exam_type'] for exam in exams]
        patient_data = dict(patient)
        patient_data['exams'] = exam_names
        return jsonify(patient_data), 200
    
    return jsonify({'message': 'Paciente no encontrado'}), 404

@app.route('/api/exam/query', methods=['GET'])
@login_required
def api_query_exam():
    query_type = request.args.get('type')
    query_value = request.args.get('value')
    db = get_db()
    
    if query_type == 'id':
        exam = db.execute('SELECT * FROM exams WHERE id = ?', (query_value,)).fetchone()
        if exam:
            patient = db.execute('SELECT name FROM patients WHERE id = ?', (exam['patient_id'],)).fetchone()
            exam_data = dict(exam)
            exam_data['patient_name'] = patient['name'] if patient else 'Desconhecido'
            return jsonify(exam_data), 200
    elif query_type == 'name':
        exams = db.execute('SELECT exams.*, patients.name as patient_name FROM exams JOIN patients ON exams.patient_id = patients.id WHERE patients.name = ?', (query_value,)).fetchall()
        if exams:
            exam_list = [dict(exam) for exam in exams]
            return jsonify(exam_list), 200
    
    return jsonify({'message': 'Examen no encontrado'}), 404

@app.route('/api/patient/edit', methods=['PUT'])
@login_required
def api_edit_patient():
    query_type = request.args.get('type')
    query_value = request.args.get('value')
    data = request.json
    db = get_db()
    if query_type == 'id':
        db.execute('UPDATE patients SET name = ?, age = ?, gender = ? WHERE id = ?',
                   (data['name'], data['age'], data['gender'], query_value))
    else:
        db.execute('UPDATE patients SET name = ?, age = ?, gender = ? WHERE name = ?',
                   (data['name'], data['age'], data['gender'], query_value))
    db.commit()
    return jsonify({'message': 'Paciente atualizado com sucesso!'}), 200

@app.route('/api/patient/delete/<int:patient_id>', methods=['DELETE'])
@login_required
def api_delete_patient(patient_id):
    db = get_db()
    db.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
    db.commit()
    return jsonify({'message': 'Paciente deletado com sucesso!'}), 200

@app.route('/api/exam/edit/<int:exam_id>', methods=['PUT'])
@login_required
def api_edit_exam(exam_id):
    data = request.json
    db = get_db()
    db.execute('UPDATE exams SET exam_type = ?, date = ?, results = ? WHERE id = ?',
               (data['exam_type'], data['date'], data['results'], exam_id))
    db.commit()
    return jsonify({'message': 'Exame atualizado com sucesso!'}), 200

@app.route('/api/exam/delete/<int:exam_id>', methods=['DELETE'])
@login_required
def api_delete_exam(exam_id):
    db = get_db()
    db.execute('DELETE FROM exams WHERE id = ?', (exam_id,))
    db.commit()
    return jsonify({'message': 'Exame deletado com sucesso!'}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
