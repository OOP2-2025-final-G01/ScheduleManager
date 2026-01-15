import eel
import time
import sqlite3
import os

# Eelの初期化
base_path = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_path, 'templates')
eel.init(template_dir) 

# --- タイマーロジック (変更なし) ---
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
    # Flaskと共存させるため、Eelのspawnを使います（どちらでも動きますがこれが安定です）
    eel.spawn(run_timer_loop)

def run_timer_loop():
    global is_running
    while is_running:
        elapsed = int(time.time() - start_time)
        m = elapsed // 60
        s = elapsed % 60
        eel.update_timer_modal(f"{m:02}:{s:02}")
        eel.sleep(0.1)

@eel.expose
def stop_python_timer():
    global is_running, current_task_id
    if not is_running: return
    is_running = False
    
    session_seconds = int(time.time() - start_time)
    
    if current_task_id:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        row = cursor.execute("SELECT actual_time, duration FROM todos WHERE id = ?", (current_task_id,)).fetchone()
        
        if row:
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
        print(f"保存完了: +{session_seconds}秒")

    eel.reload_page()

# --- ★ここが修正ポイント ---
def run_eel_server():
    print("Eelサーバー(ポート8000)を起動します...")
    # mode=None にすると、Eelはブラウザを開こうとしません。
    # 404エラーの原因（ファイル探し）がこれでなくなります。
    eel.start(port=8000, host='localhost', mode=None, close_callback=lambda x,y:None)