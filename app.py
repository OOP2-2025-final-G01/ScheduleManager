
"""
ScheduleManager - Flask app

提供する主なルート:
- /                : ダッシュボード (templates/index.html)
- /api/stats/monthly: 今月の予定に対する完了数/合計数を返す
- /api/stats/subject_time: 今月の科目別合計実作業時間を返す
- /due_date/<due_date>: 日別詳細表示 (templates/day_detail.html)

起動:
  PORT=5001 python app.py
"""


from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import sqlite3
from datetime import date
import eel        # 追加：タイマー用
import threading
import todoCheck  # これを追加！


app = Flask(__name__, template_folder='templates', static_folder='static')


def get_db_connection():
    conn = sqlite3.connect('main.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/eel.js')
def eel_js():
    """フロントエンドからEelのライブラリを呼び出すための転送設定"""
    return redirect('http://localhost:8000/eel.js')

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
    
    overdue_tasks, today_str = todoCheck.get_incomplete_tasks()
    # 取得したリストを「tasks」という名前で index.html へ送る
    
    # 取得したデータを index.html へ渡す
    return render_template('index.html', today_tasks=today_tasks, tasks=overdue_tasks)

    today_str = date.today().strftime('%Y-%m-%d')
    conn = get_db_connection()
    # 今日のTODOをDBから取得
    today_todos = conn.execute(
        "SELECT * FROM todos WHERE due_date = ? ORDER BY id DESC", (today_str,)
    ).fetchall()
    conn.close()
    return render_template('index.html', today_todos=today_todos, today_str=today_str)



@app.route('/api/stats/monthly')
def api_monthly_stats():
    today = date.today()
    first_day = today.replace(day=1)
    if today.month == 12:
        next_month = today.replace(year=today.year+1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month+1, day=1)
    last_day = next_month - date.resolution

    start_str = first_day.isoformat()
    end_str = last_day.isoformat()

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT
                SUM(CASE WHEN is_completed=1 THEN 1 ELSE 0 END) as completed,
                COUNT(*) as total
            FROM todos
            WHERE due_date IS NOT NULL
              AND due_date >= ?
              AND due_date <= ?
        """, (start_str, end_str))
        row = cur.fetchone()
        conn.close()
        completed = int(row[0] or 0)
        total = int(row[1] or 0)
    except Exception as exc:
        print('DB error in /api/stats/monthly:', exc)
        completed = 0
        total = 0
    return jsonify({"completed": completed, "total": total})


@app.route('/api/stats/subject_time')
def api_subject_time():
    """今月のタスクごとの実際の作業時間(actual_time)を科目ごとに合計して返す。
    科目は task の先頭トークン（最初の空白まで）を科目名とする簡易抽出を行う。
    レスポンス: { "series": [ { "subject": "英語", "total": 120 }, ... ] }
    actual_time は整数（分）として扱う想定。
    """
    today = date.today()
    first_day = today.replace(day=1)
    if today.month == 12:
        next_month = today.replace(year=today.year+1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month+1, day=1)
    last_day = next_month - date.resolution

    start_str = first_day.isoformat()
    end_str = last_day.isoformat()

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # task の先頭トークンを科目名とする（空白が無ければ task 全体を科目名とする）
        cur.execute("""
            SELECT
                (CASE WHEN instr(task, ' ')>0 THEN substr(task,1,instr(task,' ')-1) ELSE task END) as subject,
                SUM(COALESCE(actual_time,0)) as total
            FROM todos
            WHERE due_date IS NOT NULL
              AND due_date >= ?
              AND due_date <= ?
            GROUP BY subject
            ORDER BY total DESC
        """, (start_str, end_str))
        rows = cur.fetchall()
        conn.close()
        series = [{"subject": r[0], "total": int(r[1] or 0)} for r in rows]
    except Exception as exc:
        print('DB error in /api/stats/subject_time:', exc)
        series = []
    return jsonify({"series": series})


@app.route('/stats')
def stats():
    return render_template('stats.html')


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
        conn.execute("INSERT INTO todos (task, due_date, duration, actual_time, is_completed) VALUES (?, ?, ?, 0, 0)", 
                     (task_content, due_date, duration))
        conn.commit()
        conn.close()
        
    return redirect(url_for('day_detail', due_date=due_date))


@app.route('/delete/<int:task_id>/<due_date>', methods=['POST'])
def delete(task_id, due_date):
    conn = get_db_connection()
    conn.execute("DELETE FROM todos WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('day_detail', due_date=due_date))

@app.errorhandler(404)
def page_not_found(e):
    # 開発時は index を返して SPA ライクに振る
    return render_template('index.html'), 200

if __name__ == '__main__':

    

    # B. タイマー(Eel)サーバーを別スレッドで起動
    # これにより Flask と Eel が並列して動作可能になる
    import timer 
    eel_thread = threading.Thread(target=timer.run_eel_server, daemon=True)
    eel_thread.start()

    # 1. データベースがなければテーブルを作る（重要！）
    init_db() 
    
    # 2. ポート番号の設定（mainの書き方を採用）

    port = int(os.environ.get('PORT', 5001))
    
    # 3. タイマー(Eel)の起動（以前のステップで追加したコード）
    import timer
    eel_thread = threading.Thread(target=timer.run_eel_server, daemon=True)
    eel_thread.start()
    
    print(f"Webアプリ(Flask)を起動します: http://127.0.0.1:{port}")
    
    # 4. Flaskの起動（use_reloader=False はタイマー併用時に推奨）
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
