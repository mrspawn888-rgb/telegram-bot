import telebot
import os

# Получаем токен бота из переменной среды
TOKEN = os.getenv("BOT_TOKEN")

# Проверка, что токен найден
if TOKEN is None:
    raise ValueError("Ошибка: переменная среды BOT_TOKEN не установлена!")

# Создаём объект бота
bot = telebot.TeleBot(TOKEN)

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я твой бот и я работаю на Render 🚀")

# Команда /help
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, "Доступные команды:\n/start - запустить бота\n/help - показать помощь")

# Ответ на любое сообщение
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Ты написал: {message.text}")

# Запуск бота
bot.polling()

