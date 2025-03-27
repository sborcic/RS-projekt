from fastapi import APIRouter,FastAPI, HTTPException, Query
from models1 import Poruka
#from typing import List, Literal, Optional

router = APIRouter(prefix=("/poruka"))  

db_poruke=[]

@router.post("/", response_model=Poruka)
def posalji_poruku(poruka: Poruka):
    db_poruke.append(poruka)
    return poruka

@router.get("/")
def dohvati_poruku(primatelj: str):
    db_poruka_primatelj= []
    
    for poruka in db_poruke:
        if poruka.korisnik_primatelj == primatelj:
            db_poruka_primatelj.append(poruka)
            
    if not db_poruka_primatelj:
        raise HTTPException(status_code=404, detail="Za korisnika ovog korisničkog imena nema nove poruke!")
    
    return {"primatelj": primatelj, "poruka": db_poruka_primatelj}