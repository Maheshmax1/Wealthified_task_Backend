from sqlalchemy import Column, BIGINT, String, DateTime, Numeric, ForeignKey
from database import Base


class Transaction(Base):
    __tablename__ = "transaction"

    trxn_no = Column(BIGINT, primary_key=True, nullable=False)
    pan = Column(String(50), ForeignKey("investor.pan"), nullable=False)
    prodcode = Column(String(50), ForeignKey("mutual_fund.prodcode"), nullable=False)
    trxn_type = Column(String(50), nullable=False)
    trad_date = Column(DateTime, nullable=False)
    pur_price = Column(Numeric(18, 4), nullable=False)
    units = Column(Numeric(18, 4), nullable=False)
    amount = Column(Numeric(18, 2), nullable=False)
