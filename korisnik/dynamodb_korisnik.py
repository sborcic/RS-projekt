import boto3
from botocore.exceptions import ClientError

from models import Korisnik_profil, Korisnik
from fastapi import HTTPException

from passlib.context import CryptContext

s3 = boto3.client('s3')

client = boto3.client('dynamodb', 
    endpoint_url= 'http://dynamodb:8000',
    #'http://host.docker.internal:8000',
    region_name='eu-central-1',
    aws_access_key_id='dummy',
    aws_secret_access_key='dummy')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_lozinka(lozinka: str):
    return pwd_context.hash(lozinka)

def kreiraj_korisnici_db():
    try:
        existing_tables = client.list_tables()['TableNames']
        if 'korisnici_db' in existing_tables:
            print("Tablica 'korisnici_db' već postoji.")
            return
        
        table = client.create_table(
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
        
        return table
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"Tablica 'korisnici_db' već postoji.")
        else:
            print(f"Došlo je do neočekivane greške pri kreiranju tablice: {e}")
            raise

def dodaj_korisnika_dynamo():
        
    korisnici = [
        {
            "korisnik_ID": "2",
            "korisnicko_ime": "marko123",
            "lozinka": "lozinka1",
            "ime": "Marko",
            "prezime": "Marković",
            "email": "marko@example.com"
        },
        {
            "korisnik_ID": "3",
            "korisnicko_ime": "ana25",
            "lozinka": "lozinka2",
            "ime": "Ana",
            "prezime": "Anić",
            "email": "ana@example.com"
        },
        {
            "korisnik_ID": "4",
            "korisnicko_ime": "ivan40",
            "lozinka": "lozinka3",
            "ime": "Ivan",
            "prezime": "Ivić",
            "email": "ivan@example.com"
        },
        {
            "korisnik_ID": "5",
            "korisnicko_ime": "petra22",
            "lozinka": "lozinka4",
            "ime": "Petra",
            "prezime": "Petrović",
            "email": "petra@example.com"
        },
        {
            "korisnik_ID": "6",
            "korisnicko_ime": "luka35",
            "lozinka": "lozinka5",
            "ime": "Luka",
            "prezime": "Lukić",
            "email": "luka@example.com"
        }]
    
    for korisnik in korisnici:
        
        lozinka_u_hash=hash_lozinka(korisnik["lozinka"])
        
        client.put_item(
            TableName="korisnici_db",
            Item={
                "korisnicko_ime": {"S": korisnik["korisnicko_ime"]},
                "korisnik_ID": {"S": korisnik["korisnik_ID"]},
                "lozinka": {"S": lozinka_u_hash},
                "ime": {"S": korisnik["ime"]},
                "prezime": {"S": korisnik["prezime"]},
                "email": {"S": korisnik["email"]}
            }
        )
        

kreiraj_korisnici_db()
dodaj_korisnika_dynamo()
    
def dohvati_korisnika_dynamo(korisnicko_ime: str):
    try:
        response = client.get_item(
            TableName="korisnici_db",
                Key={"korisnicko_ime": {"S": korisnicko_ime}}
        )
        item = response.get("Item")
        if not item:
            raise HTTPException(status_code=404, detail="Korisnik nije pronađen")
        return {"korisnicko_ime": item["korisnicko_ime"]["S"],
            "lozinka": item["lozinka"]["S"],
            "ime": item["ime"]["S"],
            "prezime": item["prezime"]["S"],
            "email": item["email"]["S"],
            "korisnik_ID": int(item["korisnik_ID"]["S"])
        }
    
    except Exception as e:
        print("Greška u dohvati_korisnika_dynamo:", str(e))
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju korisnika: {str(e)}")

def dohvati_id():
    try:
        
        response = client.scan(TableName="korisnici_db")

        korisnici = response.get("Items", [])
        
        if not korisnici:
            
            return 1

        najveci_id = 0

        for korisnik in korisnici:
            korisnik_id_str = korisnik.get("korisnik_ID", {}).get("S")
            if korisnik_id_str and korisnik_id_str.isdigit():
                korisnik_id = int(korisnik_id_str)
                if korisnik_id > najveci_id:
                    najveci_id = korisnik_id

        return najveci_id + 1

    except ClientError as e:
        print("Greška pri dohvaćanju podataka iz baze:", e)
        return None

