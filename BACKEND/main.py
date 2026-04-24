#Это эндпоинт - конкретный адрес, по которому можно получить доступ к определенной функции приложения.
#Точка запуска приложения, главная задача - настроить FastAPI,
#подключить базу данных и определить маршруты для работы с контактами.



from fastapi import FastAPI, Depends, Body
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import api, schemas
from database import SessionLocal, init_db

#Создаем экземпляр FastAPI, который будет использоваться для определения маршрутов и обработки запросов.
app = FastAPI()
#Проверяет, создана ли база данных при каждом запуске приложения,
#и если нет, то создает ее. Это гарантирует, что база данных всегда будет готова к использованию.
init_db()

app.add_middleware(
    #Разрешаем фронтенду обращаться к бэкенду, даже если они находятся на разных доменах или портах.
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Для нового запроса открывает новую сессию, а когда
#запрос завершен, сессия закрывается. Это обеспечивает правильное управление ресурсами 
#базы данных и предотвращает утечки соединений.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
#get дай мне данные.
#post создай новые данные.
#patch обнови часть данных.
#delete удали данные.

@app.get("/contacts/", response_model=list[schemas.Contact])
#Эндпоинт для получения данных о контактах. 
def read_contacts(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    return api.get_contacts(db=db, skip=skip, limit=limit)

@app.post("/contacts/", response_model=schemas.Contact)
#Эндпоинт для создания нового контакта. Он принимает данные контакта в формате JSON
def create_new_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    create_data = contact.model_dump(exclude_unset=True)
    return api.create_contact(db=db, **create_data)

@app.delete("/contacts/{contact_id}/", response_model=schemas.Contact)
#Эндпоинт для удаления контакта по его ID. 
def delete_contact_route(contact_id: int, db: Session = Depends(get_db)):
    return api.delete_contact(db=db, contact_id=contact_id)

@app.patch("/contacts/{contact_id}/", response_model=schemas.Contact)
#Эндпоинт для обновления данных контакта по его ID.
def update_contact_route(contact_id: int, contact_data: schemas.ContactUpdate, db: Session = Depends(get_db)):
    update_data = contact_data.model_dump(exclude_unset=True)
    return api.update_contact(db=db, contact_id=contact_id, **update_data)

@app.delete("/contacts/", response_model=list[schemas.Contact])
#Эндпоинт для удаления нескольких контактов по списку ID.
# Он принимает список ID в теле запроса и удаляет все соответствующие контакты из базы данных.
def delete_multiple_contacts_route(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    return api.delete_contacts(db=db, ids=ids)