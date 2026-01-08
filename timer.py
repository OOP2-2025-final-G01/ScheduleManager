import eel
import time
import threading

# htmlファイルが入っているフォルダ名を指定
eel.init('templates')

# --- グローバル変数 ---
is_running = False
current_subject = ""
target_seconds = 0
start_time = 0

@eel.expose
def start_python_timer(subject_name, target_min_str):
    """ タイマーを開始する関数 """
    global is_running, current_subject, target_seconds, start_time
    
    # 既に動いていたら何もしない
    if is_running:
        print("【Python】既に実行中のため、開始をスキップしました")
        return

    is_running = True
    current_subject = subject_name
    
    # ★修正1: "0.2" などの小数を扱えるように float にしてから int にする
    try:
        # 文字列を一度小数(float)にして、秒換算してから整数(int)にする
        target_seconds = int(float(target_min_str) * 60)
    except ValueError:
        print(f"【エラー】時間の変換に失敗しました: {target_min_str}")
        target_seconds = 0 

    start_time = time.time()
    
    print(f"【Python】計測スタート！ 科目:{current_subject} 目標:{target_seconds}秒")
    
    # スレッドを開始
    threading.Thread(target=run_timer_loop, daemon=True).start()

def run_timer_loop():
    """ 1秒ごとに時間を画面に送るループ """
    global is_running, start_time
    
    print("【Python】ループ処理に入りました") # ★デバッグ用

    while is_running:
        try:
            # 経過時間を計算
            elapsed_time = int(time.time() - start_time)
            minutes = elapsed_time // 60
            seconds = elapsed_time % 60
            time_str = f"{minutes:02}:{seconds:02}"
            
            # ★デバッグ用: ターミナルに時間を表示（動いているか確認するため）
            # print(f"現在: {time_str}") 
            
            # 画面更新
            eel.update_time_display(time_str)
            eel.sleep(0.1)
            
        except Exception as e:
            print(f"【エラー】ループ内でエラー発生: {e}")
            is_running = False
            break

@eel.expose
def stop_python_timer():
    global is_running, start_time, current_subject, target_seconds
    
    if not is_running:
        return

    is_running = False
    
    final_elapsed = int(time.time() - start_time)
    minutes = final_elapsed // 60
    seconds = final_elapsed % 60
    result_str = f"{minutes}分 {seconds}秒"

    is_goal_met = final_elapsed >= target_seconds

    print(f"【Python】停止。結果: {result_str}, 達成: {is_goal_met}")
    eel.update_list_item(current_subject, result_str, is_goal_met)

# アプリ起動設定
print("--------------------------------------------------")
print(" アプリを起動します。")
print(" ブラウザで http://localhost:8000/day_detail.html が開かれます")
print("--------------------------------------------------")

eel.start('day_detail.html', mode='default', host='0.0.0.0', port=8000)