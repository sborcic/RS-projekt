from fastapi import APIRouter, HTTPException
from routers.models import Recenzija
from dynamodb.dynamodb import dodavanje_recenzije_dynamo, prikaz_recenzija_dynamo, prikaz_ocjene_dynamo


router = APIRouter(prefix=("/recenzija"))  

db_recenzije_sa_ocjenama={}

@router.post("/", response_model=Recenzija)
def dodavanje_recenzije(recenzija: Recenzija):
      
    return dodavanje_recenzije_dynamo(recenzija)

@router.get("/{korisnik_prima_recenziju}")
def prikaz_recenzije(korisnik_prima_recenziju):
        
    return prikaz_recenzija_dynamo(korisnik_prima_recenziju)

@router.get("/ocjena/{korisnik_prima_recenziju}")
def prikaz_ocjene(korisnik_prima_recenziju: str):
        
    return prikaz_ocjene_dynamo(korisnik_prima_recenziju)


