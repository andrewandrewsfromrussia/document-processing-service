## Document Processing Service

#### Сервис на Django + DRF для загрузки документов и автоматической классификации по типу (чек/договор/счёт/акт/неизвестно).
#### Файлы сохраняются, извлекается текст (txt/pdf/docx), далее сервис выставляет категорию и возвращает сообщение вида “Загружен договор”.

### Стек

- Python, Django, Django REST Framework
- PostgreSQL
- Docker, Docker Compose
- OpenAPI (Swagger UI)
- Тесты pytest с покрытием > 75%
- Code style: black + ruff

### Функциональность

- Аутентификация пользователя (требуется для доступа к API документов)
- Загрузка документа (multipart/form-data)
- Автоопределение категории:
- - receipt — чек
- - contract — договор
- - invoice — счёт
- - act — акт
- - other — неизвестный документ
- Просмотр списка загруженных документов текущего пользователя
- Просмотр деталей одного документа текущего пользователя

### Автогенерируемая документация API (OpenAPI/Swagger)

#### Запуск через Docker Compose

1. В корне проекта выполните:
```bash
docker compose up -d --build
```
2. Применить миграции (если не выполняются автоматически):
```bash
docker compose exec backend sh -lc "cd /app && python manage.py migrate"
```
3. Создать суперпользователя (по желанию, для админки):
```bash
docker compose exec backend sh -lc "cd /app && python manage.py createsuperuser"
```
### Переменные окружения

###### Проект использует переменные окружения для БД и настроек Django.
###### Обычно они задаются в docker-compose.yml / .env.

##### Минимальный набор:

- SECRET_KEY
- DEBUG
- ALLOWED_HOSTS
- DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
- CORS (доверенные домены/IP)

##### Настройка выполняется через переменные окружения:

- ##### CORS_ALLOWED_ORIGINS — список origins через запятую.
Пример:
```
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

- ##### CSRF_TRUSTED_ORIGINS — список trusted origins через запятую.
Пример:
```
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
```

- ##### ALLOWED_HOSTS — список хостов через запятую
Пример:
```
ALLOWED_HOSTS=localhost,127.0.0.1
```
##### Документация API (OpenAPI)

### После запуска:

- Swagger UI: http://127.0.0.1:8000/api/docs/

- Schema: http://127.0.0.1:8000/api/schema/

### Основные эндпоинты

- Базовый префикс: /api/
- POST /api/documents/ — загрузка документа (multipart)
- GET /api/documents/ — список документов пользователя
- GET /api/documents/{id}/ — детали документа пользователя

### Пример загрузки (curl)
```
curl -X POST "http://127.0.0.1:8000/api/documents/" \
  -H "Authorization: Token <YOUR_TOKEN>" \
  -F "file=@./samples/dogovor.pdf"
```
### Ответ (пример):
```
{
  "id": "…",
  "message": "Загружен договор",
  "category": "contract",
  "status": "processed"
}
```
## Тесты и покрытие
```
============================================= tests coverage =============================================
----------------------- coverage: platform linux, python 3.13.11-final-0 -----------------------

Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
config/__init__.py             0      0   100%
config/settings.py            27      0   100%
config/urls.py                 7      0   100%
documents/__init__.py          0      0   100%
documents/admin.py             8      0   100%
documents/apps.py              3      0   100%
documents/models.py           50      7    86%   62, 67-69, 74-75, 80
documents/serializers.py      14      0   100%
documents/services.py         52      9    83%   30, 43, 69-70, 73, 79-81, 98
documents/urls.py              5      0   100%
documents/views.py            54     18    67%   19, 35, 38-42, 70, 76-88
-------------------------------------------------------
TOTAL                        220     34    85%

Required test coverage of 75% reached. Total coverage: 84.55%
5 passed in 3.03s
```

### Запуск тестов в Docker (рекомендуется):
```bash
docker compose run --rm backend sh -lc "cd /app && pytest"
```

### PEP8 / Code Style (black + ruff)

#### Проверка (в Docker):
```bash
docker compose run --rm backend sh -lc "cd /app && black . --check && ruff check ."
```

### Автоформатирование и автофиксы:
```bash
docker compose run --rm backend sh -lc "cd /app && black . && ruff check . --fix"
```

### Остановка проекта
```bash
docker compose down
```