from pydantic import BaseModel, ConfigDict, Field


class RecipeBase(BaseModel):
    """Базовая схема для рецепта"""

    title: str = Field(
        ...,
        min_length=3,
        max_length=200,
        description="Название блюда",
        examples=["Яичница-глазунья", "Паста Карбонара"],
    )
    cooking_time: int = Field(
        ...,
        gt=0,
        le=1440,
        description="Время приготовления в минутах",
        examples=[30, 120, 5],
    )


class RecipeIn(RecipeBase):
    """Схема для создания нового рецепта"""

    ingredients: str = Field(
        ...,
        min_length=3,
        description="Список ингредиентов (с новой строки или через запятую)",
        examples=[
            "Спагетти - 400г\nБекон - 200г\nЯйца - 3 шт\n"
            "Пармезан - 100г\nСливки - 100мл",
            "Спагетти - 400г, бекон - 200г, яйца - 3 шт, "
            "пармезан - 100г, сливки - 100мл",
        ],
    )
    description: str = Field(
        ...,
        min_length=3,
        description="Текстовое описание процесса приготовления",
        examples=[
            "1. Отварите спагетти...\n2. Обжарьте бекон...\n3. Смешайте яйца "
            "со сливками и сыром...\n4. Соедините все ингредиенты..."
        ],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Паста Карбонара",
                "cooking_time": 30,
                "ingredients": "Спагетти - 400г\nБекон - 200г\nЯйца - 3 шт\n"
                "Пармезан - 100г\nСливки - 100мл",
                "description": "1. Отварите спагетти...\n"
                "2. Обжарьте бекон...\n"
                "3. Смешайте яйца со сливками и сыром...\n"
                "4. Соедините все ингредиенты...",
            }
        }
    )


class RecipeOut(RecipeBase):
    """Схема для отображения рецепта в списке"""

    recipe_id: int = Field(
        ..., description="Уникальный идентификатор рецепта", examples=[1, 3]
    )
    views: int = Field(
        default=0,
        description="Количество просмотров рецепта",
        examples=[1, 42, 100, 50],
    )

    model_config = ConfigDict(from_attributes=True)


class RecipeDetailOut(RecipeIn):
    """Схема для отображения детальной информации о рецепте"""

    recipe_id: int = Field(
        ..., description="Уникальный идентификатор рецепта", examples=[1, 3]
    )
    views: int = Field(
        default=0,
        description="Количество просмотров рецепта",
        examples=[1, 42, 100, 50],
    )

    model_config = ConfigDict(from_attributes=True)
