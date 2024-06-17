from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)

# Configuración de la base de datos
def get_db_connection():
    conn = sqlite3.connect('tasks.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with app.open_resource('schema.sql') as f:
        conn.executescript(f.read().decode('utf8'))
    conn.close()

@app.before_request
def initialize():
    init_db()

# Rutas de la API
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks').fetchall()
    conn.close()
    return jsonify([dict(task) for task in tasks])

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    title = data['title']
    description = data.get('description', '')
    status = data['status']

    conn = get_db_connection()
    conn.execute('INSERT INTO tasks (title, description, status) VALUES (?, ?, ?)',
                 (title, description, status))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Task created'}), 201

@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Task deleted'})

@app.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    data = request.json
    title = data['title']
    description = data.get('description', '')
    status = data['status']

    conn = get_db_connection()
    conn.execute('''
        UPDATE tasks
        SET title = ?, description = ?, status = ?
        WHERE id = ?
    ''', (title, description, status, id))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Task updated'})

# Ruta para la interfaz web
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
