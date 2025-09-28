import telebot
from telebot import types
import os
from flask import Flask
import threading

# === Настройки ===
TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")  # ID группы, куда будут приходить заказы
bot = telebot.TeleBot(TOKEN)

# Хранилище данных пользователей
user_data = {}

# --- Команда старт и кнопка Старт ---
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    # Клавиатура с кнопкой Старт
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_button = types.KeyboardButton("🚀 Старт")
    keyboard.add(start_button)

    bot.send_message(chat_id, "Привет! Нажми кнопку 'Старт', чтобы начать оформление заказа.", reply_markup=keyboard)

# Обработка нажатия кнопки "Старт"
@bot.message_handler(func=lambda message: message.text == "🚀 Старт")
def handle_start_button(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Введите, пожалуйста, ваше имя и фамилию:")
    user_data[chat_id] = {}
    bot.register_next_step_handler(message, get_name)

# Получаем имя и фамилию
def get_name(message):
    chat_id = message.chat.id
    user_data[chat_id]['name'] = message.text

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button = types.KeyboardButton("📞 Отправить контакт", request_contact=True)
    keyboard.add(button)

    bot.send_message(chat_id, "Теперь отправьте ваш контактный телефон:", reply_markup=keyboard)
    bot.register_next_step_handler(message, get_contact)

# Получаем контакт
@bot.message_handler(content_types=['contact'])
def get_contact(message):
    chat_id = message.chat.id
    if message.contact:
        user_data[chat_id]['phone'] = message.contact.phone_number

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        button = types.KeyboardButton("📍 Отправить локацию", request_location=True)
        keyboard.add(button)

        bot.send_message(chat_id, "Теперь отправьте вашу локацию для доставки:", reply_markup=keyboard)
        bot.register_next_step_handler(message, get_location)
    else:
        bot.send_message(chat_id, "Пожалуйста, используйте кнопку для отправки контакта.")

# Получаем локацию
@bot.message_handler(content_types=['location'])
def get_location(message):
    chat_id = message.chat.id
    if message.location:
        user_data[chat_id]['location'] = {
            'latitude': message.location.latitude,
            'longitude': message.location.longitude
        }
        main_menu(chat_id)
    else:
        bot.send_message(chat_id, "Пожалуйста, используйте кнопку для отправки локации.")

# --- Главное меню ---
def main_menu(chat_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    buttons = [
        "🥟 Сомса",
        "🥯 Сдобные булочки",
        "🍩 Сладкие булочки",
        "🍪 Из песочного теста сладкое",
        "🍱 Сеты",
        "🥗 Салаты",
        "🍲 Супы",
        "🥤 Компот",
        "🥛 Напитки"
    ]

    # Добавляем кнопки по 2 в строку
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            keyboard.add(buttons[i], buttons[i + 1])
        else:
            keyboard.add(buttons[i])

    keyboard.add("🛒 Корзина", "✅ Завершить заказ")
    bot.send_message(chat_id, "Отлично! Выберите категорию:", reply_markup=keyboard)

# Обработка выбора категорий
@bot.message_handler(func=lambda message: message.text in [
    "🥟 Сомса",
    "🥯 Сдобные булочки",
    "🍩 Сладкие булочки",
    "🍪 Из песочного теста сладкое",
    "🍱 Сеты",
    "🥗 Салаты",
    "🍲 Супы",
    "🥤 Компот",
    "🥛 Напитки"
])
def handle_category(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, f"Вы выбрали категорию: {message.text}\nЗдесь скоро появятся товары!")

# Корзина
@bot.message_handler(func=lambda message: message.text == "🛒 Корзина")
def show_cart(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Ваша корзина пока пуста. 🛍️")

# Завершение заказа
@bot.message_handler(func=lambda message: message.text == "✅ Завершить заказ")
def finish_order(message):
    chat_id = message.chat.id
    if chat_id not in user_data or 'name' not in user_data[chat_id]:
        bot.send_message(chat_id, "Ошибка: информация о пользователе не найдена.")
        return

    name = user_data[chat_id].get('name', 'Не указано')
    phone = user_data[chat_id].get('phone', 'Не указано')
    location = user_data[chat_id].get('location', {})

    # Формируем сообщение для группы
    group_message = (
        f"🆕 *Новый заказ!*\n\n"
        f"👤 Имя: {name}\n"
        f"📞 Телефон: {phone}\n"
        f"📍 Локация: https://maps.google.com/?q={location.get('latitude')},{location.get('longitude')}"
    )

    # Отправляем сообщение в группу
    bot.send_message(GROUP_CHAT_ID, group_message, parse_mode="Markdown")

    bot.send_message(chat_id, "Спасибо! Ваш заказ был отправлен на обработку. ✅")

# === Запуск бота ===
def run_bot():
    print("Бот запущен и работает...")
    bot.infinity_polling()

# === Flask сервер для Render ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# Запускаем бота и Flask параллельно
if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    threading.Thread(target=run_flask).start()



