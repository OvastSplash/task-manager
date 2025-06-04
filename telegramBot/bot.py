import menu
from api_client import ApiClient
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

API_TOKEN = 'YOUR_API_KEY'

# Обрабатывает команду /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['add_category'] = False
    context.user_data['delete_category'] = False
    context.user_data['category_number'] = None
    context.user_data['update_category'] = False
    context.user_data['update_category_name'] = False

    context.user_data['add_task'] = False
    context.user_data['task_number'] = None
    context.user_data['update_task'] = False
    context.user_data['update_task_name'] = False
    context.user_data['delete_task'] = False
    
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
    
    if message == "ℹ️ Посмотреть статистику профиля":
        data = client.get_statistic()
        print(f"DATA --- {data}")
        if data:
            await menu.main_menu(update, text=data)
        else:
            await menu.main_menu(update, text="Не удалось получить статистику")
            
        
# Обрабатывает категории
async def handle_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text
    username = context.user_data['username']
    print(username)
    client = ApiClient(username)
    
    # Вывод всех категорий
    if message == "📂 Категории":
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
    
    if context.user_data['update_category']:
        context.user_data['update_category_name'] = True
        await update.message.reply_text("Введите новое название категории: ")
        context.user_data['update_category'] = False
        
    elif context.user_data['update_category_name']:
        category_number = context.user_data['category_number']
        category_name = message
        data = client.update_category(category_number=category_number, category_title=category_name)

        updated_categories_list = client.get_categories(is_list=True)
        updated_categories = client.get_categories()

        if data:
            await menu.categories_menu(update, "Категория успешно обновлена", updated_categories_list)
        else:
            await menu.categories_menu(update, "Не удалось обновить категорию", updated_categories_list)

        await update.message.reply_text(updated_categories)
        context.user_data['update_category_name'] = False

    if message == "📂 Изменить категорию":
        data = client.get_categories(is_list=True)
        if data:
            context.user_data['update_category'] = True
            await menu.categories_menu(update, "Выберите категорию для изменения:", data)
        else:
            await menu.categories_menu(update, "Не удалось получить категории", data)


    # Обрабатывает задачи в категории
    if '. 📂' in message:
        category_number = message.split('.')[0]
        context.user_data['category_number'] = category_number
        
        # Удаление категории в базе данных
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
        elif context.user_data['update_category_name'] == False:
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
    
    
    # Вывод списка задач для удаления
    if message == "📋 Удалить задачу":
        context.user_data['delete_task'] = True
        category_number = context.user_data['category_number']
        print(f"CATEGORY NUMBER --- {category_number}")
        data = client.get_task(category_number=category_number, is_list=True)
        if data:
            await menu.delete_task_menu(update, "Выберите задачу для удаления:", data)
        else:
            await update.message.reply_text("Не удалось получить задачи")

    if message == "📋 Изменить задачу":
        context.user_data['update_task'] = True
        category_number = context.user_data['category_number']
        task_number = context.user_data['task_number']
        data = client.get_task(category_number=category_number, is_list=True)
        if data:
            await menu.delete_task_menu(update, "Выберите задачу для изменения:", data)
        else:
            await update.message.reply_text("Не удалось получить задачи")

    # Удаление задачи
    if ". ❌" in message or ". ✅" in message:
        print(f"MESSAGE --- {message}")
        task_number = message.split('.')[0]
        context.user_data['task_number'] = task_number
        category_number = context.user_data['category_number']
        print(f"CATEGORY NUMBER --- {category_number}")
        print(f"TASK NUMBER --- {task_number}")

        if context.user_data['delete_task']:
            data = client.delete_task(category_number=category_number, task_number=task_number)
            sorted_data = client.get_task(category_number=category_number)
            sorted_data_list = client.get_task(category_number=category_number, is_list=True)

            if data:
                await menu.tasks_menu(update, "Задача успешно удалена", sorted_data_list)
                await update.message.reply_text(sorted_data)
            else:
                await menu.tasks_menu(update, "Не удалось удалить задачу", sorted_data_list)
                await update.message.reply_text(sorted_data)

            context.user_data['delete_task'] = False

        elif context.user_data['update_task']:
            context.user_data['update_task_name'] = True
            await update.message.reply_text("Введите новое название задачи: ")

        else: 
            if "✅" in message:
                is_done = False
            else:
                is_done = True
            print(f"IS DONE --- {is_done}")
            data = client.done_task(category_number=category_number, task_number=task_number, is_done=is_done)
            sorted_data = client.get_task(category_number=category_number)
            sorted_data_list = client.get_task(category_number=category_number, is_list=True)

            if data:
                await menu.tasks_menu(update, "Задача было успешно выполнена", sorted_data_list)
            else:
                await menu.tasks_menu(update, "Не удалось обновить задачу", sorted_data_list)

            await update.message.reply_text(sorted_data)
                
    
    elif context.user_data['update_task_name']:
        task_name = message
        category_number = context.user_data['category_number']
        task_number = context.user_data['task_number']
        print(f"TASK NAME --- {task_name}")
        print(f"CATEGORY NUMBER --- {category_number}")
        print(f"TASK NUMBER --- {task_number}")

        data = client.update_task(category_number=category_number, task_number=task_number, task_title=task_name)
        sorted_data = client.get_task(category_number=category_number)
        sorted_data_list = client.get_task(category_number=category_number, is_list=True)

        if data:
            await menu.tasks_menu(update, "Задача успешно обновлена", sorted_data_list)
            await update.message.reply_text(sorted_data)
        else:
            await menu.tasks_menu(update, "Не удалось обновить задачу", sorted_data_list)
            await update.message.reply_text(sorted_data)

        context.user_data['update_task'] = False
        context.user_data['update_task_name'] = False
        
        

if __name__ == '__main__':
    app = ApplicationBuilder().token(API_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
