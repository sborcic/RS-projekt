import boto3 
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from models1 import Korisnik_profil, Korisnik, Korisnik_ime_prezime_lozinka_email_korisnicko_ime, Poruka
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
#print(korisnici_profil)

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
        rodendan = korisnik.rođendan.isoformat() if korisnik.rođendan else None
        
        table_profil.put_item(
            Item={
                'ime': korisnik.ime,
                'prezime': korisnik.prezime,
                'email': korisnik.email,
                'lozinka': korisnik.lozinka,
                'korisnicke_informacije': korisnik.korisničke_informacije,
                'spol': korisnik.spol,
                'rodendan': rodendan,
                'drzava': korisnik.država,
                'zupanija': korisnik.županija,
                'grad': korisnik.grad,
                'telefon': korisnik.telefon,
                'adresa': korisnik.adresa,
                'postanski_broj': korisnik.postanski_broj,})
        
    except Exception as e:
        print("Greška pri ažuriranju korisnika:", e)
        raise HTTPException(status_code=500, detail="Greška pri ažuriranju korisnika: " + str(e))

def azuriraj_korisnika_dynamo1(korisnik: Korisnik_profil):
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
                expression_attribute_values[placeholder] = value
                update_expression += f"{name_placeholder} = {placeholder}, "

        # Dodaj polja koja nisu None
        add_field("ime", korisnik.ime)
        add_field("prezime", korisnik.prezime)
        add_field("lozinka", korisnik.lozinka)
        add_field("korisnicke_informacije", korisnik.korisničke_informacije)
        add_field("spol", korisnik.spol)
        add_field("rodendan", korisnik.rođendan.isoformat() if korisnik.rođendan else None)
        add_field("drzava", korisnik.država)
        add_field("zupanija", korisnik.županija)
        add_field("grad", korisnik.grad)
        add_field("telefon", korisnik.telefon)
        add_field("adresa", korisnik.adresa)
        add_field("postanski_broj", korisnik.postanski_broj)
        add_field("status", korisnik.status if korisnik.status else "Online")

        if update_expression.endswith(", "):
            update_expression = update_expression[:-2]  # makni zadnji zarez

        table_profil.update_item(
            Key={'email': korisnik.email},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )

    except Exception as e:
        print("Greška pri ažuriranju korisnika:", e)
        raise HTTPException(status_code=500, detail="Greška pri ažuriranju korisnika: " + str(e))

def dohvati_korisnika_po_emailu_dynamo(email: str):
    response = table.scan(
        FilterExpression=Key('email').eq(email)
    )
    items = response.get("Items", [])
    return items[0] if items else None

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

dostupne_kolekcije=[{'kolekcija_naziv': 'KONZUM Zvjerići 3 Safari'},
{'kolekcija_naziv': 'LaLiga 2024-2025'},
{'kolekcija_naziv': 'FIFA 365 2025'},
{'kolekcija_naziv': 'Foot 2024-2025'},
{'kolekcija_naziv': 'Hrvatska Nogometna Liga 2024-2025'},
{'kolekcija_naziv': 'English Premier League 2024-2025'},
{'kolekcija_naziv': 'Calciatori 2024-2025'},
{'kolekcija_naziv': 'UEFA Champions League 2024-2025'}]


kolekcije_sa_brojevima_db = [
    {"kolekcija_naziv": "KONZUM Zvjerići 3 Safari", "brojevi": list(range(1, 131))},
    {"kolekcija_naziv": "LaLiga 2024-2025", "brojevi": list(range(1, 774))},
    {"kolekcija_naziv": "FIFA 365 2025", "brojevi": list(range(1, 423))},
    {"kolekcija_naziv": "Foot 2024-2025", "brojevi": list(range(1, 577))},
    {"kolekcija_naziv": "Hrvatska Nogometna Liga 2024-2025", "brojevi": list(range(1, 361))},
    {"kolekcija_naziv": "English Premier League 2024-2025", "brojevi": list(range(1, 765))},
    {"kolekcija_naziv": "Calciatori 2024-2025", "brojevi": list(range(1, 927))},
    {"kolekcija_naziv": "UEFA Champions League 2024-2025", "brojevi": list(range(1, 664))}
]


