import json
import os
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# データ保存用ファイル（サーバー内に保存されます）
DATA_FILE = 'attendance.json'

# 初期メンバーリストとデフォルトのステータス（自宅）
DEFAULT_MEMBERS = [
    "管区台長", "総務部長", "気象防災部長", "気象防災部次長", 
    "防災調整官", "危機管理調整官", "情報セキュリティ管理官", 
    "気象防災情報調整官", "地震津波対策調整官", "火山対策調整官", 
    "気候変動・海洋情報調整官", "総務課長", "会計課長", 
    "業務課長", "地域防災推進課長", "予報課長", "観測整備課長",
    "地震火山課長", "地域火山監視・警報センター所長"
]

def load_data():
    """保存されたデータを読み込む"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    # ファイルがない、または壊れている場合は初期データを返す
    return {name: "自宅" for name in DEFAULT_MEMBERS}

def save_data(data):
    """データをファイルに保存する"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# HTMLのデザイン（見た目）
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>部課長の参集状況</title>
    <style>
        body { font-family: sans-serif; background-color: #f0f0f0; margin: 0; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: white; border: 1px solid #ccc; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        .header { background-color: #003366; color: white; text-align: center; padding: 10px; font-size: 20px; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; border-bottom: 1px solid #ddd; text-align: left; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .btn-push { background-color: #ff6600; color: white; border: none; padding: 6px 12px; font-weight: bold; cursor: pointer; border-radius: 4px; }
        .btn-push:hover { background-color: #e65c00; }
        .status-badge { font-weight: bold; display: inline-block; padding: 4px 8px; border-radius: 4px; }
        .status-自宅 { color: #666; }
        .status-出社中 { color: #008800; background-color: #e6ffe6; }
        .status-登庁 { color: #cc0000; background-color: #ffe6e6; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">部課長の参集状況</div>
        <table>
            {% for name, status in data.items() %}
            <tr>
                <td style="width: 40%; font-weight: bold;">{{ name }}</td>
                <td style="width: 20%;">
                    {# URLのパラメータ名（?name=〇〇）と一致する場合だけボタンを出す #}
                    {% if name == current_user %}
                    <form action="{{ url_for('toggle_status') }}" method="POST" style="margin:0;">
                        <input type="hidden" name="username" value="{{ name }}">
                        <button type="submit" class="btn-push">PUSH</button>
                    </form>
                    {% endif %}
                </td>
                <td style="width: 40%;">
                    <span class="status-badge status-{{ status }}">{{ status }}</span>
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    # URLの ?name=xxx を取得
    current_user = request.args.get('name', '')
    data = load_data()
    return render_template_string(HTML_TEMPLATE, data=data, current_user=current_user)

@app.route('/toggle', methods=['POST'])
def toggle_status():
    username = request.form.get('username')
    data = load_data()
    
    if username in data:
        # ステータスを「自宅」→「登庁」→「出社中」などのように順繰り切り替える
        current_status = data[username]
        if current_status == "自宅":
            next_status = "参集不可"
        elif current_status == "参集不可":
            next_status = "30分以内に登庁"
        elif current_status == "30分以内に登庁":
            next_status = "1時間以内に登庁"
        elif current_status == "1時間以内に登庁":
            next_status = "登庁済み"
        else:
            next_status = "自宅"
            
        data[username] = next_status
        save_data(data)
        
    # ボタンを押したあとも、元の人のパラメータ付きURLに戻る
    return redirect(url_for('home', name=username))

if __name__ == '__main__':
    app.run(debug=True)
