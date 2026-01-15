from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3
import eel  # ★追加: eelの場所を知るために必要
from datetime import date

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("main.db")
    conn.row_factory = sqlite3.Row
    return conn

# ★追加: これがないとブラウザが「eel.jsがない！」とエラーを出します
@app.route('/eel.js')
def eel_js():
    # eelライブラリの中から eel.js ファイルを探して読み込む
    eel_js_path = os.path.join(os.path.dirname(eel.__file__), 'eel.js')
    with open(eel_js_path, encoding='utf-8') as f:
        js_content = f.read()
    # ブラウザに返す
    return js_content, 200, {'Content-Type': 'application/javascript'}

@app.route('/')
def index():
    # 今日の日付を取得 (YYYY-MM-DD)
    today_str = date.today().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    # 今日の日付に一致するタスクを取得
    today_tasks = conn.execute(
        "SELECT task, duration FROM todos WHERE due_date = ?", 
        (today_str,)
    ).fetchall()
    conn.close()
    
    # 取得したデータを index.html へ渡す
    return render_template('index.html', today_tasks=today_tasks)

@app.route('/due_date/<due_date>')
def day_detail(due_date):
    conn = get_db_connection()
    todos = conn.execute("SELECT * FROM todos WHERE due_date = ? ORDER BY id DESC", (due_date,)).fetchall()
    conn.close()
    return render_template('day_detail.html', due_date=due_date, todos=todos)

@app.route('/add/<due_date>', methods=['POST'])
def add(due_date):
    task_content = request.form.get('task_name')
    duration = request.form.get('duration') 
    
    if task_content and task_content.strip():
        conn = get_db_connection()
        conn.execute("INSERT INTO todos (task, due_date, duration, actual_time, is_completed) VALUES (?, ?, ?, 0, 0)", 
                     (task_content, due_date, duration))
        conn.commit()
        conn.close()
        
    return redirect(url_for('day_detail', due_date=due_date))

if __name__ == "__main__":
    app.run(port=5001, debug=True)