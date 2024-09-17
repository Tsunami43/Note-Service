import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from main import app

# Создаем клиент для тестов
client = TestClient(app)

# Инициализация базы данных
db = Database()


@pytest.mark.asyncio
async def test_create_user():
    """Тест на успешное создание пользователя"""
    user_data = {"username": "testuser", "password": "testpassword"}
    response = client.post("/api/register", json=user_data)
    await db.clear_db()
    assert response.status_code == 200  # Проверяем успешный код ответа
    response_data = response.json()
    assert response_data["username"] == user_data["username"]  # Проверяем данные


@pytest.mark.asyncio
async def test_create_user_missing_password():
    """Тест на создание пользователя без пароля"""
    user_data = {"username": "testuser"}
    response = client.post("/api/register", json=user_data)
    await db.clear_db()
    assert response.status_code == 422  # Должен вернуться код ошибки валидации
