from fastapi import APIRouter, FastAPI
from dynamodb import dodavanje_recenzije_dynamo, prikaz_recenzija_dynamo, prikaz_ocjene_dynamo
from models import Recenzija

app = FastAPI()

router = APIRouter(prefix=("/recenzija"))  


@router.post("/", response_model=Recenzija)
def dodavanje_recenzije(recenzija: Recenzija):
      
    return dodavanje_recenzije_dynamo(recenzija)

@router.get("/{korisnik_prima_recenziju}")
def prikaz_recenzije(korisnik_prima_recenziju, korisnik_salje_recenziju):
        
    return prikaz_recenzija_dynamo(korisnik_prima_recenziju, korisnik_salje_recenziju)

@router.get("/ocjena/{korisnik_prima_recenziju}")
def prikaz_ocjene(korisnik_prima_recenziju: str):
        
    return prikaz_ocjene_dynamo(korisnik_prima_recenziju) 

app.include_router(router)

