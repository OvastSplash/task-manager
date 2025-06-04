import requests
import json 

TOKEN = 'G5p3t2qZ6LHlJ9YapGzRZk5-_8nKk0qVY2uVJYYGvF0'
AUTH_URL = 'http://127.0.0.1:8000/telegram_auth/'
STATISTIC_URL = 'http://127.0.0.1:8000/api/v1/task/statistic/'
GET_TASKS_URL = 'http://127.0.0.1:8000/api/v1/task/'
TASK_ACTION_URL = 'http://127.0.0.1:8000/api/v1/task/action/'
CATEGORIES_URL = 'http://127.0.0.1:8000/api/v1/task/categories/'
CATEGORIES_ACTION_URL = 'http://127.0.0.1:8000/api/v1/task/categories/action/'

class ApiClient():
    def __init__(self, username):
        if username:
            self.username = username
        else: 
            raise ValueError("Username is required")
        
    def get_statistic(self):
        response = requests.get(STATISTIC_URL, headers={"TOKEN": TOKEN, "TELEGRAM-ID": self.username})
        
        if response.status_code == 200:
            data = response.json()
            message = f"📊 *Статистика*:\n\n"
            message += f"📂 *Количество категорий*: {data['categories_count']}\n"
            message += f"📋 *Количество задач*: {data['total_tasks']}\n"
            message += f"✅ *Всего выполнено задач*: {data['completed_tasks']}\n"
            message += f"❌ *Не выполнено задач*: {data['need_tasks']}\n"
            
            return message
        else:
            return None
        
    
    def auth(self):
        response = requests.get(AUTH_URL, headers={'TELEGRAM-ID': self.username})
        
        if response.status_code == 200:
            data = response.json()
            login = data['login']
            return login
        else:
            return None
        
    def get_task(self, category_number=None, is_list=False):
        if category_number:
            response = requests.get(GET_TASKS_URL, headers={'TOKEN': TOKEN, 'TELEGRAM-ID': self.username, 'CATEGORY-NUMBER': category_number})
        else:
            response = requests.get(GET_TASKS_URL, headers={'TOKEN': TOKEN, 'TELEGRAM-ID': self.username})
        
        if response.status_code == 200:
            data = response.json()
            
            result = []

            for category in data:
                if not is_list:
                    header = f"📂 *{category['title']}*"
                    result.append(header)

                if category["tasks"]:
                    for task in category["tasks"]:
                        status = "✅ " if task["is_done"] else "❌"
                        task_line = f"        {task['number']}. {status} {task['title']}"
                        result.append(task_line)
                else:
                    result.append("     — Нет задач —")

                result.append("")  # пустая строка между категориями

            if is_list:
                return result

            return "\n".join(result)
            
        else:
            return None
        
    def create_task(self, category_number, task_title):
        response = requests.post(f"{TASK_ACTION_URL}{category_number}/", headers={'TOKEN': TOKEN, 'TELEGRAM-ID': self.username}, json={'title': task_title})
        
        if response.status_code == 201:
            return "Задача успешно создана"
        else:
            return None
        
    def update_task(self, category_number, task_number, task_title):
        response = requests.put(f"{TASK_ACTION_URL}{category_number}/{task_number}/", headers={'TOKEN': TOKEN, 'TELEGRAM-ID': self.username}, json={'title': task_title})
        
        if response.status_code == 200:
            return "Задача успешно обновлена"
        else:
            return None
        
    def done_task(self, category_number, task_number, is_done):
        response = requests.put(f"{TASK_ACTION_URL}{category_number}/{task_number}/", headers={'TOKEN': TOKEN, 'TELEGRAM-ID': self.username}, json={'is_done': is_done})
        
        if response.status_code == 200:
            return "Задача успешно выполнена"
        else:
            return None
        
    def delete_task(self, category_number, task_number):
        response = requests.delete(f"{TASK_ACTION_URL}{category_number}/{task_number}/", headers={'TOKEN': TOKEN, 'TELEGRAM-ID': self.username})
        
        if response.status_code == 204:
            return "Задача успешно удалена"
        else:
            return None
        
    
    def get_categories(self, is_list=False):
        response = requests.get(CATEGORIES_URL, headers={'TOKEN': TOKEN, 'TELEGRAM-ID': self.username})
        
        if response.status_code == 200:
            data = response.json()
            result = []
            
            for cat in data: 
                result.append(f"{cat['number']}. 📂 {cat['title']}")
                
            if not result:
                return "— Нет категорий —"
            
            if is_list:
                return result
            
            return "\n".join(result)
        else:
            return None
        
    def create_category(self, category_name):
        response = requests.post(CATEGORIES_URL, headers={'TOKEN': TOKEN, 'TELEGRAM-ID': self.username}, json={'title': category_name})
        
        if response.status_code == 201:
            return "Категория успешно создана"
        else:
            return None

    def delete_category(self, category_number):
        response = requests.delete(f"{CATEGORIES_ACTION_URL}{category_number}/", headers={'TOKEN': TOKEN, 'TELEGRAM-ID': self.username})
        
        if response.status_code == 204:
            return "Категория успешно удалена"
        else:
            return None
        
    def update_category(self, category_number, category_title):
        response = requests.put(f"{CATEGORIES_ACTION_URL}{category_number}/", headers={'TOKEN': TOKEN, 'TELEGRAM-ID': self.username}, json={'title': category_title})
        
        if response.status_code == 200:
            return "Категория успешно обновлена"
        else:
            return None
