from fastapi import APIRouter, HTTPException, Depends
from models1 import Korisnik, Korisnik_prijava, Korisnik_profil, Korisnik_pretraga, Token, TokenData, Korisnik1
from typing import Optional, Annotated
import re
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from dynamodb.dynamodb import dodaj_korisnika_dynamo, dohvati_korisnika_dynamo, azuriraj_korisnika_dynamo, dodaj_profil_dynamo, dohvati_korisnika_po_emailu_dynamo, dohvati_id, table

router = APIRouter(prefix=("/korisnik"))   

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/korisnik/token")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hash_lozinka(lozinka: str):
    return pwd_context.hash(lozinka)

def verifikacija_lozinke(lozinka_unos: str, lozinka_hash: str):
    return pwd_context.verify(lozinka_unos, lozinka_hash)


"""korisnici_db = [
    Korisnik(
        korisnicko_ime="ivan123",
        lozinka=hash_lozinka("lozinka123"),
        ime="Ivan",
        prezime="Ivić",
        email="ivan@example.com",
        korisnik_ID=1
    ),
    Korisnik(
        korisnicko_ime="ana456",
        lozinka=hash_lozinka("lozinka456"),
        ime="Ana",
        prezime="Anić",
        email="ana@example.com",
        korisnik_ID=2
    ),
    Korisnik(
        korisnicko_ime="marko789",
        lozinka=hash_lozinka("lozinka789"),
        ime="Marko",
        prezime="Marković",
        email="marko@example.com",
        korisnik_ID=3
    ),
    Korisnik(
        korisnicko_ime="lucija101",
        lozinka=hash_lozinka("lozinka101"),
        ime="Lucija",
        prezime="Lučić",
        email="lucija@example.com",
        korisnik_ID=4
    )]"""

def dohvati_korisnika(korisnicko_ime: str):
    korisnik = dohvati_korisnika_dynamo(korisnicko_ime)
    
    if not korisnik:
            return None

    return korisnik

def autentifikacija_korisnika(korisnicko_ime: str, lozinka: str):
    korisnik= dohvati_korisnika_dynamo(korisnicko_ime)
    if not korisnik or not verifikacija_lozinke(lozinka, korisnik["lozinka"]):
        return None
    
    return korisnik
    
