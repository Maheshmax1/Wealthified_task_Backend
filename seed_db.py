import csv
import os
import sys
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session

# Add the current directory to sys.path so we can import local modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal, Base
from models.investor import Investor
from models.mutual_fund import MutualFund
from models.transaction import Transaction

def seed_database():
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'dataset.csv')
    
    if not os.path.exists(csv_path):
        print(f"Error: dataset.csv not found at {csv_path}")
        return

    print("Connecting to database and creating tables if they do not exist...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    print("Reading and parsing dataset.csv...")
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            # We specify quotechar="'" because the CSV uses single quotes for encapsulation
            reader = csv.DictReader(f, quotechar="'")
            
            investors_count = 0
            funds_count = 0
            transactions_count = 0
            
            for row_idx, row in enumerate(reader, 1):
                pan = row['PAN'].strip()
                inv_name = row['INV_NAME'].strip()
                tax_status = row['TAX_STATUS'].strip()
                
                prodcode = row['PRODCODE'].strip()
                scheme_name = row['SCHEME'].strip()
                scheme_type = row['SCHEME_TYPE'].strip()
                
                trxn_no = int(row['TRXNNO'])
                pur_price = Decimal(row['PURPRICE'])
                units = Decimal(row['UNITS'])
                amount = Decimal(row['AMOUNT'])
                
                # Parse date e.g. "5/27/2025 12:00:00 AM"
                trad_date_str = row['TRADDATE'].strip()
                try:
                    trad_date = datetime.strptime(trad_date_str, '%m/%d/%Y %I:%M:%S %p')
                except ValueError:
                    # Fallback parse
                    trad_date = datetime.strptime(trad_date_str.split()[0], '%m/%d/%Y')
                
                # Determine transaction type (Purchase vs Redemption)
                trxn_nature = row['TRXN_NATURE'].strip().lower()
                trxn_subtyp = row['TRXNSUBTYP'].strip().lower()
                
                if 'out' in trxn_nature or 'redemption' in trxn_nature or 'redeem' in trxn_nature or 'switch out' in trxn_nature or 'out' in trxn_subtyp:
                    trxn_type = 'Redemption'
                else:
                    trxn_type = 'Purchase'
                
                # 1. Upsert Investor
                db_investor = db.query(Investor).filter(Investor.pan == pan).first()
                if not db_investor:
                    db_investor = Investor(
                        pan=pan,
                        inv_name=inv_name,
                        tax_status=tax_status
                    )
                    db.add(db_investor)
                    db.flush()  # Push to get DB state without commit yet
                    investors_count += 1
                
                # 2. Upsert MutualFund
                db_fund = db.query(MutualFund).filter(MutualFund.prodcode == prodcode).first()
                if not db_fund:
                    db_fund = MutualFund(
                        prodcode=prodcode,
                        scheme_name=scheme_name,
                        scheme_type=scheme_type
                    )
                    db.add(db_fund)
                    db.flush()
                    funds_count += 1
                
                # 3. Upsert Transaction
                db_txn = db.query(Transaction).filter(Transaction.trxn_no == trxn_no).first()
                if not db_txn:
                    db_txn = Transaction(
                        trxn_no=trxn_no,
                        pan=pan,
                        prodcode=prodcode,
                        trxn_type=trxn_type,
                        trad_date=trad_date,
                        pur_price=pur_price,
                        units=units,
                        amount=amount
                    )
                    db.add(db_txn)
                    transactions_count += 1
            
            db.commit()
            print("\nDatabase Seeding Completed Successfully!")
            print(f"=====================================")
            print(f"Registered new Investors: {investors_count}")
            print(f"Registered new Mutual Schemes: {funds_count}")
            print(f"Registered new Transaction Ledgers: {transactions_count}")
            print(f"Total CSV lines parsed: {row_idx}")
            
    except Exception as e:
        db.rollback()
        print(f"\nError seeding database: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    seed_database()
