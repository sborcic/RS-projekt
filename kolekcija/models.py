from pydantic import BaseModel, Field
from typing import Literal, Optional, Union
from datetime import date

class Kolekcije(BaseModel):
    id: int
    naziv: str
        
class DodajKolekciju(BaseModel):
    kolekcija_naziv: str
    broj: int
    
class IzmjeniKolekciju(BaseModel):
    kolekcija_id: str
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