def korisnik_registracija_dynamo(korisnik: Korisnik):
            
    response= client.scan(TableName="korisnici_db")
    korisnici = response.get("Items", [])
    
    
    for korisnik_pojedinacni in korisnici:
        email_baza = korisnik_pojedinacni.get("email", {}).get("S") 
        korisnicko_ime_baza = korisnik_pojedinacni.get("korisnicko_ime", {}).get("S")
        
        if email_baza == korisnik.email:
            raise HTTPException(status_code=400, detail="Korisnik sa tim emailom postoji!")
        
        if korisnicko_ime_baza == korisnik.korisnicko_ime:
            raise HTTPException(status_code=400, detail="Korisnik sa tim korisnickim imenom postoji")
        
        
    specijalni_znakovi = set("!\"#$%&/()=?*")

    if not any(znak in specijalni_znakovi for znak in korisnik.lozinka):
        raise HTTPException(status_code=400, detail="Lozinka ne sadrži specijalni znak!")
    
    korisnik.lozinka = hash_lozinka(korisnik.lozinka)
    
    korisnik.korisnik_ID= dohvati_id()
    
    try:
        novi_korisnik_data = {
            "korisnicko_ime": {"S": korisnik.korisnicko_ime},
            "korisnik_ID": {"S": str(korisnik.korisnik_ID)},
            "lozinka": {"S": korisnik.lozinka},
            "ime": {"S": korisnik.ime},
            "prezime": {"S": korisnik.prezime},
            "email": {"S": korisnik.email}
        }
        client.put_item(TableName="korisnici_db", Item=novi_korisnik_data)
        
        return {"korisnik_ID": korisnik.korisnik_ID,
            "korisnicko_ime": korisnik.korisnicko_ime,
            "ime": korisnik.ime,
            "prezime": korisnik.prezime,
            "email": korisnik.email, "lozinka": "***"}

    except Exception as e:
        raise HTTPException(status_code=500, detail="Greška pri dodavanju korisnika u bazu")   
    
def azuriraj_korisnika_dynamo(korisnik: Korisnik_profil):
    try:
        update_expression = "SET "
        expression_attribute_values = {}
        expression_attribute_names = {}

        def add_field(field, value):
            nonlocal update_expression
            if value is not None:
                placeholder = f":{field}"
                name_placeholder = f"#{field}"

                expression_attribute_names[name_placeholder] = field
                expression_attribute_values[placeholder] ={"S": str(value)}
                update_expression += f"{name_placeholder} = {placeholder}, "

        
        add_field("korisnicke_informacije", korisnik.korisnicke_informacije)
        add_field("spol", korisnik.spol)
        add_field("rodendan", korisnik.rodendan.isoformat() if korisnik.rodendan else None)
        add_field("drzava", korisnik.drzava)
        add_field("zupanija", korisnik.zupanija)
        add_field("grad", korisnik.grad)
        add_field("telefon", korisnik.telefon)
        add_field("adresa", korisnik.adresa)
        add_field("postanski_broj", korisnik.postanski_broj)
        add_field("status", korisnik.status if korisnik.status else "Online")
        
        if update_expression.endswith(", "):
            update_expression = update_expression[:-2]

        if update_expression == "SET":
            raise HTTPException(status_code=400, detail="Nema podataka za ažuriranje.")

        client.update_item(
            TableName="korisnici_db",
            Key={"korisnicko_ime": {"S" : korisnik.korisnicko_ime}},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )

    except Exception as e:
        print("Greška pri ažuriranju korisnika:", e)
        raise HTTPException(status_code=500, detail="Greška pri ažuriranju korisnika: " + str(e))

def dohvati_korisnika_po_emailu_dynamo(email: str):
    response = client.scan(
        TableName="korisnici_db",
        FilterExpression="email = :email_value",
        ExpressionAttributeValues={":email_value": {"S": email}}
    )
    items = response.get("Items", [])
    
    if not items:   
        return None
    
    item = items[0]
    
    return {"korisnik_ID": item["korisnik_ID"]["S"],
        "korisnicko_ime": item["korisnicko_ime"]["S"],
            "ime": item["ime"]["S"],
            "prezime": item["prezime"]["S"],
            "email": item["email"]["S"]}

def korisnik_brisanje_dynamo(korisnicko_ime: str):
    try:
        client.delete_item(TableName="korisnici_db", Key={"korisnicko_ime":{"S": korisnicko_ime}})
        return {f"Korisnik {korisnicko_ime} je obrisan!"}
    except:
        raise HTTPException(status_code=500, detail="Greška kod brisanja korisnika!")


