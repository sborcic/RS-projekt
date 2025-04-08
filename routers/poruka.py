from fastapi import APIRouter, HTTPException
from models1 import Poruka
from dynamodb.dynamodb import dohvati_poruku_dynamo, posalji_poruku_dynamo

router = APIRouter(prefix=("/poruka"))  

db_poruke=[]

@router.post("/", response_model=Poruka)
def posalji_poruku(poruka: Poruka):
    return posalji_poruku_dynamo(poruka)

@router.get("/")
def dohvati_poruku(primatelj: str):
    
    return dohvati_poruku_dynamo(primatelj)
   