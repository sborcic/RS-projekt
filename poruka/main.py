from fastapi import APIRouter, FastAPI
from typing import Literal
from dynamodb_local.dynamodb import dohvati_kolekciju_dynamo, dohvati_kolekciju_sa_brojevima_dynamo, kolekcija_izmjena_dynamo, dodaj_kolekciju_dynamo, unos_nedostaje_dynamo, unos_duple_dynamo, brisanje_nedostaje_dynamo, brisanje_duple_dynamo, trazi_zamjenu_dynamo
from kolekcija.models import DodajKolekciju, IzmjeniKolekciju


app = FastAPI()

router = APIRouter(prefix=("/kolekcija"))  

@router.get("/")
def dohvati_kolekciju():
    return dohvati_kolekciju_dynamo()

@router.get("/kolekcija_naziv_brojevi/{kolekcija_naziv}/{kolekcija_id}")
def dohvati_kolekciju_sa_brojevima(kolekcija_naziv: Literal[
        "Calciatori 2024-2025",
        "Foot 2024-2025",
        "English Premier League 2024-2025",
        "LaLiga 2024-2025",
        "FIFA 365 2025",
        "Hrvatska Nogometna Liga 2024-2025",
        "KONZUM Zvjerići 3 Safari",
        "UEFA Champions League 2024-2025"], kolekcija_id: str):

    return dohvati_kolekciju_sa_brojevima_dynamo(kolekcija_naziv, kolekcija_id)
    
@router.post("/")
def dodaj_kolekciju(dodaj_kolekciju: DodajKolekciju):
    return dodaj_kolekciju_dynamo(**dodaj_kolekciju.model_dump())
    
@router.put("/")
def izmjena_kolekcije(izmjeni_kolekciju: IzmjeniKolekciju):
   
    naziv = izmjeni_kolekciju.kolekcija_naziv
    brojevi = izmjeni_kolekciju.brojevi
    kolekcija_id = izmjeni_kolekciju.kolekcija_id
   
    return kolekcija_izmjena_dynamo(kolekcija_id, naziv, brojevi)

@router.post("/unos/nedostaje")
def unos_nedostaje(korisnicko_ime: str, kolekcija_naziv: str, brojevi: list[int]):
                   
    return unos_nedostaje_dynamo(korisnicko_ime, kolekcija_naziv, brojevi)

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
def trazi_zamjenu(korisnicko_ime:str, korisnik_posjeduje: str, kolekcija: str):
    return trazi_zamjenu_dynamo(korisnicko_ime, korisnik_posjeduje, kolekcija)

app.include_router(router)