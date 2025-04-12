import boto3
from botocore.exceptions import ClientError
from kolekcija.models import *
from fastapi import HTTPException
from passlib.context import CryptContext
import uuid


s3 = boto3.client('s3')

client = boto3.client('dynamodb',
    endpoint_url='http://localhost:8000',
    region_name='eu-central-1',
    aws_access_key_id='dummy',
    aws_secret_access_key='dummy')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def dodaj_kolekcije():
    
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

    
    kolekcija_id = 1

    
    for kolekcija in dostupne_kolekcije:
        response = client.put_item(
            TableName='dostupne_kolekcije',
            Item={
                'kolekcija_id': {'S': str(kolekcija_id)},  
                'kolekcija_naziv': {'S': kolekcija['kolekcija_naziv']}
            }
        )
             
        
        kolekcija_id += 1


dodaj_kolekcije()

kolekcije_sa_brojevima = [
    {"kolekcija_id": "1", "kolekcija_naziv": "KONZUM Zvjerići 3 Safari", "brojevi": list(range(1, 131))},
    {"kolekcija_id": "2", "kolekcija_naziv": "LaLiga 2024-2025", "brojevi": list(range(1, 774))},
    {"kolekcija_id": "3", "kolekcija_naziv": "FIFA 365 2025", "brojevi": list(range(1, 423))},
    {"kolekcija_id": "4", "kolekcija_naziv": "Foot 2024-2025", "brojevi": list(range(1, 577))},
    {"kolekcija_id": "5", "kolekcija_naziv": "Hrvatska Nogometna Liga 2024-2025", "brojevi": list(range(1, 361))},
    {"kolekcija_id": "6", "kolekcija_naziv": "English Premier League 2024-2025", "brojevi": list(range(1, 765))},
    {"kolekcija_id": "7", "kolekcija_naziv": "Calciatori 2024-2025", "brojevi": list(range(1, 927))},
    {"kolekcija_id": "8", "kolekcija_naziv": "UEFA Champions League 2024-2025", "brojevi": list(range(1, 664))}
]

def dodaj_kolekcije_brojevi():
    for kolekcija in kolekcije_sa_brojevima:
        response = client.put_item(
            TableName='kolekcije_brojevi',
            Item={
                'kolekcija_id': {'S': kolekcija['kolekcija_id']},
                'kolekcija_naziv': {'S': kolekcija['kolekcija_naziv']},
                'brojevi': {'L': [{'N': str(broj)} for broj in kolekcija['brojevi']]}
            }
        )
        
dodaj_kolekcije_brojevi()

def dohvati_kolekciju_dynamo():
    try:
        response = client.scan(TableName="dostupne_kolekcije")
    
        items = response.get('Items', [])
        if not items:
    
            return "Kolekcija ne sadrži ništa"
        print(items)
        return items    
    
    except ClientError as e:
        print(f"Pogreška pri dohvatu podataka {e}")
        
def dohvati_kolekciju_sa_brojevima_dynamo(kolekcija_naziv: str, kolekcija_id: str):
    
    response = client.get_item(TableName="kolekcije_brojevi",
                                Key={"kolekcija_id": {"S": kolekcija_id}})
    
    if "Item" not in response:
        raise HTTPException(status_code=400, detail="Kolekcija ne postoji!") 
    
    brojevi = response['Item'].get('broj', {}).get('L', [])
    
    brojevi_lista = [int(broj['N']) for broj in brojevi]
    
    return {"kolekcija_naziv": kolekcija_naziv, "brojevi": brojevi_lista}

def dodaj_kolekciju_dynamo(kolekcija_naziv: str, broj: int):
    response = client.get_item(TableName="dostupne_kolekcije",
                                Key={"kolekcija_naziv": {"S": kolekcija_naziv}})
    
    if "Item" in response:
        raise HTTPException(status_code=400, detail="Kolekcija postoji!") 
    
    dodani_brojevi=list(range(1, broj+1))
    
    response_scan = client.scan(TableName="kolekcije_brojevi")
    broj_kolekcija = len(response_scan.get("Items", []))

    kolekcija_id = str(broj_kolekcija + 1) 
    
    client.put_item(TableName="kolekcije_brojevi", 
                    Item={"kolekcija_id": {"S": kolekcija_id},
                          "kolekcija_naziv": {"S": kolekcija_naziv},
                          "brojevi": {"L": [{"N": str(broj)} for broj in dodani_brojevi]}})
                    
    client.put_item(TableName="dostupne_kolekcije",
                    Item={"kolekcija_naziv": {"S": kolekcija_naziv}})
    
    return {"kolekcija_naziv": kolekcija_naziv, "brojevi": dodani_brojevi}

def kolekcija_izmjena_dynamo(kolekcija_id: str, kolekcija_naziv: str, brojevi: list[int]):
   try:
        response = client.get_item(TableName="kolekcije_brojevi", Key={"kolekcija_id": { "S": kolekcija_id}})
       
        item = response.get("Item")

        if not item:
            raise HTTPException(status_code=404, detail="Kolekcija ne postoji!")
    
        postojeci_brojevi = item.get("brojevi", {}).get("L", [])
        postojeci_brojevi = [broj["N"] for broj in postojeci_brojevi]
    
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

            return {"kolekcija": kolekcija_naziv, "dodani_brojevi": novi_brojevi}

        else:
            return {"poruka" : "Ne postoje novi brojevi za dodati u kolekciju"}
        
   except Exception as e:
       raise HTTPException(status_code=500, detail=f"Ažuriranje nije uspjelo str{e}")
   
