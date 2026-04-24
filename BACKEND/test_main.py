#Здесь будут находится тесты.
import pytest
from fastapi.testclient import TestClient
from main import app

#Создаем клиента для тестов
client = TestClient(app)

def test_read_contacts():
    #Тест для проверки получения списка контактов
    response = client.get("/contacts/")
    #Проверяем, что статус ответа 200 (OK) и что возвращается список контактов, даже если он пустой
    assert response.status_code == 200
    #Проверяем, что возвращаемые данные это список, даже если он пустой
    assert isinstance(response.json(), list)
    
def test_create_contact():
    new_contact = {
        "name": "Test User",
        "phone": "1234567890",
        "email": "test@example.com"
    }
    response = client.post("/contacts/", json=new_contact)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "Test User"
    assert "id" in data  #Проверяем, что поле ID существует