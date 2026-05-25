from flask import Flask, request, jsonify
import requests
import json
import re
import socket
from urllib.parse import unquote, quote
from datetime import datetime, timedelta

app = Flask(__name__)

BOT_TOKEN = "8699671728:AAGBA_82MqWds8FlyGfKcNwp8BZzNSNU6EY"
API_URL = "https://levsearchnumbertest-36dr.onrender.com"
API_TOKEN = "LevSearchApiAll"
ADMIN_ID = 6988163297

users_data = {}
promocodes = {}

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=5)
    except:
        pass

def get_user(user_id):
    uid = str(user_id)
    if uid not in users_data:
        users_data[uid] = {"requests": 0, "date": "", "promo_used": []}
    today = datetime.now().strftime("%Y-%m-%d")
    if users_data[uid]["date"] != today:
        users_data[uid]["requests"] = 0
        users_data[uid]["date"] = today
    return users_data[uid]

@app.route(f'/webhook/{BOT_TOKEN}', methods=['POST'])
def webhook():
    update = request.get_json()
    if not update or "message" not in update:
        return "ok", 200
    
    msg = update["message"]
    chat_id = msg["chat"]["id"]
    text = msg.get("text", "")
    user_id = msg["from"]["id"]
    
    if text == "/start":
        send_message(chat_id, "🔍 Lev Search Bot\n\n/phone 79999999999 - поиск по номеру\n/ip 8.8.8.8 - геолокация IP\n/card 477964 - BIN карты\n/domain google.com - информация о домене\n/vk 1 - профиль VK\n/tiktok marvel - профиль TikTok\n/telegram durov - проверка Telegram\n/bank 7707083893 - банк по ИНН\n/leakosint 79999999999 - поиск в утечках\n/intelx 79999999999 - IntelX\n/omkarphone 79999999999 - оператор\n/omkaremail test@gmail.com - верификация email\n/whatsapp 79999999999 - проверка WhatsApp\n/odnoklassniki 79999999999 - проверка ОК\n\n/status - остаток запросов\n/promo <код> - активировать промокод")
        return "ok", 200
    
    if text == "/status":
        user = get_user(user_id)
        if user_id == ADMIN_ID:
            send_message(chat_id, "👑 Админ — безлимит")
        else:
            send_message(chat_id, f"📊 Осталось запросов: {3 - user['requests']} из 3")
        return "ok", 200
    
    if text.startswith("/promo"):
        if user_id == ADMIN_ID:
            send_message(chat_id, "👑 Админу промокоды не нужны")
            return "ok", 200
        parts = text.split()
        if len(parts) < 2:
            send_message(chat_id, "❌ /promo <код>")
            return "ok", 200
        code = parts[1].upper()
        user = get_user(user_id)
        if code in user["promo_used"]:
            send_message(chat_id, "❌ Вы уже использовали этот промокод")
        elif code not in promocodes:
            send_message(chat_id, "❌ Промокод не найден")
        else:
            promo = promocodes[code]
            if promo["activations_left"] <= 0:
                send_message(chat_id, "❌ Промокод больше не активен")
            elif promo["expires"] < datetime.now().strftime("%Y-%m-%d"):
                send_message(chat_id, "❌ Срок действия промокода истёк")
            else:
                user["promo_used"].append(code)
                user["requests"] = max(0, user["requests"] - promo["bonus"])
                promo["activations_left"] -= 1
                send_message(chat_id, f"✅ Промокод активирован! +{promo['bonus']} запросов")
        return "ok", 200
    
    if text.startswith("/createpromo") and user_id == ADMIN_ID:
        parts = text.split()
        if len(parts) < 5:
            send_message(chat_id, "❌ /createpromo <код> <активаций> <бонус> <дней>")
        else:
            code = parts[1].upper()
            activations = int(parts[2])
            bonus = int(parts[3])
            days = int(parts[4])
            expires = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
            promocodes[code] = {"activations_left": activations, "bonus": bonus, "expires": expires}
            send_message(chat_id, f"✅ Создан промокод {code}: {activations} активаций, +{bonus} запросов, до {expires}")
        return "ok", 200
    
    if text.startswith("/listpromo") and user_id == ADMIN_ID:
        if not promocodes:
            send_message(chat_id, "Нет активных промокодов")
        else:
            res = "📋 Промокоды:\n"
            for code, data in promocodes.items():
                res += f"🔹 {code}: {data['activations_left']} активаций, +{data['bonus']} запросов, до {data['expires']}\n"
            send_message(chat_id, res)
        return "ok", 200
    
    # Обработка всех команд поиска
    if text.startswith("/"):
        user = get_user(user_id)
        if user_id != ADMIN_ID and user["requests"] >= 3:
            send_message(chat_id, "❌ Лимит запросов исчерпан. Используйте /promo")
            return "ok", 200
        
        parts = text.split()
        cmd = parts[0].lower()
        endpoint = None
        params = {"token": API_TOKEN}
        
        if cmd == "/ip" and len(parts) > 1:
            endpoint = f"{API_URL}/ip"
            params["address"] = parts[1]
        elif cmd == "/phone" and len(parts) > 1:
            endpoint = f"{API_URL}/search"
            params["q"] = parts[1]
        elif cmd == "/card" and len(parts) > 1:
            endpoint = f"{API_URL}/card"
            params["bin"] = parts[1]
        elif cmd == "/domain" and len(parts) > 1:
            endpoint = f"{API_URL}/domain"
            params["name"] = parts[1]
        elif cmd == "/vk" and len(parts) > 1:
            endpoint = f"{API_URL}/vk"
            params["id"] = parts[1]
        elif cmd == "/tiktok" and len(parts) > 1:
            endpoint = f"{API_URL}/tiktok"
            params["username"] = parts[1]
        elif cmd == "/telegram" and len(parts) > 1:
            endpoint = f"{API_URL}/telegram"
            params["username"] = parts[1]
        elif cmd == "/bank" and len(parts) > 1:
            endpoint = f"{API_URL}/bank"
            params["inn"] = parts[1]
        elif cmd == "/leakosint" and len(parts) > 1:
            endpoint = f"{API_URL}/leakosint"
            params["q"] = parts[1]
        elif cmd == "/intelx" and len(parts) > 1:
            endpoint = f"{API_URL}/intelx"
            params["phone"] = parts[1]
        elif cmd == "/omkarphone" and len(parts) > 1:
            endpoint = f"{API_URL}/omkar/phone"
            params["phone"] = parts[1]
        elif cmd == "/omkaremail" and len(parts) > 1:
            endpoint = f"{API_URL}/omkar/email"
            params["email"] = parts[1]
        elif cmd == "/whatsapp" and len(parts) > 1:
            endpoint = f"{API_URL}/whatsapp"
            params["phone"] = parts[1]
        elif cmd == "/odnoklassniki" and len(parts) > 1:
            endpoint = f"{API_URL}/odnoklassniki"
            params["phone"] = parts[1]
        else:
            send_message(chat_id, "❌ Неверная команда. Используйте /start для списка команд")
            return "ok", 200
        
        send_message(chat_id, "⏳ Поиск...")
        try:
            r = requests.get(endpoint, params=params, timeout=60)
            data = r.json()
            text_res = json.dumps(data, indent=2, ensure_ascii=False)
            if len(text_res) > 4096:
                text_res = text_res[:4000] + "\n\n... (обрезано, результат слишком большой)"
            send_message(chat_id, f"<pre>{text_res}</pre>")
            if user_id != ADMIN_ID:
                user["requests"] += 1
        except Exception as e:
            send_message(chat_id, f"❌ Ошибка: {e}")
        
        return "ok", 200
    
    return "ok", 200

@app.route('/')
def index():
    return "Lev Search Bot is running"

application = app