korisnik_nedostaje_db = [
    {"korisnik_kolekcija":"ivan123", "kolekcija_naziv": "KONZUM Zvjerići 3 Safari", "brojevi": [1, 3, 5, 7, 8]},
    {"korisnik_kolekcija":"petra456", "kolekcija_naziv": "FIFA 365 2025", "brojevi": [10, 12, 15, 18, 20]},
    {"korisnik_kolekcija":"marko789", "kolekcija_naziv":"LaLiga 2024-2025", "brojevi": [2, 4, 6, 9]},
    {"korisnik_kolekcija": "janko123","kolekcija_naziv": "Hrvatska Nogometna Liga 2024-2025", "brojevi": [5, 6, 7, 11, 14]},
    {"korisnik_kolekcija": "lucija321","kolekcija_naziv": "English Premier League 2024-2025", "brojevi": [1, 2, 4, 8, 10]}
]

korisnik_duple_db = [
    {"korisnik_kolekcija": "ivan123", "kolekcija_naziv": "KONZUM Zvjerići 3 Safari", "brojevi_duple": [1, 3, 5, 7, 8]},
    {"korisnik_kolekcija": "petra456","kolekcija_naziv": "FIFA 365 2025", "brojevi_duple": [10, 12, 15, 18, 20]},
    {"korisnik_kolekcija": "marko789", "kolekcija_naziv": "LaLiga 2024-2025", "brojevi_duple": [2, 4, 6, 9]}]

table_kolekcije = dynamodb.Table("dostupne_kolekcije")
table_kolekcije_sa_brojevima = dynamodb.Table("kolekcije_brojevi")
table_nedostaje = dynamodb.Table("korisnik_nedostaje")
table_duple = dynamodb.Table("korisnik_duple")

for kolekcija in dostupne_kolekcije:
    kolekcija_naziv = kolekcija["kolekcija_naziv"]
    table_kolekcije.put_item(Item={"kolekcija_naziv": kolekcija_naziv})

for kolekcija in kolekcije_sa_brojevima_db:
    kolekcija_naziv = kolekcija["kolekcija_naziv"]
    brojevi = kolekcija["brojevi"]
    table_kolekcije_sa_brojevima.put_item(Item={"kolekcija_naziv": kolekcija_naziv, "brojevi": brojevi})

for korisnik in korisnik_nedostaje_db:
    korisnik_kolekcija=korisnik["korisnik_kolekcija"]
    kolekcija_naziv = korisnik["kolekcija_naziv"]
    brojevi = korisnik["brojevi"]
    table_nedostaje.put_item(Item={
       "korisnik_kolekcija":korisnik_kolekcija,
       "kolekcija_naziv":kolekcija_naziv,
       "brojevi": brojevi
   })


for korisnik in korisnik_duple_db:
    korisnik_kolekcija=korisnik["korisnik_kolekcija"]
    kolekcija_naziv = korisnik["kolekcija_naziv"]
    brojevi_duple= korisnik["brojevi_duple"]
    table_duple.put_item(Item={
       "korisnik_kolekcija":korisnik_kolekcija,
       "kolekcija_naziv":kolekcija_naziv,
       "brojevi_duple" : brojevi_duple
   })

def dohvati_kolekciju_dynamo():
    response = table_kolekcije.scan()
    print("Scan response:", response)
    items = response.get('Items', [])
    if not items:
        print("Kolekcija je prazna")
        return "Kolekcija ne sadrži ništa"
    return items    

def dohvati_kolekciju_sa_brojevima_dynamo(kolekcija_naziv: str):
    response = table_kolekcije_sa_brojevima.query(KeyConditionExpression=Key("kolekcija_naziv").eq(kolekcija_naziv))
    items = response.get('Items', [])
    
    if not items:
        
        return "Kolekcija ne sadrži ništa"
       
    return items 
    
def dodaj_kolekciju_dynamo(kolekcija_naziv: str, broj: int):
    response = table_kolekcije_sa_brojevima.get_item(Key={"kolekcija_naziv": kolekcija_naziv})
    
    if "Item" in response:
        raise HTTPException(status_code=400, detail="Kolekcija već postoji!")
    
    response = table_kolekcije.get_item(Key={"kolekcija_naziv": kolekcija_naziv})
        
    if "Item" in response:
        raise HTTPException(status_code=400, detail="Kolekcija već postoji u tablici s nazivom!")
            
    dodani_brojevi=list(range(1, broj+1))
    
    table_kolekcije_sa_brojevima.put_item(
        Item={"kolekcija_naziv": kolekcija_naziv, "brojevi": dodani_brojevi}
    )
    
    table_kolekcije.put_item(
        Item={"kolekcija_naziv": kolekcija_naziv}
    )
    return {"kolekcija_naziv": kolekcija_naziv, "brojevi": dodani_brojevi}

