from flask import Flask, render_template
import todoCheck # Dさんのファイルを読み込む

app = Flask(__name__)

@app.route('/')
def index():
    # テストデータを準備（本番では他の人の機能がDBを更新します）
    todoCheck.init_db_for_test()
    
    # Dさんのロジックを呼び出す
    overdue_tasks, today_str = todoCheck.get_incomplete_tasks()
    
    # 画面にデータを送る
    return render_template('todoCheck_kari.html', 
                            tasks=overdue_tasks, 
                            today=today_str)

if __name__ == '__main__':
    app.run(debug=True)