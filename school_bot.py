from telegram import Update  
from telegram.ext import Updater, CommandHandler, CallbackContext  
import sqlite3  
from datetime import timedelta  

# Команда /start  
def start(update: Update, context: CallbackContext):  
    update.message.reply_text(  
        "Привет! Я твой школьный помощник. Вот что я умею:\n"  
        "/start - начать работу\n"  
        "/add_schedule - добавить расписание\n"  
        "/view_schedule - посмотреть расписание\n"  
        "/add_homework - добавить домашнее задание\n"  
        "/view_homework - посмотреть домашние задания\n"  
        "/set_reminder - установить напоминание"  
    )  

# Добавление расписания  
def add_schedule(update: Update, context: CallbackContext):  
    try:  
        day, subject, time = context.args  
        user_id = update.message.from_user.id  

        conn = sqlite3.connect('school_bot.db')  
        cursor = conn.cursor()  
        cursor.execute('INSERT INTO schedule (user_id, day, subject, time) VALUES (?, ?, ?, ?)',   
                       (user_id, day, subject, time))  
        conn.commit()  
        conn.close()  

        update.message.reply_text(f"📅 Расписание добавлено: {day}, {subject}, {time}")  
    except Exception as e:  
        update.message.reply_text("Ошибка. Используйте формат: /add_schedule день предмет время")  

# Просмотр расписания  
def view_schedule(update: Update, context: CallbackContext):  
    user_id = update.message.from_user.id  

    conn = sqlite3.connect('school_bot.db')  
    cursor = conn.cursor()  
    cursor.execute('SELECT day, subject, time FROM schedule WHERE user_id = ?', (user_id,))  
    schedule = cursor.fetchall()  
    conn.close()  

    if schedule:  
        response = "📅 Ваше расписание:\n"  
        for entry in schedule:  
            response += f"{entry[0]}: {entry[1]} в {entry[2]}\n"  
        update.message.reply_text(response)  
    else:  
        update.message.reply_text("Расписание не найдено.")  

# Добавление домашнего задания  
def add_homework(update: Update, context: CallbackContext):  
    try:  
        subject, task, deadline = " ".join(context.args).rsplit(maxsplit=2)  
        user_id = update.message.from_user.id  

        conn = sqlite3.connect('school_bot.db')  
        cursor = conn.cursor()  
        cursor.execute('INSERT INTO homework (user_id, subject, task, deadline) VALUES (?, ?, ?, ?)',   
                       (user_id, subject, task, deadline))  
        conn.commit()  
        conn.close()  

        update.message.reply_text(f"📚 Домашнее задание добавлено: {subject}, {task}, срок: {deadline}")  
    except Exception as e:  
        update.message.reply_text("Ошибка. Используйте формат: /add_homework предмет задание срок")  

# Просмотр домашних заданий  
def view_homework(update: Update, context: CallbackContext):  
    user_id = update.message.from_user.id  

    conn = sqlite3.connect('school_bot.db')  
    cursor = conn.cursor()  
    cursor.execute('SELECT subject, task, deadline FROM homework WHERE user_id = ?', (user_id,))  
    homework = cursor.fetchall()  
    conn.close()  

    if homework:  
        response = "📚 Ваши домашние задания:\n"  
        for entry in homework:  
            response += f"{entry[0]}: {entry[1]} (срок: {entry[2]})\n"  
        update.message.reply_text(response)  
    else:  
        update.message.reply_text("Домашние задания не найдены.")  

# Установка напоминания  
def set_reminder(update: Update, context: CallbackContext):  
    try:  
        reminder_time = int(context.args[0])  # Время в минутах
        user_id = update.message.from_user.id  

        # Установка напоминания через указанное время
        context.job_queue.run_once(remind_user, timedelta(minutes=reminder_time), context=user_id)
        update.message.reply_text(f"⏰ Напоминание установлено на {reminder_time} минут(ы).")  
    except (IndexError, ValueError):  # Обработка ошибок
        update.message.reply_text("Ошибка. Используйте формат: /set_reminder время_в_минутах")  

# Функция напоминания  
def remind_user(context: CallbackContext):  
    job = context.job
    context.bot.send_message(job.context, text="⏰ Время для вашего напоминания!")  

def main(): 
    telegram_token = "7768482954:AAH8BfXTQ1SuGUdtdRTw0BuUMNx5vLPdyCI" 
    updater = Updater(telegram_token, use_context=True) 
    dp = updater.dispatcher 

    # Регистрируем обработчики команд 
    dp.add_handler(CommandHandler("start", start)) 
    dp.add_handler(CommandHandler("add_schedule", add_schedule)) 
    dp.add_handler(CommandHandler("view_schedule", view_schedule)) 
    dp.add_handler(CommandHandler("add_homework", add_homework)) 
    dp.add_handler(CommandHandler("view_homework", view_homework)) 
    dp.add_handler(CommandHandler("set_reminder", set_reminder)) 

    # Запускаем бота 
    updater.start_polling() 
    updater.idle() 

if __name__ == '__main__': 
    main()
