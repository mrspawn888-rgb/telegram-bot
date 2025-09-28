import telebot
from telebot import types
import os

# Получаем токен из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# Временное хранилище данных пользователей
user_data = {}

# Стартовая команда
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "👋 Привет! Я бот для заказа выпечки. Давай начнем!")
    bot.send_message(chat_id, "Введите, пожалуйста, ваше имя и фамилию:")
    user_data[chat_id] = {}
    bot.register_next_step_handler(message, get_name)

# Получаем имя и фамилию
def get_name(message):
    chat_id = message.chat.id
    user_data[chat_id]['name'] = message.text

    # Кнопка для отправки контакта
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

        # Кнопка для отправки локации
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

        # Показываем главное меню
        main_menu(chat_id)
    else:
        bot.send_message(chat_id, "Пожалуйста, используйте кнопку для отправки локации.")

# Главное меню
def main_menu(chat_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_menu = types.KeyboardButton("🍰 Меню")
    btn_cart = types.KeyboardButton("🛒 Корзина")
    keyboard.add(btn_menu, btn_cart)

    bot.send_message(chat_id, "Отлично! Выберите, что вас интересует:", reply_markup=keyboard)

# Обработка кнопок меню
@bot.message_handler(func=lambda message: message.text in ["🍰 Меню", "🛒 Корзина"])
def handle_menu_buttons(message):
    chat_id = message.chat.id
    if message.text == "🍰 Меню":
        bot.send_message(chat_id, "Здесь будет список нашей выпечки 🍞🥐🥧")
    elif message.text == "🛒 Корзина":
        bot.send_message(chat_id, "Ваша корзина пока пуста.")

# Запуск бота
if __name__ == "__main__":
    print("Бот запущен и работает...")
    bot.infinity_polling()

