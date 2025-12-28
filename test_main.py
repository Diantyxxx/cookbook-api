from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_root():
    """Тест корневого endpoint'а"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Добро пожаловать в Cookbook API!"
    assert "docs" in data
    assert "endpoints" in data


def test_get_recipes():
    """Тест получения списка рецептов"""
    response = client.get("/recipes/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_recipe_not_found():
    """Тест получения несуществующего рецепта"""
    response = client.get("/recipes/999999")
    assert response.status_code == 404
    assert "не найден" in response.json()["detail"]


def test_create_recipe():
    """Тест создания рецепта"""
    recipe_data = {
        "title": "Тестовый рецепт",
        "cooking_time": 30,
        "ingredients": "Тестовые ингредиенты",
        "description": "Тестовое описание",
    }

    response = client.post("/recipes/", json=recipe_data)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == recipe_data["title"]
    assert data["cooking_time"] == recipe_data["cooking_time"]
    assert "recipe_id" in data
    assert "views" in data
    assert data["views"] == 0


def test_create_recipe_validation_error():
    """Тест валидации данных при создании рецепта"""
    response = client.post(
        "/recipes/",
        json={
            "title": "Тестовый",
            "cooking_time": -5,  # Отрицательное время
            "ingredients": "Ингредиенты",
            "description": "Описание",
        },
    )
    assert response.status_code == 422
    assert "cooking_time" in response.json()["detail"][0]["loc"]


def test_create_recipe_missing_fields():
    """Тест создания рецепта с отсутствующими полями"""
    response = client.post(
        "/recipes/",
        json={
            "title": "Неполный рецепт"
            # Отсутствуют обязательные поля
        },
    )
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"


def test_get_recipe_and_increment_views():
    """Тест, что просмотры увеличиваются при получении рецепта"""
    recipe_data = {
        "title": "Рецепт для теста просмотров",
        "cooking_time": 15,
        "ingredients": "Ингредиенты",
        "description": "Описание",
    }
    create_response = client.post("/recipes/", json=recipe_data)
    recipe_id = create_response.json()["recipe_id"]

    # Получаем рецепт первый раз
    response1 = client.get(f"/recipes/{recipe_id}")
    assert response1.status_code == 200
    views1 = response1.json()["views"]

    # Получаем рецепт второй раз
    response2 = client.get(f"/recipes/{recipe_id}")
    assert response2.status_code == 200
    views2 = response2.json()["views"]

    # Проверяем, что счетчик увеличился
    assert views2 == views1 + 1


def test_sorting_order():
    """Тест правильности сортировки рецептов"""
    recipes = [
        {
            "title": "Рецепт 1",
            "cooking_time": 30,
            "ingredients": "ingredients",
            "description": "description",
        },
        {
            "title": "Рецепт 2",
            "cooking_time": 15,
            "ingredients": "ingredients",
            "description": "description",
        },
        {
            "title": "Рецепт 3",
            "cooking_time": 45,
            "ingredients": "ingredients",
            "description": "description",
        },
        {
            "title": "Рецепт 4",
            "cooking_time": 60,
            "ingredients": "ingredients",
            "description": "description",
        },
    ]

    created_ids = []

    for recipe in recipes:
        response = client.post("/recipes/", json=recipe)
        assert response.status_code == 201
        created_ids.append(response.json()["recipe_id"])

    # ДОБАВЛЯЕМ ПРОСМОТРЫ для проверки сортировки
    client.get(f"/recipes/{created_ids[0]}")
    client.get(f"/recipes/{created_ids[0]}")
    client.get(f"/recipes/{created_ids[2]}")

    # Получаем список
    response = client.get("/recipes/")
    assert response.status_code == 200
    recipes_list = response.json()

    # Проверяем, что список не пустой
    assert len(recipes_list) >= len(recipes)

    # Проверяем структуру каждого рецепта в списке
    for recipe in recipes_list:
        assert "recipe_id" in recipe
        assert "title" in recipe
        assert "cooking_time" in recipe
        assert "views" in recipe
        assert "ingredients" not in recipe
        assert "description" not in recipe

    recipes_list_time_without_views = []
    recipes_list_views = []
    for recipe in recipes_list:
        if recipe["views"] == 0:
            recipes_list_time_without_views.append(recipe["cooking_time"])
        else:
            recipes_list_views.append(recipe["views"])

    assert recipes_list_views == sorted(
        recipes_list_views, reverse=True
    ), f"Просмотры должны быть отсортированы по убыванию. Получено: {recipes_list_views}"

    assert recipes_list_time_without_views == sorted(
        recipes_list_time_without_views
    ), f"Время приготовления при 0 просмотрах должно быть отсортировано по возрастанию. Получено: {recipes_list_time_without_views}"


def test_recipe_detail_contains_all_fields():
    """Тест, что детальная информация содержит все поля"""
    recipe_data = {
        "title": "Тестовый рецепт",
        "cooking_time": 30,
        "ingredients": "Ингредиенты\nсписок",
        "description": "Подробное описание",
    }
    create_response = client.post("/recipes/", json=recipe_data)
    recipe_id = create_response.json()["recipe_id"]

    # Получаем детальную информацию
    response = client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 200

    data = response.json()
    # Проверяем что есть все поля (включая те, которых нет в списке)
    assert "recipe_id" in data
    assert "title" in data
    assert "cooking_time" in data
    assert "ingredients" in data  # В детальной информации должно быть!
    assert "description" in data  # В детальной информации должно быть!
    assert "views" in data
    assert data["ingredients"] == recipe_data["ingredients"]
    assert data["description"] == recipe_data["description"]
