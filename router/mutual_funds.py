from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.mutual_fund import MutualFund
from schemas.mutual_fund import MutualFundCreate, MutualFundUpdate, MutualFundResponse
from typing import List

router = APIRouter(prefix="/api/mutual-funds", tags=["mutual_funds"])


@router.post("", response_model=MutualFundResponse, status_code=status.HTTP_201_CREATED)
def create_mutual_fund(fund: MutualFundCreate, db: Session = Depends(get_db)):
    """Create a new mutual fund"""
    existing = db.query(MutualFund).filter(MutualFund.prodcode == fund.prodcode).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mutual fund with this product code already exists",
        )

    db_fund = MutualFund(
        prodcode=fund.prodcode,
        scheme_name=fund.scheme_name,
        scheme_type=fund.scheme_type,
    )
    db.add(db_fund)
    db.commit()
    db.refresh(db_fund)
    return db_fund


@router.get("", response_model=List[MutualFundResponse])
def get_mutual_funds(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all mutual funds with pagination"""
    funds = db.query(MutualFund).offset(skip).limit(limit).all()
    return funds


@router.get("/{prodcode}", response_model=MutualFundResponse)
def get_mutual_fund(prodcode: str, db: Session = Depends(get_db)):
    """Get mutual fund by product code"""
    fund = db.query(MutualFund).filter(MutualFund.prodcode == prodcode).first()
    if not fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mutual fund not found"
        )
    return fund


@router.put("/{prodcode}", response_model=MutualFundResponse)
def update_mutual_fund(
    prodcode: str, fund: MutualFundUpdate, db: Session = Depends(get_db)
):
    """Update mutual fund details"""
    db_fund = db.query(MutualFund).filter(MutualFund.prodcode == prodcode).first()
    if not db_fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mutual fund not found"
        )

    if fund.scheme_name is not None:
        db_fund.scheme_name = fund.scheme_name
    if fund.scheme_type is not None:
        db_fund.scheme_type = fund.scheme_type

    db.commit()
    db.refresh(db_fund)
    return db_fund


@router.delete("/{prodcode}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mutual_fund(prodcode: str, db: Session = Depends(get_db)):
    """Delete mutual fund by product code"""
    db_fund = db.query(MutualFund).filter(MutualFund.prodcode == prodcode).first()
    if not db_fund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Mutual fund not found"
        )

    db.delete(db_fund)
    db.commit()
