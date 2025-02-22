from telebot import TeleBot
import time
import threading
from datetime import datetime, timedelta

bot = TeleBot(tg_tokken)

schedule = {}
homework = {}
reminder_times = {}

#Функция определения завтрашнего дня недели
def get_tomorrow_day():
    days = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
    tomorrow = (datetime.now() + timedelta(days=1)).weekday()
    return days[tomorrow]

#Функция напоминания о домашних заданий
def reminder():
    while True:
        now = datetime.now().strftime("%H:%M")
        for chat_id, reminder_time in reminder_times.items():
            if now == reminder_time:
                tomorrow_day = get_tomorrow_day()
                if chat_id in homework and tomorrow_day in homework[chat_id]:
                    tasks = homework[chat_id][tomorrow_day]
                    if tasks:
                        bot.send_message(chat_id, f"Напоминание: Домашние задания на завтра ({tomorrow_day.capitalize()}):\n" + "\n".join(tasks))
        time.sleep(60)

#Обработчик команды /start
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я бот для управления расписанием уроков и домашними заданиями. Используй команды:\n"
                                      "/add_schedule – добавить расписание\n"
                                      "/add_homework – добавить домашнее задание\n"
                                      "/view_schedule – посмотреть расписание\n"
                                      "/view_homework – посмотреть домашние задания\n"
                                      "/delete_homework – удалить домашнее задание\n"
                                      "/set_reminder_time – установить время напоминания")

#Обработчик команды /add_schedule
@bot.message_handler(commands=["add_schedule"])
def add_schedule(message):
    msg = bot.send_message(message.chat.id, "Введите день недели и расписание в формате:\n"
                                            "День\n"
                                            "8.20-9.00 Урок1\n"
                                            "9.20-10.00 Урок2\n"
                                            "Пример:\n"
                                            "понедельник\n"
                                            "8.20-9.00 Математика\n"
                                            "9.20-10.00 Русский язык")
    bot.register_next_step_handler(msg, process_schedule)

def process_schedule(message):
    try:
        lines = message.text.split('\n')
        day = lines[0].strip().lower()
        lessons = []
        for line in lines[1:]:
            if line.strip():
                time_lesson, lesson = line.strip().split(' ', 1)
                lessons.append({"time": time_lesson, "lesson": lesson})

        chat_id = message.chat.id
        if chat_id not in schedule:
            schedule[chat_id] = {}
        schedule[chat_id][day] = lessons
        bot.send_message(chat_id, f"Расписание на {day.capitalize()} добавлено.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}. Неверный формат. Попробуйте снова.")

#Обработчик команды /add_homework
@bot.message_handler(commands=["add_homework"])
def add_homework(message):
    msg = bot.send_message(message.chat.id, "Введите день недели и задание в формате:\n"
                                            "День Задание\n"
                                            "Пример: понедельник математика: решить задачу")
    bot.register_next_step_handler(msg, process_homework)
def process_homework(message):
    try:
        day, task = message.text.split(' ', 1)
        day = day.lower()
        chat_id = message.chat.id

        if chat_id not in homework:
            homework[chat_id] = {}
        if day not in homework[chat_id]:
            homework[chat_id][day] = []
        homework[chat_id][day].append(task)
        bot.send_message(chat_id, f"Домашнее задание на {day.capitalize()} добавлено: {task}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}. Неверный формат. Попробуйте снова.")

#Обработчик команды /view_schedule
@bot.message_handler(commands=["view_schedule"])
def view_schedule(message):
    chat_id = message.chat.id
    if chat_id in schedule and schedule[chat_id]:
        response = "Ваше расписание:\n"
        for day, lessons in schedule[chat_id].items():
            response += f"{day.capitalize()}:\n"
            for lesson in lessons:
                response += f"{lesson['time']} {lesson['lesson']}\n"
        bot.send_message(chat_id, response)
    else:
        bot.send_message(chat_id, "У вас нет расписания.")

#Обработчик команды /view_homework
@bot.message_handler(commands=["view_homework"])
def view_homework(message):
    chat_id = message.chat.id
    if chat_id in homework and homework[chat_id]:
        response = "Ваши домашние задания:\n"
        for day, tasks in homework[chat_id].items():
            response += f"{day.capitalize()}:\n"
            for task in tasks:
                response += f"- {task}\n"
        bot.send_message(chat_id, response)
    else:
        bot.send_message(chat_id, "У вас нет домашних заданий.")

#Обработчик команды /delete_homework
@bot.message_handler(commands=["delete_homework"])
def delete_homework(message):
    msg = bot.send_message(message.chat.id, "Введите день недели и номер задания, которое хотите удалить, в формате:\n"
                                            "День Номер\n"
                                            "Пример: понедельник 1")
    bot.register_next_step_handler(msg, process_delete_homework)

def process_delete_homework(message):
    try:
        day, task_number = message.text.split(' ', 1)
        day = day.lower()
        task_number = int(task_number) - 1
        chat_id = message.chat.id

        if chat_id in homework and day in homework[chat_id]:
            if 0 <= task_number < len(homework[chat_id][day]):
                deleted_task = homework[chat_id][day].pop(task_number)
                bot.send_message(chat_id, f"Задание '{deleted_task}' удалено.")
            else:
                bot.send_message(chat_id, "Неверный номер задания.")
        else:
            bot.send_message(chat_id, "Домашних заданий на этот день нет.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}. Неверный формат. Попробуйте снова.")

#Обработчик команды /set_reminder_time
@bot.message_handler(commands=["set_reminder_time"])
def set_reminder_time(message):
    msg = bot.send_message(message.chat.id, "Введите время для напоминания в формате ЧЧ:ММ (например, 20:00):")
    bot.register_next_step_handler(msg, process_reminder_time)

def process_reminder_time(message):
    try:
        time_str = message.text.strip()
        datetime.strptime(time_str, "%H:%M")
        chat_id = message.chat.id
        reminder_times[chat_id] = time_str
        bot.send_message(chat_id, f"Время напоминания установлено на {time_str}.")
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат времени. Используйте формат ЧЧ:ММ (например, 20:00).")

#Запуск потока для напоминаний
def start_reminder_thread():
    reminder_thread = threading.Thread(target=reminder)
    reminder_thread.daemon = True
    reminder_thread.start()

if __name__ == "__main__":
    start_reminder_thread()
    bot.polling(none_stop=True, interval=0)
