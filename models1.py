from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import date

class Korisnik_ime_prezime_lozinka_email_korisnicko_ime(BaseModel):
    ime: str = Field(max_length=25)
    prezime: str  = Field(max_length=25)
    email: str
    korisnicko_ime: str
    lozinka: str = Field(min_length=8, description="Lozinka mora sadržavati jedan specijalni znak!")
    
class Korisnik(Korisnik_ime_prezime_lozinka_email_korisnicko_ime):
    korisnik_ID: Optional[int] = None
    
class Korisnik_prijava(BaseModel):
    email: str
    lozinka: str = Field(min_length=8, description="Lozinka mora sadržavati jedan specijalni znak!")
    
class Korisnik_pretraga(BaseModel):
    ime: str
    prezime: str
    email: str
    korisnicko_ime: str
        
class Korisnik_profil(Korisnik_ime_prezime_lozinka_email_korisnicko_ime):
    korisničke_informacije: str = Field(max_length=50)
    spol: Literal["Nije odabrano", "Muško", "Žensko"] = "Nije odabrano"
    rođendan: date = Field(description= "format unosa je godina/mjesec/dan ili YYYY/MM/DD")
    država: str
    županija: Optional [str] = None
    grad: Optional [str] = None
    telefon: Optional[str] = None
    adresa: Optional[str] = None
    postanski_broj: Optional[str] = None
    status: Literal["Online", "Offline", "Nedostupan za zamjene"]
        
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

