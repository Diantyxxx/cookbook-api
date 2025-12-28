# Cookbook API

FastAPI приложение для управления кулинарной книгой.

## Технологии
- FastAPI
- SQLAlchemy 2.0
- SQLite (aiosqlite)
- Pydantic v2

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone <ваш-репозиторий>
cd cookbook-api
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Запустите приложение:
```bash
uvicorn main:app --reload
```

4. Откройте документацию:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
