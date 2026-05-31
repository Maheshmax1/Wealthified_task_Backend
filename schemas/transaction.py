from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal


class TransactionBase(BaseModel):
    pan: str
    prodcode: str
    trxn_type: str
    trad_date: datetime
    pur_price: Decimal
    units: Decimal
    amount: Decimal


class TransactionCreate(TransactionBase):
    trxn_no: int


class TransactionUpdate(BaseModel):
    trxn_type: str | None = None
    trad_date: datetime | None = None
    pur_price: Decimal | None = None
    units: Decimal | None = None
    amount: Decimal | None = None


class TransactionResponse(TransactionBase):
    trxn_no: int

    class Config:
        from_attributes = True
