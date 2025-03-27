from fastapi import APIRouter,FastAPI, HTTPException, Query
#from models1 import Korisnik, Korisnik_prijava, Korisnik_profil, Recenzija, Korisnik_pretraga, Poruka
from typing import List, Literal, Optional

router = APIRouter(prefix=("/kolekcija"))  


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


@router.get("/")
def dohvati_kolekciju():
    return dostupne_kolekcije

@router.get("/{naziv}")
def dohvati_kolekciju_sa_brojevima(naziv: str):
    if naziv in kolekcije_sa_brojevima_db:
        return kolekcije_sa_brojevima_db[naziv]
    raise HTTPException(status_code=404, detail="Kolekcija toga naziva nije pronađena!")

@router.post("/")
def dodaj_kolekciju(naziv: str, brojevi: int):
    if naziv in kolekcije_sa_brojevima_db:
        raise HTTPException(status_code=400, detail="Kolekcija je već u bazi!")
    kolekcije_sa_brojevima_db[naziv] = list(range(1, brojevi + 1))
    dostupne_kolekcije.append(naziv)
    return {"naziv": naziv, "brojevi": list(range(1, brojevi + 1))}

@router.put("/")
def izmjena_kolekcije(kolekcija: str, brojevi: list[int]):
    if kolekcija not in kolekcije_sa_brojevima_db:
        raise HTTPException(status_code=404, detail="Kolekcija ne postoji!")
    
    for broj in brojevi:
        if broj not in kolekcije_sa_brojevima_db[kolekcija]:
            kolekcije_sa_brojevima_db[kolekcija].append(broj)
    return {"kolekcija": kolekcija, "brojevi": brojevi}

@router.post("/unos/nedostaje")
def unos_nedostaje(korisnik: str, kolekcija: Literal["KONZUM Zvjerići 3 Safari", "LaLiga 2024-2025", "FIFA 365 2025", 
                                        "Foot 2024-2025", "Hrvatska Nogometna Liga 2024-2025", 
                                        "English Premier League 2024-2025", "Calciatori 2024-2025", 
                                        "UEFA Champions League 2024-2025"], brojevi: list[int]):
    korisnik_nedostaje_db.append({"korisnik": korisnik, "kolekcija": kolekcija, "brojevi": brojevi})    
    return korisnik_nedostaje_db

@router.post("/unos/duple")
def unos_duple(korisnik: str, kolekcija: Literal["KONZUM Zvjerići 3 Safari", "LaLiga 2024-2025", "FIFA 365 2025", 
                                        "Foot 2024-2025", "Hrvatska Nogometna Liga 2024-2025", 
                                        "English Premier League 2024-2025", "Calciatori 2024-2025", 
                                        "UEFA Champions League 2024-2025"], brojevi: list[int]):
    korisnik_duple_db.append({"korisnik": korisnik, "kolekcija": kolekcija, "brojevi": brojevi})
        
    return korisnik_duple_db

@router.delete("/")
def brisanje_nedostaje(kolekcija: Literal["KONZUM Zvjerići 3 Safari", "LaLiga 2024-2025", "FIFA 365 2025", 
                                        "Foot 2024-2025", "Hrvatska Nogometna Liga 2024-2025", 
                                        "English Premier League 2024-2025", "Calciatori 2024-2025", 
                                        "UEFA Champions League 2024-2025"], brojevi: list[int]):
    for dupla in korisnik_nedostaje_db:
        if dupla["kolekcija"] == kolekcija:
            dupla["brojevi"] = list(filter(lambda br: br not in brojevi, dupla["brojevi"]))
    
    return korisnik_nedostaje_db

@router.delete("/brisanje/duple")
def brisanje_duple(kolekcija: Literal["KONZUM Zvjerići 3 Safari", "LaLiga 2024-2025", "FIFA 365 2025", 
                                        "Foot 2024-2025", "Hrvatska Nogometna Liga 2024-2025", 
                                        "English Premier League 2024-2025", "Calciatori 2024-2025", 
                                        "UEFA Champions League 2024-2025"], brojevi: list[int]):
    for dupla in korisnik_duple_db:
        if dupla["kolekcija"] == kolekcija:
            dupla["brojevi"] = list(filter(lambda br: br not in brojevi, dupla["brojevi"]))
    
    return korisnik_duple_db

@router.get("/zamjena")
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

