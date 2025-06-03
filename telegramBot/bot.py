import menu
from api_client import ApiClient
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

API_TOKEN = '7863398372:AAHQPr5rMAG_BOfSjf6OK7catviIjloFOKE'

# Обрабатывает команду /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['add_category'] = False
    context.user_data['delete_category'] = False
    context.user_data['category_number'] = None
    context.user_data['add_task'] = False
    context.user_data['task_number'] = None
    
    username = update.effective_user.username
    print(username)
    client = ApiClient(username)
    auth_login = client.auth()
    
    if auth_login:
        context.user_data['username'] = username
        await update.message.reply_text(f"Привет, {auth_login}!")
        await menu.main_menu(update)
    else:
        await update.message.reply_text("Вы не авторизованы в приложении")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    username = context.user_data['username']
    client = ApiClient(username)
    await handle_category(update, context)
    await handle_task(update, context)

    if message == "📋 Посмотреть задачи":
        data = client.get_task()
        if data:
            await update.message.reply_text(data)
        else:
            await update.message.reply_text("Не удалось получить задачи")

    if message == "↩️ Вернутся в главное меню":
        await menu.main_menu(update)
    
    if message == "❓ Редактировать задачи":
        await update.message.reply_text("Выберете категорию: ")
        
# Обрабатывает категории
async def handle_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    username = context.user_data['username']
    print(username)
    client = ApiClient(username)
    
    # Вывод всех категорий
    if message == "📂 Кактегории":
        data = client.get_categories()
        if data:
            await update.message.reply_text(data)
            catalogies = client.get_categories(True)
            await menu.categories_menu(update, "Выберите опцию:", catalogies)
        else:
            await update.message.reply_text("Не удалось получить категории")
        
    # Добавление категории
    if message == "📂 Добавить категорию":
        await update.message.reply_text("Введите название категории: ")
        context.user_data['category_name'] = update.message.text
        context.user_data['add_category'] = True
        return
    
    # Добавление категории в базу данных
    if context.user_data['add_category']:
        category_name = message
        print(f"category_name: {category_name}")
        data = client.create_category(category_name)
        context.user_data['add_category'] = False
    
        # Обновление списка категорий
        updated_categories_list = client.get_categories(True)
        
        if data:
            # Обновление списка категорий
            data = client.get_categories()
            if data:
                await update.message.reply_text(data)
                await menu.categories_menu(update, "Категория успешно создана", updated_categories_list)
            else:
                await update.message.reply_text("Не удалось получить категории")
        else:
            await menu.categories_menu(update, "Категория уже существует", updated_categories_list)
    
    # Удаление категории
    if message == "📂 Удалить категорию":
        context.user_data['delete_category'] = True
        data = client.get_categories(True)
        if data:
            await menu.delete_category_menu(update, "Выберите категорию для удаления:", data)
        else:
            await update.message.reply_text("Не удалось получить категории")
    
    # Обрабатывает задачи в категории
    if '. 📂' in message:
        category_number = message.split('.')[0]
        context.user_data['category_number'] = category_number
        
        # Удаление категории в базе данных
        print(f"CATEGORY NUMBER --- {category_number}")
        if context.user_data['delete_category']:
            data = client.delete_category(category_number=category_number)
            updated_categories_list  = client.get_categories(is_list=True)
            updated_categories = client.get_categories()
                        
            if data:
                await menu.categories_menu(update, "Категория успешно удалена", updated_categories_list)
                context.user_data['category_number'] = None
            else:
                await menu.categories_menu(update, "Не удалось удалить категорию", updated_categories_list)

            await update.message.reply_text(updated_categories)
        
        # Вывод задач в категории
        else:
            # Обновлённый список задач
            sorted_data = client.get_task(category_number=category_number)
            
            if sorted_data:
                sorted_data_list = client.get_task(category_number=category_number, is_list=True)
                await update.message.reply_text(sorted_data)
                await menu.tasks_menu(update, "Выберите опцию:", sorted_data_list)
            else:
                await update.message.reply_text("Не удалось получить задачи")
                
        
        context.user_data['delete_category'] = False
        
    
async def handle_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    username = context.user_data['username']
    client = ApiClient(username)
    
    # Добавление задачи
    if message == "📋 Добавить задачу":
        await update.message.reply_text("Введите название задачи: ")
        context.user_data['task_number'] = update.message.text
        context.user_data['add_task'] = True
        return
    
    # Добавление задачи в базу данных
    if context.user_data['add_task']:
        category_number = context.user_data['category_number']
        task_name = message
        print(f"task_name: {task_name}")
        print(f"category_number: {category_number}")
        data = client.create_task(category_number=category_number, task_title=task_name)
        context.user_data['add_task'] = False
        
        if data:    
            sorted_data = client.get_task(category_number=category_number)
            sorted_data_list = client.get_task(category_number=category_number, is_list=True)
            await update.message.reply_text(sorted_data)
            await menu.tasks_menu(update, "Задача успешно добавлена", sorted_data_list)
        else:
            await update.message.reply_text("Не удалось добавить задачу")

    
    
    
    if message == "📋 Удалить задачу":
        context.user_data['delete_task'] = True
        data = client.get_task(category_number=category_number, is_list=True)
        if data:
            await menu.delete_task_menu(update, "Выберите задачу для удаления:", data)
        else:
            await update.message.reply_text("Не удалось получить задачи")
        
    
    if ". ❌" in message or ". ✅" in message:
        task_number = message.split('.')[0]
        context.user_data['task_number'] = task_number

        if context.user_data['delete_task']:
            data = client.delete_task(category_number=category_number, task_number=task_number)
            if data:
                sorted_data = client.get_task(category_number=category_number)
                sorted_data_list = client.get_task(category_number=category_number, is_list=True)
                await update.message.reply_text(sorted_data)
                await menu.tasks_menu(update, "Задача успешно удалена", sorted_data_list)
            else:
                await update.message.reply_text("Не удалось удалить задачу")
    
    

if __name__ == '__main__':
    app = ApplicationBuilder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
