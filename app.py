from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect("main.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/due_date/<due_date>')
def day_detail(due_date):
    conn = get_db_connection()
    # データを取得
    todos = conn.execute("SELECT * FROM todos WHERE due_date = ? ORDER BY id DESC", (due_date,)).fetchall()
    conn.close()
    return render_template('day_detail.html', due_date=due_date, todos=todos)

# ★ここが重要: フォームの修正に合わせて受け取り側も整備
@app.route('/add/<due_date>', methods=['POST'])
def add(due_date):
    task_content = request.form.get('task_name')
    duration = request.form.get('duration') # HTMLの input name="duration" を受け取る

    if task_content and task_content.strip():
        conn = get_db_connection()
        # duration (目標時間) を保存し、actual_time (実績) は 0 で初期化
        conn.execute("INSERT INTO todos (task, due_date, duration, actual_time, is_completed) VALUES (?, ?, ?, 0, 0)", 
                     (task_content, due_date, duration))
        conn.commit()
        conn.close()
        
    # day_detail 関数へリダイレクト（変数は due_date）
    return redirect(url_for('day_detail', due_date=due_date))

if __name__ == "__main__":
    app.run(port=5001, debug=True)