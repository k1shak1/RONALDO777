import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import json
import requests
from gigachat import GigaChat
import requests
import uuid
import time
import logging

# Инициализация
vk_session = vk_api.VkApi(token="vk1.a.2h_nONA676JwH3pU4iWOHsEY-xAIMJK7ASEuv1YSoaSayFVDpdFnT52CqHHwLXEtIvLzfVQ0LiQzhe3Noi6cCgMD2zOYnyn2IPkl01J7xsKOZZ63HL70TZs03sjGo-ldr3LwBC4YKbYAoEJJS-gBgwxzy5ItB7wfEdnh_HUZIr4tfoA4GAN0m6OMNTO6nPlsb6Iu1Y_9Ia4IcDpig7UeCg")
longpoll = VkBotLongPoll(vk_session, "231389005")
vk = vk_session.get_api()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("GigaChat_Helper")

# Конфигурация
GIGACHAT_API_KEY = "MzA5YzViY2UtMzExMC00NzEyLWEyYTYtNjNkZDAyMDMxZDJkOjczNDk2Nzc0LWM1YzItNDNiNy1iZWQ0LTI1MzU3YTJiNzA0ZQ=="

# Глобальные переменные для управления токеном
access_token = None
token_expire_time = 0
# Глобальные переменные для управления токеном
access_token = None
token_expire_time = 0

