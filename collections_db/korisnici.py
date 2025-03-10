from fastapi import FastAPI
from models import Korisnik
from typing import List

app = FastAPI()

@app.post("/registracija_korisnika", response_model=Korisnik)
def korisnik_unos(korisnik: Korisnik):
    return korisnik