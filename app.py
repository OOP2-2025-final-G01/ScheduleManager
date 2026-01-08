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
    # actual_time を含む全データを取得
    todos = conn.execute("SELECT * FROM todos WHERE due_date = ? ORDER BY id DESC", (due_date,)).fetchall()
    conn.close()
    return render_template('day_detail.html', due_date=due_date, todos=todos)

@app.route('/add/<due_date>', methods=['POST'])
def add(due_date):
    task_content = request.form.get('task_name')
    # フォームから送られた時間を actual_time として保存
    time_val = request.form.get('actual_time', 0)
    
    if task_content and task_content.strip():
        conn = get_db_connection()
        conn.execute("INSERT INTO todos (task, due_date, actual_time) VALUES (?, ?, ?)", 
                     (task_content, due_date, time_val))
        conn.commit()
        conn.close()
    return redirect(url_for('day_detail', due_date=due_date))

if __name__ == "__main__":
    app.run(port=5001, debug=True)