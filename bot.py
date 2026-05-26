import os
import re
import telebot
import requests

BOT_TOKEN = os.environ.get('BOT_TOKEN')

if not BOT_TOKEN:
    print("Ошибка: Переменная окружения BOT_TOKEN не найдена!")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

URL_PATTERN = r'https?://(?:[-a-zA-Z0-9&@#/%?=~_|!:,.;]*[-a-zA-Z0-9&@#/%=~_|])'

def shorten_url(long_url):
    try:
        api_url = f"http://tinyurl.com/api-create.php?url={long_url}"
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            return response.text
        return None
    except Exception as e:
        print(f"Ошибка API: {e}")
        return None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "Привет! Кидай мне длинную ссылку (с http:// или https://), а я её укорочу. 🔗"
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    urls = re.findall(URL_PATTERN, message.text)
    
    if not urls:
        bot.reply_to(message, "Это не похоже на ссылку. Начни с http:// или https://")
        return

    long_url = urls[0]
    status_message = bot.reply_to(message, "⚡ Сокращаю...")
    
    short_url = shorten_url(long_url)
    
    if short_url:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_message.message_id,
            text=f"✅ Готово:\n{short_url}"
        )
    else:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=status_message.message_id,
            text="❌ Что-то пошло не так при сокращении."
        )

if __name__ == '__main__':
    print("Бот успешно запущен в Render!")
    bot.infinity_polling()
