from api_client import ApiClient
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Обрабатывает главную меню
async def main_menu(update: Update):
    keyboard = [
            ["📋 Посмотреть задачи", "ℹ️ Инфо"],
            ["❓ Редактировать задачи", "📂 Кактегории"]
        ]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True  # Подгоняет клавиатуру под экран
    )
    await update.message.reply_text("Выберите опцию:", reply_markup=reply_markup)
    
async def categories_menu(update: Update, text: str, categories: list):
    keyboard = [
        ["📂 Добавить категорию", "📂 Удалить категорию", "↩️ Вернутся в главное меню"]
    ]
    
    keyboard.append(categories)
    
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )
    await update.message.reply_text(f"{text}", reply_markup=reply_markup)
    
async def delete_category_menu(update: Update, text: str, categories: list):
    keyboard = [
        ["↩️ Вернутся в главное меню"]
    ]
    keyboard.append(categories)
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )
    await update.message.reply_text(f"{text}", reply_markup=reply_markup)
    
async def tasks_menu(update: Update, text: str, tasks: list):
    keyboard = [
        ["📋 Добавить задачу", "📋 Изменить задачу", "📋 Удалить задачу", "↩️ Вернутся в главное меню"]
    ]
    if not any("Нет задач" in task for task in tasks):    
        keyboard.append(tasks)
    
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )
    await update.message.reply_text(f"{text}", reply_markup=reply_markup)
    
async def delete_task_menu(update: Update, text: str, tasks: list):
    keyboard = [
        ["↩️ Вернутся в главное меню"]
    ]
    keyboard.append(tasks)
    
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )
    await update.message.reply_text(f"{text}", reply_markup=reply_markup)