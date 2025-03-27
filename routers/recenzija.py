from fastapi import APIRouter,FastAPI, HTTPException, Query
from models1 import Korisnik, Korisnik_prijava, Korisnik_profil, Recenzija, Korisnik_pretraga, Poruka
from typing import List, Literal, Optional

router = APIRouter(prefix=("/recenzija"))  

db_recenzije_sa_ocjenama={}

@router.post("/", response_model=Recenzija)
def dodavanje_recenzije(recenzija: Recenzija):
    
    if not recenzija.korisnik:
        raise HTTPException(status_code=400, detail="Korisnik ne postoji ili je krivo uneseno korisničko ime!")
    
    if recenzija.korisnik not in db_recenzije_sa_ocjenama:
        db_recenzije_sa_ocjenama[recenzija.korisnik] = []
        
    db_recenzije_sa_ocjenama[recenzija.korisnik].append(recenzija)
   
    return recenzija

@router.get("/{korisnik}")
def prikaz_recenzije(korisnik:str):
    if korisnik not in db_recenzije_sa_ocjenama:
        raise HTTPException(status_code=404, detail= "Ovaj korisnik nije ostavio recenziju ili ne postoji u bazi!")
    
    return db_recenzije_sa_ocjenama

@router.get("/ocjena/{korisnik}")
def prikaz_ocjene(korisnik: str):
    if korisnik not in db_recenzije_sa_ocjenama:
        raise HTTPException(status_code=404, detail="Korisnik toga naziva nije ocijenjen ili ne postoji!")
    
    prosjek=sum(recenzija.ocjena for recenzija in db_recenzije_sa_ocjenama[korisnik])/len(db_recenzije_sa_ocjenama[korisnik])
    
    return {"korisnik": korisnik, "ocjena": round(prosjek, 2)}
