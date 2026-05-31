"# Mutual Fund Transaction Dashboard Backend

## Project Links
- Frontend = [https://github.com/Maheshmax1/Wealthified_task_frontend.git]
- Backend = [https://github.com/Maheshmax1/Wealthified_task_Backend.git]
- Document Link = [https://docs.google.com/document/d/1BDeaDOgSq1IVtC4PHP2CphBw6ePu1Mt2sXUA7OVSCFE/edit?usp=sharing]

A FastAPI backend for a mutual fund transaction dashboard that summarizes investor purchases, fund purchases, transaction history, and fund summaries.

---

## Requirements Met
The backend supports data aggregation and filtering for the dashboard, including:

1. Investor-wise purchase totals per mutual fund
2. Mutual fund-wise investor purchase breakdowns
3. Investor list with total investment details
4. Mutual fund summary with total amount, total units, and average NAV price
5. Date-range filtering for all dashboard endpoints
6. Dataset seeding from the repository `dataset.csv`

---

## 1. Prerequisites and Tools Required
To run this backend locally, ensure you have the following installed:

- Python 3.8+
- pip
- A modern web browser for API docs
- Optional: PostgreSQL if using a remote database via `DATABASE_URL`

### Backend Dependencies
This backend uses the Python libraries listed in `Backend/requirements.txt`:

- `fastapi`
- `uvicorn`
- `SQLAlchemy`
- `python-dotenv`
- `psycopg2` (for PostgreSQL support)

---

## 2. How to Setup

### Backend Setup
1. Open a terminal.
2. Navigate to the backend folder:
```bash
cd c:\MAHESH M\Mahesh\mahesh\wellfield_task\wellfeild_task\Backend
```
3. (Optional) Create and activate a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```
4. Install dependencies:
```bash
pip install -r requirements.txt
```

### Optional Database Configuration
If you want to use PostgreSQL instead of local SQLite, create a `.env` file in `Backend/` with:
```env
DATABASE_URL=postgresql://user:password@host:port/dbname
```
If `DATABASE_URL` is not set or a remote database cannot connect, the backend falls back to `sqlite:///./local_dashboard.db`.

### Seed the Database
The backend can seed transaction, investor, and mutual fund data from the project root `dataset.csv`:
```bash
python seed_db.py
```

---

## 3. How to Run the Code

### Start the Backend Server
From the `Backend` directory, run:
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Then open the API docs at:
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

### Open the Frontend
The frontend lives in `../frontend`. Open `../frontend/index.html` in a browser or start a simple local server from the frontend folder.

---

## 4. Dashboard API Endpoints
Base URL: `http://127.0.0.1:8000`

### 1. Investor Purchases
- Endpoint: `GET /api/dashboard/investor-purchases`
- Query Parameters: `start_date` (YYYY-MM-DD), `end_date` (YYYY-MM-DD)
- Returns investor purchase totals grouped by mutual fund.

### 2. Fund Purchases
- Endpoint: `GET /api/dashboard/fund-purchases`
- Query Parameters: `start_date` (YYYY-MM-DD), `end_date` (YYYY-MM-DD)
- Returns mutual fund purchase details with investor breakdowns.

### 3. Investors Summary
- Endpoint: `GET /api/dashboard/investors`
- Query Parameters: `start_date` (YYYY-MM-DD), `end_date` (YYYY-MM-DD)
- Returns a ranked list of investors and their total investments.

### 4. Fund Summary
- Endpoint: `GET /api/dashboard/funds/summary`
- Query Parameters: `start_date` (YYYY-MM-DD), `end_date` (YYYY-MM-DD)
- Returns each scheme with total invested amount, total units, and average NAV price.

---

## 5. Additional Backend APIs
The backend also exposes CRUD endpoints for investors, mutual funds, and transactions:

- `POST /api/investors`, `GET /api/investors`, `GET /api/investors/{pan}`
- `POST /api/mutual-funds`, `GET /api/mutual-funds`, `GET /api/mutual-funds/{prodcode}`
- `POST /api/transactions`, `GET /api/transactions`, `GET /api/transactions/investor/{pan}`
- `GET /api/transactions/fund/{prodcode}`, `GET /api/transactions/{trxn_no}`

---

## Notes
- The backend is designed to power the dashboard with aggregated purchase summaries and filters.
- Use `/docs` for interactive endpoint exploration.
- `seed_db.py` reads `dataset.csv` from the repository root and populates the local or configured database.
" 

