import telebot
import sqlite3

TOKEN = ""
bot = telebot.TeleBot(TOKEN)

user_state = {}
temp_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id,
                     "Команды: \n"
                     "/register - регистрация\n"
                     "/login - вход\n"
                     "/profile - профиль\n"
                     "/delete_account - удалить аккаунт\n"
                     )
@bot.message_handler(commands=['register'])
def register(message):
    bot.send_message(message.chat.id, "Введите желаемый логин: ")
    user_state[message.chat.id] = "wait_username"

@bot.message_handler(commands=['login'])
def login(message):
    bot.send_message(message.chat.id, "Введите ваш логин: ")
    user_state[message.chat.id] = "login_username"

@bot.message_handler(commands=['profile'])
def profile(message):
    telegram_id = message.chat.id

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()

    conn.close() 

    if user:
        username = user[0] 
        bot.send_message(message.chat.id, f"Ваш профиль: {username}")
    else:
        bot.send_message(message.chat.id, "Вы не зарегистрированы! /register")


@bot.message_handler(commands=['delete_account'])
def delete(message):
    telegram_id = message.chat.id

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
    conn.commit()

    bot.send_message(message.chat.id, "Пользователь удален!")

    conn.close()

@bot.message_handler(func=lambda m: True)
def main(message):
    text = message.text

    if user_state.get(message.chat.id) == "login_username":
        temp_data[message.chat.id] = {"username": text}
        bot.send_message(message.chat.id, "Введите пароль: ")
        user_state[message.chat.id] = "login_password"
        return

    if user_state.get(message.chat.id) == "login_password":
        username = temp_data[message.chat.id]["username"]
        password = text

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            bot.send_message(message.chat.id, f"Вы успешно вошли, {username}!")
        else:
            bot.send_message(message.chat.id, "Неверный логин или пароль!")

        user_state.pop(message.chat.id)
        temp_data.pop(message.chat.id)
        return


bot.polling()
