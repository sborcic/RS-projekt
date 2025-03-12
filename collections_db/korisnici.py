from fastapi import FastAPI, HTTPException
from models import Korisnik, Korisnik_prijava, Korisnik_profil
from typing import List

app = FastAPI()

korisnici_db=[]

korisnici_db_profil=[]

@app.post("/korisnik_registracija", response_model=Korisnik)
def korisnik_unos(korisnik: Korisnik):
    korisnici_db.append(korisnik)
    print(korisnici_db)
    return korisnik

@app.post("/korisnik_profil", response_model=Korisnik_profil)
def korisnik_unos(profil_korisnika: Korisnik_profil):
    korisnici_db_profil.append(profil_korisnika)
    print(profil_korisnika)
    return profil_korisnika

@app.post("/korisnik_prijava", response_model=Korisnik_prijava)
def korisnik_unos(prijava_korisnika: Korisnik_prijava):
        for korisnik in korisnici_db:
            if korisnik.email==prijava_korisnika.email and korisnik.lozinka==prijava_korisnika.lozinka:
                return korisnik
        raise HTTPException(status_code=401, detail="Upisan je pogrešan email ili lozinka!")
    
@app.get("/korisnik_pretraživanje_korisničkog/{korisnicko_ime}")
def korisnicko_ime(korisnicko_ime: str):
    for korisnik in korisnici_db:
        if korisnik.korisnicko_ime == korisnicko_ime:
            return korisnik
    raise HTTPException(status_code=401, detail="Korisnik nije pronađen!")

@app.delete("/korisnik_brisanje/")
def korisnik_brisanje(korisnicko_ime: str, lozinka: str):
    for korisnik in korisnici_db:
        if korisnik.korisnicko_ime==korisnicko_ime and korisnik.lozinka==lozinka:
            return {"poruka": f"Podaci za {korisnicko_ime} uspješno obrisani!"}
    
    raise HTTPException(status_code=401, detail="Nemate ovlasti za pristup ovim podacima")
    