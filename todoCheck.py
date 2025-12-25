import sqlite3
from datetime import datetime, timedelta

def get_incomplete_tasks():
    """今日より前の未完了タスクをすべて取得する関数"""
    # 判定の基準となる「今日」の日付を取得 (YYYY-MM_DD)
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    conn = sqlite3.connect('study.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 【重要】date < ? (今日より前) かつ status = 0 (未完了) を全て抽出
    # これにより、昨日だけでなく一昨年などの古いものも全て見つけ出せます
    query = "SELECT * FROM tasks WHERE date < ? AND status = 0 ORDER BY date ASC"
    cursor.execute(query, (today_str,))
    rows = cursor.fetchall()
    
    conn.close()
    return rows, today_str

def init_db_for_test():
    """テスト用に1週間前〜今日までのデータをDBに準備する関数"""
    conn = sqlite3.connect('study.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, date TEXT, status INTEGER)''')
    
    # テストのたびにデータが増えすぎないよう一旦リセット
    cursor.execute("DELETE FROM tasks")
    
    now = datetime.now()
    # 1. 1週間前の未完了（Dさんが赤くすべきもの）
    cursor.execute("INSERT INTO tasks (name, date, status) VALUES (?, ?, ?)", 
                    ('1週間前のサボり', (now - timedelta(days=7)).strftime('%Y-%m-%d'), 0))
    # 2. 昨日の未完了（Dさんが赤くすべきもの）
    cursor.execute("INSERT INTO tasks (name, date, status) VALUES (?, ?, ?)", 
                    ('昨日のやり残し', (now - timedelta(days=1)).strftime('%Y-%m-%d'), 0))
    # 3. 今日の予定（Bさんの担当分：通常色）
    cursor.execute("INSERT INTO tasks (name, date, status) VALUES (?, ?, ?)", 
                    ('今日の勉強計画', now.strftime('%Y-%m-%d'), 0))
    # 4. 過去の完了済み（Cさんの担当分：青色/グレー）
    cursor.execute("INSERT INTO tasks (name, date, status) VALUES (?, ?, ?)", 
                    ('完了済みの課題', (now - timedelta(days=2)).strftime('%Y-%m-%d'), 1))
    
    conn.commit()
    conn.close()