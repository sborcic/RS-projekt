from fastapi import FastAPI, HTTPException, Query
from models import Korisnik, Korisnik_prijava, Korisnik_profil, Recenzija, Korisnik_pretraga
from typing import List, Literal, Optional
import re

app = FastAPI()

korisnici_db=[]

korisnici_db_profil=[]

@app.post("/korisnik_registracija",response_model=Korisnik)
def korisnik_unos(korisnik: Korisnik):
   
    for svaki_korisnik in korisnici_db:
        if (svaki_korisnik.korisnicko_ime == korisnik.korisnicko_ime) or (svaki_korisnik.email == korisnik.email):
            raise HTTPException(status_code=400, detail="Korisnik s tim korisničkim imenom ili emailom već postoji!")

    specijalni_znakovi = r"[!\"#$%&/()=?*]"

    if not re.search(specijalni_znakovi, korisnik.lozinka):
        raise HTTPException(status_code=400, detail="Lozinka ne sadrži specijalni znak!")
    
    korisnik.korisnik_ID= len(korisnici_db)+1    
       
    korisnici_db.append(korisnik)
    print(korisnici_db)
    return korisnik

@app.post("/korisnik_profil", response_model=Korisnik_profil)
def korisnik_unos(profil_korisnika: Korisnik_profil):
    korisnik=next((kor for kor in korisnici_db if kor.email == profil_korisnika.email), None)
    
    if not korisnik:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen!")
    
    profil_korisnika.ime=korisnik.ime
    profil_korisnika.prezime=korisnik.prezime
    profil_korisnika.korisnicko_ime=korisnik.korisnicko_ime
    profil_korisnika.lozinka=korisnik.lozinka
    
    for postojeci_profil in korisnici_db_profil:
        if postojeci_profil.email == profil_korisnika.email:
            raise HTTPException(status_code=400, detail="Korisnik s tim emailom već postoji!")
        
        if postojeci_profil.korisnicko_ime == profil_korisnika.korisnicko_ime:
            raise HTTPException(status_code=400, detail="Korisnik s tim korisničkim imenom već postoji!")
        
        if postojeci_profil.lozinka == profil_korisnika.lozinka:
            raise HTTPException(status_code=400, detail="Ova lozinka već postoji već postoji!")
        
    korisnici_db_profil.append(profil_korisnika)
    print(profil_korisnika)
    return profil_korisnika

@app.post("/korisnik_prijava", response_model=Korisnik_prijava)
def korisnik_unos(prijava_korisnika: Korisnik_prijava):
        for korisnik in korisnici_db:
            if korisnik.email==prijava_korisnika.email and korisnik.lozinka==prijava_korisnika.lozinka:
                return korisnik
        raise HTTPException(status_code=401, detail="Upisan je pogrešan email ili lozinka!")
    
@app.get("/korisnik_pretraživanje_korisničkog", response_model=Korisnik_pretraga)
def korisnicko_pretrazivanje(ime: Optional[str] = None, prezime: Optional[str]= None, email: Optional[str]= None, korisnicko_ime: Optional[str]= None):
    
    for korisnik in korisnici_db:
        if korisnicko_ime and korisnicko_ime.lower() in korisnik["korisnicko_ime"].lower():
            return Korisnik_pretraga(**korisnik)
        if  email and korisnik["email"] ==email:
            return Korisnik_pretraga(**korisnik)
        if ime and prezime and korisnik["ime"].lower() == ime.lower() and korisnik["prezime"].lower() == prezime.lower():
            return Korisnik_pretraga(**korisnik)
    raise HTTPException(status_code=401, detail="Korisnik nije pronađen!")

@app.delete("/korisnik_brisanje/")
def korisnik_brisanje(korisnicko_ime: str, lozinka: str):
    for korisnik in korisnici_db:
        if korisnik.korisnicko_ime==korisnicko_ime and korisnik.lozinka==lozinka:
            return {"poruka": f"Podaci za {korisnicko_ime} uspješno obrisani!"}
    
    raise HTTPException(status_code=401, detail="Nemate ovlasti za pristup ovim podacima")

dostupne_kolekcije=["KONZUM Zvjerići 3 Safari",
    "LaLiga 2024-2025",
    "FIFA 365 2025",
    "Foot 2024-2025",
    "Hrvatska Nogometna Liga 2024-2025",
    "English Premier League 2024-2025",
    "Calciatori 2024-2025",
    "UEFA Champions League 2024-2025"]

