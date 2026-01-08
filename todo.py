import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for

todo_bp = Blueprint('todo', __name__)

def get_db_connection():
    conn = sqlite3.connect("main.db")
    conn.row_factory = sqlite3.Row
    return conn

# 1. 一覧表示
@todo_bp.route('/date/<selected_date>')
def index_by_date(selected_date):
    conn = get_db_connection()
    todos = conn.execute("SELECT * FROM todos WHERE due_date = ? ORDER BY id DESC", (selected_date,)).fetchall()
    conn.close()
    return render_template('day_detail.html', todos=todos, date=selected_date)

# 2. 追加処理 (duration も保存するように変更)
@todo_bp.route('/add/<selected_date>', methods=['POST'])
def add(selected_date):
    task_content = request.form.get('task_name')
    duration = request.form.get('duration') # ★追加

    if task_content and task_content.strip():
        conn = get_db_connection()
        # duration と due_date を保存
        conn.execute("INSERT INTO todos (task, due_date, duration, actual_time, is_completed) VALUES (?, ?, ?, 0, 0)", 
                     (task_content, selected_date, duration))
        conn.commit()
        conn.close()
    return redirect(url_for('todo.index_by_date', selected_date=selected_date))