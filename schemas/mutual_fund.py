from pydantic import BaseModel


class MutualFundBase(BaseModel):
    prodcode: str
    scheme_name: str
    scheme_type: str


class MutualFundCreate(MutualFundBase):
    pass


class MutualFundUpdate(BaseModel):
    scheme_name: str | None = None
    scheme_type: str | None = None


class MutualFundResponse(MutualFundBase):
    class Config:
        from_attributes = True
