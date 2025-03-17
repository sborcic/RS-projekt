from pydantic import BaseModel, Field
from typing import Literal, Optional
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
    
class Kolekcije(BaseModel):
    id: int
    naziv: str
        
class Sličice(BaseModel):
    id: int
    id_kolekcija: int
    naziv: Optional[str] = None
    
class Recenzija(BaseModel):
    korisnik: str
    recenzija: str = Field(min_length=1)
    ocjena: int = Field (ge=1, le=5)
    razmjena: bool = True
