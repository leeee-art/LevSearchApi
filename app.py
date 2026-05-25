import telebot
import requests
import json
import re
import os
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Конфигурация
BOT_TOKEN = "8699671728:AAEPBYcSFKzB1k_N3auB__NZhF2XzUyo17c"
API_URL = "https://levsearchnumbertest-36dr.onrender.com"
API_TOKEN = "LevSearchApiAll"
ADMIN_ID = 6988163297

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Хранение данных пользователей (в памяти, при перезапуске теряется)
user_data = {}

# ========== КЛАВИАТУРЫ ==========
def main_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton("📞 Поиск по номеру", callback_data="search_phone"),
        InlineKeyboardButton("💳 BIN карты", callback_data="search_bin"),
        InlineKeyboardButton("🌐 Информация о домене", callback_data="search_domain"),
        InlineKeyboardButton("👤 VK пользователь", callback_data="search_vk"),
        InlineKeyboardButton("🌍 IP адрес", callback_data="search_ip"),
        InlineKeyboardButton("🎵 TikTok", callback_data="search_tiktok"),
        InlineKeyboardButton("📱 Telegram", callback_data="search_telegram"),
        InlineKeyboardButton("🏦 Банк по ИНН", callback_data="search_bank"),
        InlineKeyboardButton("🔥 LeakOSINT", callback_data="search_leak"),
        InlineKeyboardButton("💬 WhatsApp", callback_data="search_whatsapp"),
        InlineKeyboardButton("👥 Одноклассники", callback_data="search_ok"),
        InlineKeyboardButton("📧 Email", callback_data="search_email"),
        InlineKeyboardButton("❓ Помощь", callback_data="help")
    ]
    keyboard.add(*buttons)
    return keyboard

def admin_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    buttons = [
        InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast"),
        InlineKeyboardButton("👥 Пользователи", callback_data="admin_users")
    ]
    keyboard.add(*buttons)
    return keyboard

def back_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="back"))
    return keyboard

