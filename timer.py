import eel
import time
import threading

eel.init('templates')

# --- グローバル変数 ---
is_running = False
current_subject = ""      # 現在計測中の科目名
target_seconds = 0        # 目標時間（秒換算）
start_time = 0            # 計測開始時刻

@eel.expose
def start_python_timer(subject_name, target_min_str):
    """
    タイマーを開始する関数
    subject_name: "英語" など
    target_min_str: "20" (文字列の数字)
    """
    global is_running, current_subject, target_seconds, start_time
    
    if is_running:
        return

    # 状態の保存
    is_running = True
    current_subject = subject_name
    # "20" などの文字列を数値に変換し、秒にする（20分 * 60 = 1200秒）
    try:
        target_seconds = int(target_min_str) * 60
    except ValueError:
        target_seconds = 0 # エラー時は0秒目標とする

    start_time = time.time()
    
    print(f"【Python】{current_subject} 開始 (目標: {target_seconds}秒)")
    threading.Thread(target=run_timer_loop, daemon=True).start()

def run_timer_loop():
    global is_running, start_time
    while is_running:
        elapsed_time = int(time.time() - start_time)
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_str = f"{minutes:02}:{seconds:02}"
        
        eel.update_time_display(time_str)
        eel.sleep(0.1)

@eel.expose
def stop_python_timer():
    """タイマーを停止し、結果を判定して画面に返す"""
    global is_running, start_time, current_subject, target_seconds
    
    if not is_running:
        return

    is_running = False
    
    # 最終的な時間を計算
    final_elapsed = int(time.time() - start_time)
    minutes = final_elapsed // 60
    seconds = final_elapsed % 60
    
    # 表示用の文字列 (例: "20分 5秒")
    result_str = f"{minutes}分 {seconds}秒"

    # ★目標達成判定！ (経過時間 >= 目標時間)
    is_goal_met = final_elapsed >= target_seconds

    print(f"【Python】停止。結果: {result_str}, 達成: {is_goal_met}")

    # ★JavaScriptの関数を呼び出して、リストを更新する
    # 引数: 科目名, 時間の文字, メダルを表示するか(True/False)
    eel.update_list_item(current_subject, result_str, is_goal_met)

# アプリ起動
eel.start('day_detail.html', mode='default', host='0.0.0.0', port=8000)