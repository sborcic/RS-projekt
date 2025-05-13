import bcrypt
import types

from fastapi import APIRouter, FastAPI
from models import Poruka
import boto3
from fastapi import HTTPException
from passlib.context import CryptContext
from botocore.exceptions import ClientError


if not hasattr(bcrypt, '__about__'):    #kako se ne bi pojavljivala poruka AttributeError: module 'bcrypt' has no attribute '__about__'
    print("[INFO] Patching bcrypt: dodavanje bcrypt.__about__.__version__")
    bcrypt.__about__ = types.SimpleNamespace(__version__='4.1.0')
else:
    print("[INFO] bcrypt već ima __about__.__version__")

s3 = boto3.client('s3')

client = boto3.client('dynamodb',
    endpoint_url='http://host.docker.internal:8000',    #endpoint_url="http://localhost:8000",
    region_name='eu-central-1',
    aws_access_key_id='dummy',
    aws_secret_access_key='dummy')

app = FastAPI()

router = APIRouter(prefix=("/poruka"))  

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_lozinka(lozinka: str):
    return pwd_context.hash(lozinka)

def tablica_postoji(tablica_ime):
    try:
        client.describe_table(TableName=tablica_ime)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            return False
        else:
            raise

def kreiraj_tablice():
    if not tablica_postoji('korisnici_db'):
        try:
            client.create_table(
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
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            
        except ClientError as e:
            print(f"Greška pri stvaranju tablice 'korisnici_db': {e}")
    
    if not tablica_postoji('poruke_db'):
        try:
            client.create_table(
                TableName='poruke_db',
                KeySchema=[
                    {
                        'AttributeName': 'korisnik_primatelj',
                        'KeyType': 'HASH'
                    }
                ],
                AttributeDefinitions=[
                    {
                        'AttributeName': 'korisnik_primatelj',
                        'AttributeType': 'S'
                    }
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            
        except ClientError as e:
            print(f"Greška pri stvaranju tablice 'poruke_db': {e}")

        
kreiraj_tablice()

poruke = [
    {"korisnik_primatelj": "ana", "korisnik_posiljatelj": "ivan", "poruka": "Hej Ana, želiš li zamijeniti sličicu Ronaldo?"},
    {"korisnik_primatelj": "marko", "korisnik_posiljatelj": "ana", "poruka": "Super recenzija tvoje kolekcije, jako korisno!"},
    {"korisnik_primatelj": "ivan", "korisnik_posiljatelj": "marko", "poruka": "Imam duplikate Modrića, zanima li te?"},
    {"korisnik_primatelj": "ana", "korisnik_posiljatelj": "marko", "poruka": "Recenzija primljena, hvala ti!"},
    {"korisnik_primatelj": "marko", "korisnik_posiljatelj": "ivan", "poruka": "Zamjena prihvaćena, šaljem ti sličicu danas."},
    {"korisnik_primatelj": "ivan", "korisnik_posiljatelj": "ana", "poruka": "Stigla sličica Mbappé, hvala ti puno!"},
]


for poruka in poruke:
    client.put_item(
        TableName='poruke_db',
        Item={
            'korisnik_primatelj': {'S': poruka['korisnik_primatelj']},
            'korisnik_posiljatelj': {'S': poruka['korisnik_posiljatelj']},
            'poruka': {'S': poruka['poruka']}
        }
    )

korisnici = [
    {
        "korisnik_id": "1",
        "ime": "Ana",
        "prezime": "Anić",
        "email": "ana@example.com",
        "korisnicko_ime": "ana",
        "lozinka": "tajna123"
    },
    {
        "korisnik_id": "2",
        "ime": "Ivan",
        "prezime": "Ivić",
        "email": "ivan@example.com",
        "korisnicko_ime": "ivan",
        "lozinka": "lozinka456"
    },
    {
        "korisnik_id": "3",
        "ime": "Marko",
        "prezime": "Markić",
        "email": "marko@example.com",
        "korisnicko_ime": "marko",
        "lozinka": "marko789"
    }
]

for korisnik in korisnici:
    client.put_item(
        TableName='korisnici_db',
        Item={
            'korisnicko_ime': {'S': korisnik['korisnicko_ime']},
            'korisnik_id': {'S': korisnik['korisnik_id']},
            'ime': {'S': korisnik['ime']},
            'prezime': {'S': korisnik['prezime']},
            'email': {'S': korisnik['email']},
            'lozinka': {'S': hash_lozinka(korisnik['lozinka'])}
        }
    )

@router.post("/", response_model=Poruka)
def posalji_poruku(poruka: Poruka):
    try:
        if poruka.korisnik_posiljatelj == poruka.korisnik_primatelj:
            raise HTTPException(status_code=422, detail="Ne možete slati poruke samome sebi.")
    
        response_primatelj = client.get_item(TableName="korisnici_db",
            Key={"korisnicko_ime": {"S": poruka.korisnik_primatelj}})
    
        if "Item" not in response_primatelj:
            raise HTTPException(status_code=404, detail="Korisnik primatelj ne postoji!")
    
        response_posiljatelj= client.get_item(TableName="korisnici_db",
                                            Key={"korisnicko_ime":{"S": poruka.korisnik_posiljatelj}})
       
        if "Item" not in response_posiljatelj:
            raise HTTPException(status_code=404, detail="Korisnik posiljatelj ne postoji!")
    
    
        client.put_item(TableName="poruke_db",
            Item={"korisnik_primatelj":{"S": poruka.korisnik_primatelj},
                                "korisnik_posiljatelj":{"S": poruka.korisnik_posiljatelj},
                                "poruka":{"S": poruka.poruka}})
                                
        return {"korisnik_posiljatelj": poruka.korisnik_posiljatelj, "korisnik_primatelj": poruka.korisnik_primatelj, "poruka": poruka.poruka}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri slanju poruke: {str(e)}")

@router.get("/")
def dohvati_poruku(korisnik_primatelj: str):
    
    try:
        response=client.query(TableName="poruke_db",
            KeyConditionExpression="korisnik_primatelj  = :korisnik_primatelj",
                                ExpressionAttributeValues={":korisnik_primatelj":{"S": korisnik_primatelj}})   
    
        poruka=response.get("Items", [])
        
        if not poruka:
            raise HTTPException(status_code=404, detail="Nema poruke za ovoga korisnika!")

        rezultat = [
            {
                "korisnik_posiljatelj": item["korisnik_posiljatelj"]["S"],
                "poruka": item["poruka"]["S"]
            }
            for item in poruka
        ]
        
        return {"primatelj": korisnik_primatelj, "poruka": rezultat}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju poruka: {str(e)}")
        
app.include_router(router)