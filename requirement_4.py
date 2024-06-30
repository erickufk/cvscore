## Техническое задание на разработку API для сравнения текстов

### Общие требования
- **Цель API**: предоставление функциональности для сравнения текстов с использованием моделей LLM.
- **Пользователи**: система должна обслуживать администраторов и конечных пользователей с разделением прав и возможностей.
- **Безопасность**: использование JWT токенов для аутентификации и HMAC подписей для авторизации запросов.
- **Масштабируемость**: архитектура API должна поддерживать масштабирование для обработки больших объемов запросов.
- **Реализация**: Python и Django. Для управления и настройки API использовать стандартную admin панель Django. Доступ пользователей предполагается по api.
  

### 1. Управление конфигурацией модели (TypeID)
- **Создание TypeID**:
  - Администратор создаёт TypeID с параметрами модели (scale, system, user, model, llm, description).
  - CRUD операции над TypeID выполняются через Django Admin.
  
- **Функции API**:
  - `POST /api/v1/types`: Создание TypeID.
  - `PUT /api/v1/types/{typeid}`: Редактирование TypeID.
  - `DELETE /api/v1/types/{typeid}`: Удаление TypeID.

### 2. Управление API ключами
- **Генерация и управление ключами**:
  - Администратор выдает API ключи, связанные с TypeID.
  - Пользователи могут иметь несколько ключей с разными TypeID.

- **Функции API**:
  - `POST /api/v1/keys`: Создание API ключа.
  - `DELETE /api/v1/keys/{api_key}`: Удаление API ключа.
  - `GET /api/v1/billing/{api_key}`: Получение информации о биллинге и использовании.

### 3. Авторизация пользователя
- **Процесс**:
  - Формирование HMAC подписи с использованием api_key, secret_key, и имени пользователя.
  - Проверка подписи и активности подписки сервером перед выдачей JWT токена.

- **Функции API**:
  - `POST /api/v1/auth`: Авторизация пользователя и выдача JWT токена.

### 4. Работа с текстами
- **Загрузка и сравнение текстов**:
  - Тексты загружаются и сравниваются в формате Base64.
  - Для каждого запроса используются параметры TypeID для формирования запросов к модели LLM.

- **Функции API**:
  - `POST /api/v1/reference`: Загрузка эталонного текста.
  - `POST /api/v1/compare/{reference_id}`: Сравнение загруженного текста с эталонным.

### 5. Дополнительные функции
- **Проверка подписки**:
  - Перед выполнением операций с текстами проверяется статус подписки.

- **Функции API**:
  - `GET /api/v1/subscription/{api_key}`: Проверка статуса подписки.

### Интеграция и безопасность
- **HTTPS**: все запросы к API должны использовать HTTPS для защиты данных.
- **Обновление токенов и мониторинг**: реализация механизмов для обновления токенов и мониторинга активности по API ключам.

### Документация и поддержка
- **Документация API**: создание подробной документации с описанием всех функций, параметров и примеров использования.
- **Поддержка и обработка ошибок**: система должна предоставлять информативные сообщения об ошибках на каждом этапе работы с API.

### 1. Управление конфигурацией модели (TypeID)

#### Бизнес требования:
- **Управление параметрами модели**: Администратор должен иметь возможность создавать, редактировать и удалять конфигурации моделей (TypeID), которые определяют параметры для сравнения текстов через LLM (Large Language Models).
- **Уникальность TypeID**: Каждый TypeID должен быть уникальным и содержать специфические параметры, такие как масштаб, система, пользователь, модель, LLM и описание.
- **Интерфейс управления**: Управление TypeID должно осуществляться через удобный интерфейс администратора на платформе Django.

#### Пример реализации:
```python
from django.http import JsonResponse
from django.views import View
from .models import TypeID
import json

class TypeIDView(View):
    def post(self, request):
        data = json.loads(request.body)
        new_typeid = TypeID.objects.create(
            scale=data['scale'],
            system=data['system'],
            user=data['user'],
            model=data['model'],
            llm=data['llm'],
            description=data.get('description', '')
        )
        return JsonResponse({'typeid': new_typeid.pk, 'status': 'success'}, status=201)

    def put(self, request, typeid):
        data = json.loads(request.body)
        try:
            typeid_instance = TypeID.objects.get(pk=typeid)
            for key, value in data.items():
                setattr(typeid_instance, key, value)
            typeid_instance.save()
            return JsonResponse({'status': 'success'})
        except TypeID.DoesNotExist:
            return JsonResponse({'error': 'TypeID not found'}, status=404)

    def delete(self, request, typeid):
        try:
            typeid_instance = TypeID.objects.get(pk=typeid)
            typeid_instance.delete()
            return JsonResponse({'status': 'success'})
        except TypeID.DoesNotExist:
            return JsonResponse({'error': 'TypeID not found'}, status=404)
```

