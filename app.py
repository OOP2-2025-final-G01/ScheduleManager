from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import sqlite3
from datetime import date

app = Flask(__name__, template_folder='templates', static_folder='static')

def get_db_connection():
    conn = sqlite3.connect("main.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    today_str = date.today().strftime('%Y-%m-%d')
    conn = get_db_connection()
    # 今日のTODOをDBから取得
    today_todos = conn.execute(
        "SELECT * FROM todos WHERE due_date = ? ORDER BY id DESC", (today_str,)
    ).fetchall()
    conn.close()
    return render_template('index.html', today_todos=today_todos, today_str=today_str)

@app.route('/due_date/<due_date>')
def day_detail(due_date):
    conn = get_db_connection()
    todos = conn.execute("SELECT * FROM todos WHERE due_date = ? ORDER BY id DESC", (due_date,)).fetchall()
    conn.close()
    return render_template('day_detail.html', due_date=due_date, todos=todos)

@app.route('/add/<due_date>', methods=['POST'])
def add(due_date):
    task_content = request.form.get('task_name')
    time_val = request.form.get('actual_time', 0)
    if task_content and task_content.strip():
        conn = get_db_connection()
        conn.execute("INSERT INTO todos (task, due_date, actual_time) VALUES (?, ?, ?)", 
                     (task_content, due_date, time_val))
        conn.commit()
        conn.close()
    return redirect(url_for('day_detail', due_date=due_date))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)