import telebot
import requests
from game import generate_batch
from country_service import get_country_info, get_neighbors, list_country
from utils import headers
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

with open("token.txt") as t:
    token = t.readline().strip()
    
bot = telebot.TeleBot(token)
    
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, ("Привет! Я бот для предоставления информации о странах. "
                           "Вот что я умею:\n"
                           "/start - Показать это сообщение\n"
                           "/info <название_страны> - Узнать информацию о стране\n"
                           "/neighbors <название_страны> - Вывести всех соседей\n"
                           "/game - Игра \"Угадай страну\"\n"
                           "/list - Показать список стран"))

@bot.message_handler(commands=['info'])
def send_country_info(message):
    try:
        country_name = message.text.split(maxsplit=1)[1]
        info, flag_url = get_country_info(country_name)
        if flag_url:
            bot.send_photo(message.chat.id, flag_url, caption=info)
        else:
            bot.reply_to(message, info)
    except IndexError:
        bot.reply_to(message, "Пожалуйста, укажите название страны после команды /info.")
    except requests.exceptions.HTTPError:
        bot.reply_to(message, f"Похоже такой страны не существует, попробуйте еще раз")
    except requests.exceptions.RequestException:
        bot.reply_to(message, f"Произошла ошибка с соединением. Попробуйте еще раз")
        
@bot.message_handler(commands=['game'])
def start_game(message):
    try:
        flag_url, four_coun, win_coun = generate_batch()

        bot.send_photo(message.chat.id, flag_url)
        markup = InlineKeyboardMarkup()
        for country in four_coun:
            markup.add(InlineKeyboardButton(country, callback_data=f"answer_{country}"))
        bot.send_message(message.chat.id, "Выберите правильный вариант:", reply_markup=markup)
        
        if win_coun:
            if not hasattr(bot, 'answer_data'):
                bot.answer_data = {}
            bot.answer_data[message.from_user.id] = win_coun
    except requests.exceptions.HTTPError:
        bot.reply_to(message, "Произошла ошибка, попробуйте еще раз")
    except requests.exceptions.RequestException:
        bot.reply_to(message, "Произошла ошибка с соединением. Попробуйте еще раз")

@bot.callback_query_handler(func=lambda call: call.data.startswith('answer_'))
def handle_answer(call):
    if not hasattr(bot, 'answer_data') or call.from_user.id not in bot.answer_data:
        bot.answer_callback_query(call.id, "Игра не была начата для вас.")
        return

    selected_country = call.data.split('_')[1]
    correct_answer = bot.answer_data[call.from_user.id]

    if selected_country == correct_answer:
        bot.send_message(call.message.chat.id, f"Поздравляю! Вы угадали, это {correct_answer}!")
    else:
        bot.send_message(call.message.chat.id, f"К сожалению, вы ошиблись. Правильный ответ: {correct_answer}")

    original_markup = call.message.reply_markup
    disabled_markup = InlineKeyboardMarkup()

    for button_row in original_markup.keyboard:
        disabled_row = [
            InlineKeyboardButton(button.text, callback_data="disabled")  # callback_data заменяем на фиктивное
            for button in button_row
        ]
        disabled_markup.row(*disabled_row)

    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=disabled_markup)

    del bot.answer_data[call.from_user.id]

        
@bot.message_handler(commands=['neighbors'])
def send_neighbors(message):
    try:
        country_name = message.text.split(maxsplit=1)[1]
        neighbors = get_neighbors(country_name)
        bot.reply_to(message, neighbors)
    except IndexError:
        bot.reply_to(message, "Пожалуйста, укажите название страны после команды /neighbors.")
    except requests.exceptions.HTTPError:
        bot.reply_to(message, f"Похоже такой страны не существует, попробуйте еще раз")
    except requests.exceptions.RequestException:
        bot.reply_to(message, f"Произошла ошибка с соединением. Попробуйте еще раз")
        
@bot.message_handler(commands=['list'])
def send_country_list(message):
    bot.reply_to(message, ", ".join(list_country))


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Я вас не понял. Используйте /start для просмотра доступных команд.")


if __name__ == "__main__":
    while True:
        print("Бот запущен...")
        try:
            bot.polling(none_stop=True)
        except BaseException as e:
            print(f"Ошибка в работе бота: {e}")

