import sqlite3

def init_database():
    # データベースファイル名: main.db
    conn = sqlite3.connect("main.db")
    cursor = conn.cursor()
    
    # テーブル名: todos
    # id: 自動採番される一意のID
    # task: やることの内容 (文字列)
    # due_date: いつやるか (日付文字列 'YYYY-MM-DD')
    # duration: やる時間 (数値、または '1時間' などの文字列)
    # is_completed: 完了フラグ (0:未完了, 1:完了)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            due_date TEXT,
            duration TEXT,
            actual_time INTEGER,
            is_completed INTEGER DEFAULT 0
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ main.db を初期化しました。")
    print("カラム定義: task(文字列), due_date(日付), duration(時間), is_completed(フラグ)")

if __name__ == "__main__":
    init_database()