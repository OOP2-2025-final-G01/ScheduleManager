import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for

# Blueprintの名前は 'todo'
todo_bp = Blueprint('todo', __name__)

def get_db_connection():
    conn = sqlite3.connect("main.db")
    conn.row_factory = sqlite3.Row
    return conn

# 一覧表示
@todo_bp.route('/date/<target_date>')
def index_by_date(target_date):
    conn = get_db_connection()
    todos = conn.execute("SELECT * FROM todos WHERE due_date = ? ORDER BY id DESC", (target_date,)).fetchall()
    conn.close()
    # HTML側には 'date_str' という名前で日付を渡します
    return render_template('day_detail.html', todos=todos, date_str=target_date)

# 追加処理
@todo_bp.route('/add/<target_date>', methods=['POST'])
def add(target_date):
    task_content = request.form.get('task_name')
    duration = request.form.get('duration')

    if task_content and task_content.strip():
        conn = get_db_connection()
        conn.execute("INSERT INTO todos (task, due_date, duration, actual_time, is_completed) VALUES (?, ?, ?, 0, 0)", 
                     (task_content, target_date, duration))
        conn.commit()
        conn.close()
    
    # URL生成時に 'target_date' を渡す
    return redirect(url_for('todo.index_by_date', target_date=target_date))