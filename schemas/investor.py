from pydantic import BaseModel


class InvestorBase(BaseModel):
    pan: str
    inv_name: str
    tax_status: str


class InvestorCreate(InvestorBase):
    pass


class InvestorUpdate(BaseModel):
    inv_name: str | None = None
    tax_status: str | None = None


class InvestorResponse(InvestorBase):
    class Config:
        from_attributes = True