### 2. Управление API ключами

#### Бизнес требования:
- **Выдача и управление API ключами**: Предоставить администраторам возможность генерировать, выдавать и отзывать API ключи, которые связаны с конкретными TypeID.
- **Множественность ключей**: Один пользователь может иметь несколько API ключей, каждый из которых привязан к различным TypeID.
- **Безопасность**: Обеспечить безопасный механизм аутентификации и авторизации, защищая ключи и ассоциированные с ними данные.

#### Пример реализации:
```python
from django.http import JsonResponse
from django.views import View
from .models import APIKey, User, TypeID
import json

class CreateAPIKeyView(View):
    def post(self, request):
        data = json.loads(request.body)
        user_id = data['user_id']
        typeid_id = data['typeid_id']
        llm_api_key = data['llm_api_key']  # Обязательный параметр ключ api от LLM

        try:
            user = User.objects.get(id=user_id)
            typeid = TypeID.objects.get(id=typeid_id)
            new_api_key = APIKey.objects.create(
                user=user,
                key=generate_unique_api_key(),
                secret_key=generate_secret(),
                typeid=typeid,
                llm_api_key=llm_api_key,
                tokens_remaining=1000000,
                token_limit=10000,
                status='active'
            )
            return JsonResponse({'api_key': new_api_key.key, 'status': 'success'}, status=201)
        except (User.DoesNotExist, TypeID.DoesNotExist) as e:
            return JsonResponse({'error': str(e)}, status=404)

def generate_unique_api_key():
    # Генерация уникального API ключа
    import uuid
    return str(uuid.uuid4())

def generate_secret():
    # Генерация секретного ключа
    import os
    return os.urandom(32).hex()

```

from django.db import models

