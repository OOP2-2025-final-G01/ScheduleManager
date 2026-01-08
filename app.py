"""
ScheduleManager - minimal Flask runner

使い方:
 1) 仮想環境を作成 (推奨): python3 -m venv .venv && source .venv/bin/activate
 2) 依存をインストール: pip install Flask
 3) サーバー起動: PORT=5001 python app.py

このファイルは最小限の Flask アプリを定義し、`templates/index.html` を返します。
"""

from flask import Flask, render_template
import os
import sqlite3
from flask import jsonify
from datetime import date

app = Flask(__name__, template_folder='templates', static_folder='static')


@app.route('/')
def index():
	# 単純に templates/index.html を返す
	return render_template('index.html')


@app.route('/api/stats/monthly')
def api_monthly_stats():
	"""今月の予定に対する達成数と合計数を返す。
	レスポンス: { "completed": X, "total": Y }
	条件: todos.due_date が当月に該当する行を集計する（YYYY-MM-DD）
	"""
	# 今月の最初と最後の日を計算
	today = date.today()
	first_day = today.replace(day=1)
	# 次の月の1日から1日戻して今月の最終日を作る
	if today.month == 12:
		next_month = today.replace(year=today.year+1, month=1, day=1)
	else:
		next_month = today.replace(month=today.month+1, day=1)
	last_day = next_month - (date.resolution)

	start_str = first_day.isoformat()
	end_str = last_day.isoformat()

	try:
		conn = sqlite3.connect('main.db')
		cur = conn.cursor()
		# due_date が NULL のエントリは集計対象外
		cur.execute("""
			SELECT
				SUM(CASE WHEN is_completed=1 THEN 1 ELSE 0 END) as completed,
				COUNT(*) as total
			FROM todos
			WHERE due_date IS NOT NULL
			  AND due_date >= ?
			  AND due_date <= ?
		""", (start_str, end_str))
		row = cur.fetchone()
		conn.close()

		completed = int(row[0] or 0)
		total = int(row[1] or 0)
	except Exception as exc:
		# DB ファイルやテーブルがない場合などは 0/0 を返す
		print('DB error in /api/stats/monthly:', exc)
		completed = 0
		total = 0

	return jsonify({"completed": completed, "total": total})


@app.route('/stats')
def stats():
	# 統計画面（templates/stats.html がプレースホルダでも404回避のため実装）
	return render_template('stats.html')


@app.route('/day/<date>')
def day_detail(date):
	# 日別詳細画面（テンプレートに日付を渡す）
	return render_template('day_detail.html', date=date)


@app.errorhandler(404)
def page_not_found(e):
	# 開発中は未実装ルートがあってもトップに戻す（後で変更可）
	return render_template('index.html'), 200


if __name__ == '__main__':
	# 開発用サーバーで実行
	port = int(os.environ.get('PORT', 5001))
	app.run(host='0.0.0.0', port=port, debug=True)
