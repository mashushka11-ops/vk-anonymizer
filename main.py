import os

SECRET_API_KEY = os.getenv("API_KEY", "default-dev-key")

from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
import re

# === 1. ТВОЕ ЯДРО ===
RULES = {
    "email": {
        "pattern": r"([a-zA-Z0-9._%+-]+)(@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
        "replacer": lambda match: match.group(1)[0] + "***" + match.group(2),
    },
    "passport": {
        "pattern": r"(\d{4})\s?(\d{6})",
        "replacer": lambda match: "**** ******",
    },
    "snils": {
        "pattern": r"\d{3}-\d{3}-\d{3}-(\d{2})",
        "replacer": lambda match: "***-***-***-" + match.group(1),
    },
    "name": {
        "pattern": r"([А-ЯЁ][а-яё]+)\s+([А-ЯЁ][а-яё]+)",
        "replacer": lambda match: match.group(1)[0] + ". " + match.group(2)[0] + ".",
    },
    "number": {
        "pattern": r"(\+\d\s\(\d{3}\)\s)\d{3}-\d{2}-(\d{2})",
        "replacer": lambda match: match.group(1) + "***-**-" + match.group(2),
    },
}


class Anonymizer:
    def __init__(self, rules):
        self.rules = rules

    def mask_text(self, text):
        result = text
        for rule_name, rule_data in self.rules.items():
            result = re.sub(rule_data["pattern"], rule_data["replacer"], result)
        return result


engine = Anonymizer(RULES)

# === 2. БЛОК БЕЗОПАСНОСТИ ===
# Задаем наш секретный ключ (в реальных проектах его прячут в переменные окружения)
SECRET_API_KEY = "my-super-secret-key"

# Говорим FastAPI, что мы ждем ключ в заголовке с названием X-API-Key
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


# Функция, которая проверяет ключ
def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == SECRET_API_KEY:
        return api_key_header
    # А вот и та самая ошибка 401 из твоего тестового задания!
    raise HTTPException(
        status_code=401, detail="Отказ в доступе: Неверный или отсутствующий API-ключ"
    )


# === 3. ВЕБ-СЕРВИС ===
app = FastAPI(
    title="Data Anonymizer API",
    description="API для автоматической маскировки чувствительных данных (PII).",
    version="1.0.0",
)


class AnonymizeRequest(BaseModel):
    text: str


class AnonymizeResponse(BaseModel):
    anonymized_text: str


# Обрати внимание на добавленный параметр api_key = Depends(get_api_key)
# Теперь эндпоинт не выполнится, пока не пройдет проверка ключа
@app.post("/api/v1/anonymize", response_model=AnonymizeResponse)
def anonymize_data(request: AnonymizeRequest, api_key: str = Depends(get_api_key)):
    safe_text = engine.mask_text(request.text)
    return AnonymizeResponse(anonymized_text=safe_text)
