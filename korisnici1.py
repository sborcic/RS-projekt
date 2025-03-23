from fastapi import FastAPI, HTTPException, Query
from models1 import Korisnik, Korisnik_prijava, Korisnik_profil, Recenzija, Korisnik_pretraga, Poruka
from typing import List, Literal, Optional
import re

app = FastAPI()

korisnici_db=[]

korisnici_db_profil=[]

@app.post("/korisnik",response_model=Korisnik)
def korisnik_registracija(korisnik: Korisnik):
   
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

@app.post("/korisnik/profil", response_model=Korisnik_profil)
def korisnik_profil(profil_korisnika: Korisnik_profil):
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

@app.post("/korisnik/prijava", response_model=Korisnik_prijava)
def korisnik_prijava(prijava_korisnika: Korisnik_prijava):
        for korisnik in korisnici_db:
            if korisnik.email==prijava_korisnika.email and korisnik.lozinka==prijava_korisnika.lozinka:
                return korisnik
        raise HTTPException(status_code=401, detail="Upisan je pogrešan email ili lozinka!")
    
@app.get("/korisnik", response_model=Korisnik_pretraga)
def korisnik_pretrazivanje(ime: Optional[str] = None, prezime: Optional[str]= None, email: Optional[str]= None, korisnicko_ime: Optional[str]= None):
    
    for korisnik in korisnici_db:
        if korisnicko_ime and korisnicko_ime.lower() in korisnik.korisnicko_ime.lower():
            return Korisnik_pretraga(**korisnik.model_dump())
        if  email and korisnik.email ==email:
            return Korisnik_pretraga(**korisnik.model_dump())
        if ime and prezime and korisnik.ime.lower() == ime.lower() and korisnik.prezime.lower() == prezime.lower():
            return Korisnik_pretraga(**korisnik.model_dump())
    raise HTTPException(status_code=404, detail="Korisnik nije pronađen!")

@app.delete("/korisnik")
def korisnik_brisanje(korisnicko_ime: str, lozinka: str):
    for korisnik in korisnici_db:
        if korisnik.korisnicko_ime==korisnicko_ime and korisnik.lozinka==lozinka:
            korisnici_db.remove(korisnik)
            return {"poruka": f"Korisnički profil za korisnika {korisnicko_ime} je obrisan!"}
          
    raise HTTPException(status_code=404, detail="Korisnički račun ne postoji ili je krivo upisana lozinka!")


dostupne_kolekcije=["KONZUM Zvjerići 3 Safari",
    "LaLiga 2024-2025",
    "FIFA 365 2025",
    "Foot 2024-2025",
    "Hrvatska Nogometna Liga 2024-2025",
    "English Premier League 2024-2025",
    "Calciatori 2024-2025",
    "UEFA Champions League 2024-2025"]

kolekcije_sa_brojevima_db = {
    "KONZUM Zvjerići 3 Safari": list(range(1, 131)),  
    "LaLiga 2024-2025": list(range(1, 774)),  
    "FIFA 365 2025": list(range(1, 423)),  
    "Foot 2024-2025": list(range(1, 577)),  
    "Hrvatska Nogometna Liga 2024-2025": list(range(1, 361)),  
    "English Premier League 2024-2025": list(range(1, 765)),  
    "Calciatori 2024-2025": list(range(1, 927)),  
    "UEFA Champions League 2024-2025": list(range(1, 664))  
}

#korisnik_nedostaje_db=[]
#korisnik_duple_db=[]

korisnik_nedostaje_db = [
    {"korisnik": "ivan123", "kolekcija": "KONZUM Zvjerići 3 Safari", "brojevi": [1, 3, 5, 7, 8]},
    {"korisnik": "petra456", "kolekcija": "FIFA 365 2025", "brojevi": [10, 12, 15, 18, 20]},
    {"korisnik": "marko789", "kolekcija": "LaLiga 2024-2025", "brojevi": [2, 4, 6, 9]},
    {"korisnik": "janko123", "kolekcija": "Hrvatska Nogometna Liga 2024-2025", "brojevi": [5, 6, 7, 11, 14]},
    {"korisnik": "lucija321", "kolekcija": "English Premier League 2024-2025", "brojevi": [1, 2, 4, 8, 10]}
]

