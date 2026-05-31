from sqlalchemy import Column, String
from database import Base


class Investor(Base):
    __tablename__ = "investor"

    pan = Column(String(50), primary_key=True, nullable=False)
    inv_name = Column(String(255), nullable=False)
    tax_status = Column(String(50), nullable=False)