# ========== ФУНКЦИИ API ==========
def call_api(endpoint, params):
    try:
        url = f"{API_URL}{endpoint}"
        params['token'] = API_TOKEN
        print(f"Calling API: {url} with params: {params}")
        response = requests.get(url, params=params, timeout=60)
        print(f"Response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            return json.dumps(data, indent=2, ensure_ascii=False)
        return f"Ошибка API: HTTP {response.status_code}\n{response.text[:500]}"
    except Exception as e:
        return f"Ошибка: {str(e)}"

# ========== ОБРАБОТЧИКИ КОМАНД ==========
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_data[user_id] = {"state": None}
    
    welcome_text = """
🔍 <b>Lev Search Bot - OSINT инструмент</b>

Я помогу вам найти информацию по различным данным.

<b>Доступные функции:</b>
• Поиск по номеру телефона
• Информация о BIN карты
• Данные о домене
• Информация о VK пользователе
• Геолокация IP
• Данные TikTok
• Информация о Telegram
• Поиск банка по ИНН
• LeakOSINT утечки
• Проверка WhatsApp
• Поиск в Одноклассниках
• Проверка Email

<b>Команды:</b>
/start - Запустить бота
/help - Помощь
/admin - Админ панель (только для админа)

Выберите нужную функцию:
"""
    
    bot.send_message(
        message.chat.id, 
        welcome_text, 
        parse_mode='HTML',
        reply_markup=main_keyboard()
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
<b>📖 Инструкция по использованию:</b>

1. Выберите нужную функцию из меню
2. Введите запрос (номер телефона, BIN, домен и т.д.)
3. Получите результат

<b>Примеры запросов:</b>
• Номер телефона: 79233756070
• BIN карты: 477964
• Домен: google.com
• VK ID: 1
• IP адрес: 8.8.8.8
• TikTok: marvel
• Telegram: durov
• ИНН: 7707083893
• Email: test@gmail.com

<b>⚠️ Внимание:</b>
Некоторые функции могут работать медленно из-за ограничений API.
"""
    bot.send_message(message.chat.id, help_text, parse_mode='HTML', reply_markup=back_keyboard())

@bot.message_handler(commands=['admin'])
def admin_command(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id, 
            "👑 <b>Админ панель</b>\n\nВыберите действие:", 
            parse_mode='HTML',
            reply_markup=admin_keyboard()
        )
    else:
        bot.send_message(message.chat.id, "❌ У вас нет доступа к админ панели")

# ========== ОБРАБОТЧИКИ CALLBACK ==========
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if call.data == "back":
        bot.edit_message_text(
            "Выберите нужную функцию:", 
            chat_id, 
            call.message.message_id,
            reply_markup=main_keyboard()
        )
    
    elif call.data == "help":
        help_text = """
<b>📖 Инструкция по использованию:</b>

1. Выберите нужную функцию из меню
2. Введите запрос
3. Получите результат

<b>Примеры запросов:</b>
• Номер телефона: 79233756070
• BIN карты: 477964
• Домен: google.com
• VK ID: 1
• IP адрес: 8.8.8.8
• TikTok: marvel
• Telegram: durov
• ИНН: 7707083893
• Email: test@gmail.com
"""
        bot.edit_message_text(
            help_text, 
            chat_id, 
            call.message.message_id,
            parse_mode='HTML',
            reply_markup=back_keyboard()
        )
    
    elif call.data == "search_phone":
        user_data[user_id] = {"state": "phone"}
        bot.edit_message_text(
            "📞 Введите номер телефона (например: 79233756070):", 
            chat_id, 
            call.message.message_id,
            reply_markup=back_keyboard()
        )
    
    elif call.data == "search_bin":
        user_data[user_id] = {"state": "bin"}
        bot.edit_message_text(
            "💳 Введите первые 6 цифр карты (BIN):", 
            chat_id, 
            call.message.message_id,
            reply_markup=back_keyboard()
        )
    
    elif call.data == "search_domain":
        user_data[user_id] = {"state": "domain"}
        bot.edit_message_text(
            "🌐 Введите домен (например: google.com):", 
            chat_id, 
            call.message.message_id,
            reply_markup=back_keyboard()
        )
    
    elif call.data == "search_vk":
        user_data[user_id] = {"state": "vk"}
        bot.edit_message_text(
            "👤 Введите ID пользователя VK (например: 1):", 
            chat_id, 
            call.message.message_id,
            reply_markup=back_keyboard()
        )
    
    elif call.data == "search_ip":
        user_data[user_id] = {"state": "ip"}
        bot.edit_message_text(
            "🌍 Введите IP адрес (например: 8.8.8.8):", 
            chat_id, 
            call.message.message_id,
            reply_markup=back_keyboard()
        )
    
    elif call.data == "search_tiktok":
        user_data[user_id] = {"state": "tiktok"}
        bot.edit_message_text(
            "🎵 Введите username TikTok (без @):", 
            chat_id, 
            call.message.message_id,
            reply_markup=back_keyboard()
        )
    
    elif call.data == "search_telegram":
        user_data[user_id] = {"state": "telegram"}
        bot.edit_message_text(
            "📱 Введите username Telegram (без @):", 
            chat_id, 
            call.message.message_id,
            reply_markup=back_keyboard()
        )
    
    elif call.data == "search_bank":
        user_data[user_id] = {"state": "bank"}
        bot.edit_message_text(
            "🏦 Введите ИНН организации:", 
            chat_id, 
            call.message.message_id,
            reply_markup=back_keyboard()
        )
    
    elif call.data == "search_leak":
        user_data[user_id] = {"state": "leak"}
        bot.edit_message_text(
            "🔥 Введите запрос для LeakOSINT (номер, email, логин):", 
            chat_id, 
            call.message.message_id,
            reply_markup=back_keyboard()
        )
    
    elif call.data == "search_whatsapp":
        user_data[user_id] = {"state": "whatsapp"}
        bot.edit_message_text(
            "💬 Введите номер телефона для проверки WhatsApp:", 
            chat_id, 
            call.message.message_id,
            reply_markup=back_keyboard()
        )
    
    elif call.data == "search_ok":
        user_data[user_id] = {"state": "ok"}
        bot.edit_message_text(
            "👥 Введите номер телефона для поиска в Одноклассниках:", 
            chat_id, 
            call.message.message_id,
            reply_markup=back_keyboard()
        )
    
    elif call.data == "search_email":
        user_data[user_id] = {"state": "email"}
        bot.edit_message_text(
            "📧 Введите email адрес (например: test@gmail.com):", 
            chat_id, 
            call.message.message_id,
            reply_markup=back_keyboard()
        )
    
    # Админ функции
    elif call.data == "admin_stats":
        if user_id == ADMIN_ID:
            stats = f"""
<b>📊 Статистика бота:</b>

👥 Всего пользователей: {len(user_data)}
💬 Активных сессий: {sum(1 for u in user_data.values() if u.get('state'))}
"""
            bot.edit_message_text(
                stats,
                chat_id,
                call.message.message_id,
                parse_mode='HTML',
                reply_markup=admin_keyboard()
            )
    
    elif call.data == "admin_broadcast":
        if user_id == ADMIN_ID:
            user_data[user_id] = {"state": "broadcast"}
            bot.edit_message_text(
                "📢 Введите текст для рассылки всем пользователям:",
                chat_id,
                call.message.message_id,
                reply_markup=back_keyboard()
            )
    
    elif call.data == "admin_users":
        if user_id == ADMIN_ID:
            users_list = "👥 <b>Список пользователей:</b>\n\n"
            for uid in list(user_data.keys())[:20]:
                users_list += f"• `{uid}`\n"
            bot.edit_message_text(
                users_list,
                chat_id,
                call.message.message_id,
                parse_mode='HTML',
                reply_markup=admin_keyboard()
            )

# ========== ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ ==========
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    text = message.text.strip()
    
    if user_id not in user_data:
        user_data[user_id] = {"state": None}
    
    state = user_data[user_id].get("state")
    
    # Рассылка от админа
    if state == "broadcast" and user_id == ADMIN_ID:
        sent_count = 0
        for uid in user_data:
            try:
                bot.send_message(uid, f"📢 <b>Рассылка от администратора:</b>\n\n{text}", parse_mode='HTML')
                sent_count += 1
            except:
                pass
        bot.send_message(chat_id, f"✅ Рассылка завершена! Отправлено {sent_count} пользователям.", reply_markup=admin_keyboard())
        user_data[user_id]["state"] = None
        return
    
    if not state:
        bot.send_message(chat_id, "❌ Пожалуйста, выберите функцию из меню", reply_markup=main_keyboard())
        return
    
    # Отправляем сообщение "обработка"
    status_msg = bot.send_message(chat_id, "⏳ Обработка запроса...")
    
    # Обработка разных типов запросов
    if state == "phone":
        if not re.match(r'^\+?\d{10,15}$', text):
            bot.edit_message_text("❌ Неверный формат номера. Введите 10-15 цифр.", chat_id, status_msg.message_id)
            user_data[user_id]["state"] = None
            return
        result = call_api("/search", {"q": text})
        
    elif state == "bin":
        if not re.match(r'^\d{6}$', text[:6]):
            bot.edit_message_text("❌ BIN должен содержать первые 6 цифр карты", chat_id, status_msg.message_id)
            user_data[user_id]["state"] = None
            return
        result = call_api("/card", {"bin": text[:6]})
        
    elif state == "domain":
        result = call_api("/domain", {"name": text})
        
    elif state == "vk":
        result = call_api("/vk", {"id": text})
        
    elif state == "ip":
        if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', text):
            bot.edit_message_text("❌ Неверный формат IP адреса", chat_id, status_msg.message_id)
            user_data[user_id]["state"] = None
            return
        result = call_api("/ip", {"address": text})
        
    elif state == "tiktok":
        result = call_api("/tiktok", {"username": text.replace('@', '')})
        
    elif state == "telegram":
        result = call_api("/telegram", {"username": text.replace('@', '')})
        
    elif state == "bank":
        result = call_api("/bank", {"inn": text})
        
    elif state == "leak":
        result = call_api("/leakosint", {"q": text})
        
    elif state == "whatsapp":
        result = call_api("/whatsapp", {"phone": re.sub(r'\D', '', text)})
        
    elif state == "ok":
        result = call_api("/odnoklassniki", {"phone": re.sub(r'\D', '', text)})
        
    elif state == "email":
        if '@' not in text or '.' not in text:
            bot.edit_message_text("❌ Неверный формат email", chat_id, status_msg.message_id)
            user_data[user_id]["state"] = None
            return
        result = call_api("/email", {"address": text})
        
    else:
        result = "Неизвестная команда"
    
    # Форматируем и отправляем результат
    if len(result) > 4000:
        parts = [result[i:i+4000] for i in range(0, len(result), 4000)]
        bot.edit_message_text(f"✅ <b>Результат поиска:</b>\n\n<pre>{parts[0]}</pre>", 
                            chat_id, status_msg.message_id, parse_mode='HTML')
        for part in parts[1:]:
            bot.send_message(chat_id, f"<pre>{part}</pre>", parse_mode='HTML')
    else:
        bot.edit_message_text(f"✅ <b>Результат поиска:</b>\n\n<pre>{result}</pre>", 
                            chat_id, status_msg.message_id, parse_mode='HTML')
    
    # Сбрасываем состояние
    user_data[user_id]["state"] = None
    
    # Показываем меню
    bot.send_message(chat_id, "Выберите следующую функцию:", reply_markup=main_keyboard())

# ========== FLASK WEBHOOK ==========
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Bad Request', 400

@app.route('/')
def index():
    return "LevSearch Telegram Bot is running!"

def set_webhook():
    webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    print(f"Setting webhook to: {webhook_url}")
    bot.remove_webhook()
    result = bot.set_webhook(url=webhook_url)
    print(f"Webhook set result: {result}")

if __name__ == "__main__":
    set_webhook()
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
