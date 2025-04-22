from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date
        
class Korisnik_ime_prezime_lozinka_email_korisnicko_ime(BaseModel):
    ime: str = Field(max_length=25)
    prezime: str  = Field(max_length=25)
    email: str
    korisnicko_ime: str
    lozinka: str = Field(min_length=8, description="Lozinka mora sadržavati jedan specijalni znak!")
       
class Korisnik(Korisnik_ime_prezime_lozinka_email_korisnicko_ime):
    korisnik_ID: Optional[int] = None
    
class Korisnik_bez_lozinke(BaseModel):
    ime: str = Field(max_length=25)
    prezime: str  = Field(max_length=25)
    email: str
    korisnicko_ime: str   
           
class Korisnik_prijava(BaseModel):
    email: str
    lozinka: str = Field(min_length=8, description="Lozinka mora sadržavati jedan specijalni znak!")
    
class Korisnik_prijava_korisnickim_imenom(BaseModel):
    korisnicko_ime: str
    lozinka: str = Field(min_length=8, description="Lozinka mora sadržavati jedan specijalni znak!")
    
class Korisnik_pretraga(BaseModel):
    ime: str
    prezime: str
    email: str
    korisnicko_ime: str
        
class Korisnik_profil(Korisnik_ime_prezime_lozinka_email_korisnicko_ime):
    korisnik_ID: Optional[int] = Field(default=None, exclude=True) 
    korisnicke_informacije: Optional[str] = Field(default=None, max_length=50)
    spol: Literal["Nije odabrano", "Muško", "Žensko"] = "Nije odabrano"
    rodendan: Optional[date] = None
    drzava: Optional [str] = None
    zupanija: Optional [str] = None
    grad: Optional [str] = None
    telefon: Optional[str] = None
    adresa: Optional[str] = None
    postanski_broj: Optional[str] = None
    status: Literal["Online","Offline", "Not available"] ="Online"
    
class Korisnik_profil1(Korisnik_bez_lozinke):
    korisnik_ID: Optional[int] = Field(default=None, exclude=True) 
    korisnicke_informacije: Optional[str] = Field(default=None, max_length=50)
    spol: Literal["Nije odabrano", "Muško", "Žensko"] = "Nije odabrano"
    rodendan: Optional[date] = None
    drzava: Optional [str] = None
    zupanija: Optional [str] = None
    grad: Optional [str] = None
    telefon: Optional[str] = None
    adresa: Optional[str] = None
    postanski_broj: Optional[str] = None
    status: Literal["Online","Offline", "Not available"] ="Online"

class Token(BaseModel):
    access_token: str
    token_type: str