from pydantic import BaseModel

class Korisnik(BaseModel):
    ime: str
    prezime: str
    email: str
    korisnicko_ime: str
    lozinka: str