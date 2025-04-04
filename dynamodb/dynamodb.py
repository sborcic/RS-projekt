import boto3 
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from models1 import Korisnik_profil, Korisnik, Korisnik_ime_prezime_lozinka_email_korisnicko_ime
from fastapi import HTTPException
from boto3.dynamodb.conditions import Key
from routers.utils import hash_lozinka


s3 = boto3.client('s3')

dynamodb = boto3.resource('dynamodb', region_name='eu-north-1')

table = dynamodb.Table('korisnici_db')
table_profil = dynamodb.Table("korisnici_profil")

korisnici = [
    {
        "korisnik_ID": "2",
        "korisnicko_ime": "marko123",
        "lozinka": "hashed_lozinka_1",
        "ime": "Marko",
        "prezime": "Marković",
        "email": "marko@example.com"
    },
    {
        "korisnik_ID": "3",
        "korisnicko_ime": "ana25",
        "lozinka": "hashed_lozinka_2",
        "ime": "Ana",
        "prezime": "Anić",
        "email": "ana@example.com"
    },
    {
        "korisnik_ID": "4",
        "korisnicko_ime": "ivan40",
        "lozinka": "hashed_lozinka_3",
        "ime": "Ivan",
        "prezime": "Ivić",
        "email": "ivan@example.com"
    },
    {
        "korisnik_ID": "5",
        "korisnicko_ime": "petra22",
        "lozinka": "hashed_lozinka_4",
        "ime": "Petra",
        "prezime": "Petrović",
        "email": "petra@example.com"
    },
    {
        "korisnik_ID": "6",
        "korisnicko_ime": "luka35",
        "lozinka": "hashed_lozinka_5",
        "ime": "Luka",
        "prezime": "Lukić",
        "email": "luka@example.com"
    }
]

"""korisnici_profil = [
    {
        "korisnicko_ime": "marko123",
        "ime": "Marko",
        "prezime": "Marković",
        "email": "marko@example.com",
        "lozinka": "hashed_lozinka_1"
    },
    {
        "korisnicko_ime": "ana25",
        "ime": "Ana",
        "prezime": "Anić",
        "email": "ana@example.com",
        "lozinka": "hashed_lozinka_2"
    },
    {
        "korisnicko_ime": "ivan40",
        "ime": "Ivan",
        "prezime": "Ivić",
        "email": "ivan@example.com",
        "lozinka": "hashed_lozinka_3"
    },
    {
        "korisnicko_ime": "petra22",
        "ime": "Petra",
        "prezime": "Petrović",
        "email": "petra@example.com",
        "lozinka": "hashed_lozinka_4"
    },
    {
        "korisnicko_ime": "luka35",
        "ime": "Luka",
        "prezime": "Lukić",
        "email": "luka@example.com",
        "lozinka": "hashed_lozinka_5"
    }
]"""

"""with table.batch_writer() as batch:
    for korisnik in korisnici:
        batch.put_item(Item=korisnik)"""

"""with table_profil.batch_writer() as batch:
    for korisnik in korisnici_profil:
        batch.put_item(Item=korisnik)"""

korisnici = table.scan().get("Items", [])

korisnici_profil = table_profil.scan().get("Items", [])

#print(korisnici)
print(korisnici_profil)

def create_table():
    try:
        table = dynamodb.create_table(
            TableName='korisnici_db',
            KeySchema=[
                {
                    'AttributeName': 'korisnicko_ime',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'korisnicko_ime',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print("Tablica kreirana:", table)
    except Exception as e:
        print("Greška kod kreiranja tablice:", e)

def dodaj_korisnika_dynamo(korisnik: Korisnik):
    try:
        korisnik.lozinka = hash_lozinka(korisnik.lozinka)
        
        response = table.put_item(
            Item={
                'korisnicko_ime': korisnik.korisnicko_ime,
                'lozinka': korisnik.lozinka,
                'ime': korisnik.ime,
                'prezime': korisnik.prezime,
                'email': korisnik.email,
                'korisnik_ID': korisnik.korisnik_ID
            }
        )
        print("Korisnik uspješno dodan:", response)
    except Exception as e:
        print("Greška pri dodavanju korisnika:", e)
    
def dohvati_korisnika_dynamo(korisnicko_ime: str):
    try:
        response = table.get_item(
            Key={
                'korisnicko_ime': korisnicko_ime
            }
        )
                
        return response.get('Item')
        
    except Exception as e:
        print("Greška pri dohvaćanju korisnika:", e)
        return None

def azuriraj_korisnika_dynamo(korisnik: Korisnik_profil):
    try:
        table_profil.put_item(
            Item={
                'ime': korisnik.ime,
                'prezime': korisnik.prezime,
                'email': korisnik.email,
                'lozinka': korisnik.lozinka,
                'korisnicke_informacije': korisnik.korisničke_informacije,
                'spol': korisnik.spol,
                'rodendan': korisnik.rođendan.isoformat(),
                'drzava': korisnik.država,
                'zupanija': korisnik.županija,
                'grad': korisnik.grad,
                'telefon': korisnik.telefon,
                'adresa': korisnik.adresa,
                'postanski_broj': korisnik.postanski_broj,
                'status': korisnik.status
            },
        )
        
    except Exception as e:
        print("Greška pri ažuriranju korisnika:", e)
        raise HTTPException(status_code=500, detail="Greška pri ažuriranju korisnika: " + str(e))
        
"""def dodaj_profil_dynamo(profil: Korisnik_profil):
    try:
        
        table.put_item(
            Item={
                "email": profil.email,
                "korisnicko_ime": profil.korisnicko_ime,
                "ime": profil.ime,
                "prezime": profil.prezime,
                "lozinka": profil.lozinka,  
                #"informacije": profil.informacije,
                "spol": profil.spol,
                "rodendan": profil.rodendan,
                "drzava": profil.drzava,
                "zupanija": profil.zupanija,
                "grad": profil.grad,
                "telefon": profil.telefon,
                "adresa": profil.adresa,
                "postanski_broj": profil.postanski_broj,
                "status": profil.status,
            }
        )
        print(f"Profil uspješno dodan za email: {profil.email}")
    except Exception as e:
        print("Greška pri dodavanju profila:", e)
        raise HTTPException(status_code=500, detail="Greška pri dodavanju profila u bazu: " + str(e))"""


def dohvati_korisnika_po_emailu_dynamo(email: str):
    response = table.scan(
        FilterExpression=Key('email').eq(email)
    )
    items = response.get("Items", [])
    if items:
       
        korisnik_data = items[0]
        korisnik = Korisnik(**korisnik_data)
        return korisnik
    else:
        return None

def dodaj_profil_dynamo(profil: Korisnik_profil):
    try:
        
        table_profil.put_item(
            Item={
                "email": profil.email,
                "korisnicko_ime": profil.korisnicko_ime,
                "ime": profil.ime,
                "prezime": profil.prezime,
                "lozinka": profil.lozinka,
                "korisnicke_informacije": profil.korisnicke_informacije,
                "spol": profil.spol,
                "rodendan": profil.rodendan,
                "drzava": profil.drzava,
                "zupanija": profil.zupanija,
                "grad": profil.grad,
                "telefon": profil.telefon,
                "adresa": profil.adresa,
                "postanski_broj": profil.postanski_broj,
                "status": profil.status,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Greška pri dodavanju profila u bazu: " + str(e))

def dohvati_id():
    response = table.scan(ProjectionExpression="korisnik_ID")
    korisnici = response.get("Items", [])

    if not korisnici:
        return 1
    return max(int(kor["korisnik_ID"]) for kor in korisnici) + 1