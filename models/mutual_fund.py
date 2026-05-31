from sqlalchemy import Column, String
from database import Base


class MutualFund(Base):
    __tablename__ = "mutual_fund"

    prodcode = Column(String(50), primary_key=True, nullable=False)
    scheme_name = Column(String(255), nullable=False)
    scheme_type = Column(String(50), nullable=False)