class APIKey(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    typeid = models.ForeignKey('TypeID', on_delete=models.CASCADE)
    llm_api_key = models.CharField(max_length=255)  # API ключ для LLM
    tokens_remaining = models.IntegerField(default=10000)
    token_limit = models.IntegerField(default=10000)
    status = models.CharField(max_length=10, choices=[('active', 'Active'), ('inactive', 'Inactive')])

    def __str__(self):
        return f"{self.user.username} - {self.key}"



### 3. Авторизация пользователя
Функции охватывают процесс авторизации пользователя, начиная с генерации подписи на клиентской стороне, 
отправки запроса и его обработки на сервере, включая проверку подписи и статуса подписки.

#### Бизнес требования:
- **Безопасность**: Использовать HMAC-SHA256 для генерации подписей, чтобы обеспечить безопасную авторизацию пользователя.
- **JWT токены**: После успешной верификации подписи и подписки пользователя, сервер должен генерировать JWT токен, который будет использоваться для дальнейшей аутентификации запросов.
- **Многоуровневая проверка**: Помимо проверки подписи, необходима проверка статуса подписки пользователя, прежде чем предоставлять доступ к API.

#### Функции клиента для авторизации:
```python
import hashlib
import hmac
import requests

def generate_hmac_signature(api_key, secret_key, username):
    """Генерация HMAC-SHA256 подписи."""
    message = f"{api_key}.{username}"
    signature = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).hexdigest()
    return signature

def send_auth_request(api_key, username, secret_key):
    """Отправка запроса на авторизацию."""
    signature = generate_hmac_signature(api_key, secret_key, username)
    auth_data = {
        "api_key": api_key,
        "signature": signature
    }
    response = requests.post("https://yourapi.com/api/v1/auth", json=auth_data)
    if response.status_code == 200:
        return response.json()['token']
    else:
        return None
```

#### Функции сервера для обработки запросов на авторизацию:
```python
from django.http import JsonResponse
from .models import APIKey
import jwt
import datetime

def validate_hmac_signature(api_key, signature, username):
    """Проверка HMAC подписи."""
    try:
        api_key_obj = APIKey.objects.get(key=api_key)
        secret_key = api_key_obj.secret_key
        expected_signature = hmac.new(secret_key.encode(), f"{api_key}.{username}".encode(), hashlib.sha256).hexdigest()
        return signature == expected_signature
    except APIKey.DoesNotExist:
        return False

def handle_auth_request(request):
    """Обработка запроса на авторизацию."""
    api_key = request.data.get("api_key")
    signature = request.data.get("signature")
    username = request.data.get("username")

    if validate_hmac_signature(api_key, signature, username):
        if check_subscription(api_key):  # Допустим, у нас есть функция для проверки подписки
            token = jwt.encode({
                "api_key": api_key,
                "username": username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)  # срок действия токена - 24 часа
            }, 'your_secret_key', algorithm="HS256")
            return JsonResponse({"token": token}, status=200)
        else:
            return JsonResponse({"error": "Subscription inactive"}, status=403)
    else:
        return JsonResponse({"error": "Invalid authentication"}, status=401)

def check_subscription(api_key):
    """Проверка активности подписки."""
    try:
        api_key_obj = APIKey.objects.get(key=api_key)
        return api_key_obj.subscription.is_active
    except APIKey.DoesNotExist:
        return False
```
### 4. Работа с текстами
Блок описывает работу с текстами в системе, включая загрузку текстов и их сравнение с использованием мод

#### Бизнес требования:
- **Поддержка множественных форматов**: API должен поддерживать загрузку и обработку текстовых файлов в форматах Word, TXT и PDF.
- **Сохранение и сравнение текстов**: Пользователи могут загружать эталонный текст и сравнивать его с другими текстами, предоставляя файлы в поддерживаемых форматах.
- **Авторизация и безопасность**: Доступ к функциям работы с текстами должен требовать предоставления валидного JWT токена.
- **Обработка и анализ текстов**: Система должна использовать параметры LLM (из TypeID), связанные с API ключом пользователя, для анализа и сравнения текстов.
- **Адаптивность к различным провайдерам LLM**: В зависимости от указанного в TypeID провайдера LLM (например, OpenAI или Gemini), система должна адаптировать запросы и обработку данных.

#### Описание работы функций:
1. **Загрузка эталонного текста**:
   - Пользователь отправляет файл и JWT токен. Сервер декодирует файл, извлекает текст и сохраняет его в базе данных вместе с связанным API ключом.
   - Поддерживаемые форматы: Word (.docx), TXT (.txt), PDF (.pdf).

2. **Сравнение с эталонным текстом**:
   - Пользователь отправляет файл для сравнения и ID эталонного текста вместе с JWT токеном.
   - Сервер извлекает эталонный текст, связанный TypeID и сравнивает его с предоставленным текстом, используя настройки LLM для получения анализа сходств и различий.

#### Функции работы с текстами:

##### Загрузка и декодирование файлов:
```python
import textract
from django.http import JsonResponse

def decode_file(file_path):
    """Декодирование текста из файла, поддерживающее различные форматы."""
    text = textract.process(file_path)
    return text.decode('utf-8')
```

##### Загрузка эталонного текста:
```python
from django.views import View
from .models import Text, APIKey
import jwt

class UploadReferenceTextView(View):
    def post(self, request):
        token = request.headers.get('Authorization', '').split(' ')[1]
        api_key_details = jwt.decode(token, 'your_secret_key', algorithms=["HS256"])
        api_key = api_key_details['api_key']

        file = request.FILES['file']
        file_path = handle_file_upload(file)  # Функция для сохранения файла на сервере
        text = decode_file(file_path)

        # Сохранение эталонного текста
        reference_text = Text.objects.create(api_key_id=api_key, text=text)
        return JsonResponse({'reference_id': reference_text.id}, status=201)
```

##### Сравнение текстов:
```python
class CompareTextView(View):
    def post(self, request, reference_id):
        token = request.headers.get('Authorization', '').split(' ')[1]
        api_key_details = jwt.decode(token, 'your_secret_key', algorithms=["HS256"])
        api_key = api_key_details['api_key']

        file = request.FILES['file']
        file_path = handle_file_upload(file)
        compare_text = decode_file(file_path)

        try:
            api_key_obj = APIKey.objects.get(key=api_key)
            reference_text = Text.objects.get(id=reference_id, api_key=api_key_obj)
            typeid = api_key_obj.typeid
        except (Text.DoesNotExist, APIKey.DoesNotExist):
            return JsonResponse({'error': 'Reference text or API key not found'}, status=404)

        # Сравнение текстов
        similarity_report = compare_texts_llm(reference_text.text, compare_text, typeid)
        return JsonResponse({'report': similarity_report}, status=200)
```

def update_token_usage(api_key, cost=1):
    """Обновление использования токенов при каждом запросе."""
    try:
        api_key_obj = APIKey.objects.get(key=api_key)
        if api_key_obj.tokens_remaining >= cost:
            api_key_obj.tokens_remaining -= cost
            api_key_obj.save()
            return True
        else:
            return False
    except APIKey.DoesNotExist:
        return False


###  функция compare_texts_llm

```python
def compare_texts_llm(reference_text, compare_text, typeid, api_key):
    """Функция для сравнения текстов с использованием LLM на основе параметров TypeID."""
    # Проверка и обновление токенов
    if not update_token_usage(api_key):
        return "Token limit reached. Subscription renewal required."

    system = typeid.system
    user = typeid.user
    model = typeid.model
    llm_provider = typeid.llm

    if llm_provider == 'openai':
        from openai import ChatCompletion
        client = OpenAI()
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system + reference_text},
                {"role": "user", "content": user + compare_text}
            ]
        )
        return completion.choices[0].message['content']

    elif llm_provider == 'gemini':
        import genai
        model = genai.GenerativeModel('gemini-pro')
        request = f"{system}{reference_text} {user}{compare_text}"
        try:
            response = model.generate_content(request)
            return response['result']
        except Exception as e:
            return str(e)

    else:
        return "Unsupported LLM provider"

```

### 5. Дополнительные функции

#### Бизнес требования:
- **Проверка подписки и токенов**: API должен включать механизмы для проверки статуса подписки и количества оставшихся токенов перед предоставлением доступа к функциям сравнения текстов. Это обеспечивает, что доступ к функционалу ограничен не только активностью подписки, но и доступным количеством токенов.
- **Ограничение доступа при исчерпании токенов**: Если количество токенов падает ниже установленного порога (например, 500 токенов), доступ к определенным функциям должен быть ограничен, что поможет контролировать израсходование ресурсов.
- **Динамическое управление подписками и токенами**: API должен поддерживать возможности динамического обновления статуса подписки и количества токенов через административный интерфейс или автоматические системные вызовы, включая интеграцию с системами биллинга.

#### Описание работы функций:
1. **Проверка подписки и токенов**:
   - Перед выполнением основных операций, таких как загрузка или сравнение текстов, система должна проверять не только статус подписки, но и количество оставшихся токенов. Это обеспечивает двойную проверку доступа к ресурсам.
   - Функция проверки должна быть интегрирована в каждый запрос к API для выполнения операций, связанных с текстами.

2. **Ответы API при ошибках подписки или исчерпании токенов**:
   - В случае обнаружения неактивной подписки или если количество токенов оказывается ниже установленного порога, API должен возвращать ошибку с соответствующим статусным кодом (403 Forbidden или 429 Too Many Requests).
   - Сообщения об ошибке должны четко указывать на причину ограничения доступа, будь то истечение срока подписки или недостаточное количество токенов.

#### Функции обработки подписок и токенов:
Интеграция с биллингом и управлением подписок:
Для обновления лимитов токенов и управления подписками, администраторы должны иметь возможность изменять лимиты через административный интерфейс или через интегрированную систему биллинга. Это может быть реализовано через дополнительные административные функции в Django Admin или через API, предоставляемый системой биллинга.

Изменения в административном интерфейсе:
python
Copy code
from django.contrib import admin
from .models import APIKey

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['user', 'key', 'typeid', 'llm_api_key', 'tokens_remaining', 'token_limit', 'status']
    fields = ['user', 'key', 'secret_key', 'typeid', 'llm_api_key', 'tokens_remaining', 'token_limit', 'status']
	
##### Проверка статуса подписки и токенов:
```python
def enforce_subscription_and_tokens(request):
    """Миддлваре для проверки подписки и токенов перед выполнением запросов."""
    api_key = request.headers.get('X-API-Key')
    api_key_obj = APIKey.objects.get(key=api_key)
    if not api_key_obj or not api_key_obj.subscription.is_active:
        return JsonResponse({'error': 'Subscription is inactive or expired'}, status=403)

    if api_key_obj.tokens_remaining < 500:
        return JsonResponse({'error': 'Token limit reached. Subscription renewal required.'}, status=429)

    # Обновление использования токенов
    if not update_token_usage(api_key):
        return JsonResponse({'error': 'Insufficient tokens available.'}, status=429)

    return None
```

Это обновление учитывает проверку токенов в дополнение к статусу подписки, что позволяет более тщательно контролировать доступ к ресурсам API и обеспечивать соответствие использования услугам, оплаченным пользователем.


### Дополнительные замечания:

1. **Обработка ошибок**:
   - Необходимо добавить обработку ошибок для каждого из вызовов LLM, чтобы предотвратить сбои приложения из-за возможных исключений при генерации контента.

2. **Тестирование**:
   - Проверьте форматы возвращаемых данных, так как предположения о структуре ответа могут отличаться.

3. **Хранение API ключей для LMM**:
   - Хранение ключей для LLM в файле env.


База данных должна обеспечивать хранение данных о пользователях, API ключах, конфигурациях моделей (TypeID), текстах для сравнения, и информации о подписках. Использование PostgreSQL обеспечит необходимую гибкость и масштабируемость. Предлагаемая структура базы данных:

### Таблицы базы данных:

1. **Users**
   - **id** (PK)
   - **username** (VARCHAR)
   - **email** (VARCHAR)
   - **hashed_password** (VARCHAR)
   - **created_at** (TIMESTAMP)
   - **updated_at** (TIMESTAMP)

2. **APIKeys**
   - **id** (PK)
   - **user_id** (FK to Users)
   - **key** (VARCHAR) - сам API ключ
   - **secret_key** (VARCHAR) - секретный ключ для HMAC
   - **typeid_id** (FK to TypeIDs)
   - **created_at** (TIMESTAMP)
   - **updated_at** (TIMESTAMP)
   - **status** (ENUM: 'active', 'inactive') - статус ключа
   - **tokens_remaining (INTEGER) - количество оставшихся токенов.
   - **token_limit (INTEGER) - лимит токенов, обновляемый через систему биллинга или административный интерфейс.
   - **llm_api_key (VARCHAR) - API ключ, используемый для взаимодействия с сервисами LLM.


3. **TypeIDs**
   - **id** (PK)
   - **scale** (VARCHAR) - параметр масштабирования модели
   - **system** (TEXT) - системные настройки
   - **user** (TEXT) - пользовательские настройки
   - **model** (VARCHAR) - модель LLM
   - **llm** (VARCHAR) - провайдер LLM (например, OpenAI, Gemini)
   - **description** (TEXT) - описание конфигурации
   - **created_at** (TIMESTAMP)
   - **updated_at** (TIMESTAMP)

4. **Texts**
   - **id** (PK)
   - **api_key_id** (FK to APIKeys)
   - **text** (TEXT) - содержимое текста
   - **created_at** (TIMESTAMP)
   - **updated_at** (TIMESTAMP)

5. **Subscriptions**
   - **id** (PK)
   - **api_key_id** (FK to APIKeys)
   - **type** (VARCHAR) - тип подписки
   - **start_date** (DATE)
   - **end_date** (DATE)
   - **status** (ENUM: 'active', 'inactive') - статус подписки

6. **Logs** (опционально)
   - **id** (PK)
   - **api_key_id** (FK to APIKeys)
   - **action** (TEXT) - описание действия
   - **timestamp** (TIMESTAMP) - время действия
   - **details** (JSON) - детали действия в формате JSON

### Взаимодействие таблиц:

- **Users** хранит информацию о пользователях системы.
- **APIKeys** связана с **Users** и **TypeIDs**, управляет ключами доступа к API, привязанными к конкретным пользователям и конфигурациям моделей.
- **TypeIDs** содержит параметры конфигураций для различных моделей машинного обучения, используемых в API.
- **Texts** связана с **APIKeys**, хранит тексты, загруженные пользователями для сравнения.
- **Subscriptions** связана с **APIKeys**, управляет информацией о подписках пользователей на сервисы.
- **Logs** (опционально) может использоваться для аудита и мониторинга действий в системе.

Эта структура позволяет поддерживать гибкую работу API, обеспечивая надёжное разграничение доступа и управление ресурсами.
