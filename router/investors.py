from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.investor import Investor
from schemas.investor import InvestorCreate, InvestorUpdate, InvestorResponse
from typing import List

router = APIRouter(prefix="/api/investors", tags=["investors"])


@router.post("", response_model=InvestorResponse, status_code=status.HTTP_201_CREATED)
def create_investor(investor: InvestorCreate, db: Session = Depends(get_db)):
    """Create a new investor"""
    existing = db.query(Investor).filter(Investor.pan == investor.pan).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Investor with this PAN already exists",
        )

    db_investor = Investor(
        pan=investor.pan, inv_name=investor.inv_name, tax_status=investor.tax_status
    )
    db.add(db_investor)
    db.commit()
    db.refresh(db_investor)
    return db_investor


@router.get("", response_model=List[InvestorResponse])
def get_investors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all investors with pagination"""
    investors = db.query(Investor).offset(skip).limit(limit).all()
    return investors


@router.get("/{pan}", response_model=InvestorResponse)
def get_investor(pan: str, db: Session = Depends(get_db)):
    """Get investor by PAN"""
    investor = db.query(Investor).filter(Investor.pan == pan).first()
    if not investor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Investor not found"
        )
    return investor


@router.put("/{pan}", response_model=InvestorResponse)
def update_investor(
    pan: str, investor: InvestorUpdate, db: Session = Depends(get_db)
):
    """Update investor details"""
    db_investor = db.query(Investor).filter(Investor.pan == pan).first()
    if not db_investor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Investor not found"
        )

    if investor.inv_name is not None:
        db_investor.inv_name = investor.inv_name
    if investor.tax_status is not None:
        db_investor.tax_status = investor.tax_status

    db.commit()
    db.refresh(db_investor)
    return db_investor


@router.delete("/{pan}", status_code=status.HTTP_204_NO_CONTENT)
def delete_investor(pan: str, db: Session = Depends(get_db)):
    """Delete investor by PAN"""
    db_investor = db.query(Investor).filter(Investor.pan == pan).first()
    if not db_investor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Investor not found"
        )

    db.delete(db_investor)
    db.commit()