def unos_nedostaje_dynamo(korisnicko_ime: str, kolekcija_naziv: str, brojevi: list[int]):
    try:
        response=client.get_item(TableName="korisnik_nedostaje_db", Key={"korisnicko_ime": {"S":  korisnicko_ime}})
    
        if "Item" in response:
            item = response["Item"]
        
            postojeci_brojevi = item.get("brojevi", {}).get("L", [])
            postojeci_brojevi = [broj["N"] for broj in postojeci_brojevi]
        
            novi_brojevi = [broj for broj in brojevi if str(broj) not in postojeci_brojevi]
        
            if novi_brojevi:
            
                azurirani_brojevi = postojeci_brojevi + novi_brojevi

                client.update_item(TableName="korisnik_nedostaje_db",
                Key={"korisnicko_ime": {"S": korisnicko_ime}},
                UpdateExpression="SET brojevi = :val",
                ExpressionAttributeValues={ ":val": {"L": [{"N": str(broj)} for broj in azurirani_brojevi]}}
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
            postojeci_brojevi=item.get("brojevi", {}).get("L", [])
            postojeci_brojevi = [broj["N"] for broj in postojeci_brojevi]
            
            uklonjeni_brojevi = [broj for broj in brojevi if str(broj) in postojeci_brojevi]
        
            azurirani_brojevi = [broj for broj in postojeci_brojevi if broj not in brojevi]
            
        
            client.update_item(TableName="korisnik_nedostaje_db",
                Key={"korisnicko_ime": {"S": korisnicko_ime}},
                                    UpdateExpression="SET brojevi= :val",
                                    ExpressionAttributeValues={
                                        ":val": {"L": [{"N": str(broj)} for broj in azurirani_brojevi]}})
        
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
            
            postojeci_brojevi=item.get("brojevi", {}).get("L", [])
            postojeci_brojevi = [broj["N"] for broj in postojeci_brojevi] 
            
            uklonjeni_brojevi=[broj for broj in brojevi if str(broj) in  postojeci_brojevi]
            
            azurirani_brojevi = [broj for broj in postojeci_brojevi if broj not in uklonjeni_brojevi]
            
        
            client.update_item(TableName="korisnik_duple_db",
                Key={"korisnicko_ime":  {"S": korisnicko_ime}},
                                    UpdateExpression="SET brojevi= :val",
                                    ExpressionAttributeValues={
                                        ":val": {"L": [{"N": str(broj)} for broj in azurirani_brojevi]}}
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
    
        if "Item" not in response_nedostaje or korisnicko_ime == korisnik_posjeduje:
            raise HTTPException(status_code=404,
                            detail= "Pogreška! Korisnik nije pronađen ili nije moguće unijeti dva puta isto korisničko ime!")
    
        nedostaju_slicice=response_nedostaje["Item"].get("brojevi", {}).get("L", [])
        nedostaju_slicice = [int(broj["N"]) for broj in nedostaju_slicice]
        
        zamjene={}
    
        response_duple=client.scan(TableName="korisnik_duple_db",
                                FilterExpression="kolekcija_naziv= :kolekcija",
                                ExpressionAttributeValues={":kolekcija": {"S":kolekcija}})
    
        for item in response_duple.get("Items", []):
            korisnik_nudi = item.get("korisnik_posjeduje", {}).get("S")
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
        
def posalji_poruku_dynamo(poruka: Poruka):
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

def dohvati_poruku_dynamo(primatelj: str):
    try:
        response=client.query(TableName="poruke_db",
            KeyConditionExpression="korisnik_primatelj  = :primatelj",
                                ExpressionAttributeValues={":primatelj":{"S": primatelj}})   
    
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
        
        return {"primatelj": primatelj, "poruka": rezultat}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška pri dohvaćanju poruka: {str(e)}")
        
def dodavanje_recenzije_dynamo(recenzija: Recenzija):
    if not recenzija.korisnik_prima_recenziju:
        raise HTTPException(status_code=404, detail="Potrebno je unijeti korisnika na kojega se recenzija odnosi!")
    
    try:
    
        korisnik_postoji=client.get_item(TableName="recenzije_sa_ocjenama_db",
            Key={"korisnik_kolekcija":{"S":recenzija.korisnik_prima_recenziju}})
    
        if "Item" not in korisnik_postoji:
            raise HTTPException(status_code=404, detail="Sa korisnikom niste mogli obaviti zamjenu!")
    
        client.put_item(TableName="recenzije_sa_ocjenam_db",
            Item={"korisnik_prima_recenziju":{"S":recenzija.korisnik_prima_recenziju},
                    "korisnik_salje_recenziju":{"S":recenzija.korisnik_salje_recenziju},
                    "ocjena":{"N":recenzija.ocjena},
                    "recenzija":{"S": recenzija.recenzija}})
    
        return {"prima": recenzija.korisnik_prima_recenziju,
            "salje": recenzija.korisnik_salje_recenziju,
            "recenzija": recenzija.recenzija,
            "ocjena": recenzija.ocjena}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Greška prilikom dohvaćanja ocjena: {str(e)}")
    
def prikaz_recenzija_dynamo(korisnik_prima_recenziju: str):
    try:
        response=client.scan(TableName="recenzije_sa_ocjenama_db",
            FilterExpression="korisnik_prima_recenziju = :val",
            ExpressionAttributeValues={":val": {"S": korisnik_prima_recenziju}})

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

        return {"korisnik": korisnik_prima_recenziju, "recenzija": recenzije, "ocjena": round(prosjek, 2)}
    
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