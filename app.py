from flask import Flask, request, render_template_string, jsonify
import requests
import json
import re
import socket
from urllib.parse import quote
from datetime import datetime

app = Flask(__name__)

API_URL = "https://levsearchnumbertest-36dr.onrender.com"
API_TOKEN = "LevSearchApiAll"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Lev Search — OSINT инструмент</title>
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #0a0e27;
            color: #00ff9d;
            padding: 20px;
        }
        h1 {
            color: #00ff9d;
            border-bottom: 1px solid #00ff9d;
            padding-bottom: 10px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .search-box {
            background: #0f1228;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        input, select {
            background: #1a1f3a;
            border: 1px solid #00ff9d;
            color: #00ff9d;
            padding: 10px;
            margin: 5px;
            border-radius: 5px;
        }
        button {
            background: #00ff9d;
            color: #0a0e27;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            font-weight: bold;
            border-radius: 5px;
        }
        button:hover {
            background: #00cc7a;
        }
        .result {
            background: #0f1228;
            padding: 20px;
            border-radius: 10px;
            overflow-x: auto;
        }
        pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: monospace;
            font-size: 12px;
            margin: 0;
        }
        .nav {
            margin-bottom: 20px;
        }
        .nav a {
            color: #00ff9d;
            margin-right: 15px;
            text-decoration: none;
        }
        .nav a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Lev Search — OSINT инструмент</h1>
        
        <div class="nav">
            <a href="/">🏠 Главная</a>
            <a href="/search">🔎 Поиск</a>
            <a href="/card">💳 BIN карты</a>
            <a href="/domain">🌐 Домен</a>
            <a href="/vk">👤 VK</a>
            <a href="/ip">🌍 IP</a>
            <a href="/tiktok">🎵 TikTok</a>
            <a href="/telegram">📱 Telegram</a>
            <a href="/bank">🏦 Банк по ИНН</a>
            <a href="/leakosint">🔥 LeakOSINT</a>
            <a href="/intelx">📡 IntelX</a>
        </div>
        
        <div class="search-box">
            <form method="GET" action="/search">
                <input type="text" name="q" placeholder="Телефон, email, ФИО..." value="{{ query }}" size="50">
                <button type="submit">🔍 Искать</button>
            </form>
        </div>
        
        {% if result %}
        <div class="result">
            <pre>{{ result }}</pre>
        </div>
        {% endif %}
        
        <div class="search-box">
            <h3>⚡ Быстрые примеры:</h3>
            <p>
                <a href="/search?q=79233756070">📞 Поиск по номеру</a> |
                <a href="/ip?address=8.8.8.8">🌍 IP геолокация</a> |
                <a href="/card?bin=477964">💳 BIN карты</a> |
                <a href="/domain?name=google.com">🌐 Информация о домене</a> |
                <a href="/vk?id=1">👤 VK профиль</a> |
                <a href="/tiktok?username=marvel">🎵 TikTok</a> |
                <a href="/telegram?username=durov">📱 Telegram</a> |
                <a href="/bank?inn=7707083893">🏦 Сбербанк по ИНН</a>
            </p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, query="", result=None)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return render_template_string(HTML_TEMPLATE, query="", result=None)
    
    try:
        r = requests.get(f"{API_URL}/search", params={"token": API_TOKEN, "q": query}, timeout=60)
        result = json.dumps(r.json(), indent=2, ensure_ascii=False)
        return render_template_string(HTML_TEMPLATE, query=query, result=result)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, query=query, result=f"Ошибка: {e}")

@app.route('/card')
def card():
    bin_num = request.args.get('bin', '')
    if not bin_num:
        return render_template_string(HTML_TEMPLATE, query="", result="Введите BIN (первые 6 цифр карты)")
    
    try:
        r = requests.get(f"{API_URL}/card", params={"token": API_TOKEN, "bin": bin_num}, timeout=30)
        result = json.dumps(r.json(), indent=2, ensure_ascii=False)
        return render_template_string(HTML_TEMPLATE, query=f"BIN: {bin_num}", result=result)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, query=f"BIN: {bin_num}", result=f"Ошибка: {e}")

