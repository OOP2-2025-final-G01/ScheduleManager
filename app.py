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

app = Flask(__name__, template_folder='templates', static_folder='static')


@app.route('/')
def index():
	# 単純に templates/index.html を返す
	return render_template('index.html')


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