korisnik_duple_db = [
    {"korisnik": "ivan123", "kolekcija": "KONZUM Zvjerići 3 Safari", "brojevi": [1, 3, 5, 7, 8]},
    {"korisnik": "petra456", "kolekcija": "FIFA 365 2025", "brojevi": [10, 12, 15, 18, 20]},
    {"korisnik": "marko789", "kolekcija": "LaLiga 2024-2025", "brojevi": [2, 4, 6, 9]}]


@app.get("/kolekcija")
def dohvati_kolekciju():
    return dostupne_kolekcije

@app.get("/kolekcija/{naziv}")
def dohvati_kolekciju_sa_brojevima(naziv: str):
    if naziv in kolekcije_sa_brojevima_db:
        return kolekcije_sa_brojevima_db[naziv]
    raise HTTPException(status_code=404, detail="Kolekcija toga naziva nije pronađena!")

@app.post("/kolekcija")
def dodaj_kolekciju(naziv: str, brojevi: int):
    if naziv in kolekcije_sa_brojevima_db:
        raise HTTPException(status_code=400, detail="Kolekcija je već u bazi!")
    kolekcije_sa_brojevima_db[naziv] = list(range(1, brojevi + 1))
    dostupne_kolekcije.append(naziv)
    return {"naziv": naziv, "brojevi": list(range(1, brojevi + 1))}

@app.put("/kolekcija")
def izmjena_kolekcije(kolekcija: str, brojevi: list[int]):
    if kolekcija not in kolekcije_sa_brojevima_db:
        raise HTTPException(status_code=404, detail="Kolekcija ne postoji!")
    
    for broj in brojevi:
        if broj not in kolekcije_sa_brojevima_db[kolekcija]:
            kolekcije_sa_brojevima_db[kolekcija].append(broj)
    return {"kolekcija": kolekcija, "brojevi": brojevi}

@app.post("/kolekcija/unos/nedostaje")
def unos_nedostaje(korisnik: str, kolekcija: Literal["KONZUM Zvjerići 3 Safari", "LaLiga 2024-2025", "FIFA 365 2025", 
                                        "Foot 2024-2025", "Hrvatska Nogometna Liga 2024-2025", 
                                        "English Premier League 2024-2025", "Calciatori 2024-2025", 
                                        "UEFA Champions League 2024-2025"], brojevi: list[int]):
    korisnik_nedostaje_db.append({"korisnik": korisnik, "kolekcija": kolekcija, "brojevi": brojevi})    
    return korisnik_nedostaje_db

@app.post("/kolekcija/unos/duple")
def unos_duple(korisnik: str, kolekcija: Literal["KONZUM Zvjerići 3 Safari", "LaLiga 2024-2025", "FIFA 365 2025", 
                                        "Foot 2024-2025", "Hrvatska Nogometna Liga 2024-2025", 
                                        "English Premier League 2024-2025", "Calciatori 2024-2025", 
                                        "UEFA Champions League 2024-2025"], brojevi: list[int]):
    korisnik_duple_db.append({"korisnik": korisnik, "kolekcija": kolekcija, "brojevi": brojevi})
        
    return korisnik_duple_db

@app.delete("/kolekcija")
def brisanje_nedostaje(kolekcija: Literal["KONZUM Zvjerići 3 Safari", "LaLiga 2024-2025", "FIFA 365 2025", 
                                        "Foot 2024-2025", "Hrvatska Nogometna Liga 2024-2025", 
                                        "English Premier League 2024-2025", "Calciatori 2024-2025", 
                                        "UEFA Champions League 2024-2025"], brojevi: list[int]):
    for dupla in korisnik_nedostaje_db:
        if dupla["kolekcija"] == kolekcija:
            dupla["brojevi"] = list(filter(lambda br: br not in brojevi, dupla["brojevi"]))
    
    return korisnik_nedostaje_db

