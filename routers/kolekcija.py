from fastapi import APIRouter
from typing import Literal
from dynamodb.dynamodb import dohvati_kolekciju_dynamo, dohvati_kolekciju_sa_brojevima_dynamo, dodaj_kolekciju_dynamo, kolekcija_izmjena_dynamo, unos_nedostaje_dynamo, unos_duple_dynamo, brisanje_nedostaje_dynamo, brisanje_duple_dynamo, trazi_zamjenu_dynamo
from models1 import DodajKolekciju, IzmjeniKolekciju

router = APIRouter(prefix=("/kolekcija"))  

@router.get("/")
def dohvati_kolekciju():
    return dohvati_kolekciju_dynamo()

@router.get("/kolekcija_naziv_brojevi/{kolekcija_naziv}")
def dohvati_kolekciju_sa_brojevima(kolekcija_naziv: Literal[
        "Calciatori 2024-2025",
        "Foot 2024-2025",
        "English Premier League 2024-2025",
        "LaLiga 2024-2025",
        "FIFA 365 2025",
        "Hrvatska Nogometna Liga 2024-2025",
        "KONZUM Zvjerići 3 Safari",
        "UEFA Champions League 2024-2025"
    ]
):
    return dohvati_kolekciju_sa_brojevima_dynamo(kolekcija_naziv)
    
@router.post("/")
def dodaj_kolekciju(dodaj_kolekciju: DodajKolekciju):
    return dodaj_kolekciju_dynamo(**dodaj_kolekciju.model_dump())
    #if naziv in kolekcije_sa_brojevima_db:
    #    raise HTTPException(status_code=400, detail="Kolekcija je već u bazi!")
    #kolekcije_sa_brojevima_db[naziv] = list(range(1, brojevi + 1))
    #dostupne_kolekcije.append(naziv)
    #return {"naziv": naziv, "brojevi": list(range(1, brojevi + 1))}

@router.put("/")
def izmjena_kolekcije(izmjeni_kolekciju: IzmjeniKolekciju):
   
    naziv = izmjeni_kolekciju.kolekcija_naziv
    brojevi = izmjeni_kolekciju.brojevi
   
    return kolekcija_izmjena_dynamo(naziv, brojevi)

@router.post("/unos/nedostaje")
def unos_nedostaje(korisnik_kolekcija: str, kolekcija_naziv: str, brojevi: list[int]):
                   
    return unos_nedostaje_dynamo(korisnik_kolekcija, kolekcija_naziv, brojevi)

@router.post("/unos/duple")
def unos_duple(korisnicko_ime: str, kolekcija_naziv: str, brojevi: list[int]):
    
    return unos_duple_dynamo(korisnicko_ime, kolekcija_naziv, brojevi)

@router.delete("/brisanje_nedostaje")
def brisanje_nedostaje(korisnicko_ime: str, kolekcija_naziv: str, brojevi: list[int]): 
    
    return brisanje_nedostaje_dynamo(korisnicko_ime, kolekcija_naziv, brojevi)

@router.delete("/brisanje_duple")
def brisanje_duple(korisnicko_ime, kolekcija_naziv, brojevi):
    
    return brisanje_duple_dynamo(korisnicko_ime, kolekcija_naziv, brojevi)

@router.get("/zamjena")
def trazi_zamjenu(korisnik_trazi: str, korisnik_posjeduje: str, kolekcija: str):
    return trazi_zamjenu_dynamo(korisnik_trazi, korisnik_posjeduje, kolekcija)