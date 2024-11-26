# Teoria CRUD e FastAPI: Una Guida Completa

## 1. Introduzione al CRUD
CRUD rappresenta le quattro operazioni fondamentali nella gestione dei dati:
- **Create** (Creare): Inserimento di nuovi dati
- **Read** (Leggere): Recupero di dati esistenti
- **Update** (Aggiornare): Modifica di dati esistenti
- **Delete** (Eliminare): Rimozione di dati

### 1.1 Importanza del CRUD
Il modello CRUD è fondamentale perché:
- Fornisce una struttura standardizzata per la manipolazione dei dati
- Semplifica la progettazione delle API
- Facilita la manutenzione del codice
- Migliora la scalabilità dell'applicazione

## 2. FastAPI: Framework Moderno per API

### 2.1 Caratteristiche Principali di FastAPI
- **Velocità**: Prestazioni paragonabili a NodeJS e Go
- **Tipizzazione**: Supporto completo per type hints Python
- **Documentazione Automatica**: Swagger UI e ReDoc integrati
- **Validazione**: Convalida automatica dei dati con Pydantic
- **Asincrono**: Supporto nativo per operazioni asincrone

### 2.2 Struttura Base di un'Applicazione FastAPI
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str = None
    price: float
```

## 3. Implementazione CRUD in FastAPI

### 3.1 Create (POST)
```python
@app.post("/items/")
async def create_item(item: Item):
    """
    Endpoint per creare un nuovo item
    - Accetta dati JSON nel body della richiesta
    - Valida automaticamente i dati usando Pydantic
    - Restituisce l'item creato con status code 201
    """
    return {"status": "created", "item": item}
```

### 3.2 Read (GET)
```python
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    """
    Endpoint per leggere un item esistente
    - Path parameter per l'ID
    - Query parameters opzionali
    - Gestione degli errori 404
    """
    return {"item_id": item_id}

@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    """
    Endpoint per leggere multiple items
    - Supporta paginazione
    - Filtri opzionali
    """
    return {"skip": skip, "limit": limit}
```

### 3.3 Update (PUT/PATCH)
```python
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    """
    Endpoint per aggiornare un item
    - PUT: aggiornamento completo
    - Validazione dei dati aggiornati
    """
    return {"item_id": item_id, "item": item}

@app.patch("/items/{item_id}")
async def partial_update_item(item_id: int, item: Item):
    """
    Endpoint per aggiornamento parziale
    - PATCH: modifica solo alcuni campi
    - Mantiene i campi non specificati
    """
    return {"item_id": item_id, "item": item}
```

### 3.4 Delete (DELETE)
```python
@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """
    Endpoint per eliminare un item
    - Verifica esistenza prima della cancellazione
    - Restituisce status code appropriato
    """
    return {"status": "deleted", "item_id": item_id}
```

## 4. Best Practices e Pattern Comuni

### 4.1 Gestione degli Errori
```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id not found:
        raise HTTPException(
            status_code=404,
            detail="Item non trovato"
        )
    return {"item_id": item_id}
```

### 4.2 Dipendenze e Middleware
```python
from fastapi import Depends

async def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.close()

@app.get("/items/")
async def read_items(db = Depends(get_db)):
    return db.get_items()
```

### 4.3 Validazione con Pydantic
```python
from pydantic import BaseModel, Field
from typing import Optional

class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., gt=0)
    description: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Prodotto Example",
                "price": 29.99,
                "description": "Descrizione opzionale"
            }
        }
```

## 5. Status Code e Risposte HTTP

### 5.1 Codici di Stato Comuni
- **200**: OK (GET, PUT, PATCH riusciti)
- **201**: Created (POST riuscito)
- **204**: No Content (DELETE riuscito)
- **400**: Bad Request (errore client)
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **422**: Unprocessable Entity
- **500**: Internal Server Error

### 5.2 Response Model
```python
from typing import List

class ItemResponse(BaseModel):
    id: int
    name: str
    price: float

@app.get("/items/", response_model=List[ItemResponse])
async def read_items():
    """
    Utilizzando response_model:
    - Filtra automaticamente i dati sensibili
    - Garantisce il formato della risposta
    - Genera documentazione accurata
    """
    return get_items_from_db()
```

## 6. Documentazione e Testing

### 6.1 Documentazione Automatica
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`