@app.route('/domain')
def domain():
    domain_name = request.args.get('name', '')
    if not domain_name:
        return render_template_string(HTML_TEMPLATE, query="", result="Введите домен")
    
    try:
        r = requests.get(f"{API_URL}/domain", params={"token": API_TOKEN, "name": domain_name}, timeout=30)
        result = json.dumps(r.json(), indent=2, ensure_ascii=False)
        return render_template_string(HTML_TEMPLATE, query=f"Домен: {domain_name}", result=result)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, query=f"Домен: {domain_name}", result=f"Ошибка: {e}")

@app.route('/vk')
def vk():
    vk_id = request.args.get('id', '')
    if not vk_id:
        return render_template_string(HTML_TEMPLATE, query="", result="Введите VK ID")
    
    try:
        r = requests.get(f"{API_URL}/vk", params={"token": API_TOKEN, "id": vk_id}, timeout=30)
        result = json.dumps(r.json(), indent=2, ensure_ascii=False)
        return render_template_string(HTML_TEMPLATE, query=f"VK ID: {vk_id}", result=result)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, query=f"VK ID: {vk_id}", result=f"Ошибка: {e}")

@app.route('/ip')
def ip():
    ip_address = request.args.get('address', '')
    if not ip_address:
        return render_template_string(HTML_TEMPLATE, query="", result="Введите IP адрес")
    
    try:
        r = requests.get(f"{API_URL}/ip", params={"token": API_TOKEN, "address": ip_address}, timeout=30)
        result = json.dumps(r.json(), indent=2, ensure_ascii=False)
        return render_template_string(HTML_TEMPLATE, query=f"IP: {ip_address}", result=result)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, query=f"IP: {ip_address}", result=f"Ошибка: {e}")

@app.route('/tiktok')
def tiktok():
    username = request.args.get('username', '')
    if not username:
        return render_template_string(HTML_TEMPLATE, query="", result="Введите username TikTok")
    
    try:
        r = requests.get(f"{API_URL}/tiktok", params={"token": API_TOKEN, "username": username}, timeout=30)
        result = json.dumps(r.json(), indent=2, ensure_ascii=False)
        return render_template_string(HTML_TEMPLATE, query=f"TikTok: {username}", result=result)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, query=f"TikTok: {username}", result=f"Ошибка: {e}")

@app.route('/telegram')
def telegram():
    username = request.args.get('username', '')
    if not username:
        return render_template_string(HTML_TEMPLATE, query="", result="Введите username Telegram")
    
    try:
        r = requests.get(f"{API_URL}/telegram", params={"token": API_TOKEN, "username": username}, timeout=30)
        result = json.dumps(r.json(), indent=2, ensure_ascii=False)
        return render_template_string(HTML_TEMPLATE, query=f"Telegram: {username}", result=result)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, query=f"Telegram: {username}", result=f"Ошибка: {e}")

@app.route('/bank')
def bank():
    inn = request.args.get('inn', '')
    if not inn:
        return render_template_string(HTML_TEMPLATE, query="", result="Введите ИНН банка")
    
    try:
        r = requests.get(f"{API_URL}/bank", params={"token": API_TOKEN, "inn": inn}, timeout=30)
        result = json.dumps(r.json(), indent=2, ensure_ascii=False)
        return render_template_string(HTML_TEMPLATE, query=f"ИНН: {inn}", result=result)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, query=f"ИНН: {inn}", result=f"Ошибка: {e}")

@app.route('/leakosint')
def leakosint():
    query = request.args.get('q', '')
    if not query:
        return render_template_string(HTML_TEMPLATE, query="", result="Введите запрос (телефон, email, ФИО)")
    
    try:
        r = requests.get(f"{API_URL}/leakosint", params={"token": API_TOKEN, "q": query}, timeout=60)
        result = json.dumps(r.json(), indent=2, ensure_ascii=False)
        return render_template_string(HTML_TEMPLATE, query=f"LeakOSINT: {query}", result=result)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, query=f"LeakOSINT: {query}", result=f"Ошибка: {e}")

@app.route('/intelx')
def intelx():
    phone = request.args.get('phone', '')
    if not phone:
        return render_template_string(HTML_TEMPLATE, query="", result="Введите номер телефона")
    
    try:
        r = requests.get(f"{API_URL}/intelx", params={"token": API_TOKEN, "phone": phone}, timeout=60)
        result = json.dumps(r.json(), indent=2, ensure_ascii=False)
        return render_template_string(HTML_TEMPLATE, query=f"IntelX: {phone}", result=result)
    except Exception as e:
        return render_template_string(HTML_TEMPLATE, query=f"IntelX: {phone}", result=f"Ошибка: {e}")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
