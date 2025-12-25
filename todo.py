import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for

# Blueprintの定義
todo_bp = Blueprint('todo', __name__)

def get_db_connection():
    conn = sqlite3.connect("main.db")
    conn.row_factory = sqlite3.Row
    return conn

# 1. TODO一覧の表示
@todo_bp.route('/')
def index():
    conn = get_db_connection()
    # 最新の投稿が上にくるように ID の降順で取得
    todos = conn.execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
    conn.close()
    return render_template('index.html', todos=todos)

# 2. TODOの追加（「やること」だけを入力）
@todo_bp.route('/add', methods=['POST'])
def add():
    # フォームの 'task_name' という名前のデータを受け取る
    task_content = request.form.get('task_name')
    
    if task_content and task_content.strip():
        conn = get_db_connection()
        conn.execute("INSERT INTO todos (task) VALUES (?)", (task_content,))
        conn.commit()
        conn.close()
        
    return redirect(url_for('todo.index'))