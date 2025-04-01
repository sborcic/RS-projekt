import boto3 
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from models1 import Korisnik_profil, Korisnik
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

korisnici_profil = [
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
]

with table.batch_writer() as batch:
    for korisnik in korisnici:
        batch.put_item(Item=korisnik)

with table_profil.batch_writer() as batch:
    for korisnik in korisnici_profil:
        batch.put_item(Item=korisnik)

korisnici = table.scan().get("Items", [])

print(korisnici)

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
                    'AttributeType': 'S'  # Tip atributa je string
                }
            ],
            BillingMode='PAY_PER_REQUEST'  # Koristi On-Demand kapacitet
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

def azuriraj_korisnika_dynamo(korisnik: Korisnik):
    try:
        response = table.update_item(
            Key={
                'korisnicko_ime': korisnik.korisnicko_ime
            },
            UpdateExpression="SET ime = :ime, prezime = :prezime, email = :email",
            ExpressionAttributeValues={
                ':ime': korisnik.ime,
                ':prezime': korisnik.prezime,
                ':email': korisnik.email
            },
            ReturnValues="UPDATED_NEW"
        )
        print("Korisnik ažuriran:", response)
    except Exception as e:
        print("Greška pri ažuriranju korisnika:", e)

def dodaj_profil_dynamo(profil_korisnika: Korisnik_profil):
    table_profil.put_item(
        Item={
            "email": profil_korisnika.email,
            "ime": profil_korisnika.ime,
            "prezime": profil_korisnika.prezime,
            "korisnicko_ime": profil_korisnika.korisnicko_ime,
            "lozinka": profil_korisnika.lozinka
        }
    )

def dohvati_korisnika_po_emailu_dynamo(email: str):
    response = table.query(KeyConditionExpression=Key("email").eq(email))
    items = response.get("Items", [])
    return items[0] if items else None

def dohvati_id():
    response = table.scan(ProjectionExpression="korisnik_ID")
    korisnici = response.get("Items", [])

    if not korisnici:
        return 1
    return max(int(kor["korisnik_ID"]) for kor in korisnici) + 1