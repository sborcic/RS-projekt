from fastapi import APIRouter, HTTPException, Depends
from models1 import Korisnik, Korisnik_prijava, Korisnik_profil, Korisnik_pretraga, Token, TokenData, Korisnik1
from typing import Optional, Annotated
import re
import jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from dynamodb.dynamodb import dodaj_korisnika_dynamo, dohvati_korisnika_dynamo, azuriraj_korisnika_dynamo, dodaj_profil_dynamo, dohvati_korisnika_po_emailu_dynamo, dohvati_id, table_profil, table
from routers.utils import hash_lozinka, verifikacija_lozinke


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

def dohvati_korisnika(korisnicko_ime: str):
    korisnik = dohvati_korisnika_dynamo(korisnicko_ime)
    
    if not korisnik:
            return None

    return korisnik

def autentifikacija_korisnika(korisnicko_ime: str, lozinka: str):
    korisnik = dohvati_korisnika_dynamo(korisnicko_ime)
    
    if not korisnik:
        print("Korisnik nije pronađen!")
        
    if not verifikacija_lozinke(lozinka, korisnik["lozinka"]):
        print("Kriva lozinka!")
        return None
    #print(korisnik["lozinka"])
    return korisnik
    
def kreiraj_token(podaci: dict, expires_delta: timedelta | None = None):
    to_encode = podaci.copy()
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
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        print("DEKODIRAO TOKEN")
        #print(f"TOKEN primljen: {token}")
        #print("Payload iz tokena:", payload)
        username = payload.get("sub")
        print(f"Username iz tokena: {username}")
         
        if username is None:
            print("Username nije prisutan u tokenu!")
            raise credentials_exception 
    
    except InvalidTokenError as e:
        print(f"Greška u dekodiranju tokena: {str(e)}")
        print(f"Token koji je pao: {token}")
        raise credentials_exception

    
    print(f"Pokušavam dohvatiti korisnika s korisničkim imenom: {username}")
    korisnik = dohvati_korisnika_dynamo(username)
    
    print(f"Korisnik dohvaćen: {korisnik}")  # Debug
    print(f"Tip dohvaćenog korisnika: {type(korisnik)}")  # Provjeri tip
    
    if korisnik is None:
        #or not isinstance(korisnik, Korisnik):
    #    print("Korisnik nije pronađen ili nije instanca klase Korisnik!")
        raise credentials_exception
    
    dohvati_korisnika=Korisnik(**korisnik)
    
    return dohvati_korisnika


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
        data={"sub": korisnik["korisnicko_ime"]}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

def dohvati_trenutno_aktivnog_korisnika(
    trenutni_korisnik: Annotated[Korisnik, Depends(dohvati_trenutnog_korisnika)],
):
   
    return trenutni_korisnik

@router.get("/moj_profil/", response_model=Korisnik)
def dohvati_moj_profil(trenutni_korisnik: Annotated[Korisnik, Depends(dohvati_trenutno_aktivnog_korisnika)],):
    return trenutni_korisnik

@router.post("/profil", response_model=Korisnik_profil)
def korisnik_profil(profil_korisnika: Korisnik_profil):
    korisnik=dohvati_korisnika_po_emailu_dynamo(profil_korisnika.email)
    
    if not korisnik:
        raise HTTPException(status_code=404, detail="Korisnik nije pronađen!")
    
    profil_korisnika.ime=korisnik.get("ime")
    profil_korisnika.prezime=korisnik.get("prezime")
    profil_korisnika.korisnicko_ime=korisnik.get("korisnicko_ime")
        
    svi_korisnici= table.scan().get("Items", [])
    
    korisnik_postoji = any(kor.get("email") == profil_korisnika.email and kor.get("korisnicko_ime") == profil_korisnika.korisnicko_ime for kor in svi_korisnici)
     
    if not korisnik_postoji:
        raise HTTPException(status_code=400, detail="Korisnik ne postoji u bazi!")
                
    azuriraj_korisnika_dynamo(profil_korisnika)
    
    return profil_korisnika

@router.post("/prijava", response_model=Korisnik_prijava)
def korisnik_prijava(prijava_korisnika: Korisnik_prijava):
    korisnik = dohvati_korisnika_po_emailu_dynamo(prijava_korisnika.email)

    if not korisnik:
        raise HTTPException(status_code=401, detail="Ne postoji korisnik u bazi!")
    
    if not verifikacija_lozinke(prijava_korisnika.lozinka, korisnik.lozinka):
        raise HTTPException(status_code=401, detail="Pogrešna lozinka")
    
    return Korisnik_prijava(email=korisnik.email, lozinka=prijava_korisnika.lozinka)

    
@router.get("/", response_model=Korisnik_pretraga)
def korisnik_pretrazivanje(korisnicko_ime: Optional[str]= None):
    
    if korisnicko_ime:
        korisnik = dohvati_korisnika_dynamo(korisnicko_ime)
        if korisnik:
            return Korisnik_pretraga(**korisnik)
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

