from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db
from models.transaction import Transaction
from models.investor import Investor
from models.mutual_fund import MutualFund
from schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
)
from typing import List, Optional
from datetime import date, datetime

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

@router.post(
    "", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED
)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    """Create a new transaction"""
    # Validate investor exists
    investor = db.query(Investor).filter(Investor.pan == transaction.pan).first()
    if not investor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investor not found",
        )

    # Validate mutual fund exists
    fund = db.query(MutualFund).filter(MutualFund.prodcode == transaction.prodcode).first()
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mutual fund not found",
        )

    # Check if transaction already exists
    existing = db.query(Transaction).filter(Transaction.trxn_no == transaction.trxn_no).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction with this number already exists",
        )

    db_transaction = Transaction(
        trxn_no=transaction.trxn_no,
        pan=transaction.pan,
        prodcode=transaction.prodcode,
        trxn_type=transaction.trxn_type,
        trad_date=transaction.trad_date,
        pur_price=transaction.pur_price,
        units=transaction.units,
        amount=transaction.amount,
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.get("", response_model=List[TransactionResponse])
def get_transactions(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """Get all transactions with pagination and optional date range filter"""
    query = db.query(Transaction)
    if start_date:
        query = query.filter(Transaction.trad_date >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(Transaction.trad_date <= datetime.combine(end_date, datetime.max.time()))
    transactions = query.order_by(Transaction.trad_date.desc()).offset(skip).limit(limit).all()
    return transactions


@router.get("/investor/{pan}", response_model=List[TransactionResponse])
def get_transactions_by_investor(
    pan: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Get all transactions for a specific investor"""
    investor = db.query(Investor).filter(Investor.pan == pan).first()
    if not investor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investor not found",
        )

    transactions = (
        db.query(Transaction)
        .filter(Transaction.pan == pan)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return transactions


@router.get("/fund/{prodcode}", response_model=List[TransactionResponse])
def get_transactions_by_fund(
    prodcode: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Get all transactions for a specific mutual fund"""
    fund = db.query(MutualFund).filter(MutualFund.prodcode == prodcode).first()
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mutual fund not found",
        )

    transactions = (
        db.query(Transaction)
        .filter(Transaction.prodcode == prodcode)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return transactions


@router.get("/{trxn_no}", response_model=TransactionResponse)
def get_transaction(trxn_no: int, db: Session = Depends(get_db)):
    """Get transaction by transaction number"""
    transaction = db.query(Transaction).filter(Transaction.trxn_no == trxn_no).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    return transaction


@router.put("/{trxn_no}", response_model=TransactionResponse)
def update_transaction(
    trxn_no: int, transaction: TransactionUpdate, db: Session = Depends(get_db)
):
    """Update transaction details"""
    db_transaction = db.query(Transaction).filter(Transaction.trxn_no == trxn_no).first()
    if not db_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    if transaction.trxn_type is not None:
        db_transaction.trxn_type = transaction.trxn_type
    if transaction.trad_date is not None:
        db_transaction.trad_date = transaction.trad_date
    if transaction.pur_price is not None:
        db_transaction.pur_price = transaction.pur_price
    if transaction.units is not None:
        db_transaction.units = transaction.units
    if transaction.amount is not None:
        db_transaction.amount = transaction.amount

    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.delete("/{trxn_no}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(trxn_no: int, db: Session = Depends(get_db)):
    """Delete transaction by transaction number"""
    db_transaction = db.query(Transaction).filter(Transaction.trxn_no == trxn_no).first()
    if not db_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    db.delete(db_transaction)
    db.commit()
