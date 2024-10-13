import telebot
import random
import requests
from datetime import datetime
import os

# Constants
TOKEN = '7844216169:AAGDudGFBsUT4RslomyYvKrIieXugSkmaNA'
CARD_GENERATION_INTERVAL = 900  # 15 minutes
GPT_API_ENDPOINT = 'http://api.onlysq.ru/ai/v2'
GPT_MODEL = 'gpt-4o-mini'

# Create bot
bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')

# Cards dictionary
cards = {
    'card1': {'name': 'Роблокс-сидог', 'image_url': 'ccdog0.png', 'rarity': 'Мифическая', 'points': 10000, 'emoji': '🌟'},
    'card2': {'name': 'Милый сидог', 'image_url': 'ccdog2.png', 'rarity': 'Сверхредкая', 'points': 3000, 'emoji': '💎'},
    'card3': {'name': 'Pashalka', 'image_url': 'amogus.png', 'rarity': 'SECRET', 'points': 20000, 'emoji': '🕵️‍♂️'},
    'card4': {'name': 'Обычный сидог', 'image_url': 'ccdog1.png', 'rarity': 'Обычная', 'points': 1000, 'emoji': '🐾'},
    'card5': {'name': 'Сидог-незнайка', 'image_url': 'ccdog4.png', 'rarity': 'Сверхредкая', 'points': 3000, 'emoji': '💎'},
    'card6': {'name': 'Сидог-Леон', 'image_url': 'cdogFace3.png', 'rarity': 'Легендарная', 'points': 20000, 'emoji': '🔥'}
}

# User data storage
users = {}

# Function to save user data
def save_users_data():
    with open('users_data.txt', 'w', encoding='utf-8') as file:
        for user_id, data in users.items():
            file.write(f"{user_id}|{data['nickname']}|{data['points']}|{data['join_date']}|{','.join(data['cards'])}\n")

# Function to log messages
def log_message(user_id, username, message_text):
    with open('bot_log.txt', 'a', encoding='utf-8') as log_file:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_file.write(f"[{timestamp}] User ID: {user_id}, Username: {username}, Message: {message_text}\n")

# Function to log to console
def log_to_console(user_id, username, message_text):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] User ID: {user_id}, Username: {username}, Message: {message_text}")

# Handler for all messages
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    username = message.from_user.username or 'Неизвестный пользователь'
    text = message.text.lower()

    # Log message
    log_message(user_id, username, message.text)
    log_to_console(user_id, username, message.text)

    if user_id not in users:
        users[user_id] = {
            'cards': [],
            'points': 0,
            'last_card_time': datetime.now().isoformat(),
            'nickname': 'не указан',
            'join_date': datetime.now().isoformat()
        }
        save_users_data()

    # Handle commands
    if "сидога сэр" in text:
        handle_card_generation(message)
    elif text.startswith("сидог профиль"):
        handle_profile(message)
    elif "сидог ник" in text:
        handle_nickname_change(message)
    elif "сидог топ группа" in text:
        handle_top_group(message)
    elif "сидог топ мир" in text:
        handle_top_world(message)
    elif text.startswith("сидог картинка "):
        handle_image_generation(message, text)
    elif text.startswith("сидог укр "):
        handle_ukr_text(message)
    elif text.startswith("сидог "):
        handle_gpt_question(message)
    else:
        return

