import telebot
from telebot import types
import schedule
import time

TOKEN = '6904448751:AAHJoSD1jOVxaYDmdA3KsYfrVEhRXAB8exQ'
PASSWORD = 'NovaBot_byMusta'
MAX_ATTEMPTS = 7

bot = telebot.TeleBot(TOKEN)
users_attempts = {}
user_names = {}

files_or_links_to_send = [
    "/Users/mustafa700/Desktop/programming/newBot/IELTS Reading Practice Test 1 Printable.pdf",
    "https://quizlet.com/850738609/reading-week-1-vocabulary-flash-cards/?i=2y9ju6&x=1qqt",
    "https://example.com/link3",
    "/path/to/your/file1.pdf",
    "/path/to/your/file2.pdf",
]

almaty_time_offset = 6


def send_files(chat_id, file_or_link):
    if file_or_link.endswith(".pdf"):
        with open(file_or_link, "rb") as pdf_file:
            bot.send_document(chat_id, pdf_file)
    else:
        bot.send_message(chat_id, f"Here is the link or file you requested: {file_or_link}")


def get_current_file_or_link():
    return files_or_links_to_send[0]


def update_files_list():
    files_or_links_to_send.append(files_or_links_to_send.pop(0))


def schedule_file_send(chat_id):
    schedule.every().day.at("14:00").do(send_files, chat_id, get_current_file_or_link())
    schedule.every().day.at("00:00").do(update_files_list)

    while True:
        schedule.run_pending()
        time.sleep(1)


@bot.message_handler(commands=['start'])
def handle_start(message):
    chat_id = message.chat.id
    users_attempts.setdefault(chat_id, 0)

    bot.send_message(chat_id, "Hello! Welcome to the bot. What's your name?")
    bot.register_next_step_handler(message, ask_name)


def ask_name(message):
    chat_id = message.chat.id
    user_name = message.text.strip()

    user_names[chat_id] = user_name
    bot.send_message(chat_id, f"Nice to meet you, {user_name}!")

    # Ask the user if they know the password with Yes and No buttons
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add(types.KeyboardButton('Yes'), types.KeyboardButton('No'))
    bot.send_message(chat_id, "Do you know the password?", reply_markup=markup)
    bot.register_next_step_handler(message, handle_password_knowledge)


def handle_password_knowledge(message):
    chat_id = message.chat.id
    user_name = user_names.get(chat_id, "User")

    if message.text.lower() == 'yes':
        bot.send_message(chat_id, f"Great, {user_name}! Now, please enter the password:")
        bot.register_next_step_handler(message, ask_password)
    elif message.text.lower() == 'no':
        bot.send_message(chat_id, f"Sorry, {user_name}. Please contact your mentor for assistance.")
    else:
        bot.send_message(chat_id, f"Invalid response, {user_name}. Please select 'Yes' or 'No'.")
        bot.register_next_step_handler(message, handle_password_knowledge)


def ask_password(message):
    chat_id = message.chat.id
    user_name = user_names.get(chat_id, "User")

    if message.text == PASSWORD:
        bot.send_message(chat_id, f"Welcome, {user_name}! You've gained access to the bot.")
        schedule_file_send(chat_id)
        del users_attempts[chat_id]
    else:
        handle_wrong_password(chat_id, user_name, message)


def handle_wrong_password(chat_id, user_name, message):
    users_attempts[chat_id] += 1
    remaining_attempts = MAX_ATTEMPTS - users_attempts[chat_id]

    if remaining_attempts > 0:
        bot.send_message(chat_id,
                         f"Wrong password, {user_name}. {remaining_attempts} attempts remaining. Please try again.")
        bot.register_next_step_handler(message, ask_password)
    else:
        block_access(chat_id, user_name)


def block_access(chat_id, user_name):
    bot.send_message(chat_id, f"Sorry, {user_name}. You have exceeded the maximum number of attempts. Access blocked.")


@bot.message_handler(func=lambda message: message.text.lower() == "change username")
def change_username(message):
    chat_id = message.chat.id
    user_name = user_names.get(chat_id, "User")

    bot.send_message(chat_id, f"Sure, {user_name}! What's your new username?")
    bot.register_next_step_handler(message, update_username)


def update_username(message):
    chat_id = message.chat.id
    new_username = message.text.strip()

    user_names[chat_id] = new_username
    bot.send_message(chat_id, f"Your username has been updated to {new_username}.")


if __name__ == "__main__":
    bot.polling(none_stop=True, timeout=None)
