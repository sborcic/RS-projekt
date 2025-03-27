from fastapi import FastAPI, HTTPException, Query

from routers.korisnik import router as korisnik
from routers.recenzija import router as recenzija
from routers.kolekcija import router as kolekcija
from routers.poruka import router as poruka

app = FastAPI()

app.include_router(korisnik)

app.include_router(kolekcija)

app.include_router(recenzija)

app.include_router(poruka)

@app.get("/")
def pocetna():
    return {"poruka" : "Početna stranica FastAPI poslužitelja"}