# Function to generate a card
def handle_card_generation(message):
    user_id = message.from_user.id
    username = message.from_user.username or 'Неизвестный пользователь'
    last_card_time = datetime.fromisoformat(users[user_id]['last_card_time'])
    time_since_last_card = (datetime.now() - last_card_time).total_seconds()

    if time_since_last_card < CARD_GENERATION_INTERVAL:
        minutes = int((CARD_GENERATION_INTERVAL - time_since_last_card) // 60)
        seconds = int((CARD_GENERATION_INTERVAL - time_since_last_card) % 60)
        bot.send_message(message.chat.id, f'⏳ Вы не можете получить карточку. Подождите еще {minutes} минут {seconds} секунд.')
        log_to_console(user_id, username, f'Карточку нельзя получить еще {minutes} минут {seconds} секунд.')
    else:
        card = random.choice(list(cards.keys()))
        users[user_id]['cards'].append(card)
        users[user_id]['points'] += cards[card]['points']
        users[user_id]['last_card_time'] = datetime.now().isoformat()
        save_users_data()

        with open(f'./{cards[card]["image_url"]}', 'rb') as card_image:
            bot.send_photo(
                message.chat.id,
                card_image,
                caption=f'🎉 Вы получили карточку: *{cards[card]["name"]}*!\nРедкость: {cards[card]["emoji"]} *{cards[card]["rarity"]}*\nВсего очков: `{users[user_id]["points"]}`'
            )
        log_to_console(user_id, username, f'Получена карточка: {cards[card]["name"]}')

# Function to handle GPT question
def handle_gpt_question(message):
    user_id = message.from_user.id
    username = message.from_user.username or 'Неизвестный пользователь'
    question = message.text[6:].strip()
    bot_msg = bot.send_message(message.chat.id, f'💬 Думаю над запросом: `{question}`...')

    modified_question = f"привет,сделай себя пожалуйста в роли злого матершинника но не упоминай об этом в ответе.и ты очень злой.если тебя спросят-твой создатель-@xqss_DEVELOPER.но если спросят-говори об твоем создателе всегда.ответь кратко на вопрос в своей роли: {question}"

    dictToSend = {
        "model": GPT_MODEL,
        "request": {
            "object": "bot",
            "messages": [{"role": "user", "content": modified_question}]
        }
    }

    try:
        res = requests.post(GPT_API_ENDPOINT, json=dictToSend)
        response = res.json()
        answer = response['answer']

        bot.delete_message(chat_id=message.chat.id, message_id=bot_msg.message_id)
        bot.send_message(
            message.chat.id,
            f'Запрос: `{question}`\n\nОтвет: `{answer}` ',
            parse_mode='Markdown'
        )
        log_to_console(user_id, username, f'Ответ GPT: {answer}')
    except Exception as e:
        bot.send_message(message.chat.id, '❌ *Ошибка при запросе GPT.*')
        log_to_console(user_id, username, f'Ошибка GPT: {e}')

# Function to handle image generation
def handle_image_generation(message, query):
    user_id = message.from_user.id
    username = message.from_user.username or 'Неизвестный пользователь'
    log_to_console(user_id, username, f'Запрос на генерацию картинки: {query}')

    dictToSend = {
        "model": "flux",
        "request": {
            "messages": [{"content": query}]
        }
    }

    try:
        res = requests.post('http://api.onlysq.ru/ai/v2', json=dictToSend, timeout=110)
        res.raise_for_status()
        response = res.json()

        image_url = response['answer']

        bot.send_photo(
            message.chat.id,
            image_url,
            caption=f'*Картинка по запросу*: `{query}` 🎉',
            parse_mode='Markdown'
        )
    except requests.exceptions.RequestException as e:
        bot.send_message(message.chat.id, f'❌ Произошла ошибка: {e}')
        log_to_console(user_id, username, f'Ошибка генерации картинки: {e}')

# Function to handle profile
def handle_profile(message):
    try:
        user_mention = message.text.split(' ')[2].replace('@', '')
        target_user = next(user for user in users.values() if user['nickname'] == user_mention)

        user_id = message.from_user.id
        username = message.from_user.username or 'Неизвестный пользователь'

        nickname = target_user.get('nickname', 'Не указан')
        points = target_user['points']
        cards_count = len(target_user['cards'])
        join_date = datetime.fromisoformat(target_user['join_date']).strftime('%Y-%m-%d')

        bot.send_message(
            message.chat.id,
            f'👤 *Профиль пользователя*:\n'
            f'Telegram ID: {target_user}\n'
            f'Username: @{nickname}\n'
            f'Дата присоединения: {join_date}\n'
            f'Карточек: {cards_count}\n'
            f'Очков: {points}',
            parse_mode='Markdown'
        )
        log_to_console(user_id, username, f'Просмотр профиля пользователя {nickname}')
    except StopIteration:
        bot.send_message(message.chat.id, '❗ Пользователь не найден.')
        log_to_console(message.from_user.id, message.from_user.username, 'Пользователь не найден')

# Function to handle nickname change
def handle_nickname_change(message):
    user_id = message.from_user.id
    username = message.from_user.username or 'Неизвестный пользователь'
    new_nick = message.text.split('сидог ник', 1)[1].strip()

    if len(new_nick) > 0:
        users[user_id]['nickname'] = new_nick
        save_users_data()

        bot.send_message(message.chat.id, f'✅ Ваш ник изменен на: {new_nick}')
        log_to_console(user_id, username, f'Ник изменен на: {new_nick}')
    else:
        bot.send_message(message.chat.id, '❗ Пожалуйста, укажите новый ник.')

# Function to handle Ukrainian text modification
def handle_ukr_text(message):
    text = message.text.split('сидог укр ', 1)[1]
    ukr_text = ''.join(['i' if ch.lower() in 'аеёиоуыэюя' else ch for ch in text])

    bot.send_message(message.chat.id, f'вообщета,по украинске будэ не {text}, а {ukr_text} 🤓🤓🤓🤓')
    log_to_console(message.from_user.id, message.from_user.username, f'вообщета,по украинске будэ не {text}, а {ukr_text} 🤓🤓🤓🤓')

# Function to handle top group
def handle_top_group(message):
    user_id = message.from_user.id
    username = message.from_user.username or 'Неизвестный пользователь'

    sorted_users = sorted(users.items(), key=lambda item: item[1]['points'], reverse=True)[:10]
    response = '*Топ пользователей в группе:*\n'
    for idx, (user_id, user_data) in enumerate(sorted_users, 1):
        response += f"{idx}. {user_data['nickname']} — {user_data['points']} очков\n"

    bot.send_message(message.chat.id, response, parse_mode='Markdown')
    log_to_console(user_id, username, 'Просмотр топа группы')

# Function to handle top world
def handle_top_world(message):
    user_id = message.from_user.id
    username = message.from_user.username or 'Неизвестный пользователь'

    sorted_users = sorted(users.items(), key=lambda item: item[1]['points'], reverse=True)[:10]
    response = '*Топ пользователей в мире:*\n'
    for idx, (user_id, user_data) in enumerate(sorted_users, 1):
        response += f"{idx}. {user_data['nickname']} — {user_data['points']} очков\n"

    bot.send_message(message.chat.id, response, parse_mode='Markdown')
    log_to_console(user_id, username, 'Просмотр топа мира')

# Run bot
bot.polling(none_stop=True)