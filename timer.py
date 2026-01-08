import eel
import time
import threading
import sqlite3 # ★追加: データベース操作用
import os

# htmlファイルが入っているフォルダ名を指定
# (念のため絶対パス指定にしておくと安全です)
base_path = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_path, 'templates')
eel.init(template_dir)

# --- グローバル変数 ---
is_running = False
current_task_id = None # ★追加: 現在計測中のタスクID
current_subject = ""
target_seconds = 0
start_time = 0

# timer.py に追加が必要な部分

@eel.expose
def fetch_all_tasks():
    conn = sqlite3.connect("main.db")
    conn.row_factory = sqlite3.Row
    todos = conn.execute("SELECT * FROM todos ORDER BY id DESC").fetchall()
    conn.close()
    
    task_list = []
    for row in todos:
        task_list.append({
            "id": row["id"],
            "task": row["task"],
            "target_time": row["duration"] if row["duration"] else "0", # カラム名に合わせて調整
            "actual_time": row["actual_time"],
            "is_completed": row["is_completed"]
        })
    return task_list

@eel.expose
# ★変更: task_id を受け取るように追加
def start_python_timer(task_id, subject_name, target_min_str):
    """ タイマーを開始する関数 """
    global is_running, current_task_id, current_subject, target_seconds, start_time
    
    if is_running:
        print("【Python】既に実行中のため、開始をスキップしました")
        return

    is_running = True
    current_task_id = task_id # ★IDを記憶しておく
    current_subject = subject_name
    
    try:
        # 文字列を一度小数(float)にして、秒換算してから整数(int)にする
        target_seconds = int(float(target_min_str) * 60)
    except ValueError:
        print(f"【エラー】時間の変換に失敗しました: {target_min_str}")
        target_seconds = 0 

    start_time = time.time()
    
    print(f"【Python】計測スタート！ ID:{task_id} 科目:{current_subject} 目標:{target_seconds}秒")
    
    threading.Thread(target=run_timer_loop, daemon=True).start()

def run_timer_loop():
    """ 1秒ごとに時間を画面に送るループ """
    global is_running, start_time
    
    while is_running:
        try:
            elapsed_time = int(time.time() - start_time)
            minutes = elapsed_time // 60
            seconds = elapsed_time % 60
            time_str = f"{minutes:02}:{seconds:02}"
            
            eel.update_time_display(time_str)
            eel.sleep(0.1)
            
        except Exception as e:
            print(f"【エラー】ループ内でエラー発生: {e}")
            is_running = False
            break

@eel.expose
def stop_python_timer():
    global is_running, start_time, current_subject, target_seconds, current_task_id
    
    if not is_running:
        return

    is_running = False
    
    # 最終的な時間を計算
    final_elapsed = int(time.time() - start_time)
    minutes = final_elapsed // 60
    seconds = final_elapsed % 60
    result_str = f"{minutes}分 {seconds}秒"

    is_goal_met = final_elapsed >= target_seconds

    print(f"【Python】停止。結果: {result_str}, 達成: {is_goal_met}")

    # ---------------------------------------------------------
    # ★追加: データベースに結果を保存する処理
    # ---------------------------------------------------------
    if current_task_id is not None:
        try:
            conn = sqlite3.connect("main.db")
            cursor = conn.cursor()
            
            # 指定したIDの行に、実際の時間(actual_time)を書き込む
            # 目標達成していたら完了フラグ(is_completed)も立てる例
            cursor.execute("""
                UPDATE todos 
                SET actual_time = ?, is_completed = ? 
                WHERE id = ?
            """, (result_str, 1 if is_goal_met else 0, current_task_id))
            
            conn.commit()
            conn.close()
            print(f"✅ DB保存完了: ID={current_task_id}, 時間={result_str}")
            
        except Exception as e:
            print(f"❌ DB保存エラー: {e}")
    # ---------------------------------------------------------

    eel.update_list_item(current_subject, result_str, is_goal_met)

# アプリ起動設定
print("--------------------------------------------------")
print(" アプリを起動します。")
print("--------------------------------------------------")

# Chromeが見つからない場合のエラー回避を含める
try:
    eel.start('day_detail.html', mode='default', host='0.0.0.0', port=8000)
except EnvironmentError:
    eel.start('day_detail.html', mode='edge', host='0.0.0.0', port=8000)