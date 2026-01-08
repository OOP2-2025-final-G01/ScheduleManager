import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for

todo_bp = Blueprint('todo', __name__)

def get_db_connection():
    conn = sqlite3.connect("main.db")
    conn.row_factory = sqlite3.Row
    return conn

# 1. 特定の日付のTODO一覧を表示
@todo_bp.route('/date/<selected_date>')
def index_by_date(selected_date):
    conn = get_db_connection()
    # 指定された日付のTODOのみを取得
    todos = conn.execute("SELECT * FROM todos WHERE date = ? ORDER BY id DESC", (selected_date,)).fetchall()
    conn.close()
    # テンプレートに日付を渡す
    return render_template('index.html', todos=todos, date=selected_date)

# 2. TODOの追加 (日付を紐付け)
@todo_bp.route('/add/<selected_date>', methods=['POST'])
def add(selected_date):
    task_content = request.form.get('task_name')
    if task_content and task_content.strip():
        conn = get_db_connection()
        # dateカラムにも値を保存
        conn.execute("INSERT INTO todos (task, date) VALUES (?, ?)", (task_content, selected_date))
        conn.commit()
        conn.close()
    return redirect(url_for('todo.index_by_date', selected_date=selected_date))

# 3. TODOの削除
@todo_bp.route('/delete/<int:task_id>/<selected_date>', methods=['POST'])
def delete(task_id, selected_date):
    conn = get_db_connection()
    conn.execute("DELETE FROM todos WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('todo.index_by_date', selected_date=selected_date))