import telebot
import json
import os
from datetime import datetime

TOKEN = "777"

bot = telebot.TeleBot(TOKEN)

ADMINS_FILE = "admins.json"
DEFAULT_ADMIN_ID = 1337durov
DEFAULT_ADMIN_USERNAME = "@durov"

GROUP_ALIASES = {
    "тест": -1112666222044, # АЙДИ ГРУППЫ ЭТО ЦИФРЫ ( ПУБЛИЧНАЯ ГРУППА )
}


def load_admins():
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, dict) and "ids" in data and "usernames" in data:
                    return data
                else:
                    print("Incorrect structure in admins.json, creating default admin.")
                    data = {"ids": [DEFAULT_ADMIN_ID], "usernames": [DEFAULT_ADMIN_USERNAME]}
                    with open(ADMINS_FILE, "w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                    return data

            except json.JSONDecodeError:
                print("Error decoding admins.json, creating default admin.")
                data = {"ids": [DEFAULT_ADMIN_ID], "usernames": [DEFAULT_ADMIN_USERNAME]}
                with open(ADMINS_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                return data
    else:
        print("admins.json not found, creating default admin.")
        data = {"ids": [DEFAULT_ADMIN_ID], "usernames": [DEFAULT_ADMIN_USERNAME]}
        with open(ADMINS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return data

admin_data = load_admins()
admin_ids = admin_data["ids"]
admin_usernames = admin_data["usernames"]

user_logged = set()

def record_user_info(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    filename = f"USER_{user_id}.json"
    if username:
        filename = f"NICKNAME_{username}.json"

    # Load existing data or create new
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            user_data = json.load(f)
    except FileNotFoundError:
        user_data = {
            "ID": user_id,
            "Username": username,
            "First_name": first_name,
            "Messages": []
        }
    except json.JSONDecodeError:
        user_data = {
            "ID": user_id,
            "Username": username,
            "First_name": first_name,
            "Messages": []
        }

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(user_data, f, ensure_ascii=False, indent=4)
        print(f"User information recorded for user {user_id} (file: {filename})")
    except Exception as e:
        print(f"Error writing to file: {e}")

def record_user_messages(message):
    user_id = message.from_user.id
    username = message.from_user.username
    message_text = message.text
    now = datetime.now()
    time_string = now.strftime("%H.%M")

    filename = f"USER_{user_id}.json"
    if username:
        filename = f"NICKNAME_{username}.json"

    message_data = {
        "Time": time_string,
        "Message": message_text
    }

    try:
        # Load existing data or create new
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = {
                "ID": user_id,
                "Username": username,
                "First_name": message.from_user.first_name,
                "Messages": []
            }

        # Ensure "Messages" key exists
        if "Messages" not in existing_data:
            existing_data["Messages"] = []

        existing_data["Messages"].append(message_data)


        with open(filename, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)

    except Exception as e:
        print(f"Error writing to file: {e}")


@bot.message_handler(commands=['sg'])
def send_to_group(message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        print("User is not an admin.")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.send_message(message.chat.id, "Используйте: /sg <id_группы или алиас>", reply_to_message_id=message.message_id)
            return

        group_alias = parts[1].lower()
        group_id = GROUP_ALIASES.get(group_alias)

        if group_id is None:
            try:
                group_id = int(group_alias)
            except ValueError:
                bot.send_message(message.chat.id, "Укажите корректный ID группы или алиас (артур, т1)", reply_to_message_id=message.message_id)
                return

        if not message.reply_to_message:
            bot.send_message(message.chat.id, "отметьте сообщение, которое переслать.", reply_to_message_id=message.message_id)
            return

        replied_message = message.reply_to_message
        from_chat_id = replied_message.chat.id
        message_id = replied_message.message_id

        print(f"Sending to group: {group_id}")
        print(f"From chat ID: {from_chat_id}")
        print(f"Message ID: {message_id}")
        try:
            bot.copy_message(chat_id=group_id, from_chat_id=from_chat_id, message_id=message_id)
            bot.reply_to(message, f"Сообщение переслано в группу {group_id}")
            print("Message sent successfully.")
        except telebot.apihelper.ApiTelegramException as e:
            bot.reply_to(message, f"Ошибка при пересылке сообщения: {e}")
            print(f"Telegram API Error: {e}")
        except Exception as e:
            bot.reply_to(message, f"Не удалось переслать сообщение: {e}")
            print(f"Неизвестная ошибка: {e}")


    except IndexError:
        bot.send_message(message.chat.id, "укажите ID группы или алиас (артур, т1) после /sg", reply_to_message_id=message.message_id)
    except Exception as e:
        print(f"Ошибка: {e}")


@bot.message_handler(commands=['sg2'])
def send_to_group2(message):
    user_id = message.from_user.id
    if user_id not in admin_ids:
        print("User is not an admin.")
        return

    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.send_message(message.chat.id, "Используйте: /sg2 <id_группы или алиас> <сообщение>", reply_to_message_id=message.message_id)
            return

        group_alias = parts[1].lower()
        group_id = GROUP_ALIASES.get(group_alias)

        if group_id is None:
            try:
                group_id = int(group_alias)
            except ValueError:
                bot.send_message(message.chat.id, "Укажите корректный ID группы или алиас (артур, т1)", reply_to_message_id=message.message_id)
                return

        text = ' '.join(parts[2:])  # Собираем все части после алиаса в текст

        print(f"Sending to group: {group_id} with text: {text}")
        try:
            bot.send_message(group_id, text)
        except Exception as e:
            bot.reply_to(message, f"Не удалось отправить сообщение в группу: {e}")
            return

        bot.reply_to(message, f"Сообщение отправлено в группу {group_id}")
        print("Message sent successfully.")

    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
    Доступные команды:
    (Там где бот состоит туда может отправлять)
    /sg - Пересылает отмеченное сообщение в указанную группу.
    /sg2 - Отправляет любое вид сообщения в указанную группу.

    Используйте ID группы или алиасы:
    тест - (-1112666222044) не рабочее если что
    """
    bot.send_message(message.chat.id, help_text)


@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'sticker', 'animation', 'voice'])
def handle_all_messages(message):
    user_id = message.from_user.id
    if user_id not in user_logged:
        print(f"New user {message.from_user.first_name} {message.from_user.username} ({user_id})")
        user_logged.add(user_id)

    record_user_info(message)
    record_user_messages(message)


print("Бот запущен...")
bot.infinity_polling()