kolekcije_sa_brojevima_db = {
    "KONZUM Zvjerići 3 Safari": list(range(1, 131)),  # Brojevi od 1 do 130
    "LaLiga 2024-2025": list(range(1, 774)),  # Brojevi od 1 do 773
    "FIFA 365 2025": list(range(1, 423)),  # Brojevi od 1 do 422
    "Foot 2024-2025": list(range(1, 577)),  # Brojevi od 1 do 576
    "Hrvatska Nogometna Liga 2024-2025": list(range(1, 361)),  # Brojevi od 1 do 360
    "English Premier League 2024-2025": list(range(1, 765)),  # Brojevi od 1 do 764
    "Calciatori 2024-2025": list(range(1, 927)),  # Brojevi od 1 do 926
    "UEFA Champions League 2024-2025": list(range(1, 664))  # Brojevi od 1 do 663
}

korisnik_nedostaje_db=[]
korisnik_duple_db=[]

@app.get("/kolekcije")
def dohvati_kolekciju():
    return dostupne_kolekcije

@app.post("/kolekcije_in")
def unos_nedostaje(kolekcija: Literal["KONZUM Zvjerići 3 Safari", "LaLiga 2024-2025", "FIFA 365 2025", 
                                        "Foot 2024-2025", "Hrvatska Nogometna Liga 2024-2025", 
                                        "English Premier League 2024-2025", "Calciatori 2024-2025", 
                                        "UEFA Champions League 2024-2025"], brojevi: list[int]):
    korisnik_nedostaje_db.append({"kolekcija": kolekcija, "brojevi": brojevi})    
    return korisnik_nedostaje_db

@app.post("/kolekcije_out")
def unos_duple(kolekcija: Literal["KONZUM Zvjerići 3 Safari", "LaLiga 2024-2025", "FIFA 365 2025", 
                                        "Foot 2024-2025", "Hrvatska Nogometna Liga 2024-2025", 
                                        "English Premier League 2024-2025", "Calciatori 2024-2025", 
                                        "UEFA Champions League 2024-2025"], brojevi: list[int]):
    korisnik_duple_db.append({"kolekcija": kolekcija, "brojevi": brojevi})
        
    return korisnik_duple_db

@app.delete("/kolekcije_out_brisanje")
def brisanje_duple(kolekcija: Literal["KONZUM Zvjerići 3 Safari", "LaLiga 2024-2025", "FIFA 365 2025", 
                                        "Foot 2024-2025", "Hrvatska Nogometna Liga 2024-2025", 
                                        "English Premier League 2024-2025", "Calciatori 2024-2025", 
                                        "UEFA Champions League 2024-2025"], brojevi: list[int]):
    for dupla in korisnik_duple_db:
        if dupla["kolekcija"] == kolekcija:
            dupla["brojevi"] = list(filter(lambda br: br not in brojevi, dupla["brojevi"]))
    
    return korisnik_duple_db

db_recenzije_sa_ocjenama={}

@app.post("/dodavanje_recenzije", response_model=Recenzija)
def dodavanje_recenzije(recenzija: Recenzija):
    if recenzija.korisnik not in db_recenzije_sa_ocjenama:
        db_recenzije_sa_ocjenama[recenzija.korisnik] = []
    db_recenzije_sa_ocjenama[recenzija.korisnik].append(recenzija)
   
    return recenzija

@app.get("/prikaz_recenzije{korisnik}")
def prikaz_recenzije(korisnik:str):
    if korisnik not in db_recenzije_sa_ocjenama:
        raise HTTPException(status_code=404, detail= "Ovaj korisnik nije ostavio recenziju ili ne postoji u bazi!")
    return db_recenzije_sa_ocjenama

@app.get("/prikaz_ocjene{korisnik}")
def prikaz_ocjene(korisnik: str):
    if korisnik not in db_recenzije_sa_ocjenama:
        raise HTTPException(status_code=404, detail="Korisnik toga naziva nije ocijenjen ili ne postoji!")
    prosjek=sum(recenzija.ocjena for recenzija in db_recenzije_sa_ocjenama[korisnik])/len(db_recenzije_sa_ocjenama[korisnik])
    return {"korisnik": korisnik, "ocjena": round(prosjek, 2)}
