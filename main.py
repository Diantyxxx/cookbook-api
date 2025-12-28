from contextlib import asynccontextmanager
from typing import List, AsyncGenerator
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc, asc

import models
import schemas
from database import engine, get_db


@asynccontextmanager
async def lifespan(_application: FastAPI) -> AsyncGenerator[None, None]:
    """
    Функция жизненного цикла приложения.
    Выполняется при запуске и завершении приложения.

    При запуске:
    - Создает все таблицы в базе данных
    При завершении:
    - Закрывает соединение с базой данных
    """
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(
    lifespan=lifespan,
    title="Cookbook API",
    description="API для управления кулинарной книгой",
    version="1.0.0",
)


@app.post(
    "/recipes/",
    response_model=schemas.RecipeOut,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый рецепт",
    description="Создает новый рецепт в кулинарной книге",
    response_description="Созданный рецепт",
)
async def create_recipe(
    recipe: schemas.RecipeIn, db: AsyncSession = Depends(get_db)
) -> schemas.RecipeOut:
    """
    Создает новый рецепт.

    Параметры:
    - **recipe**: Данные нового рецепта (RecipeIn схема)

    Возвращает:
    - Созданный рецепт со всеми полями, включая ID и счетчик просмотров

    Исключения:
    - HTTP 400: При ошибке валидации данных
    - HTTP 500: При внутренней ошибке сервера
    """
    new_recipe = models.Recipe(**recipe.model_dump())
    db.add(new_recipe)
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при создании рецепта: {str(e)}",
        )
    await db.refresh(new_recipe)
    return schemas.RecipeOut.model_validate(new_recipe)


@app.get(
    "/recipes/",
    response_model=List[schemas.RecipeOut],
    summary="Получить список всех рецептов",
    description="""Возвращает список всех рецептов, отсортированных по популярности.
    Сортировка:
    1. По количеству просмотров (по убыванию)
    2. По времени приготовления (по возрастанию)
    """,
    response_description="Список рецептов с основной информацией",
)
async def get_recipes(db: AsyncSession = Depends(get_db)) -> List[schemas.RecipeOut]:
    """
    Получает список всех рецептов.

    Возвращает:
    - Список рецептов, отсортированный по популярности и времени приготовления
    - Каждый рецепт содержит: ID, название, время приготовления, количество просмотров

    Исключения:
    - HTTP 500: При внутренней ошибке сервера
    """
    query = select(models.Recipe).order_by(
        desc(models.Recipe.views), asc(models.Recipe.cooking_time)
    )
    result = await db.execute(query)
    recipes = result.scalars().all()

    return [schemas.RecipeOut.model_validate(recipe) for recipe in recipes]


@app.get(
    "/recipes/{recipe_id}",
    response_model=schemas.RecipeDetailOut,
    summary="Получить детальную информацию о рецепте",
    description="""Возвращает полную информацию о конкретном рецепте.
     При каждом успешном запросе счетчик просмотров увеличивается на 1.
     """,
    response_description="Детальная информация о рецепте",
)
async def get_recipe(
    recipe_id: int, db: AsyncSession = Depends(get_db)
) -> schemas.RecipeDetailOut:
    """
    Получает детальную информацию о рецепте по его ID.

    Параметры:
    - **recipe_id**: ID рецепта (целое число)

    Возвращает:
    - Полную информацию о рецепте, включая ингредиенты и описание
    - Увеличивает счетчик просмотров на 1

    Исключения:
    - HTTP 404: Если рецепт с указанным ID не найден
    - HTTP 500: При внутренней ошибке сервера
    """
    recipe = await db.get(models.Recipe, recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Рецепт с ID {recipe_id} не найден",
        )

    recipe.views += 1
    try:
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при обновлении счетчика просмотров: {str(e)}",
        )
    await db.refresh(recipe)

    return schemas.RecipeDetailOut.model_validate(recipe)


@app.get(
    "/", summary="Информация о API", description="Основная информация о Cookbook API"
)
async def root():
    """
    Корневой endpoint API.

    Возвращает:
    - Основную информацию о API
    - Ссылки на документацию
    """
    return {
        "message": "Добро пожаловать в Cookbook API!",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "create_recipe": {
                "method": "POST",
                "path": "/recipes/",
                "description": "Создать новый рецепт",
            },
            "get_recipes": {
                "method": "GET",
                "path": "/recipes/",
                "description": "Получить список всех рецептов",
            },
            "get_recipe": {
                "method": "GET",
                "path": "/recipes/{recipe_id}",
                "description": "Получить детальную информацию о рецепте",
            },
        },
    }
