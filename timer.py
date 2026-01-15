import eel
import time
import threading
import sqlite3
import os
from flask import Flask, redirect, Response
from todo import todo_bp 

# 1. Flaskアプリの設定
app = Flask(__name__)
# Blueprintを登録 (これで url_for('todo.add') が使えるようになります)
app.register_blueprint(todo_bp)

# ★重要: ブラウザが eel.js を読み込めるようにする魔法のコード
@app.route('/eel.js')
def eel_js():
    eel_js_path = os.path.join(os.path.dirname(eel.__file__), 'eel.js')
    with open(eel_js_path, encoding='utf-8') as f:
        js_content = f.read()
    return Response(js_content, mimetype='application/javascript')

# 起動時に今日の日付へ転送
@app.route('/')
def index():
    import datetime
    today = datetime.date.today().strftime('%Y-%m-%d')
    return redirect(f'/date/{today}')

# 2. Eelの設定
base_path = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_path, 'templates')
eel.init(template_dir) 

# --- タイマーロジック ---
is_running = False
current_task_id = None
start_time = 0
target_seconds = 0

@eel.expose
def start_python_timer(task_id, subject_name, target_min_str):
    global is_running, current_task_id, start_time, target_seconds
    if is_running: return

    is_running = True
    current_task_id = task_id
    start_time = time.time()
    
    try:
        target_seconds = int(float(target_min_str) * 60)
    except:
        target_seconds = 0
        
    print(f"開始: ID={task_id} {subject_name}")
    threading.Thread(target=run_timer_loop, daemon=True).start()

def run_timer_loop():
    global is_running
    while is_running:
        elapsed = int(time.time() - start_time)
        m = elapsed // 60
        s = elapsed % 60
        eel.update_timer_modal(f"{m:02}:{s:02}")
        time.sleep(0.1)

@eel.expose
def stop_python_timer():
    global is_running, current_task_id
    if not is_running: return
    is_running = False
    
    session_seconds = int(time.time() - start_time)
    
    if current_task_id:
        conn = sqlite3.connect("main.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        row = cursor.execute("SELECT actual_time, duration FROM todos WHERE id = ?", (current_task_id,)).fetchone()
        
        current_total = row["actual_time"] if row["actual_time"] else 0
        new_total = current_total + session_seconds
        
        try:
            target_sec = int(row["duration"]) * 60
        except:
            target_sec = 0
        
        is_completed = 1 if (target_sec > 0 and new_total >= target_sec) else 0

        cursor.execute("UPDATE todos SET actual_time = ?, is_completed = ? WHERE id = ?", 
                       (new_total, is_completed, current_task_id))
        conn.commit()
        conn.close()
        print(f"保存完了: +{session_seconds}秒 (合計{new_total}秒)")

    # 画面リロード
    eel.reload_page()

# --- 起動処理 ---
def run_flask():
    # Flaskはポート5000で動かす
    app.run(port=5000, debug=False, use_reloader=False)

threading.Thread(target=run_flask, daemon=True).start()

print("アプリを起動します...")
time.sleep(1) 
# Eelはポート8000で、Flask(5000)を見に行く
eel.start('http://localhost:5000', size=(450, 700), port=8000)