from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, datetime
from typing import Optional, List
from database import get_db
from models.investor import Investor
from models.mutual_fund import MutualFund
from models.transaction import Transaction
from pydantic import BaseModel
from decimal import Decimal

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


# Response Models
class FundPurchaseDetail(BaseModel):
    prodcode: str
    scheme_name: str
    total_amount: Decimal
    total_units: Decimal


class InvestorPurchaseResponse(BaseModel):
    pan: str
    inv_name: str
    funds: List[FundPurchaseDetail]


class InvestorInFundDetail(BaseModel):
    pan: str
    inv_name: str
    amount: Decimal
    units: Decimal


class FundPurchaseResponse(BaseModel):
    prodcode: str
    scheme_name: str
    investors: List[InvestorInFundDetail]


class InvestorSummaryResponse(BaseModel):
    pan: str
    investor_name: str
    total_amount_invested: Decimal


class FundSummaryDetail(BaseModel):
    scheme_name: str
    total_amount_invested_all_investors: Decimal
    total_nav_units_purchased: Decimal
    average_nav_price: Decimal


# Endpoints
@router.get("/investor-purchases", response_model=List[InvestorPurchaseResponse])
def get_investor_purchases(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Groups by investor with their mutual fund purchase totals.
    Returns sum of amount and sum of units for each fund per investor.
    """
    query = db.query(
        Investor.pan,
        Investor.inv_name,
        MutualFund.prodcode,
        MutualFund.scheme_name,
        func.sum(Transaction.amount).label("total_amount"),
        func.sum(Transaction.units).label("total_units"),
    ).join(
        Transaction, Investor.pan == Transaction.pan
    ).join(
        MutualFund, Transaction.prodcode == MutualFund.prodcode
    ).filter(
        Transaction.trxn_type == "Purchase"
    )

    if start_date:
        query = query.filter(Transaction.trad_date >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(Transaction.trad_date <= datetime.combine(end_date, datetime.max.time()))

    query = query.group_by(
        Investor.pan, Investor.inv_name, MutualFund.prodcode, MutualFund.scheme_name
    )

    results = query.all()

    # Organize results into nested structure

    investor_map = {}
    for row in results:
        pan = row[0]
        inv_name = row[1]

        if pan not in investor_map:
            investor_map[pan] = {
                "pan": pan,
                "inv_name": inv_name,
                "funds": [],
            }

        fund_detail = FundPurchaseDetail(
            prodcode=row[2],
            scheme_name=row[3],
            total_amount=row[4],
            total_units=row[5],
        )
        investor_map[pan]["funds"].append(fund_detail)

    return [
        InvestorPurchaseResponse(**investor) for investor in investor_map.values()
    ]


@router.get("/fund-purchases", response_model=List[FundPurchaseResponse])

def get_fund_purchases(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Groups by mutual fund scheme with list of investors who purchased it.
    Returns individual amount and unit sums for each investor per fund.
    """
    query = db.query(
        MutualFund.prodcode,
        MutualFund.scheme_name,
        Investor.pan,
        Investor.inv_name,
        func.sum(Transaction.amount).label("total_amount"),
        func.sum(Transaction.units).label("total_units"),
    ).join(
        Transaction, MutualFund.prodcode == Transaction.prodcode
    ).join(
        Investor, Transaction.pan == Investor.pan
    ).filter(
        Transaction.trxn_type == "Purchase"
    )

    if start_date:
        query = query.filter(Transaction.trad_date >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(Transaction.trad_date <= datetime.combine(end_date, datetime.max.time()))

    query = query.group_by(
        MutualFund.prodcode, MutualFund.scheme_name, Investor.pan, Investor.inv_name
    )

    results = query.all()

    # Organize results into nested structure
    fund_map = {}
    for row in results:
        prodcode = row[0]
        scheme_name = row[1]

        if prodcode not in fund_map:
            fund_map[prodcode] = {
                "prodcode": prodcode,
                "scheme_name": scheme_name,
                "investors": [],
            }

        investor_detail = InvestorInFundDetail(
            pan=row[2],
            inv_name=row[3],
            amount=row[4],
            units=row[5],
        )
        fund_map[prodcode]["investors"].append(investor_detail)

    return [FundPurchaseResponse(**fund) for fund in fund_map.values()]


@router.get("/investors", response_model=List[InvestorSummaryResponse])
def get_investors(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Returns a flat list of investors with total investment amount within date range.
    Sorted from highest to lowest investment.
    """
    query = db.query(
        Investor.pan,
        Investor.inv_name,
        func.sum(Transaction.amount).label("total_amount"),
    ).join(
        Transaction, Investor.pan == Transaction.pan
    ).filter(
        Transaction.trxn_type == "Purchase"
    )

    if start_date:
        query = query.filter(Transaction.trad_date >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(Transaction.trad_date <= datetime.combine(end_date, datetime.max.time()))

    query = query.group_by(Investor.pan, Investor.inv_name).order_by(
        func.sum(Transaction.amount).desc()
    )

    results = query.all()

    return [
        InvestorSummaryResponse(
            pan=row[0],
            investor_name=row[1],
            total_amount_invested=row[2],
        )
        for row in results
    ]


@router.get("/funds/summary", response_model=List[FundSummaryDetail])
def get_funds_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Returns macro summary of all funds with total investment, total units, and average price.
    """
    query = db.query(
        MutualFund.scheme_name,
        func.sum(Transaction.amount).label("total_amount"),
        func.sum(Transaction.units).label("total_units"),
        func.avg(Transaction.pur_price).label("average_price"),
    ).join(
        Transaction, MutualFund.prodcode == Transaction.prodcode
    ).filter(
        Transaction.trxn_type == "Purchase"
    )

    if start_date:
        query = query.filter(Transaction.trad_date >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(Transaction.trad_date <= datetime.combine(end_date, datetime.max.time()))

    query = query.group_by(MutualFund.scheme_name)

    results = query.all()

    return [
        FundSummaryDetail(
            scheme_name=row[0],
            total_amount_invested_all_investors=row[1],
            total_nav_units_purchased=row[2],
            average_nav_price=row[3],
        )
        for row in results
    ]
