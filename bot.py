import telebot
from telebot import types
from flask import Flask, request
import os

# === Настройки ===
TOKEN = os.getenv("BOT_TOKEN") or "ВСТАВЬ_СВОЙ_ТОКЕН_СЮДА"
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID") or "-1003090948208"  # Замени на свой ID группы

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Хранилище данных пользователей
user_data = {}

# === Приветствие ===
@bot.message_handler(commands=['start'])
def cmd_start(message):
    chat_id = message.chat.id
    welcome_text = (
        "🍞 <b>Добро пожаловать в Булочную №1!</b>\n\n"
        "🥐 Свежая выпечка, сомса, булочки, сеты, компоты и напитки — всё с любовью!\n"
        "🕖 Время работы: <b>07:00–20:00</b> без выходных.\n"
        "☎️ Call-центр: <a href='tel:+998950130660'>+998 95 013 0660</a>\n\n"
        "📦 Нажмите на кнопку <b>«Старт»</b>, чтобы оформить заказ прямо сейчас!"
    )

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("🚀 Старт"))
    bot.send_message(chat_id, welcome_text, parse_mode="HTML", reply_markup=keyboard)

# === Кнопка старт ===
@bot.message_handler(func=lambda message: message.text == "🚀 Старт")
def handle_start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Введите, пожалуйста, ваше имя и фамилию:")
    user_data[chat_id] = {}
    bot.register_next_step_handler(message, get_name)

# === Получение имени ===
def get_name(message):
    chat_id = message.chat.id
    user_data[chat_id]['name'] = message.text

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("📞 Отправить контакт", request_contact=True)
    keyboard.add(button)
    keyboard.add("⬅️ Назад")

    bot.send_message(chat_id, "Теперь отправьте ваш контактный телефон:", reply_markup=keyboard)
    bot.register_next_step_handler(message, get_contact)

# === Получение контакта ===
@bot.message_handler(content_types=['contact'])
def get_contact(message):
    chat_id = message.chat.id
    if message.contact:
        user_data[chat_id]['phone'] = message.contact.phone_number

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton("📍 Отправить локацию", request_location=True)
        keyboard.add(button)
        keyboard.add("⬅️ Назад")

        bot.send_message(chat_id, "Теперь отправьте вашу локацию для доставки:", reply_markup=keyboard)
    else:
        bot.send_message(chat_id, "Пожалуйста, используйте кнопку для отправки контакта.")

# === Получение локации ===
@bot.message_handler(content_types=['location'])
def get_location(message):
    chat_id = message.chat.id
    if message.location:
        user_data[chat_id]['location'] = {
            'latitude': message.location.latitude,
            'longitude': message.location.longitude
        }
        show_menu(chat_id)
    else:
        bot.send_message(chat_id, "Пожалуйста, используйте кнопку для отправки локации.")

# === Главное меню ===
def show_menu(chat_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["🥟 Сомса", "🥯 Сдобные булочки", "🍩 Сладкие булочки", "⬅️ Назад"]
    for b in buttons:
        keyboard.add(b)
    bot.send_message(chat_id, "Выберите категорию:", reply_markup=keyboard)

# === Обработка кнопки Назад ===
@bot.message_handler(func=lambda message: message.text == "⬅️ Назад")
def go_back(message):
    cmd_start(message)

# === Сомса ===
@bot.message_handler(func=lambda message: message.text == "🥟 Сомса")
def somsa_menu(message):
    chat_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🥩 Сомса с мясом — 6000", "🥔 Сомса с картошкой — 5000")
    keyboard.add("⬅️ Назад")
    bot.send_message(chat_id, "Выберите вид сомсы:", reply_markup=keyboard)

# === Завершение заказа ===
@bot.message_handler(func=lambda message: "Сомса" in message.text)
def finish_order(message):
    chat_id = message.chat.id
    user = user_data.get(chat_id, {})
    name = user.get('name', 'Не указано')
    phone = user.get('phone', 'Не указано')
    loc = user.get('location', {})
    latitude = loc.get('latitude', 0)
    longitude = loc.get('longitude', 0)

    order = message.text

    group_message = (
        f"🆕 <b>Новый заказ!</b>\n\n"
        f"👤 Имя: {name}\n"
        f"📞 Телефон: {phone}\n"
        f"📦 Заказ: {order}\n"
        f"📍 Локация: https://maps.google.com/?q={latitude},{longitude}"
    )

    bot.send_message(GROUP_CHAT_ID, group_message, parse_mode="HTML")
    bot.send_message(chat_id, "✅ Спасибо! Ваш заказ был отправлен. Мы скоро свяжемся с вами!")

# === Flask Webhook ===
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))





