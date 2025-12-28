# Cookbook API

![CI](https://github.com/Diantyxxx/cookbook-api/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)

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
