from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_lozinka(lozinka: str):
    return pwd_context.hash(lozinka)

def verifikacija_lozinke(lozinka_unos: str, lozinka_hash: str):
    return pwd_context.verify(lozinka_unos, lozinka_hash)