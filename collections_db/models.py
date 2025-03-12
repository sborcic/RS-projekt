from pydantic import BaseModel
from typing import Literal
from datetime import date

class Korisnik(BaseModel):
    ime: str
    prezime: str
    email: str
    korisnicko_ime: str
    lozinka: str
    
class Korisnik_prijava(BaseModel):
    email: str
    lozinka: str
    
class Korisnik_profil(BaseModel):
    korisničke_informacije: str
    ime: str
    prezime: str
    spol: Literal["Nije odabran", "Muško", "Žensko"]
    rođendan: date
    država: str
    županija: str
    grad: str
    