import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException
from passlib.context import CryptContext
from models import Recenzija

s3 = boto3.client('s3')

client = boto3.client('dynamodb',
    endpoint_url='http://dynamodb:8000',            
    #'http://host.docker.internal:8000',    
    #endpoint_url="http://localhost:8000",
    region_name='eu-central-1',
    aws_access_key_id='dummy',
    aws_secret_access_key='dummy')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_lozinka(lozinka: str):
    return pwd_context.hash(lozinka)

def tablica_postoji(tablica_ime):
    try:
        response = client.describe_table(TableName=tablica_ime)
        return response['Table']['TableStatus'] in ['CREATING', 'UPDATING', 'ACTIVE']
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            return False
        else:
            raise

def cekaj_na_tablicu(tablica_ime):
    waiter = client.get_waiter('table_exists')
    waiter.wait(TableName=tablica_ime)
    
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
            cekaj_na_tablicu('korisnici_db')        
        
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
            
            cekaj_na_tablicu('poruke_db')
            
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

def kreiraj_tablicu_recenzije():
    table_name = "recenzije_sa_ocjenama_db"
    
    try:
        
        existing_tables = client.list_tables()['TableNames']
        if table_name in existing_tables:
            
            return
        
        client.create_table(
            TableName='recenzije_sa_ocjenama_db',
             KeySchema=[
                {'AttributeName': 'korisnik_prima_recenziju', 'KeyType': 'HASH'},
                {'AttributeName': 'korisnik_salje_recenziju', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'korisnik_prima_recenziju', 'AttributeType': 'S'},
                {'AttributeName': 'korisnik_salje_recenziju', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
            
    except Exception as e:
        print(f"Greška pri kreiranju tablice: {e}")

kreiraj_tablicu_recenzije()

recenzije_dummy = [
    {
        "korisnik_prima_recenziju": "ivan",
        "korisnik_salje_recenziju": "ana",
        "recenzija": "Super kolekcija! Drago mi je što sam razmijenila sličice s tobom.",
        "ocjena": 5
    },
    {
        "korisnik_prima_recenziju": "ana",
        "korisnik_salje_recenziju": "marko",
        "recenzija": "Brza dostava i odličan dogovor. Preporučam!",
        "ocjena": 4
    },
    {
        "korisnik_prima_recenziju": "marko",
        "korisnik_salje_recenziju": "ivan",
        "recenzija": "Sviđa mi se tvoja kolekcija! Samo malo sporije slanje.",
        "ocjena": 3
    }
]

def ubaci_recenzije():
    for recenzija in recenzije_dummy:
        try:
            client.put_item(
                TableName='recenzije_sa_ocjenama_db',
                Item={
                    'korisnik_prima_recenziju': {'S': recenzija['korisnik_prima_recenziju']},
                    'korisnik_salje_recenziju': {'S': recenzija['korisnik_salje_recenziju']},
                    'recenzija': {'S': recenzija['recenzija']},
                    'ocjena': {'N': str(recenzija['ocjena'])}
                }
            )
            
        except Exception as e:
            print(f"Greška pri unosu recenzije: {e}")

ubaci_recenzije()


def kreiraj_tablicu_dostupne_kolekcije():
    table_name= "dostupne_kolekcije"
    try:
        existing_tables = client.list_tables()['TableNames']
        if table_name in existing_tables:
            
            return
        
        client.create_table(
            TableName='dostupne_kolekcije',
            KeySchema=[
                {'AttributeName': 'kolekcija_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'kolekcija_id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
       
    except Exception as e:
        print(f"Greška pri kreiranju tablice: {e}")

kreiraj_tablicu_dostupne_kolekcije()

def dodaj_dostupne_kolekcije():
    dostupne_kolekcije = [
        {"kolekcija_naziv": "KONZUM Zvjerići 3 Safari"},
        {"kolekcija_naziv": "LaLiga 2024-2025"},
        {"kolekcija_naziv": "FIFA 365 2025"},
        {"kolekcija_naziv": "Foot 2024-2025"},
        {"kolekcija_naziv": "Hrvatska Nogometna Liga 2024-2025"},
        {"kolekcija_naziv": "English Premier League 2024-2025"},
        {"kolekcija_naziv": "Calciatori 2024-2025"},
        {"kolekcija_naziv": "UEFA Champions League 2024-2025"}
    ]

    id_count=1
    
    for kolekcija in dostupne_kolekcije:
        naziv = kolekcija.get('kolekcija_naziv')
        if not naziv:
            
            continue
        
        kolekcija_id=str(id_count)
        try:
            client.put_item(
                TableName='dostupne_kolekcije',
                Item={'kolekcija_id': {'S': kolekcija_id},
                      'kolekcija_naziv': {'S': naziv}
                }
            )
            
        except Exception as e:
            print(f" Greška pri unosu kolekcije '{naziv}': {e}")

        id_count +=1

dodaj_dostupne_kolekcije()

def kreiraj_tablicu_kolekcije_brojevi():
    
    table_name='kolekcije_brojevi'
    try:
        client.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'kolekcija_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'kolekcija_id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print(f"Tablica '{table_name}' uspješno kreirana.")
   

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceInUseException':
            
            print(f"Tablica '{table_name}' već postoji ili se kreira.")
        else:
            print(f"Greška pri kreiranju tablice '{table_name}': {e}")
            raise e 
    except Exception as e:
        
        print(f"Greška prilikom inicijalizacije tablice '{table_name}': {e}")
        raise e 
        
kreiraj_tablicu_kolekcije_brojevi()

def dodaj_kolekcije_brojevi():
    kolekcije_sa_brojevima = [
        {"kolekcija_naziv": "KONZUM Zvjerići 3 Safari", "brojevi": list(range(1, 131))},
        {"kolekcija_naziv": "LaLiga 2024-2025", "brojevi": list(range(1, 774))},
        {"kolekcija_naziv": "FIFA 365 2025", "brojevi": list(range(1, 423))},
        {"kolekcija_naziv": "Foot 2024-2025", "brojevi": list(range(1, 577))},
        {"kolekcija_naziv": "Hrvatska Nogometna Liga 2024-2025", "brojevi": list(range(1, 361))},
        {"kolekcija_naziv": "English Premier League 2024-2025", "brojevi": list(range(1, 765))},
        {"kolekcija_naziv": "Calciatori 2024-2025", "brojevi": list(range(1, 927))},
        {"kolekcija_naziv": "UEFA Champions League 2024-2025", "brojevi": list(range(1, 664))}
    ]
    
    id_count=1
    for kolekcija in kolekcije_sa_brojevima:
        naziv = kolekcija.get('kolekcija_naziv')
        brojevi = kolekcija.get('brojevi', [])
        kolekcija_id = str(id_count)

        if not naziv:
            
            continue
        try:
            
            client.put_item(
                TableName='kolekcije_brojevi',
                Item={
                    'kolekcija_id': {'S': kolekcija_id},
                    'kolekcija_naziv': {'S': naziv},
                    'brojevi': {'L': [{'N': str(b) } for b in brojevi]}
                }
            )
            
        except Exception as e:
            print(f"Greška pri unosu kolekcije '{naziv}': {e}")

        id_count += 1
        
dodaj_kolekcije_brojevi()

def kreiraj_tablicu_korisnik_nedostaje():
    try:
        
        try:
            client.describe_table(TableName='korisnik_nedostaje_db')
            
            return
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                pass
            else:
                raise e
        
        client.create_table(
            TableName='korisnik_nedostaje_db',
            KeySchema=[
                {'AttributeName': 'korisnicko_ime', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'korisnicko_ime', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
    except Exception as e:
        print(f"Greška pri kreiranju tablice")

kreiraj_tablicu_korisnik_nedostaje()

def unos_korisnik_nedostaje():
    korisnici_nedostaje = [
        {
            "korisnicko_ime": "ivan123",
            "kolekcija_naziv": "FIFA 365 2025",
            "brojevi": [2, 5, 7, 20]
        },
        {
            "korisnicko_ime": "ivan123",
            "kolekcija_naziv": "UEFA Champions League 2024-2025",
            "brojevi": [11, 66, 120]
        },
        {
            "korisnicko_ime": "ana_nogomet",
            "kolekcija_naziv": "UEFA Champions League 2024-2025",
            "brojevi": [1, 6, 12]
        },
        {
            "korisnicko_ime": "marko_kolekcionar",
            "kolekcija_naziv": "LaLiga 2024-2025",
            "brojevi": [4, 9, 15, 33]
        }
    ]

    for korisnik in korisnici_nedostaje:
        try:
            client.put_item(
                TableName='korisnik_nedostaje_db',
                Item={
                    'korisnicko_ime': {'S': korisnik['korisnicko_ime']},
                    'kolekcija_naziv': {'S': korisnik['kolekcija_naziv']},
                    'brojevi': {'L': [{'N': str(broj)} for broj in korisnik['brojevi']]}
                }
            )
            
        except Exception as e:
            print(f" Greška pri unosu korisnika {korisnik['korisnicko_ime']}: {str(e)}")

unos_korisnik_nedostaje()

def provjera_tablica_korisnik_duple_postoji(ime_tablice):
    try:
        client.describe_table(TableName=ime_tablice)
        
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            
            return False
        else:
            
            raise

def kreiraj_korisnik_duple_db():
    ime_tablice="korisnik_duple_db"
    
    if not provjera_tablica_korisnik_duple_postoji(ime_tablice):
        try:
            response = client.create_table(
                TableName="korisnik_duple_db",
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
                }],
                ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
            
            return response
        except ClientError as e:
            print("Greška pri kreiranju tablice:", e.response['Error']['Message'])
            raise

kreiraj_korisnik_duple_db()

def unos_korisnik_duple():
    
    korisnici_duple = [
        {
            "korisnicko_ime": "ivan123",
            "kolekcija_naziv": "FIFA 365 2025",
            "brojevi": [22, 55, 77, 200]
        },
        {
            "korisnicko_ime": "ana_nogomet",
            "kolekcija_naziv": "UEFA Champions League 2024-2025",
            "brojevi": [11, 66, 120]
        },
        {
            "korisnicko_ime": "marko_kolekcionar",
            "kolekcija_naziv": "LaLiga 2024-2025",
            "brojevi": [44, 99, 150, 333]
        },
        {
            "korisnicko_ime": "petra_fan",
            "kolekcija_naziv": "Premier League 2024-2025",
            "brojevi": [111, 188, 211]
        },
        {
            "korisnicko_ime": "luka_futbol",
            "kolekcija_naziv": "Bundesliga 2024-2025",
            "brojevi": [33, 88, 140, 277]
        }
    ]
    for korisnik in korisnici_duple:
        try:
        
            client.put_item(
                TableName='korisnik_duple_db',
                Item={
                    'korisnicko_ime': {'S': korisnik['korisnicko_ime']},
                    'kolekcija_naziv': {'S': korisnik['kolekcija_naziv']},
                    'brojevi': {'L': [{'N': str(broj)} for broj in korisnik['brojevi']]}
                }
            )
    
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ažuriranje nije uspjelo: {str(e)}")


unos_korisnik_duple()

def dohvati_kolekciju_dynamo():
    try:
        response = client.scan(TableName="dostupne_kolekcije")
    
        items = response.get('Items', [])
        
    
        if not items:
            return {"poruka": "Kolekcija ne sadrži ništa", "kolekcije": []}

        kolekcije = [item['kolekcija_naziv']['S'] for item in items]

        return {"kolekcije": kolekcije}   
    
    except ClientError as e:
        print(f"Pogreška pri dohvatu podataka {e}")
        
def dohvati_kolekciju_sa_brojevima_dynamo(kolekcija_naziv: str):
    
    response = client.scan(TableName="kolekcije_brojevi",
                                FilterExpression="kolekcija_naziv = :naziv",
        ExpressionAttributeValues={":naziv": {"S": kolekcija_naziv}})
    
    items = response.get("Items", [])
    
    if not items:
        raise HTTPException(status_code=400, detail="Kolekcija ne postoji!") 
    
    item = items[0]
    
    brojevi = item.get("brojevi", {}).get('L', [])
    
    brojevi_lista = [int(broj["N"]) for broj in brojevi]
    
    return {"kolekcija_naziv": kolekcija_naziv, "brojevi": brojevi_lista}

def dodaj_kolekciju_dynamo(kolekcija_naziv: str, broj: int):
    response = client.scan(TableName="dostupne_kolekcije",
                            FilterExpression="kolekcija_naziv = :naziv",
                            ExpressionAttributeValues={":naziv": {"S": kolekcija_naziv}})
    
    if response.get("Items"):
        
        raise HTTPException(status_code=400, detail="Kolekcija postoji!") 
    
    response_scan = client.scan(TableName="kolekcije_brojevi")
    broj_kolekcija = len(response_scan.get("Items", [])) + 1
    kolekcija_id=str(broj_kolekcija)  
    
    dodani_brojevi=list(range(1, broj+1))
        
    client.put_item(TableName="kolekcije_brojevi", 
                    Item={"kolekcija_id": {"S": kolekcija_id},
                          "kolekcija_naziv": {"S": kolekcija_naziv},
                          "brojevi": {"L": [{"N": str(broj)} for broj in dodani_brojevi]}})
                    
   
    return {"kolekcija_naziv": kolekcija_naziv, "brojevi": dodani_brojevi, "kolekcija_id": kolekcija_id}

def kolekcija_izmjena_dynamo(kolekcija_id: str, kolekcija_naziv: str, brojevi: list[int]):
   try:
        response = client.get_item(TableName="kolekcije_brojevi", Key={"kolekcija_id": { "S": kolekcija_id}})
       
        item = response.get("Item")

        if not item:
            raise HTTPException(status_code=404, detail="Kolekcija ne postoji!")
    
        postojeci_brojevi = item.get("brojevi", {}).get("L", [])
        postojeci_brojevi = [int(broj["N"]) for broj in postojeci_brojevi]
    
        postojeci_brojevi_u_db=[broj for broj in brojevi if broj in postojeci_brojevi]
        novi_brojevi = [broj for broj in brojevi if broj not in postojeci_brojevi]

        if novi_brojevi:
       
            azurirani_brojevi = postojeci_brojevi + novi_brojevi

            client.update_item(
                TableName="kolekcije_brojevi",
                Key={"kolekcija_id": {"S": kolekcija_id}},
                UpdateExpression="SET brojevi = :val",
                ExpressionAttributeValues={":val": {"L": [{"N": str(broj)} for broj in azurirani_brojevi]}}
            )

            return {"kolekcija": kolekcija_naziv, "dodani_brojevi": novi_brojevi, "kolekcija_id": kolekcija_id}

        else:
            return {"poruka" : "Ne postoje novi brojevi za dodati u kolekciju"}
        
   except Exception as e:
       raise HTTPException(status_code=500, detail=f"Ažuriranje nije uspjelo {e}")

def unos_nedostaje_dynamo(korisnicko_ime: str, kolekcija_naziv: str, brojevi: list[int]):
    try:
        response=client.get_item(TableName="korisnik_nedostaje_db", Key={"korisnicko_ime": {"S":  korisnicko_ime}})
        
        item=response.get("Item")
          
        if item:
                   
            postojeci_brojevi = item.get("brojevi", {}).get("L", [])
            postojeci_brojevi_ = [int(broj["N"]) for broj in postojeci_brojevi]
        
            novi_brojevi = [broj for broj in brojevi if broj not in postojeci_brojevi_]
        
            if novi_brojevi:
            
                pretvorba_brojeva = postojeci_brojevi + [{"N": str(broj)} for broj in novi_brojevi]

                client.update_item(TableName="korisnik_nedostaje_db",
                Key={"korisnicko_ime": {"S": korisnicko_ime}},
                UpdateExpression="SET brojevi = :val, kolekcija_naziv = :naziv",
                ExpressionAttributeValues={":val": {"L": pretvorba_brojeva},":naziv": {"S": kolekcija_naziv}
                    }
                )
                return {"korisnicko_ime": korisnicko_ime, "kolekcija_naziv": kolekcija_naziv, "dodani_brojevi": novi_brojevi}
            else:
                return {"poruka": "Ovi brojevi već postoje!"}
        else:
        
            client.put_item(TableName="korisnik_nedostaje_db",
                Item={
                "korisnicko_ime": {"S":   korisnicko_ime},
                "kolekcija_naziv": {"S": kolekcija_naziv},
                "brojevi":  {"L": [{"N": str(broj)} for broj in brojevi]}
                }
            
        )
        
            return {"korisnicko_ime": korisnicko_ime, "kolekcija_naziv": kolekcija_naziv, "dodani_brojevi": brojevi}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ažuriranje nije uspjelo: {str(e)}")

def unos_duple_dynamo(korisnicko_ime: str, kolekcija_naziv: str, brojevi: list[int]):
    try:
        response=client.get_item(TableName="korisnik_duple_db", Key={"korisnicko_ime":{"S": korisnicko_ime}})
    
        if "Item" in response:
            item = response["Item"]
        
            postojeci_brojevi = item.get("brojevi", {}).get("L", [])
            
            postojeci_brojevi = [broj["N"] for broj in postojeci_brojevi]
        
            novi_brojevi = [broj for broj in brojevi if str(broj) not in postojeci_brojevi]
            
            if novi_brojevi:
            
                azurirani_brojevi = postojeci_brojevi + novi_brojevi

                client.update_item(TableName="korisnik_duple_db",
                Key={"korisnicko_ime": {"S" : korisnicko_ime}},
                UpdateExpression="SET brojevi = :val",
                ExpressionAttributeValues={":val": {"L": [{"N": str(broj)} for broj in azurirani_brojevi]}}
            )
                return {"korisnicko_ime": korisnicko_ime, "kolekcija_naziv":kolekcija_naziv, "dodani_brojevi": novi_brojevi}
            
            else:
                return {"poruka": "Ovi brojevi već postoje!"}
        
        else:
        
            client.put_item(TableName="korisnik_duple_db",
                Item={
                "korisnicko_ime":{"S": korisnicko_ime},
                "kolekcija_naziv":{"S": kolekcija_naziv},
                "brojevi": {"L": [{"N": str(broj)} for broj in brojevi]}
            }
        )
        
        return {"korisnicko_ime": korisnicko_ime, "kolekcija_naziv": kolekcija_naziv, "dodani_brojevi": brojevi}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ažuriranje nije uspjelo: {str(e)}")
    
def brisanje_nedostaje_dynamo(korisnicko_ime: str, kolekcija_naziv: str, brojevi: list[int]):
    try:
        
        response=client.get_item(TableName="korisnik_nedostaje_db",
            Key={"korisnicko_ime":{"S": korisnicko_ime}})
    
        if "Item" in response:
        
            item=response["Item"]
            
            postojeca_kolekcija_naziv = item.get("kolekcija_naziv", {}).get("S")
            
            if postojeca_kolekcija_naziv != kolekcija_naziv:
                raise HTTPException(status_code= 400, detail=f"Kolekcija {kolekcija_naziv} ne postoji za korisnika {korisnicko_ime}")
            
            postojeci_brojevi_dynamo=item.get("brojevi", {}).get("L", [])
            
            postojeci_brojevi = [int(broj["N"]) for broj in postojeci_brojevi_dynamo]
           
            nepostojeci_brojevi= [broj for broj in brojevi if broj not in postojeci_brojevi]
           
            if nepostojeci_brojevi:
                raise HTTPException(status_code=400, detail= f"Brojevi {nepostojeci_brojevi} nisu pronađeni u bazi brojeva koji nedostaju")
            
            uklonjeni_brojevi = [broj for broj in brojevi if broj in postojeci_brojevi]

            azurirani_brojevi = [broj for broj in postojeci_brojevi if broj not in uklonjeni_brojevi]
            
            azurirani_brojevi_dynamo=[{"N": str(broj)} for broj in azurirani_brojevi]
        
            client.update_item(TableName="korisnik_nedostaje_db",
                Key={"korisnicko_ime": {"S": korisnicko_ime}},
                                    UpdateExpression="SET brojevi= :val",
                                    ExpressionAttributeValues={
                                        ":val": {"L":  azurirani_brojevi_dynamo}})
        
            return {"kolekcija_naziv": kolekcija_naziv, "obrisani_br": uklonjeni_brojevi}
        
        else:
            return {"poruka": "Nepostojeci korisnik ili kolekcija!"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brisanje nije uspjelo: {str(e)}")

def brisanje_duple_dynamo(korisnicko_ime: str, kolekcija_naziv: str, brojevi: list[int]):
    
    try:
                
        response=client.get_item(TableName="korisnik_duple_db",
        Key={"korisnicko_ime": {"S": korisnicko_ime}})
    
        if "Item" in response:
            item=response["Item"]
            
            postojeca_kolekcija_naziv = item.get("kolekcija_naziv", {}).get("S")
            if postojeca_kolekcija_naziv != kolekcija_naziv:
                raise HTTPException(status_code=400, detail=f"Kolekcija {kolekcija_naziv} ne postoji za korisnika {korisnicko_ime}")
            
            postojeci_brojevi = item.get("brojevi", {}).get("L", [])
                  
            brojevi_pretvorba = [broj["N"] for broj in postojeci_brojevi]
            brojevi_pretvorba_str=[str(broj) for broj in brojevi]
            
                                 
            nepostojeci_brojevi = [broj for broj in brojevi_pretvorba_str if broj not in brojevi_pretvorba]
            
            if nepostojeci_brojevi:
                
                raise HTTPException(status_code=400, detail=f"Brojevi {', '.join(map(str, nepostojeci_brojevi))} nisu pronađeni u bazi duplih brojeva")
           
            azurirani_brojevi = [{"N": broj} for broj in brojevi_pretvorba if broj not in brojevi]
            
            uklonjeni_brojevi=[broj for broj in brojevi_pretvorba if broj in brojevi_pretvorba_str]           
            
            client.update_item(TableName="korisnik_duple_db",
                Key={"korisnicko_ime":  {"S": korisnicko_ime}},
                                    UpdateExpression="SET brojevi= :val",
                                    ExpressionAttributeValues={
                                        ":val": {"L": azurirani_brojevi}}
            )
            
            return {"kolekcija_naziv": kolekcija_naziv, "obrisani_br": uklonjeni_brojevi}
        
        else:
            return {"poruka": "Nepostojeci korisnik ili kolekcija!"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brisanje nije uspjelo: {str(e)}")

def trazi_zamjenu_dynamo(korisnicko_ime: str, korisnik_posjeduje: str, kolekcija: str):
    try:  
        response_nedostaje=client.get_item(TableName="korisnik_nedostaje_db",
        Key={"korisnicko_ime":{"S": korisnicko_ime}})
    
        if "Item" not in response_nedostaje:  
            raise HTTPException(status_code=404, detail= "Korisnik nije pronađen!")
        
        if korisnicko_ime == korisnik_posjeduje:
            raise HTTPException(status_code=404, detail= "Nije moguću unijeti dva puta isto korisničko ime" )
        
        nedostaju_slicice=response_nedostaje["Item"].get("brojevi", {}).get("L", [])
        nedostaju_slicice = [int(broj["N"]) for broj in nedostaju_slicice]
        
        zamjene={}
    
        response_duple=client.scan(TableName="korisnik_duple_db",
                                FilterExpression="kolekcija_naziv= :kolekcija",
                                ExpressionAttributeValues={":kolekcija": {"S":kolekcija}})
    
        for item in response_duple.get("Items", []):
            korisnik_nudi = item.get("korisnicko_ime", {}).get("S")
            brojevi = item.get("brojevi", {}).get("L", [])
            brojevi = [int(broj["N"]) for broj in brojevi] 
            
            dostupne_slicice=[broj for broj in brojevi if broj in nedostaju_slicice]
        
            if dostupne_slicice:
            
                if korisnik_nudi and korisnik_nudi != korisnicko_ime:
                    if korisnik_nudi not in zamjene:
                        zamjene[korisnik_nudi]=[]
                    zamjene[korisnik_nudi].extend(dostupne_slicice)
        
        if not zamjene:
            return {"poruka": "Nema dostupnih zamjena!"}
                      
        return {"posjeduje": korisnik_posjeduje, "traži": korisnicko_ime, "kolekcija": kolekcija, "dostupne_sličice": dostupne_slicice }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Došlo je do pogreške: {str(e)}")
        
def dodavanje_recenzije_dynamo(recenzija: Recenzija):
    if not recenzija.korisnik_prima_recenziju:
        raise HTTPException(status_code=404, detail="Potrebno je unijeti korisnika na kojega se recenzija odnosi!")
    
    try:
    
        korisnik_postoji=client.get_item(TableName="korisnici_db",
            Key={"korisnicko_ime":{"S":recenzija.korisnik_prima_recenziju}})
    
        if "Item" not in korisnik_postoji:
            raise HTTPException(status_code=404, detail="Sa korisnikom niste mogli obaviti zamjenu!")
    
        client.put_item(TableName="recenzije_sa_ocjenama_db",
            Item={"korisnik_salje_recenziju":{"S":recenzija.korisnik_salje_recenziju},
                  "korisnik_prima_recenziju":{"S":recenzija.korisnik_prima_recenziju},
                    "recenzija":{"S": recenzija.recenzija},
                    "ocjena":{"N": str(recenzija.ocjena)}})
                    
    
        return  {"korisnik_prima_recenziju": recenzija.korisnik_prima_recenziju,
                "korisnik_salje_recenziju": recenzija.korisnik_salje_recenziju,
                "recenzija": recenzija.recenzija,
                "ocjena": recenzija.ocjena}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška prilikom dohvaćanja ocjena: {str(e)}")
    
def prikaz_recenzija_dynamo(korisnik_prima_recenziju: str, korisnik_salje_recenziju: str):
    try:
        response = client.query(
            TableName="recenzije_sa_ocjenama_db",
            KeyConditionExpression="korisnik_prima_recenziju = :val AND korisnik_salje_recenziju = :val2",  # Pretražuje prema oba ključa
          ExpressionAttributeValues={
            ":val": {"S": korisnik_prima_recenziju}, 
            ":val2": {"S": korisnik_salje_recenziju}}
        )
        items=response.get("Items", [])
    
        if not items:
            raise HTTPException(status_code=404, detail="Korisnik nema niti jednu recenziju")
        
        recenzije = [
            {
                "korisnik_prima_recenziju": item["korisnik_prima_recenziju"]["S"],
                "korisnik_salje_recenziju": item["korisnik_salje_recenziju"]["S"],
                "ocjena": int(item["ocjena"]["N"]),
                "recenzija": item["recenzija"]["S"]
            }
            for item in items
        ]
        
        ocjene = [int(item["ocjena"]["N"]) for item in items]

        prosjek = sum(ocjene) / len(ocjene) if ocjene else 0

        return {"korisnik_prima_recenziju": korisnik_prima_recenziju, "recenzija": recenzije, "ocjena": round(prosjek, 2)}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška prilikom dohvaćanja ocjena: {str(e)}")

def prikaz_ocjene_dynamo(korisnik_prima_recenziju: str):
    try:
        response = client.scan(
            TableName="recenzije_sa_ocjenama_db",
            FilterExpression="korisnik_prima_recenziju = :val",
            ExpressionAttributeValues={":val": {"S": korisnik_prima_recenziju}}
        )
        
        items = response.get("Items", [])
    
        if not items:
            raise HTTPException(status_code=404, detail="Korisnik nema niti jednu ocjenu")
    
        
        ocjene = [int(item["ocjena"]["N"]) for item in items]
    
       
        prosjek = sum(ocjene) / len(ocjene) if ocjene else 0
    
        return {
            "korisnik": korisnik_prima_recenziju,
            "prosječna_ocjena": round(prosjek, 2)
        }
    
    except Exception as e:
        
        raise HTTPException(status_code=500, detail=f"Greška prilikom dohvaćanja ocjena: {str(e)}")
    
