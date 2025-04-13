from pydantic import BaseModel, Field
    
class Recenzija(BaseModel):
    korisnik_salje_recenziju: str
    korisnik_prima_recenziju: str
    recenzija: str = Field(min_length=1)
    ocjena: int = Field (ge=1, le=5)
    
