from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_unauthorized_access():
    # Обе эти строки сдвинуты ровно на 4 пробела вправо
    response = client.post(
        "/api/v1/anonymize", json={"text": "Мой паспорт 1234 567890"}
    )
    assert response.status_code == 401


def test_successful_anonymization():
    # 1. Задаем правильный ключ, который мы прописали в main.py
    headers = {"X-API-Key": "my-super-secret-key"}

    # 2. Отправляем запрос с текстом и ключом доступа
    response = client.post(
        "/api/v1/anonymize", headers=headers, json={"text": "Мой паспорт 1234 567890"}
    )

    # 3. Убеждаемся, что сервер нас пустил (статус 200 ОК)
    assert response.status_code == 200

    # 4. Убеждаемся, что ответ содержит правильно замаскированный текст
    assert response.json()["anonymized_text"] == "Мой паспорт **** ******"