@app.delete("/kolekcija/brisanje/duple")
def brisanje_duple(kolekcija: Literal["KONZUM Zvjerići 3 Safari", "LaLiga 2024-2025", "FIFA 365 2025", 
                                        "Foot 2024-2025", "Hrvatska Nogometna Liga 2024-2025", 
                                        "English Premier League 2024-2025", "Calciatori 2024-2025", 
                                        "UEFA Champions League 2024-2025"], brojevi: list[int]):
    for dupla in korisnik_duple_db:
        if dupla["kolekcija"] == kolekcija:
            dupla["brojevi"] = list(filter(lambda br: br not in brojevi, dupla["brojevi"]))
    
    return korisnik_duple_db

@app.get("/kolekcija_zamjena")
def trazi_zamjenu(moje_korisnicko_ime: str, korisnik: str, kolekcija: Literal["KONZUM Zvjerići 3 Safari", "LaLiga 2024-2025", "FIFA 365 2025", 
                                        "Foot 2024-2025", "Hrvatska Nogometna Liga 2024-2025", 
                                        "English Premier League 2024-2025", "Calciatori 2024-2025", 
                                        "UEFA Champions League 2024-2025"]):
    nedostaju_slicice=[]
    
    for kor in korisnik_nedostaje_db:
        if kor["korisnik"] == korisnik and kor["korisnik"] != moje_korisnicko_ime:
            nedostaju_slicice= kor["brojevi"]
            break
        
    if not nedostaju_slicice:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen ili ne možete upisati vlastito korisničko ime!")
    
    moguca_zamjena = {}

    for kor in korisnik_duple_db:
        if kor["kolekcija"] == kolekcija:
            if "brojevi" in kor:
                brojevi=kor["brojevi"]
        else:
                brojevi=[]
                
        zajednicke_slicice = []  
        
        for broj in brojevi:  
            if broj in nedostaju_slicice:
                zajednicke_slicice.append(broj)

        if zajednicke_slicice:  
            moguca_zamjena[kor["korisnik"]] = zajednicke_slicice

    return {"korisnik": korisnik, "kolekcija": kolekcija, "moguca_zamjena": moguca_zamjena} 

db_recenzije_sa_ocjenama={}

@app.post("/recenzija", response_model=Recenzija)
def dodavanje_recenzije(recenzija: Recenzija):
    
    if not recenzija.korisnik:
        raise HTTPException(status_code=400, detail="Korisnik ne postoji ili je krivo uneseno korisničko ime!")
    
    if recenzija.korisnik not in db_recenzije_sa_ocjenama:
        db_recenzije_sa_ocjenama[recenzija.korisnik] = []
        
    db_recenzije_sa_ocjenama[recenzija.korisnik].append(recenzija)
   
    return recenzija

@app.get("/recenzija/{korisnik}")
def prikaz_recenzije(korisnik:str):
    if korisnik not in db_recenzije_sa_ocjenama:
        raise HTTPException(status_code=404, detail= "Ovaj korisnik nije ostavio recenziju ili ne postoji u bazi!")
    
    return db_recenzije_sa_ocjenama

@app.get("/recenzija/ocjena/{korisnik}")
def prikaz_ocjene(korisnik: str):
    if korisnik not in db_recenzije_sa_ocjenama:
        raise HTTPException(status_code=404, detail="Korisnik toga naziva nije ocijenjen ili ne postoji!")
    
    prosjek=sum(recenzija.ocjena for recenzija in db_recenzije_sa_ocjenama[korisnik])/len(db_recenzije_sa_ocjenama[korisnik])
    
    return {"korisnik": korisnik, "ocjena": round(prosjek, 2)}

db_poruke=[]

@app.post("/poruka", response_model=Poruka)
def posalji_poruku(poruka: Poruka):
    db_poruke.append(poruka)
    return poruka

@app.get("/poruka")
def dohvati_poruku(primatelj: str):
    db_poruka_primatelj= []
    
    for poruka in db_poruke:
        if poruka.korisnik_primatelj == primatelj:
            db_poruka_primatelj.append(poruka)
            
    if not db_poruka_primatelj:
        raise HTTPException(status_code=404, detail="Za korisnika ovog korisničkog imena nema nove poruke!")
    
    return {"primatelj": primatelj, "poruka": db_poruka_primatelj}