# bot.py
# Telegram-бот «Отработочка» для студентов
import os
import telebot
from telebot import types
import random
from flask import Flask, request

# === FLASK APP FOR RENDER ===
app = Flask(__name__)

# === НАСТРОЙКИ И ИНИЦИАЛИЗАЦИЯ ===
# Токен берётся из переменных окружения Render
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not TELEGRAM_BOT_TOKEN:
    raise ValueError(
        "Токен бота не задан! Установите переменную окружения TELEGRAM_BOT_TOKEN в настройках Render."
    )

# Создаём экземпляр бота
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# === КЛАВИАТУРЫ ===
# Основная клавиатура
main_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
main_markup.add(
    types.KeyboardButton('👋 Привет'),
    types.KeyboardButton('📓 Я пропустил занятие:('),
    types.KeyboardButton('📚 Сдать ДЗ'),
    types.KeyboardButton('🎲 Какой у меня вариант?')
)

# Клавиатура для выбора ДЗ
def get_dz_markup():
    markup = types.InlineKeyboardMarkup(row_width=6)
    buttons = [
        types.InlineKeyboardButton(f"ДЗ {i}", callback_data=f'dz_{i}')
        for i in range(1, 7)
    ]
    markup.add(*buttons)
    return markup

# Клавиатура для выбора темы
def get_tema_markup():
    markup = types.InlineKeyboardMarkup()
    topics = [
        ("Тема 1. Системы счисления", "tema_1"),
        ("Тема 2. Алгебра логики", "tema_2"),
        ("Тема 3. Интернет", "tema_3"),
        ("Тема 4. Защита информации", "tema_4"),
        ("Тема 5. Текстовый процессор", "tema_5"),
        ("Тема 6. Компьютерная графика", "tema_6")
    ]
    for text, callback in topics:
        markup.add(types.InlineKeyboardButton(text, callback_data=callback))
    return markup

# === ОБРАБОТЧИКИ TELEGRAM ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "Привет! Я бот для помощи с занятиями. Выберите опцию:",
        reply_markup=main_markup
    )

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.text == '👋 Привет':
        bot.send_message(message.chat.id, "Привет! Чем могу помочь?")
    elif message.text == '📓 Я пропустил занятие:(':
        bot.send_message(
            message.chat.id,
            "Выберите тему занятия:",
            reply_markup=get_tema_markup()
        )
    elif message.text == '📚 Сдать ДЗ':
        bot.send_message(
            message.chat.id,
            "Выберите номер ДЗ:",
            reply_markup=get_dz_markup()
        )
    elif message.text == '🎲 Какой у меня вариант?':
        variant = random.randint(1, 20)
        bot.send_message(
            message.chat.id,
            f"Ваш вариант: {variant}",
            reply_markup=main_markup
        )
    else:
        bot.send_message(
            message.chat.id,
            "Используйте кнопки для навигации",
            reply_markup=main_markup
        )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.startswith('tema_'):
        tema_map = {
            'tema_1': 'Системы счисления',
            'tema_2': 'Алгебра логики', 
            'tema_3': 'Интернет',
            'tema_4': 'Защита информации',
            'tema_5': 'Текстовый процессор',
            'tema_6': 'Компьютерная графика'
        }
        tema_name = tema_map.get(call.data, 'неизвестная тема')
        bot.send_message(
            call.message.chat.id,
            f"Материалы по теме '{tema_name}' скоро будут доступны!"
        )
    elif call.data.startswith('dz_'):
        dz_num = call.data.split('_')[1]
        bot.send_message(
            call.message.chat.id,
            f"Инструкции по сдаче ДЗ {dz_num} будут отправлены позже!"
        )

# === WEBHOOK FOR TELEGRAM (OPTIONAL) ===
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Forbidden', 403

# === HEALTH CHECK FOR RENDER ===
@app.route('/')
def health_check():
    return 'Bot is running!', 200

# === MAIN ENTRY POINT ===
if __name__ == '__main__':
    # Start the Flask app on port 8000
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting bot on port {port}...")
    
    # Start bot polling in background
    import threading
    def start_bot():
        print("Bot started polling...")
        bot.remove_webhook()
        bot.infinity_polling()
    
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Start Flask app (this binds to the port)
    app.run(host='0.0.0.0', port=port, debug=False)

# === ОБРАБОТЧИКИ СООБЩЕНИЙ ===
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Ты что-то пропустил?",
        reply_markup=main_markup
    )