def kolekcija_izmjena_dynamo(kolekcija_naziv: str, brojevi: list[int]):
    response = table_kolekcije_sa_brojevima.get_item(Key={"kolekcija_naziv": kolekcija_naziv})
    item = response.get("Item")

    if not item:
        raise HTTPException(status_code=404, detail="Kolekcija ne postoji!")
    
    postojeci_brojevi = item.get("brojevi", [])
    
    postojeci_brojevi_u_db=[broj for broj in brojevi if broj in postojeci_brojevi]
    novi_brojevi = [broj for broj in brojevi if broj not in postojeci_brojevi]

    if novi_brojevi:
       
        azurirani_brojevi = postojeci_brojevi + novi_brojevi

        table_kolekcije_sa_brojevima.update_item(
            Key={"kolekcija_naziv": kolekcija_naziv},
            UpdateExpression="SET brojevi = :val",
            ExpressionAttributeValues={":val": azurirani_brojevi}
        )

        table_kolekcije_sa_brojevima.update_item(
            Key={"kolekcija_naziv": kolekcija_naziv},
            UpdateExpression="SET brojevi = :val",
            ExpressionAttributeValues={":val": azurirani_brojevi}
        )

        return {"kolekcija": kolekcija_naziv, "dodani_brojevi": novi_brojevi}

    else:
        return {"poruka" : "ne postoje novi brojevi za dodati u kolekciju"}
    
def unos_nedostaje_dynamo(korisnicko_ime: str, kolekcija_naziv: str, brojevi: list[int]):
    response=table.get_item(Key={"korisnicko_ime":korisnicko_ime})
    
    if 'Item' in response:
        item = response['Item']
        postojeci_brojevi = item.get("brojevi", [])
        
        novi_brojevi = [broj for broj in brojevi if broj not in postojeci_brojevi]
        
        if novi_brojevi:
            
            azurirani_brojevi = postojeci_brojevi + novi_brojevi

            table_nedostaje.update_item(
                Key={"korisnik_kolekcija": korisnik_kolekcija},
                UpdateExpression="SET brojevi = :val",
                ExpressionAttributeValues={":val": azurirani_brojevi}
            )
            return {"korisnicko_ime": korisnicko_ime, "kolekcija_naziv":kolekcija_naziv, "dodani_brojevi": novi_brojevi}
        else:
            return {"poruka": "Ovi brojevi već postoje!"}
    else:
        
        table_nedostaje.put_item(
            Item={
                "korisnik_kolekcija": korisnik_kolekcija,
                "kolekcija_naziv": kolekcija_naziv,
                "brojevi": brojevi
            }
        )
def unos_duple_dynamo(korisnicko_ime: str, kolekcija_naziv: str, brojevi: list[int]):
    response=table.get_item(Key={"korisnicko_ime":korisnicko_ime})
    
    if 'Item' in response:
        item = response['Item']
        postojeci_brojevi = item.get("brojevi", [])
        
        novi_brojevi = [broj for broj in brojevi if broj not in postojeci_brojevi]
        
        if novi_brojevi:
            
            azurirani_brojevi = postojeci_brojevi + novi_brojevi

            table_duple.update_item(
                Key={"korisnik_kolekcija": korisnik_kolekcija},
                UpdateExpression="SET brojevi = :val",
                ExpressionAttributeValues={":val": azurirani_brojevi}
            )
            return {"korisnicko_ime": korisnicko_ime, "kolekcija_naziv":kolekcija_naziv, "dodani_brojevi": novi_brojevi}
        else:
            return {"poruka": "Ovi brojevi već postoje!"}
    else:
        
        table_duple.put_item(
            Item={
                "korisnik_kolekcija": korisnik_kolekcija,
                "kolekcija_naziv": kolekcija_naziv,
                "brojevi": brojevi
            }
        )
