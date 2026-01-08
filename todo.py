import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for

todo_bp = Blueprint('todo', __name__)

def get_db_connection():
    conn = sqlite3.connect("main.db")
    conn.row_factory = sqlite3.Row
    return conn

# 1. 一覧表示（日付指定）
@todo_bp.route('/date/<selected_date>')
def index(selected_date):
    conn = get_db_connection()
    todos = conn.execute("SELECT * FROM todos WHERE date = ? ORDER BY id DESC", (selected_date,)).fetchall()
    conn.close()
    return render_template('todo.html', todos=todos, date=selected_date)

# 2. TODOの追加
@todo_bp.route('/add/<selected_date>', methods=['POST'])
def add(selected_date):
    task_content = request.form.get('task_name')
    if task_content and task_content.strip():
        conn = get_db_connection()
        conn.execute("INSERT INTO todos (task, date) VALUES (?, ?)", (task_content, selected_date))
        conn.commit()
        conn.close()
    return redirect(url_for('todo.index', selected_date=selected_date))

# 3. TODOの編集（更新）
@todo_bp.route('/update/<int:task_id>/<selected_date>', methods=['POST'])
def update(task_id, selected_date):
    new_task = request.form.get('task_name')
    if new_task and new_task.strip():
        conn = get_db_connection()
        conn.execute("UPDATE todos SET task = ? WHERE id = ?", (new_task, task_id))
        conn.commit()
        conn.close()
    return redirect(url_for('todo.index', selected_date=selected_date))

# 4. TODOの削除
@todo_bp.route('/delete/<int:task_id>/<selected_date>', methods=['POST'])
def delete(task_id, selected_date):
    conn = get_db_connection()
    conn.execute("DELETE FROM todos WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('todo.index', selected_date=selected_date))