@bot.message_handler(func=lambda msg: True)
def handle_all_messages(message):
    try:
        user_text = message.text.lower()

        if 'привет' in user_text:
            bot.send_message(message.chat.id, "И тебе привет! 😊")

        elif user_text == '📓 я пропустил занятие:(':
            bot.send_message(
                message.chat.id,
                "Выберите пропущенную тему:",
                reply_markup=get_tema_markup()
            )

        elif user_text == '📚 сдать дз':
            bot.send_message(
                message.chat.id,
                "Выберите номер ДЗ:",
                reply_markup=get_dz_markup()
            )

        elif user_text == '🎲 какой у меня вариант?':
            bot.send_message(
                message.chat.id,
                f"Ваше число: {random.randint(1, 10)}"
            )

        else:
            bot.send_message(
                message.chat.id,
                "Не понял ваш запрос. Воспользуйтесь клавиатурой ниже."
            )

    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте ещё раз.")
        print(f"[ERROR] {e}")

# === ОБРАБОТЧИКИ CALLBACK ===
@bot.callback_query_handler(func=lambda call: call.data.startswith('dz_'))
def handle_dz_callback(call):
    dz_number = call.data[3:]
    assignments = {
        '1': (
            "ДЗ 1: Системы счисления\n"
            "Задание: Реши самостоятельную в тетради, а результат покажи учителю.\n"
            "Вариант узнай у меня\n"
            "Ссылка на материалы: https://disk.yandex.ru/d/APQE4mDwBTSbkA"
        ),
        '2': (
            "ДЗ 2: Алгебра логики\n"
            "Задание: Реши самостоятельно по учебнику, а решение покажи учителю:\n"
            "с. 3 Вариант 4, Задача №1,2\n"
            "с. 4 Вариант 3, Задача №1\n"
            "с.11 Вариант 4, Задача 2.\n"
            "Ссылка на материалы: https://disk.yandex.ru/d/BPjzUvFeiSOvVw"
        ),
        '3': (
            "ДЗ 3: Интернет\n"
            "Задание: Для этого задания используй MS Visio или Draw.io\n"
            "Результат выполнения отправь преподавателю на почту polinavladimirovn@yandex.ru\n"
            "Ссылка на материалы: https://disk.yandex.ru/d/w_85PUK6rneizQ"
        ),
        '4': (
            "ДЗ 4: Защита информации\n"
            "Задание: Для этого задания используй MS Word\n"
            "Результат выполнения отправь преподавателю на почту polinavladimirovn@yandex.ru\n"
            "Ссылка на материалы: https://disk.yandex.ru/d/JycaZ67-mUxadQ"
        ),
        '5': (
            "ДЗ 5: Текстовый процессор\n"
            "Задание: Для этого задания используй MS Word\n"
            "с. 31 Практическая работа №9\n"
            "с. 37 Практическая работа №10\n"
            "с. 41 Практическая работа №11\n"
            "с. 46 Практическая работа №12\n"
            "Результат выполнения отправь преподавателю на почту polinavladimirovn@yandex.ru\n"
            "Ссылка на материалы: https://disk.yandex.ru/d/aiykc237nTqJBg"
        ),
        '6': (
            "ДЗ 6: Компьютерная графика\n"
            "Задание: Для этого задания используй MS Publisher или LO Impress\n"
            "Результат выполнения отправь преподавателю на почту polinavladimirovn@yandex.ru\n"
            "Ссылка на материалы: https://disk.yandex.ru/d/qKQ3ZFQHg59wGQ"
        )
    }

    if dz_number in assignments:
        bot.send_message(
            call.message.chat.id,
            assignments[dz_number]
        )
    else:
        bot.send_message(call.message.chat.id, "ДЗ не найдено. Обратитесь к преподавателю.")

    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('tema_'))
def handle_tema_callback(call):
    tema_number = call.data[5:]
    topics = {
        '1': "Системы счисления",
        '2': "Алгебра логики",
        '3': "Интернет",
        '4': "Защита информации",
        '5': "Текстовый процессор",
        '6': "Компьютерная графика"
    }

    if tema_number in topics:
        link = f"https://disk.yandex.ru/d/{['APQE4mDwBTSbkA', 'BPjzUvFeiSOvVw', 'w_85PUK6rneizQ', 'JycaZ67-mUxadQ', 'aiykc237nTqJBg', 'qKQ3ZFQHg59wGQ'][int(tema_number)-1]}"
        bot.send_message(
            call.message.chat.id,
            f"Тема {tema_number}: {topics[tema_number]}. Задание: Напиши конспект Лекции по ссылке в тетрадь. Не забудь про ДЗ! {link}"
        )
    else:
        bot.send_message(call.message.chat.id, "Тема не найдена.")

    bot.answer_callback_query(call.id)

# === ЗАПУСК БОТА ===
if __name__ == '__main__':
    print("Бот запущен. Ожидание сообщений...")
    bot.polling(none_stop=True, timeout=60)