def brisanje_nedostaje_dynamo(korisnicko_ime: str, kolekcija_naziv: str, brojevi: list[int]):
    response=table_nedostaje.get_item(Key={"korisnik_kolekcija": korisnicko_ime})
    
    if "Item" in response:
        item=response["Item"]
        postojeci_brojevi=item.get("brojevi", [])
        
        azurirani_brojevi = [broj for broj in postojeci_brojevi if broj not in brojevi]
        uklonjeni_brojevi=[broj for broj in brojevi if broj in brojevi]
        
        table_nedostaje.update_item(Key={"korisnik_kolekcija":korisnicko_ime},
                                    UpdateExpression="SET brojevi= :val",
                                    ExpressionAttributeValues={":val": uklonjeni_brojevi})
        
        return {"kolekcija_naziv": kolekcija_naziv, "obrisani_br": uklonjeni_brojevi}
    else:
        return {"poruka": "Nepostojeci korisnik ili kolekcija!"}
    
def brisanje_duple_dynamo(korisnicko_ime: str, kolekcija_naziv: str, brojevi: list[int]):
    response=table_duple.get_item(Key={"korisnik_kolekcija": korisnicko_ime})
    
    if "Item" in response:
        item=response["Item"]
        postojeci_brojevi=item.get("brojevi", [])
        
        azurirani_brojevi = [broj for broj in postojeci_brojevi if broj not in brojevi]
        uklonjeni_brojevi=[broj for broj in brojevi if broj in brojevi]
        
        table_duple.update_item(Key={"korisnik_kolekcija":korisnicko_ime},
                                    UpdateExpression="SET brojevi= :val",
                                    ExpressionAttributeValues={":val": uklonjeni_brojevi})
        
        return {"kolekcija_naziv": kolekcija_naziv, "obrisani_br": uklonjeni_brojevi}
    else:
        return {"poruka": "Nepostojeci korisnik ili kolekcija!"}

                                      
def trazi_zamjenu_dynamo(korisnik_trazi: str, korisnik_posjeduje: str, kolekcija: str):
      
    response_nedostaje=table_nedostaje.get_item(Key={"korisnik_kolekcija": korisnik_trazi})
    
    if "Item" not in response_nedostaje or korisnik_trazi == korisnik_posjeduje:
        raise HTTPException(status_code=404, detail= "Pogreška! Korisnik nije pronađen ili nije moguće unijeti dva puta isto korisničko ime!")
    
    nedostaju_slicice=response_nedostaje["Item"].get("brojevi", [])
    
    response_duple=table_duple.scan()
    
    zamjene={}
    
    for item in response_duple.get("Items", []):
        if item.get("kolekcija_naziv") == kolekcija:
            korisnik_nudi = item.get("korisnik_kolekcija")
        
            if korisnik_nudi and korisnik_nudi != korisnik_trazi:
                dohvati_br=item.get("brojevi", [])
                dostupne_slicice=[broj for broj in dohvati_br if broj in nedostaju_slicice]
            
                if dostupne_slicice:
                    if korisnik_nudi not in zamjene:
                        zamjene[korisnik_nudi] = []
                    
                    for broj in dostupne_slicice:
                        zamjene[korisnik_nudi].append(broj)
   
    return {"posjeduje": korisnik_posjeduje, "traži": korisnik_trazi, "kolekcija": kolekcija, "dostupne_sličice": dostupne_slicice }

table_poruke=dynamodb.Table("poruke_db")

def posalji_poruku_dynamo(poruka: Poruka):
    
    if poruka.korisnik_posiljatelj == poruka.korisnik_primatelj:
        raise HTTPException(status_code=422, detail="Ne možete slati poruke samome sebi.")
    
    primatelj_postoji = table.get_item(Key={"korisnicko_ime": poruka.korisnik_primatelj})
    
    if "Item" not in primatelj_postoji:
        raise HTTPException(status_code=404, detail="Korisnik primatelj ne postoji!")
    
    posiljatelj_postoji = table.get_item(Key={"korisnicko_ime": poruka. korisnik_posiljatelj})
       
    if "Item" not in posiljatelj_postoji:
        raise HTTPException(status_code=404, detail="Korisnik posiljatelj ne postoji!")
    
    
    table_poruke.put_item(Item={"korisnik_primatelj": poruka.korisnik_primatelj,
                                "korisnik_posiljatelj": poruka.korisnik_posiljatelj,
                                "poruka": poruka.poruka
                                })
    return poruka
    

def dohvati_poruku_dynamo(primatelj: str):
    response=table_poruke.query(KeyConditionExpression="korisnik_primatelj  = :primatelj",
                                ExpressionAttributeValues={":primatelj":primatelj})    
    
    poruka=response.get("Items", [])
    if not poruka:
        raise HTTPException(status_code=404, detail="Nema poruke za ovoga korisnika!")
    
    return {"primatelj": primatelj, "poruka": poruka}
