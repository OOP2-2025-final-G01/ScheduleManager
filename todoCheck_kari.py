from flask import Flask, render_template
import todoCheck as todoCheck  # ← ここを「todoCheck」に変更！

app = Flask(__name__)

@app.route('/')
def index():
    #検索ロジック呼び出し
    overdue_tasks, today_str = todoCheck.get_incomplete_tasks()
    # 画面にデータを送る
    return render_template('todoCheck_kari.html', tasks=overdue_tasks, today=today_str)

if __name__ == '__main__':
    # ポート番号は app.py に合わせて 5001 にしておくと衝突しにくいです
    app.run(host='0.0.0.0', port=5001, debug=True)