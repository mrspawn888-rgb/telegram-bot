import telebot

# 🔹 Вставь сюда свой токен, который дал BotFather
TOKEN = "7664553338:AAEQ3TpJlPhzsARhVOxw4OtJaiAT8NPJjWI"

# Создаём объект бота
bot = telebot.TeleBot(TOKEN)

# Команда /start — приветственное сообщение
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я твой бот для заказов выпечки. 🥐\n\nОтправь мне сообщение, чтобы сделать заказ!")

# Команда /help — подсказка
@bot.message_handler(commands=['help'])
def help_command(message):
    bot.reply_to(message, "Напиши мне, что хочешь заказать, и я передам заказ в пекарню. 🍞")

# Любой текст — временно просто отвечает, что заказ принят
@bot.message_handler(content_types=['text'])
def handle_text(message):
    bot.reply_to(message, f"Ваш заказ принят: {message.text}\n\nМы скоро свяжемся с вами для подтверждения! ✅")

# Запуск бота
print("Бот запущен и ждёт сообщений...")
bot.polling(none_stop=True)