def get_gigachat_token():
    """Получаем новый токен доступа для GigaChat API"""
    global access_token, token_expire_time
    
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    
    payload = {
        'scope': 'GIGACHAT_API_PERS'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'Basic {GIGACHAT_API_KEY}'
    }
    
    try:
        response = requests.post(
            url, 
            headers=headers, 
            data=payload, 
            timeout=10,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            access_token = data['access_token']
            token_expire_time = time.time() + 25 * 60
            logger.info("Токен GigaChat успешно получен")
            return True
        else:
            logger.error(f"Ошибка получения токена: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        logger.error(f"Ошибка при получении токена: {str(e)}")
        return False

def ask_gigachat(question):
    """Отправляем запрос к GigaChat API и получаем ответ"""
    global access_token, token_expire_time
    
    if not access_token or time.time() > token_expire_time:
        if not get_gigachat_token():
            return "Сервис временно недоступен. Попробуйте позже."
    
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    
    messages = [
        {
            "role": "system",
            "content": (
                "Ты помощник для проектов VK Education. Отвечай кратко (1-2 предложения), "
                "используя только информацию с официального сайта VK Education. "
                "Будь дружелюбным и полезным. Если вопрос не связан с образовательными проектами VK, "
                "вежливо предложи посетить официальный сайт VK Education. "
                "Не упоминай, что ты ИИ-модель. Используй эмодзи для выразительности."
            )
        },
        {
            "role": "user",
            "content": question
        }
    ]
    
    data = {
        "model": "GigaChat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 200
    }
    
    try:
        response = requests.post(
            url, 
            headers=headers, 
            json=data, 
            timeout=15,
            verify=False
        )
        
        if response.status_code == 401:
            logger.warning("Токен недействителен. Пробуем обновить...")
            if get_gigachat_token():
                headers['Authorization'] = f'Bearer {access_token}'
                response = requests.post(
                    url, 
                    headers=headers, 
                    json=data, 
                    timeout=15,
                    verify=False
                )
            else:
                return "Ошибка авторизации. Попробуйте позже."
                
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            logger.error(f"Ошибка API GigaChat: {response.status_code}, {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        logger.warning("Таймаут при запросе к GigaChat API")
        return None
    except Exception as e:
        logger.error(f"Ошибка запроса к GigaChat: {str(e)}")
        return None

# Список частых вопросов и ответов
FAQ = [
    {
        "question": "Кто может участвовать в программе?", "answer": "Школьники, студенты бакалавриата, специалитета, магистратуры и аспирантуры всех вузов России, а также научные руководители и преподаватели."
    },
    {
        "question": "Можно ли выбрать несколько задач?", "answer": "Да, можно решать неограниченное количество задач."
    },
    {
        "question": "Где можно использовать решения задач?", "answer": "Задачи от VK можно использовать в практической части выпускных квалификационных, курсовых и научно-исследовательских работ, а также взять за основу домашних заданий."
    },
    {
        "question": "Как получить данные для решения?", "answer": "Выбери задачу, пройди регистрацию — и тебе откроется доступ к материалам, которые понадобятся в процессе работы над задачей."
    },
    {
        "question": "Я получу сертификат?", "answer": "Если ты выполнишь все условия, описанные в выбранной задаче, то сможешь получить сертификат о работе над проектом VK."
    },
    {
        "question": "Будут ли ставить оценки?", "answer": "Нет, оценки за решения задач не предусмотрены. Однако если ты выполнишь требования, описанные в задаче, поделишься с нами результатами работы и твоё решение высоко оценят эксперты, мы свяжемся с тобой и подготовим рецензию."
    },
    {
        "question": "Как формировались задачи?", "answer": "Все задачи на витрине — исследовательские и носят экспериментальный характер, составлены с учётом актуального бизнес-контекста. Задачи сформулированы таким образом, чтобы у участников была возможность реализовать свой талант, работая над интересными проектными кейсами."
    },
    {
        "question": "Кому я могу задать вопросы?", "answer": "Следи за расписанием вебинаров на странице проекта — ты сможешь задать вопросы по задаче экспертам VK."
    },
    {
        "question": "Я не могу найти подходящую задачу","answer": "В банке задач появляются новые интересные кейсы от департаментов VK, следи за обновлениями."    
    }
]

PROFANITY_FILTER = [
    "бля", "хуй", "пизд", "еба", "хуе", "хуя", "ебал", "залуп", "мудак", "гандон",
    "шлюх", "долбоеб", "сука", "пидор", "член", "вагин", "пенис", "анус", "срак",
    "жопа", "ссать", "перд", "дрист", "елда", "мразь", "ублюдок", "падл", "бляд",
    "оху", "ебан", "ебу", "ебн", "писе", "попк", "сучк", "трах", "выеб", "вздроч",
    "гондон", "дроч", "заеб", "конч", "лох", "манда", "мудил", "педр", "пезд",
    "соси", "сперм", "суч", "хер", "хуи", "шмар"
]

def contains_profanity(text):
    """Проверяет, содержит ли текст нецензурную лексику"""
    text_lower = text.lower()
    return any(word in text_lower for word in PROFANITY_FILTER)

def is_closed_question(question):
    """Определяет, является ли вопрос закрытым (да/нет) и возвращает ответ"""
    closed_keywords = [
        "можно ли", "возможно ли", "есть ли", "будет ли", "имеется ли", 
        "существует ли", "доступно ли", "разрешено ли", "допустимо ли",
        "можно?", "разрешено?", "будет?", "есть?", "доступно?", "допустимо?",
        " ли ", ",будут ли"
    ]
    
    question_lower = question.lower()
    if any(keyword in question_lower for keyword in closed_keywords):
        # Проверяем FAQ для точного соответствия
        for item in FAQ:
            if item["question"].lower() in question_lower:
                return item["answer"]
        return "✅ Да." if "не" not in question_lower else "❌ Нет."
    return None

# Клавиатуры
def create_start_keyboard():
    return {
        "one_time": True,
        "buttons": [[{
            "action": {"type": "text", "label": "Начать", "payload": "{\"command\":\"start\"}"},
            "color": "positive"
        }]]
    }

def create_main_keyboard():
    return {
        "one_time": False,
        "buttons": [
            [
                {"action": {"type": "text", "label": "Частые вопросы", "payload": "{\"command\":\"faq\"}"}, "color": "positive"},
            ],
            [
                {"action": {"type": "text", "label": "Другой вопрос", "payload": "{\"command\":\"other_question\"}"}, "color": "secondary"}
            ]
        ]
    }

def create_faq_keyboard():
    buttons = []
    # Группируем по 2 вопроса в строку
    for i in range(0, len(FAQ), 2):
        row = []
        if i < len(FAQ):
            row.append({
                "action": {
                    "type": "text",
                    "label": FAQ[i]["question"][:40],
                    "payload": json.dumps({"command": "faq_answer", "index": i})
                },
                "color": "primary"
            })
        if i+1 < len(FAQ):
            row.append({
                "action": {
                    "type": "text",
                    "label": FAQ[i+1]["question"][:40],
                    "payload": json.dumps({"command": "faq_answer", "index": i+1})
                },
                "color": "primary"
            })
        if row:
            buttons.append(row)
    
    # Добавляем кнопку "Назад"
    buttons.append([{"action": {"type": "text", "label": "Назад", "payload": "{\"command\":\"back\"}"}, "color": "negative"}])
    
    return {"one_time": False, "buttons": buttons}

# Основной цикл бота
user_states = {}

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        msg = event.object.message
        user_id = msg["from_id"]
        text = msg["text"].lower()

        # Инициализация состояния
        if user_id not in user_states:
            user_states[user_id] = {"state": "start", "data": None}
            
            vk.messages.send(
                user_id=user_id,
                message="Привет! Я бот VK Education. Нажмите 'Начать'",
                keyboard=json.dumps(create_start_keyboard()),
                random_id=0
            )
            continue
        # Проверка на нецензурную лексику
        if contains_profanity(text):
            vk.messages.send(
                user_id=user_id,
                message="🚫 Пожалуйста, воздержитесь от использования нецензурной лексики в нашем образовательном сообществе.",
                random_id=0
            )
            continue  # Пропускаем дальнейшую обработку сообщения
            
        text = text.lower()

        # Обработка команд
        if user_states[user_id]["state"] == "start":
            if text == "начать":
                user_states[user_id] = {"state": "main", "data": None}
                vk.messages.send(
                    user_id=user_id,
                    message="Добро пожаловать! Выберите действие:",
                    keyboard=json.dumps(create_main_keyboard()),
                    random_id=0
                )
            else:
                vk.messages.send(
                    user_id=user_id,
                    message="Пожалуйста, нажмите 'Начать'",
                    keyboard=json.dumps(create_start_keyboard()),
                    random_id=0
                )
        
        elif user_states[user_id]["state"] == "main":
            if text == "частые вопросы":
                user_states[user_id] = {"state": "faq", "data": None}
                vk.messages.send(
                    user_id=user_id,
                    message="Выберите вопрос:",
                    keyboard=json.dumps(create_faq_keyboard()),
                    random_id=0
                )
            
            elif text == "другой вопрос":
                user_states[user_id] = {"state": "other_question", "data": None}
                vk.messages.send(
                    user_id=user_id,
                    message="Вы можете задать любой вопрос. Я постараюсь помочь!",
                    keyboard=json.dumps({
                        "one_time": False,
                        "buttons": [[
                            {"action": {"type": "text", "label": "Назад", "payload": "{\"command\":\"back\"}"}, "color": "negative"}
                        ]]
                    }),
                    random_id=0
                )

        elif user_states[user_id]["state"] == "other_question":
            if text == "назад":
                user_states[user_id] = {"state": "main", "data": None}
                vk.messages.send(
                    user_id=user_id,
                    message="Главное меню:",
                    keyboard=json.dumps(create_main_keyboard()),
                    random_id=0
                )
            else:
                # Сначала проверяем, не закрытый ли вопрос
                closed_answer = is_closed_question(text)
                if closed_answer:
                    vk.messages.send(
                        user_id=user_id,
                        message=closed_answer,
                        keyboard=json.dumps({
                            "one_time": False,
                            "buttons": [[
                                {"action": {"type": "text", "label": "Назад", "payload": "{\"command\":\"back\"}"}, "color": "negative"}
                            ]]
                        }),
                        random_id=0
                    )
                    continue
            
                # Если вопрос не закрытый, обрабатываем как обычно
                loading_msg = vk.messages.send(
                    user_id=user_id,
                    message="🔍 Ищу ответ на ваш вопрос...",
                    random_id=0
                )    
            
            # Получаем ответ от GigaChat
                giga_response = ask_gigachat(text)
            
                if giga_response:
                    response_text = f"🤖 Ответ на ваш вопрос:\n\n{giga_response}\n\n" \
                                f"Если нужна дополнительная информация, посетите: " \
                                f"https://education.vk.company/education_projects"
                else:
                    response_text = "⚠️ Не удалось получить ответ. Попробуйте задать вопрос позже или " \
                                "посетите https://education.vk.company/education_projects"
            
            # Отправляем ответ
                vk.messages.send(
                    user_id=user_id,
                    message=response_text,
                    keyboard=json.dumps({
                        "one_time": False,
                        "buttons": [[
                            {"action": {"type": "text", "label": "Назад", "payload": "{\"command\":\"back\"}"}, "color": "negative"}
                        ]]
                    }),
                    random_id=0
                )

    # В основном цикле обработки команд добавляем:
        elif user_states[user_id]["state"] == "main":
            if text == "другой вопрос":
                user_states[user_id] = {"state": "other_question", "data": None}
                vk.messages.send(
                    user_id=user_id,
                    message="Задайте ваш вопрос, и я постараюсь помочь!\n"
                        "Вы можете спросить о программах, сроках, требованиях и т.д.",
                    keyboard=json.dumps({
                        "one_time": False,
                        "buttons": [[
                            {"action": {"type": "text", "label": "Назад", "payload": "{\"command\":\"back\"}"}, "color": "negative"}
                        ]]
                    }),
                    random_id=0
                )
                    
        elif user_states[user_id]["state"] == "faq":
            if text.lower() == "назад":
                user_states[user_id] = {"state": "main", "data": None}
                vk.messages.send(
                    user_id=user_id,
                    message="Главное меню:",
                    keyboard=json.dumps(create_main_keyboard()),
                    random_id=0
                )

            elif "payload" in msg and msg["payload"]:
                # Обработка кнопки
                try:
                    payload = json.loads(msg["payload"])
                    if payload.get("command") == "faq_answer":
                        index = int(payload["index"])
                        if 0 <= index < len(FAQ):
                            vk.messages.send(
                                user_id=user_id,
                                message=FAQ[index]["answer"],
                                keyboard=json.dumps({
                                    "one_time": False,
                                    "buttons": [[
                                        {"action": {"type": "text", "label": "Назад", "payload": "{\"command\":\"back\"}"}, "color": "negative"}
                                    ]]
                                }),
                                random_id=0
                            )
                except Exception as e:
                    logger.warning(f"Ошибка при обработке payload: {e}")

            else:
                # 🔍 Попробуем найти текстовый вопрос в списке FAQ
                matched = None
                for item in FAQ:
                    if text.strip().lower() == item["question"].strip().lower():
                        matched = item
                        break

                if matched:
                    vk.messages.send(
                        user_id=user_id,
                        message=matched["answer"],
                        keyboard=json.dumps({
                            "one_time": False,
                            "buttons": [[
                                {"action": {"type": "text", "label": "Назад", "payload": "{\"command\":\"back\"}"}, "color": "negative"}
                            ]]
                        }),
                        random_id=0
                    )
                else:
                    # Не нашли совпадение
                    vk.messages.send(
                        user_id=user_id,
                        message="Пожалуйста, выбери вопрос из списка ниже, или напиши его точно, как в кнопке 👇",
                        keyboard=json.dumps(create_faq_keyboard()),
                        random_id=0
                    )


# # .styles_card__nDUcX
# #MzA5YzViY2UtMzExMC00NzEyLWEyYTYtNjNkZDAyMDMxZDJkOjczNDk2Nzc0LWM1YzItNDNiNy1iZWQ0LTI1MzU3YTJiNzA0ZQ==

        # elif user_states[user_id]["state"] == "other_question":
        #     if text == "назад":
        #         user_states[user_id] = {"state": "main", "data": None}
        #         vk.messages.send(
        #             user_id=user_id,
        #             message="Главное меню:",
        #             keyboard=json.dumps(create_main_keyboard()),
        #             random_id=0
        #         )
        #     else:
        #         # Получаем ответ от GigaChat
        #         gigachat_response = get_gigachat_response(text)
                
        #         vk.messages.send(
        #             user_id=user_id,
        #             message=f"🔍 Ваш вопрос: {text}\n\n💡 Ответ от GigaChat:\n{gigachat_response}",
        #             keyboard=json.dumps({
        #                 "one_time": False,
        #                 "buttons": [[
        #                     {"action": {"type": "text", "label": "Назад", "payload": "{\"command\":\"back\"}"}, "color": "negative"}
        #                 ]]
        #             }),
        #             random_id=0
        #         )




# import vk_api
# from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
# from vk_api.keyboard import VkKeyboard, VkKeyboardColor
# import datetime
# import time
# import logging
# import requests
# import uuid

# # Конфигурация
# GROUP_ID = 231389005
# TOKEN = "vk1.a.2h_nONA676JwH3pU4iWOHsEY-xAIMJK7ASEuv1YSoaSayFVDpdFnT52CqHHwLXEtIvLzfVQ0LiQzhe3Noi6cCgMD2zOYnyn2IPkl01J7xsKOZZ63HL70TZs03sjGo-ldr3LwBC4YKbYAoEJJS-gBgwxzy5ItB7wfEdnh_HUZIr4tfoA4GAN0m6OMNTO6nPlsb6Iu1Y_9Ia4IcDpig7UeCg"
# VK_EDU_LINK = "https://vk.com/vkedu"
# GIGACHAT_API_KEY = "MzA5YzViY2UtMzExMC00NzEyLWEyYTYtNjNkZDAyMDMxZDJkOjczNDk2Nzc0LWM1YzItNDNiNy1iZWQ0LTI1MzU3YTJiNzA0ZQ=="

# # Настройка логирования
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger("VK_Education_Bot")

# # База знаний (FAQ) - основные вопросы о VK Education
# FAQ = {
#     "Кто может участвовать?": "Школьники, студенты бакалавриата, специалитета, магистратуры и аспирантуры всех вузов России, а также научные руководители и преподаватели.",
#     "Можно выбрать несколько задач?": "Да, можно выбрать неограниченное количество задач.",
#     "Где использовать решения?": "В практической части выпускных квалификационных работ, курсовых, НИР и домашних заданий.",
#     "Как получить данные?": "Выбери задачу, пройди регистрацию — и получишь доступ к материалам.",
#     "Будут сертификаты?": "Да, при выполнении всех условий задачи.",
#     "Будут оценки?": "Нет, но эксперты дадут рецензию на хорошие решения.",
#     "Откуда задачи?": "Исследовательские задачи с актуальным бизнес-контекстом от VK.",
#     "Кому задать вопрос?": "Экспертам на вебинарах или на обучающей платформе.",
#     "Нет подходящей задачи?": "Следи за обновлениями в банке задач VK."
# }

# # Список нецензурных слов (фильтр)
# PROFANITY_FILTER = [
#     "бля", "хуй", "пизд", "еба", "хуе", "хуя", "ебал", "залуп", "мудак", "гандон",
#     "шлюх", "долбоеб", "сука", "пидор", "член", "вагин", "пенис", "анус", "срак",
#     "жопа", "ссать", "перд", "дрист", "елда", "мразь", "ублюдок", "падл", "бляд",
#     "оху", "ебан", "ебу", "ебн", "писе", "попк", "сучк", "трах", "выеб", "вздроч",
#     "гондон", "дроч", "заеб", "конч", "лох", "манда", "мудил", "педр", "пезд",
#     "соси", "сперм", "суч", "хер", "хуи", "шмар"
# ]

# def create_keyboard():
#     """Создает интерактивную клавиатуру с вопросами"""
#     keyboard = VkKeyboard(inline=True)
#     questions = list(FAQ.keys())
    
#     for i, question in enumerate(questions):
#         keyboard.add_button(question, color=VkKeyboardColor.PRIMARY)
#         if (i + 1) % 2 == 0 and i < len(questions) - 1:
#             keyboard.add_line()
    
#     keyboard.add_line()
#     keyboard.add_button("Другой вопрос", color=VkKeyboardColor.SECONDARY)
#     return keyboard.get_keyboard()

# # Глобальные переменные для управления токеном GigaChat
# access_token = None
# token_expire_time = 0


# def get_gigachat_token():
#     """Получаем новый токен доступа для GigaChat API"""
#     global access_token, token_expire_time
    
#     url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    
#     payload = {
#         'scope': 'GIGACHAT_API_PERS'
#     }
#     headers = {
#         'Content-Type': 'application/x-www-form-urlencoded',
#         'Accept': 'application/json',
#         'RqUID': str(uuid.uuid4()),
#         'Authorization': f'Basic {GIGACHAT_API_KEY}'
#     }
    
#     try:
#         # Отключаем проверку SSL для этого запроса
#         response = requests.post(
#             url, 
#             headers=headers, 
#             data=payload, 
#             timeout=10,
#             verify=False  # ОТКЛЮЧАЕМ ПРОВЕРКУ SSL
#         )
        
#         if response.status_code == 200:
#             data = response.json()
#             access_token = data['access_token']
#             token_expire_time = time.time() + 25 * 60
#             logger.info("Токен GigaChat успешно получен")
#             return True
#         else:
#             logger.error(f"Ошибка получения токена: {response.status_code}, {response.text}")
#             return False
#     except Exception as e:
#         logger.error(f"Ошибка при получении токена: {str(e)}")
#         return False

# def contains_profanity(text):
#     """Проверяет текст на наличие нецензурной лексики"""
#     text_lower = text.lower()
#     for word in PROFANITY_FILTER:
#         if word in text_lower:
#             return True
#     return False

# def is_closed_question(question):
#     """Определяет, является ли вопрос закрытым (да/нет)"""
#     closed_keywords = [
#         "можно ли", "возможно ли", "есть ли", "будет ли", "имеется ли", 
#         "существует ли", "доступно ли", "разрешено ли", "допустимо ли",
#         "можно?", "разрешено?", "будет?", "есть?", "доступно?", "допустимо?"
#     ]
    
#     question_lower = question.lower()
#     return any(keyword in question_lower for keyword in closed_keywords)

# def ask_gigachat(question):
#     """Отправляем запрос к GigaChat API с использованием токена"""
#     global access_token, token_expire_time
    
#     if not access_token or time.time() > token_expire_time:
#         if not get_gigachat_token():
#             return "Сервис временно недоступен. Попробуйте позже."
    
#     url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
#     headers = {
#         'Content-Type': 'application/json',
#         'Accept': 'application/json',
#         'Authorization': f'Bearer {access_token}'
#     }
    
#     messages = [
#         {
#             "role": "system",
#             "content": (
#                 "Ты помощник для проектов VK Education. Отвечай кратко (1-2 предложения), "
#                 "используя только информацию с официального сайта VK Education. "
#                 "Будь дружелюбным и полезным. Если вопрос не связан с образовательными проектами VK, "
#                 "вежливо предложи посетить официальный сайт VK Education. "
#                 "Не упоминай, что ты ИИ-модель. Используй эмодзи для выразительности."
#             )
#         },
#         {
#             "role": "user",
#             "content": question
#         }
#     ]
    
#     data = {
#         "model": "GigaChat",
#         "messages": messages,
#         "temperature": 0.7,
#         "max_tokens": 200
#     }
    
#     try:
#         # Отключаем проверку SSL для этого запроса
#         response = requests.post(
#             url, 
#             headers=headers, 
#             json=data, 
#             timeout=15,
#             verify=False  # ОТКЛЮЧАЕМ ПРОВЕРКУ SSL
#         )
        
#         if response.status_code == 401:
#             logger.warning("Токен недействителен. Пробуем обновить...")
#             if get_gigachat_token():
#                 headers['Authorization'] = f'Bearer {access_token}'
#                 response = requests.post(
#                     url, 
#                     headers=headers, 
#                     json=data, 
#                     timeout=15,
#                     verify=False  # ОТКЛЮЧАЕМ ПРОВЕРКУ SSL
#                 )
#             else:
#                 return "Ошибка авторизации. Попробуйте позже."
                
#         if response.status_code == 200:
#             result = response.json()
#             return result['choices'][0]['message']['content']
#         else:
#             logger.error(f"Ошибка API GigaChat: {response.status_code}, {response.text}")
#             return None
            
#     except requests.exceptions.Timeout:
#         logger.warning("Таймаут при запросе к GigaChat API")
#         return None
#     except Exception as e:
#         logger.error(f"Ошибка запроса к GigaChat: {str(e)}")
#         return None

# def get_answer(question):
#     """Генерирует ответ на вопрос пользователя"""
#     if contains_profanity(question):
#         return "⚠️ Пожалуйста, соблюдайте правила общения. Недопустимо использовать нецензурную лексику."
    
#     if is_closed_question(question):
#         positive_keywords = ["можно", "возможно", "есть", "будет", "разрешено", "доступно", "допустимо"]
#         question_lower = question.lower()
#         if any(keyword in question_lower for keyword in positive_keywords):
#             return "✅ Да."
#         else:
#             return "❌ Нет."
    
#     if question in FAQ:
#         return FAQ[question]
    
#     question_lower = question.lower()
#     for key, answer in FAQ.items():
#         if question_lower in key.lower():
#             return answer
    
#     giga_response = ask_gigachat(question)
#     if giga_response:
#         return giga_response
    
#     return f"🤔 Я не нашел ответ на ваш вопрос. Посетите официальный сайт VK Education для получения информации: {VK_EDU_LINK}"

# def main():
#     vk_session = vk_api.VkApi(token=TOKEN)
#     vk = vk_session.get_api()
#     longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    
#     logger.info("Бот VK Education запущен!")
#     logger.info("Ожидание сообщений...")
    
#     if not get_gigachat_token():
#         logger.error("Не удалось получить токен GigaChat при запуске. Бот будет работать без GigaChat.")
    
#     keyboard = create_keyboard()
    
#     for event in longpoll.listen():
#         if event.type == VkBotEventType.MESSAGE_NEW:
#             msg = event.object.message
#             user_id = msg['from_id']
#             text = msg['text']
#             current_time = datetime.datetime.now().strftime("%H:%M:%S")
            
#             logger.info(f"[{current_time}] Сообщение от {user_id}: {text}")
            
#             if text.lower() in ["помощь", "меню", "клавиатура", "start"]:
#                 vk.messages.send(
#                     user_id=user_id,
#                     message="👋 Привет! Я бот VK Education. Выберите вопрос из меню:",
#                     keyboard=keyboard,
#                     random_id=0
#                 )
#                 continue
            
#             if text == "Другой вопрос":
#                 response = "❓ Задайте ваш вопрос текстом, и я постараюсь помочь!"
#                 vk.messages.send(
#                     user_id=user_id,
#                     message=response,
#                     keyboard=keyboard,
#                     random_id=0
#                 )
#                 continue
            
#             response = get_answer(text)
            
#             vk.messages.send(
#                 user_id=user_id,
#                 message=response,
#                 keyboard=keyboard,
#                 random_id=0
#             )
#             logger.info(f"[{current_time}] Отправлен ответ")

# if __name__ == '__main__':
#     main()