def kreiraj_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def dohvati_trenutnog_korisnika(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
         
        if username is None:
            raise credentials_exception 
    
    except InvalidTokenError:
        raise credentials_exception
    
    korisnik = dohvati_korisnika_dynamo(username)   
 
    if korisnik is None or not isinstance(korisnik, Korisnik):
        raise credentials_exception
        
    return korisnik

@router.post("/registracija/",response_model=Korisnik)
def korisnik_registracija(korisnik: Korisnik):
   
    postojeci_korisnik=dohvati_korisnika_dynamo(korisnik.korisnicko_ime)
    if postojeci_korisnik:
        raise HTTPException(status_code=400, detail="Korisnik s tim korisničkim imenom ili emailom već postoji!")
    
    response = table.scan()
    korisnici = response.get("Items", [])
    
    postoji_email= False
    for postojeci_korisnik in korisnici:
        if postojeci_korisnik.get("email") == korisnik.email:
            postoji_email=True
            break    
        
    if postoji_email:
        raise HTTPException(status_code=400, detail="Korisnik s tim emailom već postoji!")
                            
    specijalni_znakovi = r"[!\"#$%&/()=?*]"

    if not re.search(specijalni_znakovi, korisnik.lozinka):
        raise HTTPException(status_code=400, detail="Lozinka ne sadrži specijalni znak!")
    
    korisnik.lozinka=hash_lozinka(korisnik.lozinka)
    
    korisnik.korisnik_ID= dohvati_id()   
    
    dodaj_korisnika_dynamo(korisnik)
    
    return korisnik

@router.post("/token/", response_model=Token)
def prijava_korisnika_tokenom(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], ) -> Token:
    korisnik =autentifikacija_korisnika(form_data.username, form_data.password)    
    if not korisnik:
        raise HTTPException(
            status_code=401,
            detail="Pogrešno korisničko ime ili lozinka",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = kreiraj_token(
        data={"sub": korisnik.korisnicko_ime}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

def dohvati_trenutno_aktivnog_korisnika(
    trenutni_korisnik: Annotated[Korisnik, Depends(dohvati_trenutnog_korisnika)],
):
   
    return trenutni_korisnik

@router.get("/moj_profil/", response_model=Korisnik)
def dohvati_moj_profil(trenutni_korisnik: Annotated[Korisnik, Depends(dohvati_trenutno_aktivnog_korisnika)],):
    return trenutni_korisnik


    
#korisnici_db=[]


#korisnici_db_profil=[]

@router.post("/profil", response_model=Korisnik_profil)
def korisnik_profil(profil_korisnika: Korisnik_profil):
    korisnik=dohvati_korisnika_po_emailu(profil_korisnika.email)
    
    if not korisnik:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen!")
    
    profil_korisnika.ime=korisnik.get("ime")
    profil_korisnika.prezime=korisnik.get("prezime")
    profil_korisnika.korisnicko_ime=korisnik.get("korisnicko_ime")
    profil_korisnika.lozinka=korisnik.get("lozinka")
    
    svi_korisnici=table_profil.scan().get("Item", [])
    
    for postojeci_profil in svi_korisnici:
        if postojeci_profil.get("email") == profil_korisnika.email:
            raise HTTPException(status_code=400, detail="Korisnik s tim emailom već postoji!")
        
        if postojeci_profil.get("korisnicko_ime") == profil_korisnika.korisnicko_ime:
            raise HTTPException(status_code=400, detail="Korisnik s tim korisničkim imenom već postoji!")
        
        if postojeci_profil.get("lozinka") == profil_korisnika.lozinka:
            raise HTTPException(status_code=400, detail="Ova lozinka već postoji već postoji!")
        
    dodaj_profil_dynamo(profil_korisnika)
    
    return profil_korisnika

@router.post("/prijava", response_model=Korisnik_prijava)
def korisnik_prijava(prijava_korisnika: Korisnik_prijava):
    korisnik = dohvati_korisnika_po_emailu_dynamo(prijava_korisnika.email)

    if not korisnik or not verifikacija_lozinke(prijava_korisnika.lozinka, korisnik["lozinka"]):
        raise HTTPException(status_code=401, detail="Upisan je pogrešan email ili lozinka!")
    
    return Korisnik_prijava(korisnicko_ime=korisnik["korisnicko_ime"], email=korisnik["email"])
    
@router.get("/", response_model=Korisnik_pretraga)
def korisnik_pretrazivanje(korisnicko_ime: Optional[str]= None):
    
    if korisnicko_ime:
        korisnik = dohvati_korisnika_dynamo(korisnicko_ime)
        if korisnik:
            return Korisnik_pretraga(**korisnik.model_dump())
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen!")

@router.delete("/")
def korisnik_brisanje(korisnicko_ime: str, lozinka: str):
    korisnik = dohvati_korisnika_dynamo(korisnicko_ime)
    
    if not korisnik or not verifikacija_lozinke(lozinka, korisnik["lozinka"]):
        raise HTTPException(status_code=404, detail="Korisnički račun ne postoji ili je krivo upisana lozinka!")   
        
    table.delete_item(Key={"korisnicko_ime": korisnicko_ime})
        
    return {"poruka": f"Korisnički profil za korisnika {korisnicko_ime} je obrisan!"}
          
          
@router.put("/azuriraj_profil/", response_model=Korisnik)
def azuriraj_profil_korisnika(korisnik: Korisnik):
    postojeci_korisnik = dohvati_korisnika_dynamo(korisnik.korisnicko_ime)
    if not postojeci_korisnik:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen!")
    
    azuriraj_korisnika_dynamo(korisnik)
    return korisnik
