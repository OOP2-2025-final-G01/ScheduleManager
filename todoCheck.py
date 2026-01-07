import sqlite3
from datetime import datetime, timedelta

def get_incomplete_tasks():
    """
    今日より前の未完了タスクをすべて取得する関数
    """
    # 判定の基準となる「今日」の日付を取得 (YYYY-MM_DD)
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    # データベースへの接続
    conn = sqlite3.connect('main.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # ★ここを追加：テーブルがあるか確認し、なければ空で返す
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='todos'")
    if not cursor.fetchone():
        conn.close()
        return [], today_str
    
    # 既存の todos テーブルから「期限切れ」かつ「未完了」を抽出
    # due_date < ? (今日より前) かつ is_completed = 0 (未完了) を全て抽出
    # これにより、昨日だけでなく一昨年などの古いものも全て見つけ出せます
    query = "SELECT * FROM todos WHERE due_date < ? AND is_completed = 0 ORDER BY due_date ASC"
    
    try:
        cursor.execute(query, (today_str,))
        rows = cursor.fetchall()
    except sqlite3.OperationalError:
        # 万が一、他メンバーの初期化がまだでテーブルがない場合は空リストを返す
        rows = []
    
    conn.close()
    return rows, today_str