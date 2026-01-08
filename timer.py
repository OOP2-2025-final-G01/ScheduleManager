import eel
import time
import threading
import sqlite3
import os
from flask import Flask, redirect
from todo import todo_bp # todo.pyを読み込み

# 1. Flaskアプリの設定
app = Flask(__name__)
app.register_blueprint(todo_bp)

# ルートにアクセスしたら今日の日付へ飛ばす（簡易対応）
@app.route('/')
def index():
    import datetime
    today = datetime.date.today().strftime('%Y-%m-%d')
    return redirect(f'/date/{today}')

# 2. Eelの設定
# FlaskのtemplatesフォルダをEelも見れるように設定
base_path = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_path, 'templates')
eel.init(template_dir) 

# --- タイマーロジック (Eel) ---
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
        eel.update_timer_modal(f"{m:02}:{s:02}") # JS更新
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
        
        # 累積時間を計算して更新
        row = cursor.execute("SELECT actual_time, duration FROM todos WHERE id = ?", (current_task_id,)).fetchone()
        
        current_total = row["actual_time"] if row["actual_time"] else 0
        new_total = current_total + session_seconds
        
        # 目標達成チェック
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

    # ★Flaskで再描画するためにページをリロードさせる
    eel.reload_page()

# --- 起動処理 ---
def run_flask():
    # Flaskをポート5000で動かす
    app.run(port=5000, debug=False, use_reloader=False)

# Flaskを別スレッドで起動
threading.Thread(target=run_flask, daemon=True).start()

print("アプリを起動します...")
# 少し待ってからEelでFlaskのURLを開く
time.sleep(1) 
eel.start('http://localhost:5000', size=(450, 700))