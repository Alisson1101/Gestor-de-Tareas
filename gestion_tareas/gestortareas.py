from flask import Flask, render_template_string, request, redirect, url_for
import pyodbc
from datetime import datetime

app = Flask(__name__)

# Configuración de SQL Server
SERVER = 'localhost'
DATABASE = 'Tareas'
DRIVER = 'ODBC Driver 17 for SQL Server'
CONN_STR = f'DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};Trusted_Connection=yes;'

def get_connection():
    return pyodbc.connect(CONN_STR)

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tareas' AND xtype='U')
            CREATE TABLE tareas (
                id INT IDENTITY(1,1) PRIMARY KEY,
                titulo NVARCHAR(255) NOT NULL,
                descripcion NVARCHAR(MAX),
                fecha DATE,
                encargado NVARCHAR(255),
                prioridad NVARCHAR(10),
                estado NVARCHAR(20)
            )
        ''')
        conn.commit()

# Plantilla HTML básica
TEMPLATE = '''
<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Gestor de Tareas</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  </head>
  <body class="bg-light">
    <div class="container py-5">
      <h1 class="mb-4">Gestor de Tareas</h1>
      <form method="POST" action="/crear" class="mb-4">
        <div class="row g-2 mb-2">
          <div class="col-md-4">
            <input name="titulo" class="form-control" placeholder="Título de la tarea" required>
          </div>
          <div class="col-md-4">
            <input name="descripcion" class="form-control" placeholder="Descripción">
          </div>
          <div class="col-md-4">
            <input type="date" name="fecha" class="form-control" required>
          </div>
        </div>
        <div class="row g-2">
          <div class="col-md-3">
            <input name="encargado" class="form-control" placeholder="Encargado" required>
          </div>
          <div class="col-md-3">
            <select name="prioridad" class="form-control" required>
              <option value="Alta">Alta</option>
              <option value="Media">Media</option>
              <option value="Baja">Baja</option>
            </select>
          </div>
          <div class="col-md-3">
            <select name="estado" class="form-control" required>
              <option value="Pendiente">Pendiente</option>
              <option value="Completada">Completada</option>
            </select>
          </div>
          <div class="col-md-3">
            <button class="btn btn-primary w-100">Agregar</button>
          </div>
        </div>
      </form>

      <ul class="list-group">
        {% for tarea in tareas %}
          <li class="list-group-item">
            <div><strong>{{ tarea[1] }}</strong> - {{ tarea[2] }}</div>
            <div>Fecha: {{ tarea[3] }} | Encargado: {{ tarea[4] }} | Prioridad: {{ tarea[5] }} | Estado: {{ tarea[6] }}</div>
            <div class="mt-2">
              <a href="/editar/{{ tarea[0] }}" class="btn btn-sm btn-warning">Editar</a>
              <a href="/eliminar/{{ tarea[0] }}" class="btn btn-sm btn-danger">Eliminar</a>
            </div>
          </li>
        {% endfor %}
      </ul>
    </div>
  </body>
</html>
'''

@app.route('/')
def index():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tareas')
        tareas = cursor.fetchall()
    return render_template_string(TEMPLATE, tareas=tareas)

@app.route('/crear', methods=['POST'])
def crear():
    titulo = request.form['titulo']
    descripcion = request.form['descripcion']
    fecha = request.form['fecha']
    encargado = request.form['encargado']
    prioridad = request.form['prioridad']
    estado = request.form['estado']
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tareas (titulo, descripcion, fecha, encargado, prioridad, estado)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (titulo, descripcion, fecha, encargado, prioridad, estado))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/eliminar/<int:id>')
def eliminar(id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tareas WHERE id = ?', (id,))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/editar/<int:id>')
def editar(id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tareas WHERE id = ?', (id,))
        tarea = cursor.fetchone()
    return f'''
    <form method="POST" action="/actualizar/{id}" style="padding:2rem">
        <h3>Editar Tarea</h3>
        <input name="titulo" value="{tarea[1]}" class="form-control mb-2">
        <input name="descripcion" value="{tarea[2]}" class="form-control mb-2">
        <input name="fecha" type="date" value="{tarea[3]}" class="form-control mb-2">
        <input name="encargado" value="{tarea[4]}" class="form-control mb-2">
        <select name="prioridad" class="form-control mb-2">
            <option {'selected' if tarea[5]=='Alta' else ''}>Alta</option>
            <option {'selected' if tarea[5]=='Media' else ''}>Media</option>
            <option {'selected' if tarea[5]=='Baja' else ''}>Baja</option>
        </select>
        <select name="estado" class="form-control mb-2">
            <option {'selected' if tarea[6]=='Pendiente' else ''}>Pendiente</option>
            <option {'selected' if tarea[6]=='Completada' else ''}>Completada</option>
        </select>
        <button class="btn btn-success">Actualizar</button>
        <a href="/" class="btn btn-secondary">Cancelar</a>
    </form>
    '''

@app.route('/actualizar/<int:id>', methods=['POST'])
def actualizar(id):
    titulo = request.form['titulo']
    descripcion = request.form['descripcion']
    fecha = request.form['fecha']
    encargado = request.form['encargado']
    prioridad = request.form['prioridad']
    estado = request.form['estado']
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tareas
            SET titulo = ?, descripcion = ?, fecha = ?, encargado = ?, prioridad = ?, estado = ?
            WHERE id = ?
        ''', (titulo, descripcion, fecha, encargado, prioridad, estado, id))
        conn.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
