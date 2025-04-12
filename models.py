from pydantic import BaseModel, Field
from typing import Literal, Optional, Union
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
    
class Korisnik_prijava_korisnickim_imenom(BaseModel):
    korisnicko_ime: str
    lozinka: str
    
class Korisnik_pretraga(BaseModel):
    ime: str
    prezime: str
    email: str
    korisnicko_ime: str
        
class Korisnik_profil(Korisnik_ime_prezime_lozinka_email_korisnicko_ime):
    korisničke_informacije: Optional[str] = Field(default=None, max_length=50)
    spol: Literal["Nije odabrano", "Muško", "Žensko"] = "Nije odabrano"
    rođendan: Optional[date] = None
    država: Optional [str] = None
    županija: Optional [str] = None
    grad: Optional [str] = None
    telefon: Optional[str] = None
    adresa: Optional[str] = None
    postanski_broj: Optional[str] = None
    status: Literal["Online","Offline", "Not available"] ="Online"
          
class Kolekcije(BaseModel):
    id: int
    naziv: str
        
class DodajKolekciju(BaseModel):
    kolekcija_naziv: str
    broj: int
    
class IzmjeniKolekciju(BaseModel):
    kolekcija_naziv: str
    brojevi: list[int]

class Sličice(BaseModel):
    id: int
    id_kolekcija: int
    naziv: Optional[str] = None
    
class Recenzija(BaseModel):
    korisnik_salje_recenziju: str
    korisnik_prima_recenziju: str
    recenzija: str = Field(min_length=1)
    ocjena: int = Field (ge=1, le=5)
    
class Poruka(BaseModel):
    korisnik_primatelj: str
    korisnik_posiljatelj: str
    poruka:str

class Korisnik1(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    
class Token(BaseModel):
    access_token: str
    token_type: str

#class TokenData(BaseModel):
    ime_korisnika: str | None = None
