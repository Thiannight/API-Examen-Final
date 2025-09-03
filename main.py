from typing import List, Dict
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

app = FastAPI(title="Phones API")

class Characteristic(BaseModel):
    ram_memory: float = Field(..., description="RAM size")
    rom_memory: float = Field(..., description="ROM/Storage size")

class Phone(BaseModel):
    identifier: str
    brand: str
    model: str
    characteristics: Characteristic

class CharacteristicUpdate(Characteristic):
    pass

_db: Dict[str, Phone] = {}

@app.get("/health", response_class=PlainTextResponse, summary="Health check")
def health() -> str:
    return "Ok"

@app.post(
    "/phones",
    status_code=201,
    response_model=List[Phone],
    summary="Create and persist a list of phones in memory",
)
def create_phones(phones: List[Phone]) -> List[Phone]:
    _db.clear()
    for phone in phones:
        _db[phone.identifier] = phone
    return list(_db.values())

@app.get(
    "/phones",
    response_model=List[Phone],
    summary="Get the list of phones previously saved in memory",
)
def list_phones() -> List[Phone]:
    return list(_db.values())

@app.get(
    "/phones/{id}",
    response_model=Phone,
    responses={404: {"model": dict, "description": "Phone not found"}},
    summary="Get a single phone by its identifier",
)
def get_phone(id: str) -> JSONResponse | Phone:
    phone = _db.get(id)
    if not phone:
        return JSONResponse(
            status_code=404,
            content={"message": f"Le phone fourni avec l’identifiant '{id}' n’existe pas ou n’a pas été trouvé."},
        )
    return phone

@app.put(
    "/phones/{id}/characteristics",
    response_model=Phone,
    responses={404: {"model": dict, "description": "Phone not found"}},
    summary="(BONUS) Update only the characteristics of a phone",
)
def update_characteristics(id: str, payload: CharacteristicUpdate) -> JSONResponse | Phone:
    phone = _db.get(id)
    if not phone:
        return JSONResponse(
            status_code=404,
            content={"message": f"Le phone fourni avec l’identifiant '{id}' n’existe pas ou n’a pas été trouvé."},
        )
    updated = phone.copy(update={"characteristics": payload})
    _db[id] = updated
    return updated
