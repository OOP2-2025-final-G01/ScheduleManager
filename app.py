from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3

app = Flask(__name__, template_folder='templates', static_folder='static')

# データベース接続
def get_db_connection():
    conn = sqlite3.connect("main.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

# ★ここが重要：カレンダーから飛んでくる先
@app.route('/due_date/<due_date>')
def day_detail(due_date):
    conn = get_db_connection()
    # 指定された日付のTODOのみを取得
    todos = conn.execute("SELECT * FROM todos WHERE due_date = ? ORDER BY id DESC", (due_date,)).fetchall()
    conn.close()
    # day_detail.html を表示し、日付とTODOリストを渡す
    return render_template('day_detail.html', due_date=due_date, todos=todos)

# TODOの追加
@app.route('/add/<due_date>', methods=['POST'])
def add(due_date):
    task_content = request.form.get('task_name')
    if task_content and task_content.strip():
        conn = get_db_connection()
        conn.execute("INSERT INTO todos (task, due_date) VALUES (?, ?)", (task_content, due_date))
        conn.commit()
        conn.close()
    return redirect(url_for('day_detail', due_date=due_date))

# TODOの削除
@app.route('/delete/<int:task_id>/<due_date>', methods=['POST'])
def delete(task_id, due_date):
    conn = get_db_connection()
    conn.execute("DELETE FROM todos WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('day_detail', due_date=due_date))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)